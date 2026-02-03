import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The Agent Loop: Building Production Agents with LangChain 1.0

    In this notebook, we'll explore the foundational concepts of AI agents and learn how to build production-grade agents using LangChain's new `create_agent` abstraction with middleware support.

    **Learning Objectives:**
    - Understand what an "agent" is and how the agent loop works
    - Learn the core constructs of LangChain (Runnables, LCEL)
    - Master the `create_agent` function and middleware system
    - Build an agentic RAG application using Qdrant

    ## Table of Contents:

    - **Breakout Room #1:** Introduction to LangChain, LangSmith, and `create_agent`
      - Task 1: Dependencies
      - Task 2: Environment Variables
      - Task 3: LangChain Core Concepts (Runnables & LCEL)
      - Task 4: Understanding the Agent Loop
      - Task 5: Building Your First Agent with `create_agent()`
      - Question #1 & Question #2
      - Activity #1: Create a Custom Tool

    - **Breakout Room #2:** Middleware - Agentic RAG with Qdrant
      - Task 6: Loading & Chunking Documents
      - Task 7: Setting up Qdrant Vector Database
      - Task 8: Creating a RAG Tool
      - Task 9: Introduction to Middleware
      - Task 10: Building Agentic RAG with Middleware
      - Question #3 & Question #4
      - Activity #2: Enhance the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🤝 Breakout Room #1
    ## Introduction to LangChain, LangSmith, and `create_agent`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Dependencies

    First, let's ensure we have all the required packages installed. We'll be using:

    - **LangChain 1.0+**: The core framework with the new `create_agent` API
    - **LangChain-OpenAI**: OpenAI model integrations
    - **LangSmith**: Observability and tracing
    - **Qdrant**: Vector database for RAG
    - **tiktoken**: Token counting for text splitting
    """)
    return


@app.cell
def _():
    # Run this cell to install dependencies (if not using uv sync)
    # !pip install langchain>=1.0.0 langchain-openai langfuse langgraph qdrant-client langchain-qdrant tiktoken nest-asyncio
    return


@app.cell
def _():
    # Core imports we'll use throughout the notebook
    import os
    import getpass
    from uuid import uuid4

    import nest_asyncio

    nest_asyncio.apply()  # Required for async operations in Jupyter
    return getpass, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 2: Environment Variables

    We need to set up our API keys for:
    1. **OpenAI** - For the GPT-5 model
    2. **LangFuse** - For tracing and observability (self-hosted, open source)
    """)
    return


@app.cell
def _(getpass, os):
    # Set OpenAI API Key
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key: ")
    return


@app.cell
def _(os):
    # Set up LangFuse for tracing (self-hosted, open source)
    # This provides powerful debugging and observability for your agents
    # Note: LangFuse server needs to be running at the specified URL

    os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-b76a11bf-0d3e-4b42-981d-aef04ac7ac80"
    os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-31d5642a-6af9-436a-a2aa-a3ab1b310995"

    if os.environ["LANGFUSE_PUBLIC_KEY"] and os.environ["LANGFUSE_SECRET_KEY"]:
        os.environ["LANGFUSE_BASE_URL"] = os.environ.get(
            "LANGFUSE_BASE_URL", "http://localhost:3000"
        )
        print(f"LangFuse tracing enabled. Base URL: {os.environ['LANGFUSE_BASE_URL']}")
    else:
        print("LangFuse tracing disabled")
    return


