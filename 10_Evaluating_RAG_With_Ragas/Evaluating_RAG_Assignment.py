import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 10: Using Ragas to Evaluate a RAG Application built with LangChain and LangGraph

    In the following notebook, we'll be looking at how [Ragas](https://github.com/explodinggradients/ragas) can be helpful in a number of ways when looking to evaluate your RAG applications!

    While this example is rooted in LangChain/LangGraph - Ragas is framework agnostic (you don't even need to be using a framework!).

    ## 🤝 Breakout Room #1
      - Task 1: Installing Required Libraries
      - Task 2: Set Environment Variables
      - Task 3: Synthetic Dataset Generation for Evaluation using Ragas
      - Task 4: Construct our RAG application
      - Task 5: Evaluating our Application with Ragas
      - Task 6: Making Adjustments and Re-Evaluating
      - ***Activity #1: Implement a Different Reranking Strategy***
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Installing Required Libraries

    If you have not already done so, install the required libraries using the uv package manager:
    ``` bash

    uv sync

    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 2: Set Environment Variables:

    We'll also need to provide our API keys.
    > NOTE: In addition to OpenAI's models, this notebook will be using Cohere's Reranker - please be sure to [sign-up for an API key!](https://docs.cohere.com/reference/about)

    You have two options for supplying your API keys in this session:
    - Use environment variables (see Prerequisite #2 in the README.md)
    - Provide them via a prompt when the notebook runs

    The following code will load all of the environment variables in your `.env`. Then, it checks for the two API keys we need. If they are not there, it will prompt you to provide them.

    First, OpenAI's for our LLM/embedding model combination!

    Second, Cohere's for our reranking
    """)
    return


@app.cell
def _():
    import os
    from getpass import getpass
    from dotenv import load_dotenv

    # Suppress HuggingFace/Transformers warning about bert.embeddings.position_ids | UNEXPECTED
    os.environ["HF_HUB_VERBOSITY"] = "error"
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"

    load_dotenv()

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "Dummy-API-Key"

    if not os.environ.get("COHERE_API_KEY"):
        os.environ["COHERE_API_KEY"] = "Dummy-API-Key"
    return (os,)


@app.cell
def _(os):
    from langfuse import Langfuse

    langfuse = Langfuse(
        public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
        host=os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 3: Synthetic Dataset Generation for Evaluation using Ragas

    We wil be using Ragas to build out a set of synthetic test questions, references, and reference contexts. This is useful because it will allow us to find out how our system is performing.

    > NOTE: Ragas is best suited for finding *directional* changes in your LLM-based systems. The absolute scores aren't comparable in a vacuum.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data Preparation

    We'll prepare our data using the Health & Wellness Guide - a comprehensive resource covering exercise, nutrition, sleep, and stress management.
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
    from langchain_community.document_loaders import TextLoader

    _loader = TextLoader("data/HealthWellnessGuide.txt")
    docs = _loader.load()
    return TextLoader, docs


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
    ### Abstracted SDG

    The above method is the full process - but we can shortcut that using the provided abstractions!

    This will generate our knowledge graph under the hood, and will - from there - generate our personas and scenarios to construct our queries.
    """)
    return


@app.cell
def _():
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from langchain_openai import ChatOpenAI
    from langchain_openai import OpenAIEmbeddings

    generator_llm = LangchainLLMWrapper(
        ChatOpenAI(
            model="minimax-m2.5-mlx@4bit",
            base_url="http://192.168.1.79:8080/v1",
            api_key="dummy-key",
        )
    )
    generator_embeddings = LangchainEmbeddingsWrapper(
        OpenAIEmbeddings(
            model="text-embedding-qwen3-embedding-4b",
            base_url="http://192.168.1.79:8080/v1",
            check_embedding_ctx_length=False,
        )
    )
    return (
        ChatOpenAI,
        LangchainLLMWrapper,
        OpenAIEmbeddings,
        generator_embeddings,
        generator_llm,
    )


@app.cell
def _(docs, generator_embeddings, generator_llm):
    from ragas.testset import TestsetGenerator

    generator = TestsetGenerator(
        llm=generator_llm, embedding_model=generator_embeddings
    )
    dataset = generator.generate_with_langchain_docs(docs, testset_size=10)
    return (dataset,)


@app.cell
def _(dataset):
    print("Initial columns:", dataset.to_pandas().columns.tolist())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Construct our RAG application

    Now we'll construct our LangChain RAG, which we will be evaluating using the above created test data!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### R - Retrieval

    Let's start with building our retrieval pipeline, which will involve loading the same data we used to create our synthetic test set above.

    > NOTE: We need to use the same data - as our test set is specifically designed for this data.
    """)
    return


@app.cell
def _(TextLoader):
    _loader = TextLoader("data/HealthWellnessGuide.txt")
    docs_1 = _loader.load()
    return (docs_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now that we have our data loaded, let's split it into chunks!
    """)
    return


@app.cell
def _(docs_1):
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    _text_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=0)
    split_documents = _text_splitter.split_documents(docs_1)
    len(split_documents)
    return RecursiveCharacterTextSplitter, split_documents


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #1:

    What is the purpose of the `chunk_overlap` parameter in the `RecursiveCharacterTextSplitter`?

    ##### Answer:

    The `chunk_overlap` parameter specifies how many characters should overlap between adjacent chunks. This helps preserve context at chunk boundaries so important information isn't accidentally split across separate chunks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next up, we'll need to provide an embedding model that we can use to construct our vector store.
    """)
    return


@app.cell
def _(OpenAIEmbeddings):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-nomic-embed-text-v2-moe",
        base_url="http://192.168.1.79:8080/v1",
        check_embedding_ctx_length=False,
    )
    return (embeddings,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can build our in memory QDrant vector store.
    """)
    return


@app.cell
def _(embeddings):
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams

    _client = QdrantClient(":memory:")
    _client.create_collection(
        collection_name="use_case_data",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    vector_store = QdrantVectorStore(
        client=_client, collection_name="use_case_data", embedding=embeddings
    )
    return (
        Distance,
        QdrantClient,
        QdrantVectorStore,
        VectorParams,
        vector_store,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can now add our documents to our vector store.
    """)
    return


@app.cell
def _(split_documents, vector_store):
    _ = vector_store.add_documents(documents=split_documents)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's define our retriever.
    """)
    return


@app.cell
def _(vector_store):
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    return (retriever,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can produce a node for retrieval!
    """)
    return


@app.cell
def _(retriever):
    def retrieve(state):
        retrieved_docs = retriever.invoke(state["question"])
        return {"context": retrieved_docs}

    return (retrieve,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### A - Augmented

    Let's create a simple RAG prompt!
    """)
    return


@app.cell
def _():
    from langchain.prompts import ChatPromptTemplate

    RAG_PROMPT = """\
    You are a helpful assistant who answers questions based on provided context. You must only use the provided context, and cannot use your own knowledge.

    ### Question
    {question}

    ### Context
    {context}
    """

    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
    return (rag_prompt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### G - Generation

    We'll also need an LLM to generate responses - we'll use `gpt-4o-nano` to avoid using the same model as our judge model.
    """)
    return


@app.cell
def _(ChatOpenAI):
    llm = ChatOpenAI(
        model="minimax-m2.5-mlx@4bit",
        base_url="http://192.168.1.79:8080/v1",
        api_key="dummy-key",
    )
    return (llm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Then we can create a `generate` node!
    """)
    return


@app.cell
def _(llm, rag_prompt):
    def generate(state):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = rag_prompt.format_messages(
            question=state["question"], context=docs_content
        )
        response = llm.invoke(messages)
        return {"response": response.content}

    return (generate,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Building RAG Graph with LangGraph

    Let's create some state for our LangGraph RAG graph!
    """)
    return


@app.cell
def _():
    from langgraph.graph import START, StateGraph
    from typing_extensions import List, TypedDict
    from langchain_core.documents import Document

    class State(TypedDict):
        question: str
        context: List[Document]
        response: str

    return Document, List, START, State, StateGraph, TypedDict


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can build our simple graph!

    > NOTE: We're using `add_sequence` since we will always move from retrieval to generation. This is essentially building a chain in LangGraph.
    """)
    return


@app.cell
def _(START, State, StateGraph, generate, retrieve):
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    return (graph,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's do a test to make sure it's doing what we'd expect.
    """)
    return


@app.cell
def _(graph):
    response = graph.invoke({"question": "What exercises help with lower back pain?"})
    return (response,)


@app.cell
def _(response):
    response["response"]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 5: Evaluating our Application with Ragas

    Now we can finally do our evaluation!

    We'll start by running the queries we generated usign SDG above through our application to get context and responses.
    """)
    return


@app.cell
def _(dataset, graph):
    for _test_row in dataset:
        response_1 = graph.invoke({"question": _test_row.eval_sample.user_input})
        _test_row.eval_sample.response = response_1["response"]
        _test_row.eval_sample.retrieved_contexts = [
            context.page_content for context in response_1["context"]
        ]

    df = dataset.to_pandas()
    print("Columns in DataFrame:", df.columns.tolist())
    return (df,)


@app.cell
def _(dataset):
    print(dataset.samples[0].eval_sample.response)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Then we can convert that table into a `EvaluationDataset` which will make the process of evaluation smoother.
    """)
    return


@app.cell
def _(df):
    from ragas import EvaluationDataset

    evaluation_dataset = EvaluationDataset.from_pandas(df)
    return EvaluationDataset, evaluation_dataset


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We'll need to select a judge model - in this case we're using the same model that was used to generate our Synthetic Data.
    """)
    return


@app.cell
def _(ChatOpenAI, LangchainLLMWrapper):
    from ragas import evaluate

    evaluator_llm = LangchainLLMWrapper(
        ChatOpenAI(
            model="minimax-m2.5-mlx@4bit",
            base_url="http://192.168.1.79:8080/v1",
            api_key="dummy-key",
        )
    )
    return evaluate, evaluator_llm


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next up - we simply evaluate on our desired metrics!
    """)
    return


@app.cell
def _(evaluate, evaluation_dataset, evaluator_llm, generator_embeddings):
    from ragas.metrics import (
        LLMContextRecall,
        Faithfulness,
        FactualCorrectness,
        ResponseRelevancy,
        ContextEntityRecall,
        NoiseSensitivity,
    )
    from ragas import RunConfig

    custom_run_config = RunConfig(timeout=1000000)
    baseline_result = evaluate(
        dataset=evaluation_dataset,
        metrics=[
            LLMContextRecall(),
            Faithfulness(),
            FactualCorrectness(),
            ResponseRelevancy(),
            ContextEntityRecall(),
            NoiseSensitivity(),
        ],
        llm=evaluator_llm,
        embeddings=generator_embeddings,
        run_config=custom_run_config,
    )
    baseline_result
    return (
        ContextEntityRecall,
        FactualCorrectness,
        Faithfulness,
        LLMContextRecall,
        NoiseSensitivity,
        ResponseRelevancy,
        custom_run_config,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 6: Making Adjustments and Re-Evaluating

    Now that we've got our baseline - let's make a change and see how the model improves or doesn't improve!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We'll first set our retriever to return more documents, which will allow us to take advantage of the reranking.
    """)
    return


@app.cell
def _(
    Distance,
    OpenAIEmbeddings,
    QdrantClient,
    QdrantVectorStore,
    RecursiveCharacterTextSplitter,
    VectorParams,
    docs_1,
):
    _text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=30)
    split_documents_1 = _text_splitter.split_documents(docs_1)
    len(split_documents_1)
    embeddings_1 = OpenAIEmbeddings(
        model="text-embedding-nomic-embed-text-v2-moe",
        base_url="http://192.168.1.79:8080/v1",
        check_embedding_ctx_length=False,
    )
    _client = QdrantClient(":memory:")
    _client.create_collection(
        collection_name="use_case_data_new_chunks",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    vector_store_1 = QdrantVectorStore(
        client=_client,
        collection_name="use_case_data_new_chunks",
        embedding=embeddings_1,
    )
    _ = vector_store_1.add_documents(documents=split_documents_1)
    adjusted_example_retriever = vector_store_1.as_retriever(search_kwargs={"k": 20})
    return (adjusted_example_retriever,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Reranking, or contextual compression, is a technique that uses a reranker to compress the retrieved documents into a smaller set of documents.

    This is essentially a slower, more accurate form of semantic similarity that we use on a smaller subset of our documents.
    """)
    return


@app.cell
def _(adjusted_example_retriever):
    from sentence_transformers import CrossEncoder
    import numpy as np

    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def retrieve_adjusted(state):
        initial_docs = adjusted_example_retriever.invoke(state["question"])

        if not initial_docs:
            return {"context": initial_docs}

        pairs = [[state["question"], doc.page_content] for doc in initial_docs]
        scores = cross_encoder.predict(pairs)

        top_indices = np.argsort(scores)[::-1][:5]
        reranked_docs = [initial_docs[i] for i in top_indices]

        return {"context": reranked_docs}

    return (retrieve_adjusted,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can simply rebuild our graph with the new retriever!
    """)
    return


@app.cell
def _(
    Document,
    List,
    START,
    StateGraph,
    TypedDict,
    generate,
    retrieve_adjusted,
):
    class AdjustedState(TypedDict):
        question: str
        context: List[Document]
        response: str

    adjusted_graph_builder = StateGraph(AdjustedState).add_sequence(
        [retrieve_adjusted, generate]
    )
    adjusted_graph_builder.add_edge(START, "retrieve_adjusted")
    adjusted_graph = adjusted_graph_builder.compile()
    return (adjusted_graph,)


@app.cell
def _(adjusted_graph):
    response_2 = adjusted_graph.invoke(
        {"question": "How can I improve my sleep quality?"}
    )
    response_2["response"]
    return


@app.cell
def _(adjusted_graph, dataset):
    import time
    import copy

    rerank_dataset = copy.deepcopy(dataset)
    for _test_row in rerank_dataset:
        response_3 = adjusted_graph.invoke(
            {"question": _test_row.eval_sample.user_input}
        )
        _test_row.eval_sample.response = response_3["response"]
        _test_row.eval_sample.retrieved_contexts = [
            context.page_content for context in response_3["context"]
        ]
        time.sleep(2)
    return copy, rerank_dataset, time


@app.cell
def _(rerank_dataset):
    rerank_dataset.samples[0].eval_sample.response
    return


@app.cell
def _(EvaluationDataset, rerank_dataset):
    rerank_evaluation_dataset = EvaluationDataset.from_pandas(
        rerank_dataset.to_pandas()
    )
    return (rerank_evaluation_dataset,)


@app.cell
def _(
    ContextEntityRecall,
    FactualCorrectness,
    Faithfulness,
    LLMContextRecall,
    NoiseSensitivity,
    ResponseRelevancy,
    custom_run_config,
    evaluate,
    evaluator_llm,
    generator_embeddings,
    rerank_evaluation_dataset,
):
    rerank_result = evaluate(
        dataset=rerank_evaluation_dataset,
        metrics=[
            LLMContextRecall(),
            Faithfulness(),
            FactualCorrectness(),
            ResponseRelevancy(),
            ContextEntityRecall(),
            NoiseSensitivity(),
        ],
        llm=evaluator_llm,
        embeddings=generator_embeddings,
        run_config=custom_run_config,
    )
    rerank_result
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #2:

    Which system performed better, on what metrics, and why?

    ##### Answer:

    *The reranked system performed better than the adjusted system, which performed better than the baseline*:

    Baseline: Based on the provided context, I cannot give you specific exercise examples from "The Personal Wellness Guide."The context only fragmentarily mentions:1. There are **recommended exercises for lower back pain**2. Something about **shoulder tension**3. That these exercises can provide relief for **neck and back pain**However, the actual exercise names, descriptions, or instructions are not included in the provided text. The context appears to be incomplete or cut off.To properly answer your question, I would need more complete information from the guide that actually lists the specific exercises recommended for lower back pain and neck tension.

    Adjusted: '# How to Improve Your Sleep Quality\n\nBased on the provided context, here are several strategies you can use:\n\n## Essential Sleep Hygiene Practices\n\n1. **Maintain a consistent sleep schedule** - Go to bed and wake up at the same time every day, even on weekends\n2. **Create a relaxing bedtime routine** - Try reading, gentle stretching, or taking a warm bath before bed\n3. **Limit screen exposure** - Avoid screens for 1-2 hours before bedtime\n4. **Avoid caffeine after 2 PM**\n5. **Exercise regularly** - But not too close to bedtime\n6. **Limit alcohol and heavy meals before bed**\n\n## Optimize Your Sleep Environment\n\n- **Temperature**: Keep your bedroom between 65-68°F (18-20°C)\n- **Darkness**: Use blackout curtains or a sleep mask\n- **Quiet**: Consider white noise machines or earplugs\n- **Comfort**: Invest in a quality mattress and pillows\n\n## Natural Remedies for Better Sleep\n\n- Cognitive Behavioral Therapy for Insomnia (CBT-I)\n- Relaxation techniques like progressive muscle relaxation\n- Herbal teas such as chamomile or valerian root\n- Magnesium supplements (consult a healthcare provider first)\n- Meditation and deep breathing exercises\n\n## Additional Health Strategies\n\nSince sleep is connected to overall health, also consider:\n- Aiming for 7-9 hours of sleep per night\n- Eating a nutrient-rich diet with plenty of fruits and vegetables\n- Managing stress effectively\n- Staying hydrated\n- Maintaining a healthy weight'

    Reranked: 'Based on The Personal Wellness Guide, here are the recommended exercises:\n\n## For Lower Back Pain:\n\n1. **Cat-Cow Stretch**: Start on hands and knees, alternate between arching your back up (cat) and letting it sag down (cow). Do 10-15 repetitions.\n\n2. **Bird Dog**: From hands and knees, extend opposite arm and leg while keeping your core engaged. Hold for 5 seconds, then switch sides. Do 10 repetitions per side.\n\n## For Neck and Shoulder Tension:\n\n1. **Neck Rolls**: Slowly roll your head in a circle, 5 times in each direction.\n\n2. **Shoulder Shrugs**: Raise shoulders toward ears, hold for 5 seconds, then release. Repeat 10 times.\n\n3. **Chest Opener**: Clasp hands behind back, squeeze shoulder blades together, and lift arms slightly. Hold for 15-30 seconds.\n\nThese exercises are described in the guide as gentle stretching and strengthening movements designed to help alleviate discomfort from lower back pain and relieve tension caused by desk work and poor posture.'
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #3:

    What are the benefits and limitations of using synthetic data generation for RAG evaluation? Consider both the practical advantages and potential pitfalls.

    ##### Answer:

    Benefits include fast, scalable test case generation without manual annotation and the ability to create diverse edge cases. Limitations are that synthetic data may not reflect real-world query distributions and can contain hallucinations or unrealistic scenarios that your production users wouldn't encounter.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #4:

    If you were building a production wellness assistant, which Ragas metrics would be most important to optimize for and why? Consider the healthcare/wellness domain specifically.

    ##### Answer:

    For a production wellness assistant, **Faithfulness** and **FactualCorrectness** are the most critical metrics. In healthcare, giving users inaccurate or made-up information can directly harm their health, so the assistant must only provide responses grounded in the retrieved context with verified facts.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Activity #1: Implement a Different Reranking Strategy

    In this activity, you'll experiment with different reranking parameters or strategies to see how they affect the evaluation metrics.

    **Requirements:**
    1. Modify the `retrieve_adjusted` function to use different parameters (e.g., change `k` values, try different top_n for reranking)
    2. Or implement a different retrieval enhancement strategy (e.g., hybrid search, query expansion)
    3. Run the evaluation and compare results with the baseline and reranking results above
    4. Document your findings in the markdown cell below
    """)
    return


@app.cell
def _(adjusted_example_retriever):
    ### YOUR CODE HERE ###

    # Implement your custom retrieval strategy here
    # Query Expansion + Deduplication Strategy

    def retrieve_custom(state):
        from sentence_transformers import CrossEncoder
        import numpy as np

        cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        original_query = state["question"]

        query_expansions = {
            "sleep": ["sleep hygiene", "insomnia remedies", "better sleep"],
            "exercise": ["physical activity", "workout tips", "fitness routine"],
            "nutrition": ["healthy eating", "dietary guidelines", "food choices"],
            "stress": ["stress management", "mental wellness", "relaxation techniques"],
            "back pain": [
                "lower back exercises",
                "spinal health",
                "posture improvement",
            ],
            "neck": ["neck tension relief", "shoulder stretches", "headache treatment"],
            "weight": [
                "healthy weight management",
                "calorie balance",
                "body mass index",
            ],
            "hydration": ["water intake", "drinking fluids", "dehydration prevention"],
        }

        expanded_queries = [original_query]
        query_lower = original_query.lower()
        for key, expansions in query_expansions.items():
            if key in query_lower:
                expanded_queries.extend(expansions)

        all_docs = []
        for q in set(expanded_queries):
            docs = adjusted_example_retriever.invoke(q)
            all_docs.extend(docs)

        seen_content = set()
        unique_docs = []
        for doc in all_docs:
            content_hash = hash(doc.page_content[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)

        if not unique_docs:
            return {"context": []}

        pairs = [[original_query, doc.page_content] for doc in unique_docs]
        scores = cross_encoder.predict(pairs)

        top_indices = np.argsort(scores)[::-1][:8]
        reranked_docs = [unique_docs[i] for i in top_indices]

        return {"context": reranked_docs}

    return (retrieve_custom,)


@app.cell
def _(Document, List, START, StateGraph, TypedDict, generate, retrieve_custom):
    class CustomState(TypedDict):
        question: str
        context: List[Document]
        response: str

    custom_graph_builder = StateGraph(CustomState).add_sequence(
        [retrieve_custom, generate]
    )
    custom_graph_builder.add_edge(START, "retrieve_custom")
    custom_graph = custom_graph_builder.compile()
    return (custom_graph,)


@app.cell
def _(custom_graph):
    test_response = custom_graph.invoke(
        {"question": "How can I improve my sleep quality?"}
    )
    test_response["response"]
    return


@app.cell
def _(copy, custom_graph, dataset, time):
    custom_dataset = copy.deepcopy(dataset)
    for _test_row in custom_dataset:
        response_custom = custom_graph.invoke(
            {"question": _test_row.eval_sample.user_input}
        )
        _test_row.eval_sample.response = response_custom["response"]
        _test_row.eval_sample.retrieved_contexts = [
            context.page_content for context in response_custom["context"]
        ]
        time.sleep(2)
    return (custom_dataset,)


@app.cell
def _(EvaluationDataset, custom_dataset):
    custom_evaluation_dataset = EvaluationDataset.from_pandas(
        custom_dataset.to_pandas()
    )
    return (custom_evaluation_dataset,)


@app.cell
def _(
    ContextEntityRecall,
    FactualCorrectness,
    Faithfulness,
    LLMContextRecall,
    NoiseSensitivity,
    ResponseRelevancy,
    custom_evaluation_dataset,
    custom_run_config,
    evaluate,
    evaluator_llm,
    generator_embeddings,
):
    custom_result = evaluate(
        dataset=custom_evaluation_dataset,
        metrics=[
            LLMContextRecall(),
            Faithfulness(),
            FactualCorrectness(),
            ResponseRelevancy(),
            ContextEntityRecall(),
            NoiseSensitivity(),
        ],
        llm=evaluator_llm,
        embeddings=generator_embeddings,
        run_config=custom_run_config,
    )
    custom_result
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Activity #1 Findings:

    I implemented a **Query Expansion + Deduplication** custom retrieval strategy.

    **Strategy Details:**
    1. **Query Expansion**: Detected keywords in the original query (e.g., "sleep", "exercise", "stress") and automatically expanded with 2-3 related health terms
       - E.g., "sleep quality" → also retrieves using "sleep hygiene", "insomnia remedies", "better sleep"
    2. **Multi-query Retrieval**: Ran the retriever with each expanded query variant to gather more diverse results
    3. **Content-based Deduplication**: Used hash of first 100 characters to remove duplicate/very similar documents
    4. **Reranking**: Applied cross-encoder reranking to get final top 8 results

    **Comparison:**
    - Baseline: Uses k=3 with no reranking
    - Reranked (original): Uses k=20 initial retrieval, then reranks to top 5
    - Custom: Query expansion + deduplication + reranking to top 8

    Despite all of this engineering I put into making the query expansion relevant, and deduplicating the retrieved documents so to get more unique rerankings, the output of this custom project was almost exactly the same as the Adjusted graph without reranking.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## RAGAS Metrics vs RAG Pipeline Components Diagram

    ```
    ┌─────────────────────────────────────────────────────────────────────────────────────────┐
    │                              RAG PIPELINE                                               │
    └─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │   INPUT      │     │  RETRIEVAL   │     │  AUGMENTED   │     │  GENERATION │
    │   (Query)    │────▶│  (Retriever) │────▶│  CONTEXT     │────▶│    (LLM)     │
    └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                    │                   │                    │
                                    ▼                   ▼                    ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────────┐
    │                              RAGAS METRICS                                              │
    └─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌────────────────────────────┐  ┌────────────────────────────┐  ┌────────────────────────────┐
    │   RETRIEVAL METRICS        │  │   CONTEXT METRICS          │  │   RESPONSE METRICS         │
    ├────────────────────────────┤  ├────────────────────────────┤  ├────────────────────────────┤
    │ • Context Precision        │  │ • LLMContextRecall         │  │ • Faithfulness             │
    │   (Is relevant context     │  │   (How much of ground      │  │   (Response matches        │
    │    ranked highest?)        │  │    truth is retrieved?)    │  │    context?)               │
    │                            │  │                            │  │                            │
    │ • Context Recall           │  │ • ContextEntityRecall      │  │ • FactualCorrectness       │
    │   (Are relevant docs       │  │   (Entities from ground    │  │   (Answer matches          │
    │    retrieved?)             │  │    truth in context?)      │  │    ground truth?)          │
    │                            │  │                            │  │                            │
    │ • Noise Sensitivity        │  │                            │  │ • ResponseRelevancy        │
    │   (Impact of irrelevant    │  │                            │  │   (Answer relevant to      │
    │    docs on response?)      │  │                            │  │    query?)                 │
    └────────────────────────────┘  └────────────────────────────┘  └────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────────────────┐
    │                              AGENT METRICS (for Agentic RAG)                           │
    └─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌────────────────────────────┐  ┌────────────────────────────┐  ┌────────────────────────────┐
    │ • Tool Call Accuracy       │  │ • Agent Goal Accuracy      │  │ • Topic Adherence          │
    │   (Correct tool called     │  │   (Did agent achieve       │  │   (Agent stays on          │
    │    with correct args?)     │  │    user's goal?)           │  │    topic?)                 │
    └────────────────────────────┘  └────────────────────────────┘  └────────────────────────────┘

    ```

    ### Mapping Summary:

    **Retrieval Component** → Context Precision, Context Recall, Noise Sensitivity
    - These metrics evaluate the quality of documents retrieved from the vector store

    **Context/Augmentation** → LLMContextRecall, ContextEntityRecall  
    - These metrics measure how well the retrieved context captures the needed information

    **Generation Component** → Faithfulness, FactualCorrectness, ResponseRelevancy
    - These metrics assess the quality of the LLM-generated response

    **Agent/Tool Use** → ToolCallAccuracy, AgentGoalAccuracy, TopicAdherence
    - These metrics evaluate agent behavior beyond simple RAG
    """)
    return


if __name__ == "__main__":
    app.run()
