import marimo

__generated_with = "0.19.10"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 9: Synthetic Data Generation and RAG Evaluation with Langfuse

    In the following notebook we'll explore a use-case for RAGAS' synthetic testset generation workflow, and use it to evaluate and iterate on a RAG pipeline with LangSmith!

    **Learning Objectives:**
    - Understand Ragas' knowledge graph-based synthetic data generation workflow
    - Generate synthetic test sets with different query synthesizer types
    - Load synthetic data into Langfuse for evaluation
    - Evaluate a RAG chain using OpenEvals evaluators
    - Iterate on RAG pipeline parameters and measure the impact

    ## Table of Contents:

    - **Breakout Room #1:** Synthetic Data Generation with Ragas
      - Task 1: Dependencies and API Keys
      - Task 2: Data Preparation and Knowledge Graph Construction
      - Task 3: Generating Synthetic Test Data
      - Question #1 & Question #2
      - 🏗️ Activity #1: Custom Query Distribution

    - **Breakout Room #2:** RAG Evaluation with Langfuse
      - Task 4: Langfuse Dataset Setup
      - Task 5: Building a Basic RAG Chain
      - Task 6: Evaluating with OpenEvals
      - Task 7: Modifying the Pipeline and Re-Evaluating
      - Question #3 & Question #4
      - 🏗️ Activity #2: Analyze Evaluation Results
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🤝 Breakout Room #1
    ## Synthetic Data Generation with Ragas
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Dependencies and API Keys

    We'll need to install a number of API keys and dependencies, since we'll be leveraging a number of great technologies for this pipeline!

    1. OpenAI-compatible endpoints to handle the Synthetic Data Generation
    2. OpenAI-compatible Endpoints for our RAG pipeline and evaluation
    3. QDrant as our vectorstore
    4. Langfuse for our evaluation coordinator!

    Let's install and provide all the required information below!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dependencies and API Keys:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### NLTK Import

    To prevent errors that may occur based on OS - we'll import NLTK and download the needed packages to ensure correct handling of data.
    """)
    return


@app.cell
def _():
    import nltk

    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    return


@app.cell
def _():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY", "")
    os.environ["LANGFUSE_BASE_URL"] = os.getenv(
        "LANGFUSE_BASE_URL", "http://localhost:3000"
    )
    os.environ["OPENAI_API_KEY"] = "dummy-api-key"
    os.environ["OPENAI_BASE_URL"] = "http://192.168.1.79:8080/v1"
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We'll also want to set a project name to make things easier for ourselves.
    """)
    return


@app.cell
def _():
    from uuid import uuid4

    # Langfuse uses project through UI/API keys, no project env var needed
    pass
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    OpenAI's API Key!
    """)
    return


@app.cell
def _():
    pass  # OpenAI API key already configured with local endpoint
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Generating Synthetic Test Data

    We wil be using Ragas to build out a set of synthetic test questions, references, and reference contexts. This is useful because it will allow us to find out how our system is performing.

    > NOTE: Ragas is best suited for finding *directional* changes in your LLM-based systems. The absolute scores aren't comparable in a vacuum.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data Preparation

    We'll prepare our data using two complementary guides — a Health & Wellness Guide covering exercise, nutrition, sleep, and stress management, and a Mental Health & Psychology Handbook covering mental health conditions, therapeutic approaches, resilience, and daily mental health practices. The topical overlap between documents helps RAGAS build rich cross-document relationships in the knowledge graph.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next, let's load our data into a familiar LangChain format using the `TextLoader`.
    """)
    return