@app.cell
def _(os):
    # Initialize LangFuse for tracing (if enabled)
    import os as _os

    langfuse_handler = None
    langfuse = None

    if os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY"):
        from langfuse import get_client
        from langfuse.langchain import CallbackHandler

        # Get LangFuse client singleton
        langfuse = get_client()

        # Create LangFuse callback handler for LangChain
        langfuse_handler = CallbackHandler()

        print("LangFuse handler initialized!")
    else:
        print("LangFuse handler disabled - skipping initialization")
    return (langfuse_handler,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 3: LangChain Core Concepts

    Before diving into agents, let's understand the fundamental building blocks of LangChain.

    ### What is a Runnable?

    A **Runnable** is the core abstraction in LangChain - think of it as a standardized component that:
    - Takes an input
    - Performs some operation
    - Returns an output

    Every component in LangChain (models, prompts, retrievers, parsers) is a Runnable, which means they all share the same interface:

    ```python
    result = runnable.invoke(input)           # Single input
    results = runnable.batch([input1, input2]) # Multiple inputs
    for chunk in runnable.stream(input):       # Streaming
        print(chunk)
    ```

    ### What is LCEL (LangChain Expression Language)?

    **LCEL** allows you to chain Runnables together using the `|` (pipe) operator:

    ```python
    chain = prompt | model | output_parser
    result = chain.invoke({"query": "Hello!"})
    ```

    This is similar to Unix pipes - the output of one component becomes the input to the next.
    """)
    return


@app.cell
def _():
    # Let's see LCEL in action with a simple example
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    # Create our components (each is a Runnable)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant that speaks like a pirate."),
            ("human", "{question}"),
        ]
    )

    model = ChatOpenAI(
        model="openai/gpt-oss-120b",
        base_url="http://192.168.1.79:8080/v1",
        temperature=0.7,
    )

    output_parser = StrOutputParser()

    # Chain them together with LCEL
    pirate_chain = prompt | model | output_parser
    return ChatOpenAI, pirate_chain


@app.cell
def _(langfuse_handler, pirate_chain):
    # Invoke the chain (with LangFuse tracing if enabled)
    config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}
    response = pirate_chain.invoke(
        {"question": "What is the capital of France?"}, config=config
    )
    print(response)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Understanding the Agent Loop

    ### What is an Agent?

    An **agent** is a system that uses an LLM to decide what actions to take. Unlike a simple chain that follows a fixed sequence, an agent can:

    1. **Reason** about what to do next
    2. **Take actions** by calling tools
    3. **Observe** the results
    4. **Iterate** until the task is complete

    ### The Agent Loop

    The core of every agent is the **agent loop**:

    ```
                              AGENT LOOP

          +----------+     +----------+     +----------+
          |  Model   | --> |   Tool   | --> |  Model   | --> ...
          |   Call   |     |   Call   |     |   Call   |
          +----------+     +----------+     +----------+
               |                                  |
               v                                  v
          "Use search"                   "Here's the answer"
    ```

    1. **Model Call**: The LLM receives the current state and decides whether to:
       - Call a tool (continue the loop)
       - Return a final answer (exit the loop)

    2. **Tool Call**: If the model decides to use a tool, the tool is executed and its output is added to the conversation

    3. **Repeat**: The loop continues until the model decides it has enough information to answer

    ### Why `create_agent`?

    LangChain 1.0 introduced `create_agent` as the new standard way to build agents. It provides:

    - **Simplified API**: One function to create production-ready agents
    - **Middleware Support**: Hook into any point in the agent loop
    - **Built on LangGraph**: Uses the battle-tested LangGraph runtime under the hood
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 5: Building Your First Agent with `create_agent()`

    Let's build a simple agent that can perform calculations and tell the time.

    ### Step 1: Define Tools

    Tools are functions that the agent can call. We use the `@tool` decorator to create them.
    """)
    return


@app.cell
def _():
    from langchain_core.tools import tool

    @tool
    def calculate(expression: str) -> str:
        """Evaluate a mathematical expression. Use this for any math calculations.

        Args:
            expression: A mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')
        """
        try:
            # Using eval with restricted globals for safety
            result = eval(expression, {"__builtins__": {}}, {})
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"Error evaluating expression: {e}"

    @tool
    def get_current_time() -> str:
        """Get the current date and time. Use this when the user asks about the current time or date."""
        from datetime import datetime

        return f"The current date and time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Create our tool belt
    tools = [calculate, get_current_time]

    print("Tools created:")
    for t in tools:
        print(f"  - {t.name}: {t.description[:60]}...")
    return calculate, get_current_time, tool, tools


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 2: Create the Agent

    Now we use `create_agent` to build our agent. The function takes:
    - `model`: The LLM to use (can be a string like `"gpt-5"` or a model instance)
    - `tools`: List of tools the agent can use
    - `prompt`: Optional system prompt to customize behavior
    """)
    return


@app.cell
def _(ChatOpenAI, tools):
    from langchain.agents import create_agent

    local_model = ChatOpenAI(
        model="openai/gpt-oss-120b",
        base_url="http://192.168.1.79:8080/v1",
        temperature=0.7,
    )

    # Create our first agent
    simple_agent = create_agent(
        model=local_model,
        tools=tools,
        system_prompt="You are a helpful assistant that can perform calculations and tell the time. Always explain your reasoning.",
    )

    print("Agent created successfully!")
    print(f"Type: {type(simple_agent)}")
    return create_agent, local_model, simple_agent


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 3: Run the Agent

    The agent is a Runnable, so we can invoke it like any other LangChain component.
    """)
    return


