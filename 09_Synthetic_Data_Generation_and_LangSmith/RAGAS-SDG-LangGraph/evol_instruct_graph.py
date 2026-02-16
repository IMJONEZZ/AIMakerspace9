from typing import List, Dict, TypedDict, Annotated, Literal, Any, cast
import operator
import uuid
import random

from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from evolution_nodes import (
    simple_evolution_node,
    multi_context_evolution_node,
    reasoning_evolution_node,
)
from qa_context_nodes import generate_answers_node, retrieve_contexts_node


def merge_lists(left: List, right: List) -> List:
    """Merge two lists by concatenating them.

    Args:
        left: First list to merge
        right: Second list to merge

    Returns:
        Concatenated list containing all elements from both input lists
    """
    return left + right


class EvolutionConfig(TypedDict):
    """Configuration for the evolution process.

    Attributes:
        evolution_mode: Either 'all' to run all evolutions sequentially or
                       'selective' to route based on document characteristics
        evolution_ratios: Dictionary mapping evolution types to their weights
        min_doc_length_for_reasoning: Minimum average document length required
                                      for reasoning evolution
        max_doc_count_for_simple: Maximum document count to still use simple evolution
    """

    evolution_mode: Literal["all", "selective"]
    evolution_ratios: Dict[str, float]
    min_doc_length_for_reasoning: int
    max_doc_count_for_simple: int


class EvolInstructState(TypedDict):
    """State for the EvolInstruct synthetic data generation pipeline.

    Attributes:
        documents: List of input documents to process
        evolved_questions: Accumulated list of evolved questions across all steps
        q_a_pairs: Question-answer pairs generated for evolved questions
        contexts: Retrieved contexts for each question
        current_step: Current step in the evolution pipeline
        evolution_config: Configuration parameters for the evolution process
        doc_characteristics: Analyzed characteristics of input documents
        selected_evolutions: List of evolution types already executed
    """

    documents: List[Document]

    evolved_questions: Annotated[List[Dict[str, str]], merge_lists]

    q_a_pairs: Annotated[List[Dict[str, str]], merge_lists]

    contexts: Annotated[List[Dict[str, str]], merge_lists]

    current_step: str

    evolution_config: EvolutionConfig

    doc_characteristics: Dict[str, Any]

    selected_evolutions: Annotated[List[str], merge_lists]


def analyze_document_characteristics(state: EvolInstructState) -> Dict:
    """Analyze characteristics of input documents for intelligent routing.

    Calculates metrics including document count, average length, total length,
    and vocabulary complexity to inform evolution type selection.

    Args:
        state: Current pipeline state containing documents

    Returns:
        Updated state with doc_characteristics field populated
    """
    documents = state.get("documents", [])

    if not documents:
        return {**state, "doc_characteristics": {}}

    total_length = sum(len(doc.page_content) for doc in documents)
    avg_length = total_length / len(documents) if documents else 0
    doc_count = len(documents)

    unique_words = set()
    for doc in documents:
        words = doc.page_content.lower().split()
        unique_words.update(words)

    vocabulary_complexity = len(unique_words) / total_length if total_length > 0 else 0

    characteristics = {
        "doc_count": doc_count,
        "avg_length": avg_length,
        "total_length": total_length,
        "vocabulary_complexity": vocabulary_complexity,
    }

    return {**state, "doc_characteristics": characteristics}