@app.cell
def _():
    from langchain_community.document_loaders import DirectoryLoader, TextLoader

    loader = DirectoryLoader("data/", glob="*.txt", loader_cls=TextLoader)
    docs = loader.load()
    print(f"Loaded {len(docs)} documents: {[d.metadata['source'] for d in docs]}")
    return (docs,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Knowledge Graph Based Synthetic Generation

    Ragas uses a knowledge graph based approach to create data. This is extremely useful as it allows us to create complex queries rather simply. The additional testset complexity allows us to evaluate larger problems more effectively, as systems tend to be very strong on simple evaluation tasks.

    Let's start by defining our `generator_llm` (which will generate our questions, summaries, and more), and our `generator_embeddings` which will be useful in building our graph.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Unrolled SDG
    """)
    return


@app.cell
def _():
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from langchain_openai import ChatOpenAI
    from langchain_openai import OpenAIEmbeddings

    generator_llm = LangchainLLMWrapper(ChatOpenAI(model="minimax-m2.5-mlx@4bit"))
    generator_embeddings = LangchainEmbeddingsWrapper(
        OpenAIEmbeddings(
            model="text-embedding-nomic-embed-text-v2-moe",
            check_embedding_ctx_length=False,
        )
    )
    return ChatOpenAI, OpenAIEmbeddings, generator_embeddings, generator_llm


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next, we're going to instantiate our Knowledge Graph.

    This graph will contain N number of nodes that have M number of relationships. These nodes and relationships (AKA "edges") will define our knowledge graph and be used later to construct relevant questions and responses.
    """)
    return


@app.cell
def _():
    from ragas.testset.graph import KnowledgeGraph

    kg = KnowledgeGraph()
    kg
    return KnowledgeGraph, kg


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The first step we're going to take is to simply insert each of our full documents into the graph. This will provide a base that we can apply transformations to.
    """)
    return


@app.cell
def _(docs, kg):
    from ragas.testset.graph import Node, NodeType

    for doc in docs:
        kg.nodes.append(
            Node(
                type=NodeType.DOCUMENT,
                properties={
                    "page_content": doc.page_content,
                    "document_metadata": doc.metadata,
                },
            )
        )
    kg
    return (Node,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, we'll apply the *default* transformations to our knowledge graph. This will take the nodes currently on the graph and transform them based on a set of [default transformations](https://docs.ragas.io/en/latest/references/transforms/#ragas.testset.transforms.default_transforms).

    These default transformations are dependent on the corpus length, in our case:

    - Producing Summaries -> produces summaries of the documents
    - Extracting Headlines -> finding the overall headline for the document
    - Theme Extractor -> extracts broad themes about the documents

    It then uses cosine-similarity and heuristics between the embeddings of the above transformations to construct relationships between the nodes.
    """)
    return


@app.cell
def _(docs, generator_embeddings, generator_llm, kg):
    from ragas.testset.transforms import default_transforms, apply_transforms

    transformer_llm = generator_llm
    embedding_model = generator_embeddings

    default_transforms = default_transforms(
        documents=docs, llm=transformer_llm, embedding_model=embedding_model
    )
    apply_transforms(kg, default_transforms)
    kg
    return (embedding_model,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can save and load our knowledge graphs as follows.
    """)
    return


@app.cell
def _(KnowledgeGraph, kg):
    kg.save("usecase_data_kg.json")
    usecase_data_kg = KnowledgeGraph.load("usecase_data_kg.json")
    usecase_data_kg
    return (usecase_data_kg,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Knowledge Graph Relationship Debug

    Let's check what relationship types exist in our knowledge graph.
    """)
    return


@app.cell
def _(usecase_data_kg):
    # Debug: Check what relationship types exist in the KG
    rel_types = set(rel.type for rel in usecase_data_kg.relationships)
    print(f"Relationship types in KG: {rel_types}")
    print(f"Total relationships: {len(usecase_data_kg.relationships)}")
    print(f"Total nodes: {len(usecase_data_kg.nodes)}")
    return