@app.cell
def _(langfuse_handler, simple_agent):
    # Test the agent with a simple calculation (with LangFuse tracing if enabled)
    response_1 = simple_agent.invoke(
        {"messages": [{"role": "user", "content": "What is 25 * 48?"}]},
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )
    print("Agent Response:")
    # Print the final response
    print(response_1["messages"][-1].content)
    return


@app.cell
def _(langfuse_handler, simple_agent):
    # Test with a multi-step question that requires multiple tool calls (with LangFuse tracing if enabled)
    response_2 = simple_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What time is it, and what is 100 divided by the current hour?",
                }
            ]
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )
    print("Agent Response:")
    print(response_2["messages"][-1].content)
    return (response_2,)


@app.cell
def _(response_2):
    print("Full Agent Conversation:")
    print("=" * 50)
    for _msg in response_2["messages"]:
        role = _msg.type if hasattr(_msg, "type") else "unknown"
        content = _msg.content if hasattr(_msg, "content") else str(_msg)
        print(f"\n[{role.upper()}]")
        print(content[:500] if len(str(content)) > 500 else content)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Streaming Agent Responses

    For better UX, we can stream the agent's responses as they're generated.
    """)
    return


@app.cell
def _(simple_agent):
    # Stream the agent's response
    print("Streaming Agent Response:")
    print("=" * 50)
    for chunk in simple_agent.stream(
        {"messages": [{"role": "user", "content": "Calculate 15% of 250"}]},
        stream_mode="updates",
    ):
        for node, values in chunk.items():
            print(f"\n[Node: {node}]")
            if "messages" in values:
                for _msg in values["messages"]:
                    if hasattr(_msg, "content") and _msg.content:
                        print(_msg.content)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ❓ Question #1:

    In the agent loop, what determines whether the agent continues to call tools or returns a final answer to the user? How does `create_agent` handle this decision internally?

    ##### ✅ Answer:
    *The LLM decides whether to call tools or return a final answer based on the current conversation state. `create_agent` handles this using LangGraph, which repeatedly calls the model and checks its output for tool calls—if there are any, it executes them and loops back; if not, it returns the final response.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #2:

    Looking at the `calculate` and `get_current_time` tools we created, why is the **docstring** so important for each tool? How does the agent use this information when deciding which tool to call?

    ##### ✅ Answer:
    *The docstring describes what each tool does and when to use it. The agent reads these descriptions to match the user's request with the right tool.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #1: Create a Custom Tool

    Create your own custom tool and add it to the agent!

    Ideas:
    - A tool that converts temperatures between Celsius and Fahrenheit
    - A tool that generates a random number within a range
    - A tool that counts words in a given text

    Requirements:
    1. Use the `@tool` decorator
    2. Include a clear docstring (this is what the agent sees!)
    3. Add it to the agent and test it
    """)
    return


@app.cell
def _(create_agent, local_model, tool):
    ### YOUR CODE HERE ###

    # Create your custom tool
    from langchain_community.utilities import SearxSearchWrapper

    @tool
    def my_custom_tool(query: str) -> str:
        """Search the web using SearxNG meta search engine. Use this tool when you need to find current information, answer questions about recent events, or look up facts that may not be in your training data.

        Args:
            query: The search query to look up on the web
        """
        try:
            searx = SearxSearchWrapper(searx_host="http://192.168.1.36:4000", k=5)
            results = searx.results(query, num_results=5)

            if not results:
                return f"No search results found for query: {query}"

            formatted_results = []
            for i, result in enumerate(results[:5], 1):
                title = result.get("title", "No title")
                link = result.get("link", "No URL")
                snippet = result.get("snippet", "No description available")
                formatted_results.append(
                    f"{i}. {title}\n   URL: {link}\n   Description: {snippet}"
                )

            return f"Search results for '{query}':\n\n" + "\n\n".join(formatted_results)
        except Exception as e:
            return f"Error performing web search: {str(e)}"

    # Add your tool to the tools list and create a new agent
    web_search_tools = [my_custom_tool]

    web_search_agent = create_agent(
        model=local_model,
        tools=web_search_tools,
        system_prompt="You are a helpful assistant with web search capabilities. Use the web search tool to find current information and answer questions about recent events or topics that may require up-to-date data.",
    )

    print("Web Search Agent created successfully!")
    return (web_search_agent,)