def select_evolution_type(
    state: EvolInstructState,
) -> Literal["simple", "multi_context", "reasoning"]:
    """Select the next evolution type based on configuration and document characteristics.

    In 'all' mode, cycles through all evolution types sequentially.
    In 'selective' mode, uses weighted random selection based on document
    characteristics and configured ratios.

    Args:
        state: Current pipeline state with configuration and document analysis

    Returns:
        Selected evolution type as a string literal
    """
    config = state.get("evolution_config", {})
    mode = config.get("evolution_mode", "all")
    ratios = config.get(
        "evolution_ratios", {"simple": 0.33, "multi_context": 0.34, "reasoning": 0.33}
    )

    if mode == "all":
        selected = state.get("selected_evolutions", [])

        if "simple" not in selected:
            return "simple"
        elif "multi_context" not in selected:
            return "multi_context"
        elif "reasoning" not in selected:
            return "reasoning"
        else:
            return "simple"

    characteristics = state.get("doc_characteristics", {})
    selected = state.get("selected_evolutions", [])

    doc_count = characteristics.get("doc_count", 0)
    avg_length = characteristics.get("avg_length", 0)
    complexity = characteristics.get("vocabulary_complexity", 0)

    min_reasoning_length = config.get("min_doc_length_for_reasoning", 300)
    max_simple_count = config.get("max_doc_count_for_simple", 5)

    remaining_evolutions = ["simple", "multi_context", "reasoning"]
    for e in selected:
        if e in remaining_evolutions:
            remaining_evolutions.remove(e)

    if not remaining_evolutions:
        return "simple"

    weighted_choices = []
    for evo_type in remaining_evolutions:
        weight = ratios.get(evo_type, 0.33)

        if evo_type == "reasoning" and avg_length < min_reasoning_length:
            weight *= 0.3

        if evo_type == "simple" and doc_count > max_simple_count:
            weight *= 0.5

        if evo_type == "multi_context" and doc_count < 2:
            weight *= 0.1

        weighted_choices.append((weight, evo_type))

    total_weight = sum(w for w, _ in weighted_choices)
    if total_weight == 0:
        return cast(
            Literal["simple", "multi_context", "reasoning"], remaining_evolutions[0]
        )

    rand_val = random.random() * total_weight
    cumulative = 0

    for weight, evo_type in sorted(weighted_choices):
        cumulative += weight
        if rand_val <= cumulative:
            return cast(Literal["simple", "multi_context", "reasoning"], evo_type)

    return cast(
        Literal["simple", "multi_context", "reasoning"], remaining_evolutions[0]
    )


def track_evolution_selection(state: EvolInstructState, evolution_type: str) -> Dict:
    """Track which evolution types have been executed.

    Adds the evolution type to the selected_evolutions list if not already present.

    Args:
        state: Current pipeline state
        evolution_type: The evolution type that was just executed

    Returns:
        Updated state with selected_evolutions list updated
    """
    selected = state.get("selected_evolutions", [])
    if evolution_type not in selected:
        selected.append(evolution_type)

    return {**state, "selected_evolutions": selected}


def should_continue_evolution(
    state: EvolInstructState,
) -> Literal["continue", "generate_answers"]:
    """Determine whether to continue evolution or proceed to answer generation.

    In 'all' mode, continues until all three evolution types have been executed.
    In 'selective' mode, stops after at least one suitable evolution has run
    or when no more evolutions are appropriate for the document characteristics.

    Args:
        state: Current pipeline state with configuration and evolution tracking

    Returns:
        'continue' to run more evolutions or 'generate_answers' to proceed
    """
    config = state.get("evolution_config", {})
    mode = config.get("evolution_mode", "all")

    if mode == "all":
        selected = state.get("selected_evolutions", [])
        required = ["simple", "multi_context", "reasoning"]

        if all(e in selected for e in required):
            return "generate_answers"
        else:
            return "continue"

    characteristics = state.get("doc_characteristics", {})
    selected = state.get("selected_evolutions", [])

    doc_count = characteristics.get("doc_count", 0)
    avg_length = characteristics.get("avg_length", 0)

    min_reasoning_length = config.get("min_doc_length_for_reasoning", 300)
    max_simple_count = config.get("max_doc_count_for_simple", 5)

    available_evolutions = []

    if "simple" not in selected and doc_count <= max_simple_count:
        available_evolutions.append("simple")

    if "multi_context" not in selected and doc_count >= 2:
        available_evolutions.append("multi_context")

    if "reasoning" not in selected and avg_length >= min_reasoning_length:
        available_evolutions.append("reasoning")

    if available_evolutions and len(selected) < 2:
        return "continue"

    return "generate_answers"


def create_evol_instruct_graph():
    """Create a basic evolved instruction graph with sequential execution.

    This graph runs all three evolution types in sequence:
    1. Simple evolution (paraphrasing)
    2. Multi-context evolution (synthesizing across documents)
    3. Reasoning evolution (adding complexity)

    Returns:
        Compiled StateGraph ready for execution
    """
    workflow = StateGraph(EvolInstructState)

    workflow.add_node("simple_evolution", simple_evolution_node)
    workflow.add_node("multi_context_evolution", multi_context_evolution_node)
    workflow.add_node("reasoning_evolution", reasoning_evolution_node)
    workflow.add_node("generate_answers", generate_answers_node)
    workflow.add_node("retrieve_contexts", retrieve_contexts_node)

    workflow.add_edge(START, "simple_evolution")
    workflow.add_edge("simple_evolution", "multi_context_evolution")
    workflow.add_edge("multi_context_evolution", "reasoning_evolution")
    workflow.add_edge("reasoning_evolution", "generate_answers")
    workflow.add_edge("generate_answers", "retrieve_contexts")
    workflow.add_edge("retrieve_contexts", END)

    graph = workflow.compile()

    return graph