@app.cell
def _(embedding_model, generator_llm, usecase_data_kg):
    from ragas.testset import TestsetGenerator

    generator = TestsetGenerator(
        llm=generator_llm,
        embedding_model=embedding_model,
        knowledge_graph=usecase_data_kg,
    )
    return TestsetGenerator, generator


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    However, we'd like to be able to define the kinds of queries we're generating - which is made simple by Ragas having pre-created a number of different "QuerySynthesizer"s.

    Each of these Synthetsizers is going to tackle a separate kind of query which will be generated from a scenario and a persona.

    In essence, Ragas will use an LLM to generate a persona of someone who would interact with the data - and then use a scenario to construct a question from that data and persona.
    """)
    return


@app.cell
def _(KnowledgeGraph, Node, generator_llm):
    from dataclasses import dataclass
    from ragas.testset.synthesizers.multi_hop.abstract import (
        MultiHopAbstractQuerySynthesizer,
    )
    from ragas.testset.synthesizers import (
        SingleHopSpecificQuerySynthesizer,
        MultiHopSpecificQuerySynthesizer,
    )
    import typing as t

    @dataclass
    class CustomMultiHopAbstractQuerySynthesizer(MultiHopAbstractQuerySynthesizer):
        """Custom synthesizer that checks relationship type instead of property."""

        relation_type: str = "entities_overlap"

        def get_node_clusters(
            self,
            knowledge_graph: KnowledgeGraph,
            n: int = 1,
        ) -> t.List[t.Set[Node]]:
            """Override to use relationship type instead of property."""
            # Use find_indirect_clusters and limit results to n
            node_clusters = knowledge_graph.find_indirect_clusters(
                relationship_condition=lambda rel: (
                    True if rel.type == self.relation_type else False
                ),
                depth_limit=3,
            )
            # Limit to n clusters
            return node_clusters[:n]

    # Use custom synthesizer for multi-hop abstract queries
    # MultiHopAbstractQuerySynthesizer looks for 'summary_similarity' property which doesn't exist
    # Our custom version uses 'entities_overlap' relationship type which DOES exist
    query_distribution = [
        (SingleHopSpecificQuerySynthesizer(llm=generator_llm), 0.5),
        (
            CustomMultiHopAbstractQuerySynthesizer(
                llm=generator_llm, relation_type="entities_overlap"
            ),
            0.25,
        ),
        (
            MultiHopSpecificQuerySynthesizer(
                llm=generator_llm, relation_type="entities_overlap"
            ),
            0.25,
        ),
    ]
    return (
        CustomMultiHopAbstractQuerySynthesizer,
        MultiHopSpecificQuerySynthesizer,
        SingleHopSpecificQuerySynthesizer,
        query_distribution,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #1:

    What are the three types of query synthesizers doing? Describe each one in simple terms.

    ##### Answer:
    SingleHopSpecificQuerySynthesizer creates questions that need just one piece of information from a single document. MultiHopAbstractQuerySynthesizer and MultiHopSpecificQuerySynthesizer both create questions requiring multiple information sources across documents, with the abstract version asking conceptual questions and the specific version asking factual ones.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Finally, we can use our `TestSetGenerator` to generate our testset!
    """)
    return


@app.cell
def _(generator, query_distribution):
    testset = generator.generate(testset_size=10, query_distribution=query_distribution)
    testset.to_pandas()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Abstracted SDG

    The above method is the full process - but we can shortcut that using the provided abstractions!

    This will generate our knowledge graph under the hood, and will - from there - generate our personas and scenarios to construct our queries.
    """)
    return


@app.cell
def _(TestsetGenerator, docs, generator_embeddings, generator_llm):
    generator_1 = TestsetGenerator(
        llm=generator_llm, embedding_model=generator_embeddings
    )
    dataset = generator_1.generate_with_langchain_docs(docs, testset_size=10)
    return (dataset,)


@app.cell
def _(dataset):
    dataset.to_pandas()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #2:

    Ragas offers both an "unrolled" (manual) approach and an "abstracted" (automatic) approach to synthetic data generation. What are the trade-offs between these two approaches? When would you choose one over the other?

    ##### Answer:
    The unrolled approach gives you full control to customize query distributions and debug each step, but requires more code. The abstracted approach is simpler and faster for basic use cases, but offers limited customization options.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #1: Custom Query Distribution

    Modify the `query_distribution` to experiment with different ratios of query types.

    ### Requirements:
    1. Create a custom query distribution with different weights than the default
    2. Generate a new test set using your custom distribution
    3. Compare the types of questions generated with the default distribution
    4. Explain why you chose the weights you did
    """)
    return