@app.cell
def _(web_search_agent):
    # Test your custom tool with the agent
    response_test = web_search_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What are the latest developments in AI?",
                }
            ]
        },
    )

    print("Web Search Agent Response:")
    print("=" * 50)
    print(response_test["messages"][-1].content)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🤝 Breakout Room #2
    ## Middleware - Agentic RAG with Qdrant
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now that we understand the basics of agents, let's build something more powerful: an **Agentic RAG** system.

    Traditional RAG follows a fixed pattern: retrieve → generate. But **Agentic RAG** gives the agent control over when and how to retrieve information, making it more flexible and intelligent.

    We'll also introduce **middleware** - hooks that let us customize the agent's behavior at every step.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 6: Loading & Chunking Documents

    We'll use the same Health & Wellness Guide from Session 2 to maintain continuity.
    """)
    return


@app.cell
def _():
    # Load the document using our aimakerspace utilities
    from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter

    # Load the document
    text_loader = TextFileLoader("data/HealthWellnessGuide.txt")
    documents = text_loader.load_documents()

    print(f"Loaded {len(documents)} document(s)")
    print(f"Total characters: {sum(len(doc) for doc in documents):,}")
    return CharacterTextSplitter, documents


@app.cell
def _(CharacterTextSplitter, documents):
    # Split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    chunks = text_splitter.split_texts(documents)

    print(f"Split into {len(chunks)} chunks")
    print(f"\nSample chunk:")
    print("-" * 50)
    print(chunks[0][:300] + "...")
    return (chunks,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 7: Setting up Qdrant Vector Database

    Qdrant is a production-ready vector database. We'll use an in-memory instance for development, but the same code works with a hosted Qdrant instance.

    Key concepts:
    - **Collection**: A namespace for storing vectors (like a table in SQL)
    - **Points**: Individual vectors with optional payloads (metadata)
    - **Distance**: How similarity is measured (we'll use cosine similarity)
    """)
    return


@app.cell
def _():
    from langchain_openai import OpenAIEmbeddings
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams

    # Initialize the embedding model
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-nomic-embed-text-v2-moe",
        base_url="http://192.168.1.79:8080/v1",
        check_embedding_ctx_length=False,
    )

    # Get embedding dimension
    sample_embedding = embedding_model.embed_query("test")
    embedding_dim = len(sample_embedding)
    print(f"Embedding dimension: {embedding_dim}")
    return (
        Distance,
        QdrantClient,
        QdrantVectorStore,
        VectorParams,
        embedding_dim,
        embedding_model,
    )


@app.cell
def _(Distance, QdrantClient, VectorParams, embedding_dim):
    # Create Qdrant client (in-memory for development)
    qdrant_client = QdrantClient(":memory:")

    # Create a collection for our wellness documents
    collection_name = "wellness_knowledge_base"

    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
    )

    print(f"Created collection: {collection_name}")
    return collection_name, qdrant_client


@app.cell
def _(
    QdrantVectorStore,
    chunks,
    collection_name,
    embedding_model,
    qdrant_client,
):
    # Create the vector store and add documents
    from langchain_core.documents import Document

    # Add metadata to documents for filtering
    # We'll categorize chunks by content type and assign chunk indices
    from typing import List, Tuple

    langchain_docs = []
    for idx, chunk in enumerate(chunks):
        # Determine category based on content
        category = "general"
        chunk_lower = chunk.lower()

        if any(
            word in chunk_lower for word in ["sleep", "rest", "bedtime", "insomnia"]
        ):
            category = "sleep"
        elif any(
            word in chunk_lower
            for word in ["exercise", "workout", "fitness", "training"]
        ):
            category = "fitness"
        elif any(
            word in chunk_lower
            for word in ["nutrition", "diet", "food", "meal", "protein"]
        ):
            category = "nutrition"
        elif any(
            word in chunk_lower
            for word in ["stress", "mental", "anxiety", "mindfulness", "meditation"]
        ):
            category = "mental_health"

        doc = Document(
            page_content=chunk,
            metadata={
                "source": "HealthWellnessGuide.txt",
                "chunk_id": idx,
                "category": category,
                "total_chunks": len(chunks),
            },
        )
        langchain_docs.append(doc)

    # Create vector store
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embedding_model,
    )

    # Add documents to the vector store
    vector_store.add_documents(langchain_docs)

    print(f"Added {len(langchain_docs)} documents to vector store with metadata")

    # Print category distribution
    from collections import Counter

    categories = [doc.metadata["category"] for doc in langchain_docs]
    print(f"Document distribution: {dict(Counter(categories))}")

    return (
        langchain_docs,
        vector_store,
    )