def create_evol_instruct_graph_with_routing():
    """Create an evolved instruction graph with intelligent routing.

    This graph uses conditional edges to route between evolution types
    based on document characteristics and configuration. It analyzes
    documents first, then selectively applies evolution types.

    Returns:
        Compiled StateGraph with routing logic ready for execution
    """
    workflow = StateGraph(EvolInstructState)

    workflow.add_node("analyze_docs", analyze_document_characteristics)
    workflow.add_node("simple_evolution", simple_evolution_node)
    workflow.add_node("multi_context_evolution", multi_context_evolution_node)
    workflow.add_node("reasoning_evolution", reasoning_evolution_node)
    workflow.add_node("generate_answers", generate_answers_node)
    workflow.add_node("retrieve_contexts", retrieve_contexts_node)

    workflow.add_edge(START, "analyze_docs")

    workflow.add_conditional_edges(
        "analyze_docs",
        select_evolution_type,
        {
            "simple": "simple_evolution",
            "multi_context": "multi_context_evolution",
            "reasoning": "reasoning_evolution",
        },
    )

    workflow.add_conditional_edges(
        "simple_evolution",
        should_continue_evolution,
        {
            "continue": "analyze_docs",
            "generate_answers": "generate_answers",
        },
    )

    workflow.add_conditional_edges(
        "multi_context_evolution",
        should_continue_evolution,
        {
            "continue": "analyze_docs",
            "generate_answers": "generate_answers",
        },
    )

    workflow.add_conditional_edges(
        "reasoning_evolution",
        should_continue_evolution,
        {
            "continue": "analyze_docs",
            "generate_answers": "generate_answers",
        },
    )

    workflow.add_edge("generate_answers", "retrieve_contexts")
    workflow.add_edge("retrieve_contexts", END)

    graph = workflow.compile()

    return graph


evol_instruct_graph = create_evol_instruct_graph()
evol_instruct_graph_routing = create_evol_instruct_graph_with_routing()


def run_evol_instruct_sdg(
    documents: List[Document],
    evolution_mode: Literal["all", "selective"] = "all",
    evolution_ratios: Dict[str, float] | None = None,
) -> Dict[str, List[Dict]]:
    if evolution_ratios is None:
        evolution_ratios = {"simple": 0.33, "multi_context": 0.34, "reasoning": 0.33}

    evolution_config = EvolutionConfig(
        evolution_mode=evolution_mode,
        evolution_ratios=evolution_ratios,
        min_doc_length_for_reasoning=300,
        max_doc_count_for_simple=5,
    )

    initial_state = EvolInstructState(
        documents=documents,
        evolved_questions=[],
        q_a_pairs=[],
        contexts=[],
        current_step="",
        evolution_config=evolution_config,
        doc_characteristics={},
        selected_evolutions=[],
    )

    if evolution_mode == "selective":
        graph_to_use = evol_instruct_graph_routing
    else:
        graph_to_use = evol_instruct_graph

    final_state = graph_to_use.invoke(initial_state)

    evolved_questions_output = []
    for idx, q in enumerate(final_state.get("evolved_questions", [])):
        evolved_questions_output.append(
            {
                "id": q.get("question_id") or f"q_{idx}",
                "question": q.get("question", ""),
                "evolution_type": q.get("evolution_type"),
            }
        )

    q_a_pairs_output = []
    for qa in final_state.get("q_a_pairs", []):
        q_a_pairs_output.append(
            {"question_id": qa.get("question_id"), "answer": qa.get("answer", "")}
        )

    contexts_output = []
    for ctx in final_state.get("contexts", []):
        contexts_output.append(
            {
                "question_id": ctx.get("question_id"),
                "relevant_contexts": ctx.get("relevant_contexts", []),
            }
        )

    return {
        "evolved_questions": evolved_questions_output,
        "q_a_pairs": q_a_pairs_output,
        "contexts": contexts_output,
    }


def setup_vector_store(
    documents: List[Document],
    collection_name: str = "evol_instruct_docs",
    location: str = ":memory:",
) -> QdrantVectorStore:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-nomic-embed-text-v2-moe",
        check_embedding_ctx_length=False,
    )

    vector_store = QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        location=location,
        collection_name=collection_name,
    )

    return vector_store


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = text_splitter.split_documents(documents)

    return chunks