@app.cell
def _(
    CustomMultiHopAbstractQuerySynthesizer,
    MultiHopSpecificQuerySynthesizer,
    SingleHopSpecificQuerySynthesizer,
    generator,
    generator_llm,
):
    ### YOUR CODE HERE ###

    custom_query_distribution = [
        (SingleHopSpecificQuerySynthesizer(llm=generator_llm), 0.30),
        (
            CustomMultiHopAbstractQuerySynthesizer(
                llm=generator_llm, relation_type="entities_overlap"
            ),
            0.35,
        ),
        (
            MultiHopSpecificQuerySynthesizer(
                llm=generator_llm, relation_type="entities_overlap"
            ),
            0.35,
        ),
    ]

    custom_testset = generator.generate(
        testset_size=10, query_distribution=custom_query_distribution
    )
    custom_testset.to_pandas()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Default Distribution:
    SingleHop: 3, 30%
    MultiHopAbstract: 4: 40%
    MultiHopSpecific: 3, 30%

    Custom Distribution:
    SingleHop: 3, 27%
    MultiHopAbstract: 4: 36%
    MultiHopSpecific: 4, 36%

    So I only generated a single extra question, even with what felt like larger changes to the distribution. I forgot we were only generating 10 in the first one. So the Custom distribution generated one more MultiHopSpecific.

    I had originally meant to prioritize complex reasoning with more multihop specific questions without losing MultiHopAbstract questions (I liked those because specific felt easier to ground with actual retrieval than abstract), which I think it may have done better if I had generated like a thousand instead of 11. I wanted to reduce the number of SingleHop questions, as I haven't experienced any model being unable to answer SingleHop questions badly, but keeping everything around 30% also felt safe as far as representative distributions (30% is close to 1/3, where our number of categories is 3).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We'll need to provide our LangSmith API key, and set tracing to "true".

    Loooool, no, we have to do so so so much more.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🤝 Breakout Room #2
    ## RAG Evaluation with Langfuse
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Langfuse Dataset

    Now we can move on to creating a dataset for Langfuse!

    First, we'll need to create a dataset on Langfuse!

    We'll name our Dataset to make it easy to work with later.
    """)
    return


@app.cell
def _():
    from langfuse import Langfuse, get_client
    from langfuse.langchain import CallbackHandler
    import uuid

    Langfuse()
    langfuse = get_client()
    langfuse_handler = CallbackHandler()

    dataset_name = f"Use Case Synthetic Data - AIE9 - {uuid.uuid4()}"

    langfuse.create_dataset(
        name=dataset_name, description="Synthetic Data for Use Cases"
    )
    return dataset_name, langfuse, langfuse_handler


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We'll iterate through the RAGAS created dataframe - and add each item to our created dataset!

    > NOTE: We need to conform the outputs to the expected format - which in this case is: `question` and `answer`.
    """)
    return


@app.cell
def _(dataset, dataset_name, langfuse):
    for data_row in dataset.to_pandas().iterrows():
        langfuse.create_dataset_item(
            dataset_name=dataset_name,
            input={"question": data_row[1]["user_input"]},
            expected_output={"answer": data_row[1]["reference"]},
            metadata={
                "context": data_row[1]["reference_contexts"],
                "reference": data_row[1]["reference"],
            },
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Basic RAG Chain

    Time for some RAG!
    """)
    return


@app.cell
def _(docs):
    rag_documents = docs
    return (rag_documents,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To keep things simple, we'll just use LangChain's recursive character text splitter!
    """)
    return


@app.cell
def _(rag_documents):
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    _text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    rag_documents_1 = _text_splitter.split_documents(rag_documents)
    return RecursiveCharacterTextSplitter, rag_documents_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We'll create our vectorstore using OpenAI's [`text-embedding-3-small`](https://platform.openai.com/docs/guides/embeddings/embedding-models) embedding model.
    """)
    return


@app.cell
def _(OpenAIEmbeddings):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-nomic-embed-text-v2-moe",
        check_embedding_ctx_length=False,
    )
    return (embeddings,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As usual, we will power our RAG application with Qdrant!
    """)
    return


@app.cell
def _(embeddings, rag_documents_1):
    from langchain_qdrant import QdrantVectorStore

    vectorstore = QdrantVectorStore.from_documents(
        documents=rag_documents_1,
        embedding=embeddings,
        location=":memory:",
        collection_name="use_case_rag",
    )
    return QdrantVectorStore, vectorstore