@app.cell
def _(vector_store):
    # Test the retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    test_results = retriever.invoke("How can I improve my sleep?")

    print("Retrieved documents:")
    for i, doc in enumerate(test_results, 1):
        print(f"\n--- Document {i} ---")
        print(doc.page_content[:200] + "...")
    return (retriever,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 8: Creating a RAG Tool

    Now we'll wrap our retriever as a tool that the agent can use. This is the key to **Agentic RAG** - the agent decides when to retrieve information.
    """)
    return


@app.cell
def _(retriever, tool, vector_store):
    from typing import Optional

    @tool
    def search_wellness_knowledge(
        query: str, category_filter: Optional[str] = None
    ) -> str:
        """Search the wellness knowledge base for information about health, fitness, nutrition, sleep, and mental wellness.

        Use this tool when the user asks questions about:
        - Physical health and fitness
        - Nutrition and diet
        - Sleep and rest
        - Mental health and stress management
        - General wellness tips

        Args:
            query: The search query to find relevant wellness information
            category_filter: Optional filter by category - use values like 'sleep', 'fitness', 'nutrition', or 'mental_health'
        """

        # Build metadata filter if category is specified
        from qdrant_client.http import models as qdrant_models

        search_kwargs = {"k": 3}
        qdrant_filter = None

        if category_filter:
            # Map friendly names to metadata values
            category_map = {
                "sleep": "sleep",
                "fitness": "fitness",
                "nutrition": "nutrition",
                "mental health": "mental_health",
                "mental_health": "mental_health",
            }

            mapped_category = category_map.get(category_filter.lower())
            if mapped_category:
                qdrant_filter = qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="metadata.category",
                            match=qdrant_models.MatchValue(value=mapped_category),
                        )
                    ]
                )

        # Use similarity_search_with_relevance_scores to get documents with scores
        if qdrant_filter:
            results = vector_store.similarity_search_with_relevance_scores(
                query, k=3, filter=qdrant_filter
            )
        else:
            results = vector_store.similarity_search_with_relevance_scores(query, k=3)

        if not results:
            return "No relevant information found in the wellness knowledge base."

        # Sort by relevance score (highest first) for reranking
        results.sort(key=lambda x: x[1], reverse=True)

        # Format with source citations and relevance scores
        formatted_results = []
        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get("source", "Unknown")
            chunk_id = doc.metadata.get("chunk_id", "?")
            category = doc.metadata.get("category", "general")

            formatted_results.append(
                f"[Source {i} - Relevance: {score:.2%}] (Category: {category}, Source: {source}#{chunk_id}):\n"
                f"{doc.page_content}"
            )

        return "\n\n".join(formatted_results)

    print(
        "Enhanced wellness knowledge base tool created with metadata filtering, reranking, and citations!"
    )
    return (search_wellness_knowledge,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 9: Introduction to Middleware

    **Middleware** in LangChain 1.0 allows you to hook into the agent loop at various points:

    ```
                           MIDDLEWARE HOOKS

       +--------------+                    +--------------+
       | before_model | --> MODEL CALL --> | after_model  |
       +--------------+                    +--------------+

       +-------------------+
       | wrap_model_call   |  (intercept and modify calls)
       +-------------------+
    ```

    Common use cases:
    - **Logging**: Track what the agent is doing
    - **Guardrails**: Filter or modify inputs/outputs
    - **Rate limiting**: Control API usage
    - **Human-in-the-loop**: Pause for human approval

    LangChain provides middleware through **decorator functions** that hook into specific points in the agent loop.
    """)
    return


@app.cell
def _():
    from langchain.agents.middleware import before_model, after_model

    call_count = {"value": 0}

    @before_model
    def log_before_model(state, runtime):
        """Called before each model invocation."""
        call_count["value"] = call_count["value"] + 1
        message_count = len(state.get("messages", []))
        print(
            f"[LOG] Model call #{call_count['value']} - Messages in state: {message_count}"
        )
        return None

    @after_model
    def log_after_model(state, runtime):
        """Called after each model invocation."""
        last_message = state.get("messages", [])[-1] if state.get("messages") else None
        if last_message:
            has_tool_calls = (
                hasattr(last_message, "tool_calls") and last_message.tool_calls
            )
            print(f"[LOG] After model - Tool calls requested: {has_tool_calls}")
        return None

    print("Logging middleware created!")
    return log_after_model, log_before_model


