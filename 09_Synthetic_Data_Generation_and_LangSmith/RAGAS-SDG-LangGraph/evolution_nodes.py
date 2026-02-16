from typing import Dict, List
import json

from langchain_core.messages import HumanMessage, SystemMessage
from openai import OpenAI


class EvolInstructNode:
    def __init__(self):
        self.client = OpenAI(base_url="http://192.168.1.79:8080/v1", api_key="dummy")
        self.model = "glm-4.7"


def simple_evolution_node(state: Dict) -> Dict:
    node = EvolInstructNode()

    documents = state.get("documents", [])
    evolved_questions = state.get("evolved_questions", [])

    if not documents:
        return {**state, "current_step": "simple_evolution_skipped"}

    prompt = """You are a question evolution expert. Your task is to take a simple base question and create a slightly modified version through paraphrasing or rewording.

Instructions:
1. Read the base question and its context
2. Create a new version that:
   - Paraphrases the original meaning using different words
   - Maintains the same core question intent
   - Changes sentence structure or wording slightly
   - Keeps similar complexity level

3. Return ONLY a valid JSON object with this structure:
{{
    "question": "the evolved question text",
    "evolution_type": "simple",
    "original_question": "the original base question"
}}

Context:
{context}

Base Question:
{base_question}"""

    new_questions = []
    for doc in documents:
        if hasattr(doc, "metadata") and "question" in doc.metadata:
            base_question = doc.metadata["question"]

            response = node.client.chat.completions.create(
                model=node.model,
                messages=[
                    SystemMessage(
                        content="You are a helpful assistant that evolves questions by paraphrasing and rewording."
                    ),
                    HumanMessage(
                        content=prompt.format(
                            context=doc.page_content[:500], base_question=base_question
                        )
                    ),
                ],
                temperature=0.7,
                max_tokens=500,
            )

            try:
                result = json.loads(response.choices[0].message.content)
                new_questions.append(result)
            except (json.JSONDecodeError, KeyError):
                continue

    return {
        **state,
        "evolved_questions": evolved_questions + new_questions,
        "current_step": "simple_evolution_complete",
    }


def multi_context_evolution_node(state: Dict) -> Dict:
    node = EvolInstructNode()

    documents = state.get("documents", [])
    evolved_questions = state.get("evolved_questions", [])

    if len(documents) < 2:
        return {**state, "current_step": "multi_context_evolution_skipped"}

    prompt = """You are a question evolution expert. Your task is to create questions that require information from multiple document chunks.

Instructions:
1. Analyze two different document contexts
2. Create a question that:
   - Combines information or concepts from both documents
   - Requires synthesizing knowledge across multiple sections
   - Connects ideas that span different parts of the content
   - Cannot be answered from a single document alone

3. Return ONLY a valid JSON object with this structure:
{{
    "question": "the evolved question requiring multi-context understanding",
    "evolution_type": "multi_context",
    "sources_used": ["brief description of first source concept", "brief description of second source concept"]
}}

Context 1:
{context1}

Context 2:
{context2}"""

    new_questions = []
    for i in range(0, len(documents) - 1, 2):
        doc1 = documents[i]
        doc2 = documents[i + 1]

        response = node.client.chat.completions.create(
            model=node.model,
            messages=[
                SystemMessage(
                    content="You are a helpful assistant that evolves questions by combining multiple contexts."
                ),
                HumanMessage(
                    content=prompt.format(
                        context1=doc1.page_content[:500],
                        context2=doc2.page_content[:500],
                    )
                ),
            ],
            temperature=0.8,
            max_tokens=600,
        )

        try:
            result = json.loads(response.choices[0].message.content)
            new_questions.append(result)
        except (json.JSONDecodeError, KeyError):
            continue

    return {
        **state,
        "evolved_questions": evolved_questions + new_questions,
        "current_step": "multi_context_evolution_complete",
    }


def reasoning_evolution_node(state: Dict) -> Dict:
    node = EvolInstructNode()

    documents = state.get("documents", [])
    evolved_questions = state.get("evolved_questions", [])

    if not documents:
        return {**state, "current_step": "reasoning_evolution_skipped"}

    prompt = """You are a question evolution expert. Your task is to transform simple questions into reasoning-intensive challenges.

Instructions:
1. Read the base question and its context
2. Evolve it by adding one or more of these elements:
   - Constraints (e.g., "under specific conditions", "within these parameters")
   - Multi-step thinking requirements
   - Comparative or analytical dimensions
   - Complex reasoning chains
   - Hypothetical scenarios requiring deduction
   
3. Return ONLY a valid JSON object with this structure:
{{
    "question": "the evolved reasoning-intensive question",
    "evolution_type": "reasoning",
    "original_question": "the original base question",
    "complexity_enhancements": ["constraint1", "reasoning_step1", "enhancement2"]
}}

Context:
{context}

Base Question:
{base_question}"""

    new_questions = []
    for doc in documents:
        if hasattr(doc, "metadata") and "question" in doc.metadata:
            base_question = doc.metadata["question"]

            response = node.client.chat.completions.create(
                model=node.model,
                messages=[
                    SystemMessage(
                        content="You are a helpful assistant that evolves questions by adding reasoning complexity and constraints."
                    ),
                    HumanMessage(
                        content=prompt.format(
                            context=doc.page_content[:500], base_question=base_question
                        )
                    ),
                ],
                temperature=0.9,
                max_tokens=700,
            )

            try:
                result = json.loads(response.choices[0].message.content)
                new_questions.append(result)
            except (json.JSONDecodeError, KeyError):
                continue

    return {
        **state,
        "evolved_questions": evolved_questions + new_questions,
        "current_step": "reasoning_evolution_complete",
    }