@app.cell
def _(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    return (retriever,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To get the "A" in RAG, we'll provide a prompt.
    """)
    return


@app.cell
def _():
    from langchain_core.prompts import ChatPromptTemplate

    RAG_PROMPT = """\
    Given a provided context and question, you must answer the question based only on context.

    If you cannot answer the question based on the context - you must say "I don't know".

    Context: {context}
    Question: {question}
    """

    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
    return ChatPromptTemplate, rag_prompt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As is usual: We'll be using `gpt-4.1-mini` for our RAG!
    """)
    return


@app.cell
def _(ChatOpenAI):
    llm = ChatOpenAI(model="minimax-m2.5-mlx@4bit")
    return (llm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Finally, we can set-up our RAG LCEL chain!
    """)
    return


@app.cell
def _(llm, rag_prompt, retriever):
    from operator import itemgetter
    from langchain_core.runnables import RunnablePassthrough, RunnableParallel
    from langchain_core.output_parsers import StrOutputParser

    rag_chain = (
        {
            "context": itemgetter("question") | retriever,
            "question": itemgetter("question"),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    return StrOutputParser, itemgetter, rag_chain


@app.cell
def _(langfuse_handler, rag_chain):
    rag_chain.invoke(
        {"question": "What are some recommended exercises for lower back pain?"},
        config={"callbacks": [langfuse_handler]},
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Evaluation Set-up

    We'll use the local LLM as our evaluation LLM for our base Evaluators.
    """)
    return


@app.cell
def _(ChatOpenAI):
    eval_llm = ChatOpenAI(model="minimax-m2.5-mlx@4bit")
    return (eval_llm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We'll be using a number of evaluators - from OpenEvals, to a few custom evaluators!
    """)
    return


@app.cell
def _(eval_llm):
    from openevals.llm import create_llm_as_judge

    def create_custom_evaluator(llm, prompt_template, feedback_key):
        def evaluator(inputs, outputs, reference_outputs=None):
            prompt = prompt_template.format(
                inputs=inputs,
                outputs=outputs,
                reference_outputs=reference_outputs or "",
            )
            response = llm.invoke(prompt)
            content = response.content.strip().lower()

            if "true" in content or "1" in content or "yes" in content:
                score = True
            elif "false" in content or "0" in content or "no" in content:
                score = False
            else:
                score = False

            return {"key": feedback_key, "score": score, "comment": content}

        return evaluator

    # 1. QA Correctness (replaces LangChainStringEvaluator("qa"))
    qa_evaluator = create_custom_evaluator(
        eval_llm,
        "You are evaluating a QA system. Given the input, assess whether the prediction is correct.\n\nInput: {inputs}\nPrediction: {outputs}\nReference answer: {reference_outputs}\n\nIs the prediction correct? Return 1 if correct, 0 if incorrect.",
        "qa",
    )

    # 2. Labeled Helpfulness (replaces LangChainStringEvaluator("labeled_criteria"))
    labeled_helpfulness_evaluator = create_custom_evaluator(
        eval_llm,
        (
            "You are assessing a submission based on the following criterion:\n\n"
            "helpfulness: Is this submission helpful to the user, "
            "taking into account the correct reference answer?\n\n"
            "Input: {inputs}\n"
            "Submission: {outputs}\n"
            "Reference answer: {reference_outputs}\n\n"
            "Does the submission meet the criterion? Return 1 if yes, 0 if no."
        ),
        "helpfulness",
    )

    # 3. Dopeness (replaces LangChainStringEvaluator("criteria"))
    dopeness_evaluator = create_custom_evaluator(
        eval_llm,
        (
            "You are assessing a submission based on the following criterion:\n\n"
            "dopeness: Is this response dope, lit, cool, or is it just a generic response?\n\n"
            "Input: {inputs}\n"
            "Submission: {outputs}\n\n"
            "Does the submission meet the criterion? Return 1 if yes, 0 if no."
        ),
        "dopeness",
    )

    # Simple evaluate function wrapper for Langfuse compatibility
    def evaluate(target, data, evaluators, metadata=None, callbacks=None):
        """Simple evaluation wrapper that runs target on dataset items and applies evaluators"""
        from langfuse import get_client

        langfuse = get_client()
        dataset = langfuse.get_dataset(data)

        # Setup callback config if provided (must be a list)
        callback_config = {"callbacks": [callbacks]} if callbacks else {}

        results = []
        for item in dataset.items:
            # Get input as string (LangFuse stores as dict like {"question": "..."})
            input_str = (
                item.input.get("question")
                if isinstance(item.input, dict)
                else str(item.input)
            )

            # Get reference output as string
            reference_str = (
                item.expected_output.get("answer")
                if isinstance(item.expected_output, dict)
                else str(item.expected_output)
            )

            # Run the target function with callback handler to create trace
            output = target(item.input, config=callback_config)
            if hasattr(output, "content"):
                output = output.content

            # Run evaluators
            for evaluator in evaluators:
                try:
                    eval_result = evaluator(
                        inputs=input_str,
                        outputs=output,
                        reference_outputs=reference_str,
                    )

                    # Convert score to float for Langfuse
                    score_value = 1.0 if eval_result.get("score") else 0.0

                    # Log score to Langfuse - find the most recent trace for this input
                    try:
                        # Fetch recent traces and find one matching our input
                        traces = langfuse.api.trace.list(limit=10)
                        trace_id = None
                        for trace in traces.data:
                            if trace.input.get("question") == input_str:
                                trace_id = trace.id
                                break

                        if trace_id:
                            langfuse.create_score(
                                trace_id=trace_id,
                                name=eval_result.get("key", "unknown"),
                                value=score_value,
                                data_type="NUMERIC",
                                comment=eval_result.get("comment"),
                            )
                        else:
                            print(f"No trace found for input: {input_str[:50]}...")
                    except Exception as e:
                        print(f"Failed to create score: {e}")
                except Exception as e:
                    print(f"Evaluator failed: {e}")

            results.append({"input": item.input, "output": output})

        return results

    return (
        dopeness_evaluator,
        evaluate,
        labeled_helpfulness_evaluator,
        qa_evaluator,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **Describe what each evaluator is evaluating:**
    >
    > - `qa_evaluator`: Whether a prediction is _correct_
    > - `labeled_helpfulness_evaluator`: Does the submission meet the criterion *and* is helpful?
    > - `dopeness_evaluator`: Is the response dope lol
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Running Evaluation
    """)
    return


@app.cell
def _(
    dataset_name,
    dopeness_evaluator,
    evaluate,
    labeled_helpfulness_evaluator,
    langfuse_handler,
    qa_evaluator,
    rag_chain,
):
    evaluate(
        rag_chain.invoke,
        data=dataset_name,
        evaluators=[
            qa_evaluator,
            labeled_helpfulness_evaluator,
            dopeness_evaluator,
        ],
        metadata={"revision_id": "default_chain_init"},
        callbacks=langfuse_handler,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dope-ifying Our Application

    We'll be making a few changes to our RAG chain to increase its performance on our SDG evaluation test dataset!

    - Include a "dope" prompt augmentation
    - Use larger chunks
    - Improve the retriever model to: `qwen3-embedding-4b`

    Let's see how this changes our evaluation!
    """)
    return


@app.cell
def _(ChatPromptTemplate):
    DOPENESS_RAG_PROMPT = """\
    Given a provided context and question, you must answer the question based only on context.

    If you cannot answer the question based on the context - you must say "I don't know".

    Make your answer rad, ensure high levels of dopeness. Do not be generic, or give generic responses.

    Context: {context}
    Question: {question}
    """

    dopeness_rag_prompt = ChatPromptTemplate.from_template(DOPENESS_RAG_PROMPT)
    return (dopeness_rag_prompt,)


@app.cell
def _(docs):
    rag_documents_2 = docs
    return (rag_documents_2,)


@app.cell
def _(RecursiveCharacterTextSplitter, rag_documents_2):
    _text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    rag_documents_3 = _text_splitter.split_documents(rag_documents_2)
    return (rag_documents_3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #3:

    Why would modifying our chunk size modify the performance of our application?

    ##### Answer:
    Smaller chunks give more precise semantic matches for specific questions, while larger chunks provide more context per retrieval but can dilute relevance and make matching less accurate.
    """)
    return


@app.cell
def _(OpenAIEmbeddings):
    embeddings_1 = OpenAIEmbeddings(
        model="text-embedding-qwen3-embedding-4b",
        check_embedding_ctx_length=False,
    )
    return (embeddings_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #4:

    Why would modifying our embedding model modify the performance of our application?

    ##### Answer:
    Embedding models convert text into vectors differently, so changing them affects how well your system matches queries to relevant documents. Different models capture semantic meaning in distinct ways with varying vector dimensions, which directly impacts retrieval quality.
    """)
    return


@app.cell
def _(QdrantVectorStore, embeddings_1, rag_documents_3):
    vectorstore_1 = QdrantVectorStore.from_documents(
        documents=rag_documents_3,
        embedding=embeddings_1,
        location=":memory:",
        collection_name="Use Case RAG Docs",
    )
    return (vectorstore_1,)


@app.cell
def _(vectorstore_1):
    retriever_1 = vectorstore_1.as_retriever()
    return (retriever_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Setting up our new and improved DOPE RAG CHAIN.
    """)
    return


@app.cell
def _(StrOutputParser, dopeness_rag_prompt, itemgetter, llm, retriever_1):
    dopeness_rag_chain = (
        {
            "context": itemgetter("question") | retriever_1,
            "question": itemgetter("question"),
        }
        | dopeness_rag_prompt
        | llm
        | StrOutputParser()
    )
    return (dopeness_rag_chain,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's test it on the same output that we saw before.
    """)
    return


@app.cell
def _(dopeness_rag_chain, langfuse_handler):
    dopeness_rag_chain.invoke(
        {"question": "How can I improve my sleep quality?"},
        config={"callbacks": [langfuse_handler]},
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Finally, we can evaluate the new chain on the same test set!
    """)
    return


@app.cell
def _(
    dataset_name,
    dopeness_evaluator,
    dopeness_rag_chain,
    evaluate,
    labeled_helpfulness_evaluator,
    langfuse_handler,
    qa_evaluator,
):
    evaluate(
        dopeness_rag_chain.invoke,
        data=dataset_name,
        evaluators=[
            qa_evaluator,
            labeled_helpfulness_evaluator,
            dopeness_evaluator,
        ],
        metadata={"revision_id": "dopeness_rag_chain"},
        callbacks=langfuse_handler,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #2: Analyze Evaluation Results

    Provide a screenshot of the difference between the two chains in Langfuse, and explain why you believe certain metrics changed in certain ways.

    ##### Answer:
    *I mean, the obvvious metric change is that on the first chain, (bottom traces in the 2nd picture), you'll see that the entire first column of scores is zero. It got zeroes on all dopeness evals. One more subtle change is that there are a couple of questions where the first chain got zeroes across the board, no qa, not helpful, and not dope, and the second chain, while being a dopeness chain, got zero on dopeness, but got a 1 on helpfulness and qa. I can't say that asking the model to be doper adds helpfulness, because I think that change actually came from a far better embedding model (higher dimensionality, larger chunking, etc)*
    """)
    return


@app.cell
def _(mo):
    mo.image("/home/imjonezz/Desktop/AIE9/09_Synthetic_Data_Generation_and_LangSmith/Screenshot 2026-02-15 172158.png")
    return


@app.cell
def _(mo):
    mo.image("/home/imjonezz/Desktop/AIE9/09_Synthetic_Data_Generation_and_LangSmith/Screenshot 2026-02-16 070107.png")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    In this session, we:

    1. **Generated synthetic test data** using Ragas' knowledge graph-based approach
    2. **Explored query synthesizers** for creating diverse question types
    3. **Loaded synthetic data** into a Langfuse dataset for evaluation
    4. **Built and evaluated a RAG chain** using OpenEvals evaluators
    5. **Iterated on the pipeline** by modifying chunk size, embedding model, and prompt — then measured the impact

    ### Key Takeaways:

    - **Synthetic data generation** is critical for early iteration — it provides high-quality signal without manually creating test data
    - **Langfuse + OpenEvals** enable systematic comparison of pipeline versions
    - **Small changes matter** — chunk size, embedding model, and prompt modifications can significantly affect evaluation scores
    """)
    return


if __name__ == "__main__":
    app.run()