@app.cell
def _():
    # You can also use the built-in ModelCallLimitMiddleware to prevent runaway agents
    from langchain.agents.middleware import ModelCallLimitMiddleware

    # This middleware will stop the agent after 10 model calls per thread
    call_limiter = ModelCallLimitMiddleware(
        thread_limit=10,  # Max calls per conversation thread
        run_limit=5,  # Max calls per single run
        exit_behavior="end",  # What to do when limit is reached
    )

    print("Call limit middleware created!")
    print(f"  - Thread limit: {call_limiter.thread_limit}")
    print(f"  - Run limit: {call_limiter.run_limit}")
    return (call_limiter,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 10: Building Agentic RAG with Middleware

    Now let's put it all together: an agentic RAG system with middleware support!
    """)
    return


@app.cell
def _(
    calculate,
    call_limiter,
    create_agent,
    get_current_time,
    local_model,
    log_after_model,
    log_before_model,
    search_wellness_knowledge,
):
    rag_tools = [search_wellness_knowledge, calculate, get_current_time]

    wellness_agent = create_agent(
        model=local_model,
        tools=rag_tools,
        system_prompt="You are a helpful wellness assistant with access to a comprehensive health and wellness knowledge base.\n\nYour role is to:\n1. Answer questions about health, fitness, nutrition, sleep, and mental wellness\n2. Always search the knowledge base when the user asks wellness-related questions\n3. Provide accurate, helpful information based on the retrieved context\n4. Be supportive and encouraging in your responses\n5. If you cannot find relevant information, say so honestly\n\nRemember: Always cite information from the knowledge base when applicable.",
        middleware=[log_before_model, log_after_model, call_limiter],
    )
    print("Wellness Agent created with middleware!")
    return (wellness_agent,)


@app.cell
def _(langfuse_handler, wellness_agent):
    # Test the wellness agent (with LangFuse tracing if enabled)
    print("Testing Wellness Agent")
    print("=" * 50)

    response_3 = wellness_agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "What are some tips for better sleep?"}
            ]
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )
    print("\\n" + "=" * 50)
    print("FINAL RESPONSE:")
    print("=" * 50)
    print(response_3["messages"][-1].content)
    return


@app.cell
def _(langfuse_handler, wellness_agent):
    # Test with a more complex query (with LangFuse tracing if enabled)
    print("Testing with complex query")
    print("=" * 50)
    response_4 = wellness_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I'm feeling stressed and having trouble sleeping. What should I do, and if I sleep 6 hours a night for a week, how many total hours is that?",
                }
            ]
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )
    print("\\n" + "=" * 50)
    print("FINAL RESPONSE:")
    print("=" * 50)
    print(response_4["messages"][-1].content)
    return


@app.cell
def _(langfuse_handler, wellness_agent):
    # Test the agent\'s ability to know when NOT to use RAG (with LangFuse tracing if enabled)
    print("Testing agent decision-making (should NOT use RAG)")
    print("=" * 50)
    response_5 = wellness_agent.invoke(
        {"messages": [{"role": "user", "content": "What is 125 * 8?"}]},
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )
    print("\\n" + "=" * 50)
    print("FINAL RESPONSE:")
    print("=" * 50)
    print(response_5["messages"][-1].content)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualizing the Agent

    The agent created by `create_agent` is built on LangGraph, so we can visualize its structure.
    """)
    return


@app.cell
def _(wellness_agent):
    # Display the agent graph
    try:
        from IPython.display import display, Image

        display(Image(wellness_agent.get_graph().draw_mermaid_png()))
    except Exception as e:
        print(f"Could not display graph: {e}")
        print("\nAgent structure:")
        print(wellness_agent.get_graph().draw_ascii())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ❓ Question #3:

    How does **Agentic RAG** differ from traditional RAG? What are the advantages and potential disadvantages of letting the agent decide when to retrieve information?

    ##### ✅ Answer:
    *Traditional RAG always retrieves before answering, while Agentic RAG lets the agent choose when to retrieve based on what it needs. The advantage is skipping unnecessary retrievals for simple questions, but the downside is the agent might sometimes miss retrieving important information it actually needs.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #4:

    Looking at the middleware examples (`log_before_model`, `log_after_model`, and `ModelCallLimitMiddleware`), describe a real-world scenario where middleware would be essential for a production agent. What specific middleware hooks would you use and why?

    ##### ✅ Answer:
    *A customer service bot would need `before_model` to log user IDs for tracking, `after_model` to capture token usage for billing, and `ModelCallLimitMiddleware` to stop users from spamming the system with too many requests.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #2: Enhance the Agentic RAG System

    Now it's your turn! Enhance the wellness agent by implementing ONE of the following:

    ### Option A: Add a New Tool
    Create a new tool that the agent can use. Ideas:
    - A tool that calculates BMI given height and weight
    - A tool that estimates daily calorie needs
    - A tool that creates a simple workout plan

    ### Option B: Create Custom Middleware
    Build middleware that adds new functionality:
    - Middleware that tracks which tools are used most frequently
    - Middleware that adds a friendly greeting to responses
    - Middleware that enforces a response length limit

    ### Option C: Improve the RAG Tool
    Enhance the retrieval tool:
    - Add metadata filtering
    - Implement reranking of results
    - Add source citations with relevance scores
    """)
    return


@app.cell
def _(
    call_limiter,
    calculate,
    create_agent,
    get_current_time,
    local_model,
    log_after_model,
    log_before_model,
    search_wellness_knowledge,
):
    ### OPTION C: Improve the RAG Tool - Already Implemented Above! ###

    # The search_wellness_knowledge tool has been enhanced with:
    # 1. Metadata Filtering - Supports category_filter parameter (sleep, fitness, nutrition, mental_health)
    # 2. Reranking - Results are sorted by relevance score (highest first)
    # 3. Source Citations - Each result includes source file, chunk_id, category, and relevance score

    # Create the enhanced wellness agent (this is already done above, but shown here for clarity)
    enhanced_rag_tools = [search_wellness_knowledge, calculate, get_current_time]

    enhanced_wellness_agent = create_agent(
        model=local_model,
        tools=enhanced_rag_tools,
        system_prompt="You are a helpful wellness assistant with access to a comprehensive health and wellness knowledge base.\n\nYour role is to:\n1. Answer questions about health, fitness, nutrition, sleep, and mental wellness\n2. Always search the knowledge base when the user asks wellness-related questions\n3. You can optionally filter searches by category: 'sleep', 'fitness', 'nutrition', or 'mental_health'\n4. The search tool provides results with relevance scores and source citations\n5. Provide accurate, helpful information based on the retrieved context\n6. Be supportive and encouraging in your responses\n7. If you cannot find relevant information, say so honestly",
        middleware=[log_before_model, log_after_model, call_limiter],
    )

    print("Enhanced Wellness Agent created with improved RAG tool!")
    print("\n✅ Enhancements implemented:")
    print(
        "  • Metadata Filtering: Filter by category (sleep, fitness, nutrition, mental_health)"
    )
    print("  • Reranking: Results automatically sorted by relevance score")
    print(
        "  • Source Citations: Each result includes source, chunk_id, category, and relevance score"
    )
    return (enhanced_wellness_agent,)


@app.cell
def _(enhanced_wellness_agent, langfuse_handler):
    # Test your enhanced agent here

    print("=" * 70)
    print("TEST 1: Basic Search with Relevance Scores and Citations")
    print("=" * 70)

    response_test1 = enhanced_wellness_agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "What are some tips for better sleep?"}
            ]
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )

    print("\nAgent Response:")
    print(response_test1["messages"][-1].content)

    print("\n" + "=" * 70)
    print("TEST 2: Search with Metadata Filtering (Category: Nutrition)")
    print("=" * 70)

    response_test2 = enhanced_wellness_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I want to improve my diet. What should I eat for better nutrition? Please search using the nutrition category filter.",
                }
            ]
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )

    print("\nAgent Response:")
    print(response_test2["messages"][-1].content)

    print("\n" + "=" * 70)
    print("TEST 3: Search with Metadata Filtering (Category: Mental Health)")
    print("=" * 70)

    response_test3 = enhanced_wellness_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I'm feeling stressed. How can I manage stress better? Please use the mental health category filter.",
                }
            ]
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )

    print("\nAgent Response:")
    print(response_test3["messages"][-1].content)

    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    return (response_test1, response_test2, response_test3)


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
