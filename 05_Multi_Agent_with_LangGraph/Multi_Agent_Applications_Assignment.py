import marimo

__generated_with = "0.19.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Multi-Agent Applications: Building Agent Teams with LangGraph

    In this notebook, we'll explore **multi-agent systems** - applications where multiple specialized agents collaborate to solve complex tasks. We'll build on our LangGraph foundation from Session 4 and create agent teams for our Personal Wellness Assistant.

    **Learning Objectives:**
    - Understand when and why to use multi-agent systems
    - Master the Supervisor pattern for orchestrating agent teams
    - Implement Agent Handoffs for dynamic task routing
    - Use SearxNG Search for web research capabilities
    - Apply context engineering principles to optimize agent performance
    - Visualize and debug multi-agent systems with Langfuse

    ## Table of Contents:

    - **Breakout Room #1:** Multi-Agent Fundamentals & Supervisor Pattern
      - Task 1: Dependencies & Environment Setup
      - Task 2: Understanding Multi-Agent Systems
      - Task 3: Building a Supervisor Agent Pattern
      - Task 4: Adding SearxNG Search for Web Research
      - Question #1 & Question #2
      - Activity #1: Add a Custom Specialist Agent

    - **Breakout Room #2:** Handoffs & Context Engineering
      - Task 5: Agent Handoffs Pattern
      - Task 6: Building a Wellness Agent Team
      - Task 7: Context Engineering & Optimization
      - Task 8: Visualizing and Debugging with Langfuse
      - Question #3 & Question #4
      - Activity #2: Implement Hierarchical Teams
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🤝 Breakout Room #1
    ## Multi-Agent Fundamentals & Supervisor Pattern
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Dependencies & Environment Setup

    Before we begin, make sure you have:

    1. **Self-hosted Services**:
       - Local LLM endpoint at http://192.168.1.79:8080/v1 (using glm-4.7 model)
       - SearxNG instance at http://192.168.1.36:4000 for web search
       - Langfuse instance (optional, for tracing) at http://localhost:3000

    2. **Dependencies installed** via `uv sync`

    **Models Used:**
    - **glm-4.7**: Both supervisor and specialist agents (local, self-hosted LLM)

    **Documentation:**
    - [SearxNG Search Tool](https://docs.langchain.com/oss/python/integrations/providers/searx)
    - [Langfuse for Tracing](https://langfuse.com/docs/sdks/python/low-level-sdk)
    """)
    return


@app.cell
def _():
    # Core imports
    import os
    import getpass
    import json
    from uuid import uuid4
    from typing import Annotated, TypedDict, Literal, Sequence
    import operator

    import nest_asyncio

    nest_asyncio.apply()  # Required for async operations in Jupyter
    return Annotated, Literal, TypedDict, getpass, os, uuid4


@app.cell
def _(os):
    # Set API Keys - Local LLM endpoint doesn't require an API key
    # We'll set a dummy key for compatibility with langchain-openai
    os.environ["OPENAI_API_KEY"] = "dummy-key-for-local-endpoint"
    return


@app.cell
def _():
    # SearxNG is self-hosted, no API key needed
    pass
    return


@app.cell
def _(getpass, os, uuid4):
    # Langfuse for tracing (self-hosted alternative to LangSmith)
    os.environ["LANGFUSE_PUBLIC_KEY"] = (
        getpass.getpass("Langfuse Public Key (press Enter to skip): ") or ""
    )
    os.environ["LANGFUSE_SECRET_KEY"] = (
        getpass.getpass("Langfuse Secret Key (press Enter to skip): ") or ""
    )
    os.environ["LANGFUSE_HOST"] = "http://localhost:3000"  # Default self-hosted URL
    os.environ["LANGFUSE_PROJECT"] = (
        f"AIE9 - Multi-Agent Applications - {uuid4().hex[0:8]}"
    )

    if not os.environ["LANGFUSE_PUBLIC_KEY"] or not os.environ["LANGFUSE_SECRET_KEY"]:
        print("Langfuse tracing disabled")
    else:
        print(f"Langfuse tracing enabled. Project: {os.environ['LANGFUSE_PROJECT']}")
    return


@app.cell
def _():
    # Initialize Langfuse callback handler for tracing
    try:
        from langfuse.langchain import CallbackHandler
        from langfuse import observe, propagate_attributes

        langfuse_handler = CallbackHandler()
    except Exception as e:
        print(f"Could not initialize Langfuse handler: {e}")
        langfuse_handler = None
    return langfuse_handler, observe, propagate_attributes


@app.cell
def _():
    # Initialize LLMs - Using local endpoint with glm-4.7 for both supervisor and specialists
    from langchain_openai import ChatOpenAI

    # Supervisor model - better reasoning for routing and orchestration
    supervisor_llm = ChatOpenAI(
        model="glm-4.7", temperature=0, base_url="http://192.168.1.79:8080/v1"
    )

    # Specialist model - cost-effective for domain-specific tasks
    specialist_llm = ChatOpenAI(
        model="glm-4.7", temperature=0, base_url="http://192.168.1.79:8080/v1"
    )

    # Test both models
    print("Testing models...")
    supervisor_response = supervisor_llm.invoke(
        "Say 'Supervisor ready!' in exactly 2 words."
    )
    specialist_response = specialist_llm.invoke(
        "Say 'Specialist ready!' in exactly 2 words."
    )

    print(f"Supervisor (glm-4.7): {supervisor_response.content}")
    print(f"Specialist (glm-4.7): {specialist_response.content}")
    return specialist_llm, supervisor_llm


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 2: Understanding Multi-Agent Systems

    ### When to Use Multi-Agent Systems

    Before building multi-agent systems, ask yourself:

    > **"Do I really need several specialized dynamic reasoning machines collaborating to solve this task more effectively than a single agent could?"**

    Multi-agent systems are useful when:
    1. **Tool/responsibility grouping**: Different tasks require different expertise
    2. **Prompt separation**: Different agents need different instructions/few-shot examples
    3. **Piecewise optimization**: Easier to improve individual components

    ### Key Multi-Agent Patterns

    | Pattern | Description | Use Case |
    |---------|-------------|----------|
    | **Supervisor** | Central orchestrator routes to specialist agents | Task delegation, quality control |
    | **Handoffs** | Agents transfer control to each other | Conversation flows, expertise routing |
    | **Hierarchical** | Supervisors manage teams of agents | Large-scale systems, departments |
    | **Network/Swarm** | Agents communicate freely | Collaborative problem-solving |

    ### Context Engineering Principles

    From leading practitioners:

    - **Dex Horthy (12-Factor Agents)**: "Own your context window and treat it like prime real estate"
    - **swyx (Agent Engineering)**: "Agent reliability = great context construction"
    - **Chroma (Context Rot)**: "Longer ≠ better when it comes to context"

    **Documentation:**
    - [Building Effective Agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents)
    - [Don't Build Multi-Agents (Cognition)](https://cognition.ai/blog/dont-build-multi-agents)
    - [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 3: Building a Supervisor Agent Pattern

    The **Supervisor Pattern** uses a central agent to:
    1. Analyze incoming requests
    2. Route to the appropriate specialist agent
    3. Aggregate and refine responses

    ```
                        ┌─────────────────┐
                        │   Supervisor    │
                        │   (Orchestrator)│
                        └────────┬────────┘
                                 │
               ┌─────────────────┼─────────────────┐
               │                 │                 │
               ▼                 ▼                 ▼
        ┌────────────┐    ┌────────────┐    ┌────────────┐
        │  Exercise  │    │  Nutrition │    │   Sleep    │
        │   Agent    │    │   Agent    │    │   Agent    │
        └────────────┘    └────────────┘    └────────────┘
    ```

    **Documentation:**
    - [LangGraph Supervisor Tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)
    """)
    return


@app.cell
def _():
    # Import LangGraph and LangChain components
    from langgraph.graph import StateGraph, START, END
    from langgraph.graph.message import add_messages
    from langchain.agents import create_agent  # LangChain 1.0 API
    from langchain_core.messages import (
        HumanMessage,
        AIMessage,
        SystemMessage,
        BaseMessage,
    )
    from langchain_core.tools import tool

    print("LangGraph and LangChain components imported!")
    return (
        AIMessage,
        BaseMessage,
        END,
        HumanMessage,
        START,
        StateGraph,
        SystemMessage,
        add_messages,
        create_agent,
        tool,
    )


@app.cell
def _():
    # First, let's set up our RAG system for the wellness knowledge base
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams

    # Load and chunk the wellness document
    loader = TextLoader("data/HealthWellnessGuide.txt")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    print(f"Loaded and split into {len(chunks)} chunks")
    return (
        Distance,
        OpenAIEmbeddings,
        QdrantClient,
        QdrantVectorStore,
        VectorParams,
        chunks,
    )


@app.cell
def _(
    Distance,
    OpenAIEmbeddings,
    QdrantClient,
    QdrantVectorStore,
    VectorParams,
    chunks,
):
    # Set up vector store with local endpoint
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-nomic-embed-text-v2-moe",
        base_url="http://192.168.1.79:8080/v1",
        check_embedding_ctx_length=False,
    )
    embedding_dim = len(embedding_model.embed_query("test"))

    qdrant_client = QdrantClient(":memory:")
    qdrant_client.create_collection(
        collection_name="wellness_multiagent",
        vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
    )

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name="wellness_multiagent",
        embedding=embedding_model,
    )
    vector_store.add_documents(chunks)

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    print(f"Vector store ready with {len(chunks)} documents")
    return (retriever,)


@app.cell
def _(retriever, tool):
    # Create specialized tools for each agent domain

    @tool
    def search_exercise_info(query: str) -> str:
        """Search for exercise, fitness, and workout information from the wellness knowledge base.
        Use this for questions about physical activity, workout routines, and exercise techniques.
        """
        results = retriever.invoke(f"exercise fitness workout {query}")
        if not results:
            return "No exercise information found."
        return "\n\n".join(
            [f"[Source {i + 1}]: {doc.page_content}" for i, doc in enumerate(results)]
        )

    @tool
    def search_nutrition_info(query: str) -> str:
        """Search for nutrition, diet, and healthy eating information from the wellness knowledge base.
        Use this for questions about food, meal planning, and dietary guidelines.
        """
        results = retriever.invoke(f"nutrition diet food meal {query}")
        if not results:
            return "No nutrition information found."
        return "\n\n".join(
            [f"[Source {i + 1}]: {doc.page_content}" for i, doc in enumerate(results)]
        )

    @tool
    def search_sleep_info(query: str) -> str:
        """Search for sleep, rest, and recovery information from the wellness knowledge base.
        Use this for questions about sleep quality, insomnia, and sleep hygiene.
        """
        results = retriever.invoke(f"sleep rest recovery insomnia {query}")
        if not results:
            return "No sleep information found."
        return "\n\n".join(
            [f"[Source {i + 1}]: {doc.page_content}" for i, doc in enumerate(results)]
        )

    @tool
    def search_stress_info(query: str) -> str:
        """Search for stress management and mental wellness information from the wellness knowledge base.
        Use this for questions about stress, anxiety, mindfulness, and mental health.
        """
        results = retriever.invoke(
            f"stress mental wellness mindfulness anxiety {query}"
        )
        if not results:
            return "No stress management information found."
        return "\n\n".join(
            [f"[Source {i + 1}]: {doc.page_content}" for i, doc in enumerate(results)]
        )

    print("Specialist tools created!")
    return (
        search_exercise_info,
        search_nutrition_info,
        search_sleep_info,
        search_stress_info,
    )


@app.cell
def _(
    create_agent,
    search_exercise_info,
    search_nutrition_info,
    search_sleep_info,
    search_stress_info,
    specialist_llm,
):
    # Create specialist agents using create_agent (LangChain 1.0 API)
    # Each specialist uses glm-4.7 for domain-specific tasks

    exercise_agent = create_agent(
        model=specialist_llm,
        tools=[search_exercise_info],
        system_prompt="You are an Exercise Specialist. Help users with workout routines, fitness tips, and physical activity guidance. Always search the knowledge base before answering. Be concise and helpful.",
    )

    nutrition_agent = create_agent(
        model=specialist_llm,
        tools=[search_nutrition_info],
        system_prompt="You are a Nutrition Specialist. Help users with diet advice, meal planning, and healthy eating. Always search the knowledge base before answering. Be concise and helpful.",
    )

    sleep_agent = create_agent(
        model=specialist_llm,
        tools=[search_sleep_info],
        system_prompt="You are a Sleep Specialist. Help users with sleep quality, insomnia, and rest optimization. Always search the knowledge base before answering. Be concise and helpful.",
    )

    stress_agent = create_agent(
        model=specialist_llm,
        tools=[search_stress_info],
        system_prompt="You are a Stress Management Specialist. Help users with stress relief, mindfulness, and mental wellness. Always search the knowledge base before answering. Be concise and helpful.",
    )

    print("Specialist agents created (using glm-4.7 with create_agent)!")
    return exercise_agent, nutrition_agent, sleep_agent, stress_agent


@app.cell
def _(Annotated, BaseMessage, Literal, TypedDict, add_messages):
    # Define the supervisor state and routing
    from typing import List
    from pydantic import BaseModel

    # Define routing options - supervisor picks ONE specialist, then that specialist responds
    class RouterOutput(BaseModel):
        """The supervisor's routing decision."""

        next: Literal["exercise", "nutrition", "sleep", "stress"]
        reasoning: str

    class SupervisorState(TypedDict):
        """State for the supervisor multi-agent system."""

        messages: Annotated[list[BaseMessage], add_messages]
        next: str

    print("Supervisor state defined!")
    return BaseModel, RouterOutput, SupervisorState


@app.cell
def _(
    HumanMessage,
    RouterOutput,
    SupervisorState,
    observe,
    propagate_attributes,
    supervisor_llm,
):
    # Create the supervisor node (using glm-4.7 for routing decisions)
    from langchain_core.prompts import ChatPromptTemplate

    supervisor_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Wellness Supervisor coordinating a team of specialist agents.

    Your team:
    - exercise: Handles fitness, workouts, physical activity, movement questions
    - nutrition: Handles diet, meal planning, healthy eating, food questions
    - sleep: Handles sleep quality, insomnia, rest, recovery questions
    - stress: Handles stress management, mindfulness, mental wellness, anxiety questions

    Based on the user's question, decide which ONE specialist should respond.
    Choose the most relevant specialist for the primary topic of the question.""",
            ),
            (
                "human",
                "User question: {question}\n\nWhich specialist should handle this?",
            ),
        ]
    )

    # Create structured output for routing (using glm-4.7)
    routing_llm = supervisor_llm.with_structured_output(RouterOutput)

    observe()

    def supervisor_node(state: SupervisorState):
        """The supervisor decides which agent to route to."""
        # Get the user's question from the last human message
        user_question = ""
        with propagate_attributes(session_id="supervisor_node"):
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    user_question = msg.content
                    break

            # Get routing decision
            prompt_value = supervisor_prompt.invoke({"question": user_question})
            result = routing_llm.invoke(prompt_value)

        print(f"[Supervisor glm-4.7] Routing to: {result.next}")
        print(f"  Reason: {result.reasoning}")

        return {"next": result.next}

    print("Supervisor node created (using glm-4.7)!")
    return ChatPromptTemplate, supervisor_node


@app.cell
def _(
    AIMessage,
    SupervisorState,
    exercise_agent,
    nutrition_agent,
    sleep_agent,
    stress_agent,
):
    # Create agent nodes that wrap the specialist agents

    def create_agent_node(agent, name: str):
        """Create a node that runs a specialist agent and returns the final response."""

        def agent_node(state: SupervisorState):
            print(f"[{name.upper()} Agent] Processing request...")

            # Invoke the specialist agent with the conversation
            result = agent.invoke({"messages": state["messages"]})

            # Get the agent's final response
            agent_response = result["messages"][-1]

            # Add agent identifier to the response
            response_with_name = AIMessage(
                content=f"[{name.upper()} SPECIALIST]\n\n{agent_response.content}",
                name=name,
            )

            print(f"[{name.upper()} Agent] Response complete.")
            return {"messages": [response_with_name]}

        return agent_node

    # Create nodes for each specialist
    exercise_node = create_agent_node(exercise_agent, "exercise")
    nutrition_node = create_agent_node(nutrition_agent, "nutrition")
    sleep_node = create_agent_node(sleep_agent, "sleep")
    stress_node = create_agent_node(stress_agent, "stress")

    print("Agent nodes created!")
    return exercise_node, nutrition_node, sleep_node, stress_node


@app.cell
def _(
    END,
    START,
    StateGraph,
    SupervisorState,
    exercise_node,
    nutrition_node,
    sleep_node,
    stress_node,
    supervisor_node,
):
    # Build the supervisor graph
    # KEY: Specialists go directly to END (no loop back to supervisor)

    def route_to_agent(state: SupervisorState) -> str:
        """Route to the next agent based on supervisor decision."""
        return state["next"]

    # Create the graph
    supervisor_workflow = StateGraph(SupervisorState)

    # Add nodes
    supervisor_workflow.add_node("supervisor", supervisor_node)
    supervisor_workflow.add_node("exercise", exercise_node)
    supervisor_workflow.add_node("nutrition", nutrition_node)
    supervisor_workflow.add_node("sleep", sleep_node)
    supervisor_workflow.add_node("stress", stress_node)

    # Add edges: START -> supervisor
    supervisor_workflow.add_edge(START, "supervisor")

    # Conditional routing from supervisor to specialists
    supervisor_workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "exercise": "exercise",
            "nutrition": "nutrition",
            "sleep": "sleep",
            "stress": "stress",
        },
    )

    # KEY FIX: Each specialist goes directly to END (no looping!)
    supervisor_workflow.add_edge("exercise", END)
    supervisor_workflow.add_edge("nutrition", END)
    supervisor_workflow.add_edge("sleep", END)
    supervisor_workflow.add_edge("stress", END)

    # Compile
    supervisor_graph = supervisor_workflow.compile()

    print("Supervisor multi-agent system built!")
    print("Flow: User -> Supervisor -> Specialist -> END")
    return route_to_agent, supervisor_graph, supervisor_workflow


@app.cell
def _(supervisor_graph):
    # Visualize the graph
    try:
        from IPython.display import display, Image

        display(Image(supervisor_graph.get_graph().draw_mermaid_png()))
    except Exception as e:
        print(f"Could not display graph: {e}")
        print("\nGraph structure:")
        print(supervisor_graph.get_graph().draw_ascii())
    return Image, display


@app.cell
def _(HumanMessage, langfuse_handler, supervisor_graph):
    # Test the supervisor system
    print("Testing Supervisor Multi-Agent System")
    print("=" * 50)

    _response = supervisor_graph.invoke(
        {
            "messages": [
                HumanMessage(content="What exercises can help with lower back pain?")
            ]
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )
    print("\nFinal Response:")
    print("=" * 50)
    print(_response["messages"][-1].content)

    # Flush Langfuse events
    if langfuse_handler:
        from langfuse import get_client

        langfuse = get_client()
        langfuse.flush()
    return (langfuse,)


@app.cell
def _(HumanMessage, langfuse, langfuse_handler, supervisor_graph):
    # Test with a nutrition question
    print("Testing with nutrition question")
    print("=" * 50)
    _response = supervisor_graph.invoke(
        {
            "messages": [
                HumanMessage(content="What should I eat for better gut health?")
            ]
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )
    print("\nFinal Response:")
    print("=" * 50)
    print(_response["messages"][-1].content)

    # Flush Langfuse events
    if langfuse_handler:
        langfuse.flush()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Adding SearxNG Search for Web Research

    Sometimes the wellness knowledge base doesn't have the latest information. Let's add **SearxNG Search** to allow agents to search the web for current information.

    SearxNG is a privacy-respecting metasearch engine that aggregates results from multiple search engines.

    **Documentation:**
    - [SearxNG Search Tool](https://docs.langchain.com/oss/python/integrations/providers/searx)
    """)
    return


@app.cell
def _():
    # Create a SearxNG search tool (using langchain-community)
    from langchain_community.tools.searx_search.tool import SearxSearchResults
    from langchain_community.utilities import SearxSearchWrapper

    # Create wrapper for self-hosted SearxNG instance
    searxng_wrapper = SearxSearchWrapper(searx_host="http://192.168.1.36:4000")

    # Create search tool
    searxng_search = SearxSearchResults(wrapper=searxng_wrapper, num_results=3)

    print(f"SearxNG search tool created")
    return (searxng_search,)


@app.cell
def _(searxng_search):
    # Test SearxNG search
    search_results = searxng_search.invoke(
        "latest research on benefits of morning exercise 2024"
    )
    print("SearxNG Search Results:")
    print("-" * 50)

    # Handle SearxNG response format
    if isinstance(search_results, str):
        print(search_results[:500])
    elif isinstance(search_results, dict) and "results" in search_results:
        for result in search_results["results"][:2]:
            print(f"\nTitle: {result.get('title', 'N/A')}")
            print(f"URL: {result.get('url', 'N/A')}")
            print(
                f"Content: {result.get('content', result.get('snippet', 'N/A'))[:200]}..."
            )
    return


@app.cell
def _(create_agent, retriever, searxng_search, specialist_llm, tool):
    # Create a research agent that can search both the knowledge base AND the web
    @tool
    def search_wellness_kb(query: str) -> str:
        """Search the local wellness knowledge base for established health information.
        Use this first for general wellness questions.
        """
        results = retriever.invoke(query)
        if not results:
            return "No information found in knowledge base."
        return "\n\n".join(
            [
                f"[KB Source {i + 1}]: {doc.page_content}"
                for i, doc in enumerate(results)
            ]
        )

    @tool
    def search_web_current(query: str) -> str:
        """Search the web for current/recent health and wellness information.
        Use this when you need the latest research, news, or information not in the knowledge base.
        """
        _response = searxng_search.invoke(query)
        if not _response:
            return "No web results found."

        # Handle SearxNG response format (returns string or dict)
        if isinstance(_response, str):
            return _response
        elif isinstance(_response, dict) and "results" in _response:
            formatted = []
            for i, r in enumerate(_response["results"][:3]):
                content = r.get("content", r.get("snippet", "N/A"))
                url = r.get("url", "N/A")
                formatted.append(f"[Web Source {i + 1}]: {content}\nURL: {url}")
            return "\n\n".join(formatted)
        else:
            return "No web results found."

    research_agent = create_agent(
        model=specialist_llm,
        tools=[search_wellness_kb, search_web_current],
        system_prompt="You are a Wellness Research Agent. You have access to both a curated knowledge base \nand web search. Use the knowledge base for established information and web search for \ncurrent/recent updates. Always cite your sources.",
    )
    # Create a research agent with both tools (using create_agent)
    print("Research agent with web search created (using create_agent)!")
    return (research_agent,)


@app.cell
def _(HumanMessage, langfuse, langfuse_handler, research_agent):
    # Test the research agent
    print("Testing Research Agent (KB + Web)")
    print("=" * 50)
    _response = research_agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What are the benefits of cold water immersion for recovery?"
                )
            ]
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )
    print("\nResearch Agent Response:")
    print(_response["messages"][-1].content)

    # Flush Langfuse events
    if langfuse_handler:
        langfuse.flush()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(rf"""
    ---
    ## ❓ Question #1:

    In the Supervisor pattern, the supervisor routes requests to specialist agents. What are the **advantages** and **disadvantages** of having agents loop back to the supervisor after responding, versus having them respond directly to the user?

    ##### Answer:
    *So I don't think you're necessarily looking for this answer, but Brooke's Law. Basically, anytime we add more agents to a project, we add not only more points of possible failure, but also "more hands make more work." This is shown in CooperBench.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #2:

    We added SearxNG web search alongside the knowledge base. In what scenarios would you want to **restrict** an agent to only use the knowledge base (no web search)? What are the trade-offs between freshness and reliability?

    ##### Answer:
    *I switched to SearxNG instead of Tavily because it's free and I'm self-hosting it, first off. Now, I would want to restrict an agent to only use the knowledge base when I know already that the answer isn't online. For example, I teach a graduate-level course at a university, and the students can use AI in the course, but our syllabus cannot be found with a Google Search, so if the students want to get the right answer to some of the homework based on the syllabus, they can't rely on web search to find it.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #1: Add a Custom Specialist Agent

    Add a new specialist agent to the supervisor system. Ideas:
    - **Habits Agent**: Helps with habit formation and routines
    - **Hydration Agent**: Focuses on water intake and hydration
    - **Lifestyle Agent**: Addresses work-life balance and digital wellness

    Requirements:
    1. Create a specialized search tool for your agent's domain
    2. Create the specialist agent with an appropriate system prompt
    3. Add the agent to the supervisor graph
    4. Update the routing logic
    5. Test with relevant questions
    """)
    return


@app.cell
def _(
    AIMessage,
    BaseModel,
    ChatPromptTemplate,
    END,
    HumanMessage,
    Literal,
    RouterOutput,
    START,
    StateGraph,
    SupervisorState,
    create_agent,
    exercise_agent,
    nutrition_agent,
    propagate_attributes,
    retriever,
    route_to_agent,
    sleep_agent,
    specialist_llm,
    stress_agent,
    supervisor_llm,
    tool,
):
    # Step 1: Create a specialized search tool
    @tool
    def search_hydration_info(query: str) -> str:
        """Search for hydration, water intake, and dehydration information from the wellness knowledge base.
        Use this for questions about daily water requirements, signs of dehydration, and hydration tips.
        """
        results = retriever.invoke(f"hydration water intake dehydrated {query}")
        if not results:
            return "No hydration information found."
        return "\n\n".join(
            [f"[Source {i + 1}]: {doc.page_content}" for i, doc in enumerate(results)]
        )

    # Step 2: Create the specialist agent
    hydration_agent = create_agent(
        model=specialist_llm,
        tools=[search_hydration_info],
        system_prompt="You are a Hydration Specialist. Help users with water intake recommendations, dehydration signs, and hydration tips. Always search the knowledge base before answering. Be concise and helpful.",
    )

    # Step 3: Rebuild the supervisor graph with hydration agent

    # Update routing options
    class NewRouterOutput(BaseModel):
        """The supervisor's routing decision."""

        next: Literal["exercise", "nutrition", "sleep", "stress", "hydration"]
        reasoning: str

    # Update supervisor prompt
    new_supervisor_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Wellness Supervisor coordinating a team of specialist agents.

    Your team:
    - exercise: Handles fitness, workouts, physical activity, movement questions
    - nutrition: Handles diet, meal planning, healthy eating, food questions
    - sleep: Handles sleep quality, insomnia, rest, recovery questions
    - stress: Handles stress management, mindfulness, mental wellness, anxiety questions
    - hydration: Handles water intake, dehydration signs, hydration tips, fluid balance questions

    Based on the user's question, decide which ONE specialist should respond.
    Choose the most relevant specialist for the primary topic of the question.""",
            ),
            (
                "human",
                "User question: {question}\n\nWhich specialist should handle this?",
            ),
        ]
    )

    # Create structured output for routing
    new_routing_llm = supervisor_llm.with_structured_output(RouterOutput)

    def new_supervisor_node(state: SupervisorState):
        """The supervisor decides which agent to route to."""
        user_question = ""
        with propagate_attributes(session_id="supervisor_node"):
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    user_question = msg.content
                    break

            prompt_value = new_supervisor_prompt.invoke({"question": user_question})
            result = new_routing_llm.invoke(prompt_value)

        print(f"[Supervisor] Routing to: {result.next}")
        print(f"  Reason: {result.reasoning}")

        return {"next": result.next}

    # Create hydration agent node
    def new_create_agent_node(agent, name: str):
        """Create a node that runs a specialist agent and returns the final response."""

        def agent_node(state: SupervisorState):
            print(f"[{name.upper()} Agent] Processing request...")
            result = agent.invoke({"messages": state["messages"]})
            agent_response = result["messages"][-1]
            response_with_name = AIMessage(
                content=f"[{name.upper()} SPECIALIST]\n\n{agent_response.content}",
                name=name,
            )
            print(f"[{name.upper()} Agent] Response complete.")
            return {"messages": [response_with_name]}

        return agent_node

    hydration_node = new_create_agent_node(hydration_agent, "hydration")

    # Rebuild the graph
    def new_route_to_agent(state: SupervisorState) -> str:
        """Route to the next agent based on supervisor decision."""
        return state["next"]

    # Create nodes for other specialists
    new_exercise_node = new_create_agent_node(exercise_agent, "exercise")
    new_nutrition_node = new_create_agent_node(nutrition_agent, "nutrition")
    new_sleep_node = new_create_agent_node(sleep_agent, "sleep")
    new_stress_node = new_create_agent_node(stress_agent, "stress")

    # Build the graph
    new_supervisor_workflow = StateGraph(SupervisorState)
    new_supervisor_workflow.add_node("supervisor", new_supervisor_node)
    new_supervisor_workflow.add_node("exercise", new_exercise_node)
    new_supervisor_workflow.add_node("nutrition", new_nutrition_node)
    new_supervisor_workflow.add_node("sleep", new_sleep_node)
    new_supervisor_workflow.add_node("stress", new_stress_node)
    new_supervisor_workflow.add_node("hydration", hydration_node)

    # Add edges
    new_supervisor_workflow.add_edge(START, "supervisor")
    new_supervisor_workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "exercise": "exercise",
            "nutrition": "nutrition",
            "sleep": "sleep",
            "stress": "stress",
            "hydration": "hydration",
        },
    )

    # Each specialist goes directly to END
    new_supervisor_workflow.add_edge("exercise", END)
    new_supervisor_workflow.add_edge("nutrition", END)
    new_supervisor_workflow.add_edge("sleep", END)
    new_supervisor_workflow.add_edge("stress", END)
    new_supervisor_workflow.add_edge("hydration", END)

    # Compile
    new_supervisor_graph = new_supervisor_workflow.compile()
    return


@app.cell
def _(HumanMessage, langfuse, langfuse_handler, supervisor_graph):
    # Step 4: Test the new agent
    print("Testing Hydration Specialist Agent")
    print("=" * 50)

    test_response = supervisor_graph.invoke(
        {"messages": [HumanMessage(content="What are the signs of dehydration?")]},
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )

    print("\nTest Response:")
    print("=" * 50)
    print(test_response["messages"][-1].content)

    # Additional test
    test_response2 = supervisor_graph.invoke(
        {"messages": [HumanMessage(content="How much water should I drink daily?")]},
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )

    print("\nSecond Test Response:")
    print("=" * 50)
    print(test_response2["messages"][-1].content)

    # Flush Langfuse events
    if langfuse_handler:
        langfuse.flush()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    #  🤝 Breakout Room #2
    ## Handoffs & Context Engineering
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 5: Agent Handoffs Pattern

    The **Handoffs Pattern** allows agents to transfer control to each other based on the conversation context. Unlike the supervisor pattern, agents decide themselves when to hand off.

    ```
        User Question
             │
             ▼
        ┌─────────┐    "I need nutrition help"   ┌─────────┐
        │ Fitness │ ─────────────────────────────► Nutrition│
        │  Agent  │                               │  Agent  │
        └─────────┘ ◄───────────────────────────── └─────────┘
                     "Back to fitness questions"
    ```

    **Documentation:**
    - [LangGraph Agent Handoffs](https://langchain-ai.github.io/langgraph/how-tos/agent-handoffs/)
    """)
    return


@app.cell
def _(tool):
    # Create handoff tools that agents can use to transfer control
    # Each tool returns a special HANDOFF string that the graph will detect

    @tool
    def transfer_to_exercise(reason: str) -> str:
        """Transfer to Exercise Specialist for fitness, workouts, and physical activity questions.

        Args:
            reason: Why you're transferring to this specialist
        """
        return f"HANDOFF:exercise:{reason}"

    @tool
    def transfer_to_nutrition(reason: str) -> str:
        """Transfer to Nutrition Specialist for diet, meal planning, and food questions.

        Args:
            reason: Why you're transferring to this specialist
        """
        return f"HANDOFF:nutrition:{reason}"

    @tool
    def transfer_to_sleep(reason: str) -> str:
        """Transfer to Sleep Specialist for sleep quality, insomnia, and rest questions.

        Args:
            reason: Why you're transferring to this specialist
        """
        return f"HANDOFF:sleep:{reason}"

    @tool
    def transfer_to_stress(reason: str) -> str:
        """Transfer to Stress Management Specialist for stress, anxiety, and mindfulness questions.

        Args:
            reason: Why you're transferring to this specialist
        """
        return f"HANDOFF:stress:{reason}"

    print("Handoff tools created!")
    return (
        transfer_to_exercise,
        transfer_to_nutrition,
        transfer_to_sleep,
        transfer_to_stress,
    )


@app.cell
def _(
    create_agent,
    search_exercise_info,
    search_nutrition_info,
    search_sleep_info,
    search_stress_info,
    specialist_llm,
    transfer_to_exercise,
    transfer_to_nutrition,
    transfer_to_sleep,
    transfer_to_stress,
):
    # Create agents with handoff capabilities (using create_agent)

    exercise_handoff_agent = create_agent(
        model=specialist_llm,
        tools=[
            search_exercise_info,
            transfer_to_nutrition,
            transfer_to_sleep,
            transfer_to_stress,
        ],
        system_prompt="""You are an Exercise Specialist. Answer fitness and workout questions.
    If the user's question is better suited for another specialist, use the appropriate transfer tool.
    Always search the knowledge base before answering exercise questions.""",
    )

    nutrition_handoff_agent = create_agent(
        model=specialist_llm,
        tools=[
            search_nutrition_info,
            transfer_to_exercise,
            transfer_to_sleep,
            transfer_to_stress,
        ],
        system_prompt="""You are a Nutrition Specialist. Answer diet and meal planning questions.
    If the user's question is better suited for another specialist, use the appropriate transfer tool.
    Always search the knowledge base before answering nutrition questions.""",
    )

    sleep_handoff_agent = create_agent(
        model=specialist_llm,
        tools=[
            search_sleep_info,
            transfer_to_exercise,
            transfer_to_nutrition,
            transfer_to_stress,
        ],
        system_prompt="""You are a Sleep Specialist. Answer sleep and rest questions.
    If the user's question is better suited for another specialist, use the appropriate transfer tool.
    Always search the knowledge base before answering sleep questions.""",
    )

    stress_handoff_agent = create_agent(
        model=specialist_llm,
        tools=[
            search_stress_info,
            transfer_to_exercise,
            transfer_to_nutrition,
            transfer_to_sleep,
        ],
        system_prompt="""You are a Stress Management Specialist. Answer stress and mindfulness questions.
    If the user's question is better suited for another specialist, use the appropriate transfer tool.
    Always search the knowledge base before answering stress questions.""",
    )

    print("Handoff-enabled agents created (using create_agent)!")
    return (
        exercise_handoff_agent,
        nutrition_handoff_agent,
        sleep_handoff_agent,
        stress_handoff_agent,
    )


@app.cell
def _(
    AIMessage,
    Annotated,
    BaseMessage,
    TypedDict,
    add_messages,
    exercise_handoff_agent,
    nutrition_handoff_agent,
    sleep_handoff_agent,
    stress_handoff_agent,
):
    # Build the handoff graph with transfer limit to prevent infinite loops
    class HandoffState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]
        current_agent: str
        transfer_count: int

    MAX_TRANSFERS = 2  # Track transfers to prevent infinite loops

    def parse_handoff(
        content: str,
    ) -> tuple[bool, str, str]:  # Maximum number of handoffs allowed
        """Parse a handoff from agent response."""
        if "HANDOFF:" in content:
            parts = content.split("HANDOFF:")[1].split(":")
            return (True, parts[0], parts[1] if len(parts) > 1 else "")
        return (False, "", "")

    def create_handoff_node(agent, name: str):
        """Create a node that can handle handoffs."""

        def node(state: HandoffState):
            print(f"[{name.upper()} Agent] Processing...")
            result = agent.invoke({"messages": state["messages"]})
            last_message = result["messages"][-1]
            if state["transfer_count"] < MAX_TRANSFERS:
                for msg in result["messages"]:
                    if (
                        hasattr(msg, "content") and "HANDOFF:" in str(msg.content)
                    ):  # Check for handoff in tool messages (only if under transfer limit)
                        is_handoff, target, reason = parse_handoff(str(msg.content))
                        if is_handoff:
                            print(f"[{name.upper()}] Handing off to {target}: {reason}")
                            return {
                                "messages": [
                                    AIMessage(
                                        content=f"[{name}] Transferring to {target} specialist: {reason}"
                                    )
                                ],
                                "current_agent": target,
                                "transfer_count": state["transfer_count"] + 1,
                            }
            _response = AIMessage(
                content=f"[{name.upper()} SPECIALIST]\n\n{last_message.content}",
                name=name,
            )
            print(f"[{name.upper()} Agent] Response complete.")
            return {
                "messages": [_response],
                "current_agent": "done",
                "transfer_count": state["transfer_count"],
            }

        return node

    exercise_handoff_node = create_handoff_node(exercise_handoff_agent, "exercise")
    nutrition_handoff_node = create_handoff_node(nutrition_handoff_agent, "nutrition")
    sleep_handoff_node = create_handoff_node(sleep_handoff_agent, "sleep")
    stress_handoff_node = create_handoff_node(stress_handoff_agent, "stress")
    # Create nodes
    print(
        "Handoff nodes created!"
    )  # No handoff (or limit reached), return final response
    return (
        HandoffState,
        exercise_handoff_node,
        nutrition_handoff_node,
        sleep_handoff_node,
        stress_handoff_node,
    )


@app.cell
def _(
    END,
    HandoffState,
    START,
    StateGraph,
    exercise_handoff_node,
    nutrition_handoff_node,
    sleep_handoff_node,
    stress_handoff_node,
    supervisor_llm,
):
    # Build the handoff graph with initial routing (using glm-4.7)
    def entry_router(state: HandoffState):
        """Initial routing based on the user's question (using glm-4.7)."""
        user_question = state["messages"][-1].content
        router_prompt = f"Based on this question, which specialist should handle it?\nOptions: exercise, nutrition, sleep, stress\n\nQuestion: {user_question}\n\nRespond with just the specialist name (one word)."
        _response = supervisor_llm.invoke(router_prompt)
        agent = _response.content.strip().lower()
        if agent not in ["exercise", "nutrition", "sleep", "stress"]:
            agent = "stress"
        print(f"[Router glm-4.7] Initial routing to: {agent}")
        return {"current_agent": agent, "transfer_count": 0}

    def route_by_current_agent(state: HandoffState) -> str:
        """Route based on current_agent field."""
        return state["current_agent"]

    handoff_workflow = StateGraph(HandoffState)
    handoff_workflow.add_node("router", entry_router)  # Validate
    handoff_workflow.add_node("exercise", exercise_handoff_node)
    handoff_workflow.add_node(
        "nutrition", nutrition_handoff_node
    )  # Default to stress for general wellness
    handoff_workflow.add_node("sleep", sleep_handoff_node)
    handoff_workflow.add_node("stress", stress_handoff_node)
    handoff_workflow.add_edge(START, "router")
    handoff_workflow.add_conditional_edges(
        "router",
        route_by_current_agent,
        {
            "exercise": "exercise",
            "nutrition": "nutrition",
            "sleep": "sleep",
            "stress": "stress",
        },
    )
    for agent_name in ["exercise", "nutrition", "sleep", "stress"]:
        handoff_workflow.add_conditional_edges(
            agent_name,
            route_by_current_agent,
            {
                "exercise": "exercise",
                "nutrition": "nutrition",
                "sleep": "sleep",
                "stress": "stress",
                "done": END,
            },
        )
    handoff_graph = handoff_workflow.compile()
    # Build graph
    # Add nodes
    # Entry point
    # Router to agents
    # Agents can handoff to each other or end
    # Compile
    print("Handoff multi-agent system built!")
    return (handoff_graph,)


@app.cell
def _(Image, display, handoff_graph):
    # Visualize the handoff graph
    try:
        display(Image(handoff_graph.get_graph().draw_mermaid_png()))
    except Exception as e:
        print(f"Could not display graph: {e}")
        print("\nGraph structure:")
        print(handoff_graph.get_graph().draw_ascii())
    return


@app.cell
def _(HumanMessage, handoff_graph, langfuse, langfuse_handler):
    # Test the handoff system
    print("Testing Handoff System")
    print("=" * 50)
    _response = handoff_graph.invoke(
        {
            "messages": [
                HumanMessage(content="I'm stressed and can't sleep. What should I do?")
            ],
            "current_agent": "",
            "transfer_count": 0,
        },
        config={"callbacks": [langfuse_handler]} if langfuse_handler else {},
    )
    print("\n" + "=" * 50)
    print("FINAL RESPONSE:")
    print("=" * 50)
    print(_response["messages"][-1].content)

    # Flush Langfuse events
    if langfuse_handler:
        langfuse.flush()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 6: Building a Wellness Agent Team

    Now let's combine what we've learned to build a complete wellness team that can:
    1. Handle complex multi-domain questions
    2. Search both the knowledge base and the web
    3. Maintain conversation context
    4. Provide comprehensive wellness advice
    """)
    return


@app.cell
def _(supervisor_workflow):
    # Create a unified wellness team with memory
    from langgraph.checkpoint.memory import MemorySaver

    # Add memory to the supervisor graph
    memory = MemorySaver()

    supervisor_with_memory = supervisor_workflow.compile(checkpointer=memory)

    print("Supervisor with memory created!")
    return (supervisor_with_memory,)


@app.cell
def _(HumanMessage, langfuse, langfuse_handler, supervisor_with_memory):
    # Test multi-turn conversation
    thread_id = "wellness-session-1"
    config = {"configurable": {"thread_id": thread_id}}

    # Add Langfuse callback if available
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]

    print("Multi-turn Conversation Test")
    print("=" * 50)

    # First question
    response1 = supervisor_with_memory.invoke(
        {
            "messages": [
                HumanMessage(content="What's a good morning routine for energy?")
            ]
        },
        config=config,
    )
    print("\n[Turn 1 Response]:")
    print(response1["messages"][-1].content[:500])

    # Flush Langfuse events
    if langfuse_handler:
        langfuse.flush()
    return (config,)


@app.cell
def _(
    HumanMessage,
    config,
    langfuse,
    langfuse_handler,
    supervisor_with_memory,
):
    # Follow-up question (should remember context)

    # Add Langfuse callback if available
    config_with_callback = config.copy()
    if langfuse_handler:
        config_with_callback["callbacks"] = [langfuse_handler]

    response2 = supervisor_with_memory.invoke(
        {
            "messages": [
                HumanMessage(content="What should I eat as part of that routine?")
            ]
        },
        config=config_with_callback,
    )
    print("\n[Turn 2 Response]:")
    print(response2["messages"][-1].content[:500])

    # Flush Langfuse events
    if langfuse_handler:
        langfuse.flush()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 7: Context Engineering & Optimization

    As conversations grow, we need to manage context carefully. Key principles:

    1. **Context Window as Prime Real Estate**: Only include what's necessary
    2. **Summarization**: Compress long conversations
    3. **Selective Retrieval**: Don't retrieve everything, just what's relevant
    4. **Context Rot**: More tokens doesn't mean better performance
    """)
    return


@app.cell
def _(BaseMessage, SystemMessage, specialist_llm):
    # Implement a context summarization function (using glm-4.7)

    def summarize_conversation(
        messages: list[BaseMessage], max_messages: int = 6
    ) -> list[BaseMessage]:
        """Summarize older messages to manage context length."""
        if len(messages) <= max_messages:
            return messages

        # Keep the first message (original question) and last few messages
        old_messages = messages[1 : -max_messages + 1]
        recent_messages = messages[-max_messages + 1 :]

        # Summarize old messages
        summary_prompt = f"""Summarize this conversation history in 2-3 sentences, 
    capturing the key topics discussed and any important decisions made:

    {chr(10).join([f"{m.type}: {m.content[:200]}" for m in old_messages])}"""

        summary = specialist_llm.invoke(summary_prompt)

        # Return: first message + summary + recent messages
        return [
            messages[0],
            SystemMessage(
                content=f"[Previous conversation summary: {summary.content}]"
            ),
            *recent_messages,
        ]

    print("Context summarization function created!")
    return (summarize_conversation,)


@app.cell
def _(AIMessage, HumanMessage, summarize_conversation):
    # Demonstrate context optimization
    sample_messages = [
        HumanMessage(content="I want to get healthier"),
        AIMessage(content="Great! Let's start with your goals."),
        HumanMessage(content="I want to lose weight and sleep better"),
        AIMessage(content="Here are some exercise tips..."),
        HumanMessage(content="What about diet?"),
        AIMessage(content="For nutrition, consider..."),
        HumanMessage(content="And sleep?"),
        AIMessage(content="For better sleep..."),
        HumanMessage(content="How do I manage stress?"),
    ]

    print(f"Original messages: {len(sample_messages)}")

    optimized = summarize_conversation(sample_messages, max_messages=4)
    print(f"Optimized messages: {len(optimized)}")
    print("\nOptimized conversation:")
    for msg in optimized:
        print(f"  [{msg.type}]: {msg.content[:100]}...")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ❓ Question #3:

    Compare the **Supervisor pattern** and the **Handoffs pattern** we implemented. What are the key differences in how routing decisions are made? When would you choose one pattern over the other?

    ##### Answer:
    *The Supervisor pattern has a central agent decide routing once at the start, while the Handoffs pattern lets agents themselves transfer control dynamically during the conversation. Use Supervisor for single-domain requests and Handoffs when a question might need multiple specialists to respond.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #4:

    We discussed "Context Rot" - the idea that longer context doesn't always mean better performance. How does this principle apply to multi-agent systems? What strategies can you use to manage context effectively across multiple agents?

    ##### Answer:
    *In multi-agent systems, context rot happens when each agent gets the full conversation history passed between them, making responses worse as it grows. Fix this by summarizing conversations before sharing between agents and only passing relevant messages to each specialist.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #2: Implement Hierarchical Teams

    Build a **Hierarchical Agent System** where a top-level supervisor manages multiple team supervisors, each with their own specialist agents.

    ### Requirements:

    1. Create a **Wellness Director** (top-level supervisor using glm-4.7) that:
       - Receives user questions and determines which team should handle it
       - Routes to either the "Physical Wellness Team" or "Mental Wellness Team"
       - Aggregates final responses from teams

    2. Create two **Team Supervisors**:
       - **Physical Wellness Team Lead**: Manages Exercise Agent and Nutrition Agent
       - **Mental Wellness Team Lead**: Manages Sleep Agent and Stress Agent

    3. Implement the hierarchical routing:
       - User question → Wellness Director → Team Lead → Specialist Agent → Response

    4. Test with questions that require different teams:
       - "What exercises help with weight loss?" (Physical team)
       - "How can I improve my sleep when stressed?" (Mental team)

    ### Architecture:
    ```
                        ┌─────────────────────┐
                        │  Wellness Director  │
                        │     (glm-4.7)      │
                        └──────────┬──────────┘
                                   │
                  ┌────────────────┴────────────────┐
                  │                                 │
                  ▼                                 ▼
       ┌─────────────────────┐          ┌─────────────────────┐
       │  Physical Wellness  │          │  Mental Wellness    │
       │    Team Lead        │          │    Team Lead        │
       └──────────┬──────────┘          └──────────┬──────────┘
                  │                                 │
           ┌──────┴──────┐                   ┌──────┴──────┐
           │             │                   │             │
           ▼             ▼                   ▼             ▼
      ┌─────────┐  ┌──────────┐        ┌─────────┐  ┌─────────┐
      │Exercise │  │Nutrition │        │  Sleep  │  │ Stress  │
      │  Agent  │  │  Agent   │        │  Agent  │  │  Agent  │
      └─────────┘  └──────────┘        └─────────┘  └─────────┘
    ```

    **Documentation:**
    - [LangGraph Hierarchical Teams](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/)
    """)
    return


@app.cell
def _(
    BaseModel,
    ChatPromptTemplate,
    Literal,
    TypedDict,
    Annotated,
    add_messages,
    BaseMessage,
    AIMessage,
    HumanMessage,
    StateGraph,
    START,
    END,
    supervisor_llm,
    exercise_agent,
    nutrition_agent,
    sleep_agent,
    stress_agent,
    propagate_attributes,
):
    class TeamRouterOutput(BaseModel):
        next: str
        reasoning: str

    physical_team_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are the Physical Wellness Team Lead.
Your team has two specialists:
- exercise: Handles fitness, workouts, and physical activity
- nutrition: Handles diet, meal planning, and healthy eating

Route to the most appropriate specialist for the user's question.""",
            ),
            ("human", "Question: {question}"),
        ]
    )

    mental_team_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are the Mental Wellness Team Lead.
Your team has two specialists:
- sleep: Handles sleep quality, insomnia, and rest
- stress: Handles stress management, mindfulness, and mental wellness

Route to the most appropriate specialist for the user's question.""",
            ),
            ("human", "Question: {question}"),
        ]
    )

    class DirectorRouterOutput(BaseModel):
        team: Literal["physical", "mental"]
        reasoning: str

    director_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are the Wellness Director overseeing two teams:
- physical: Physical Wellness Team (exercise, nutrition)
- mental: Mental Wellness Team (sleep, stress)

Route to the appropriate team based on the user's question.""",
            ),
            ("human", "Question: {question}"),
        ]
    )

    class HierarchicalState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]
        current_team: str
        next_agent: str

    director_routing_llm = supervisor_llm.with_structured_output(DirectorRouterOutput)

    def wellness_director_node(state: HierarchicalState):
        user_question = ""
        with propagate_attributes(session_id="wellness_director"):
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    user_question = msg.content
                    break

            prompt_value = director_prompt.invoke({"question": user_question})
            result = director_routing_llm.invoke(prompt_value)

        print(f"[Wellness Director] Routing to {result.team} team")
        print(f"  Reason: {result.reasoning}")

        return {"current_team": result.team, "next_agent": ""}

    physical_routing_llm = supervisor_llm.with_structured_output(TeamRouterOutput)

    def physical_team_lead_node(state: HierarchicalState):
        user_question = ""
        with propagate_attributes(session_id="physical_team_lead"):
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    user_question = msg.content
                    break

            prompt_value = physical_team_prompt.invoke({"question": user_question})
            result = physical_routing_llm.invoke(prompt_value)

        print(f"[Physical Team Lead] Routing to {result.next} specialist")
        print(f"  Reason: {result.reasoning}")

        return {"next_agent": result.next}

    mental_routing_llm = supervisor_llm.with_structured_output(TeamRouterOutput)

    def mental_team_lead_node(state: HierarchicalState):
        user_question = ""
        with propagate_attributes(session_id="mental_team_lead"):
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    user_question = msg.content
                    break

            prompt_value = mental_team_prompt.invoke({"question": user_question})
            result = mental_routing_llm.invoke(prompt_value)

        print(f"[Mental Team Lead] Routing to {result.next} specialist")
        print(f"  Reason: {result.reasoning}")

        return {"next_agent": result.next}

    def create_hierarchical_agent_node(agent, name: str):
        def agent_node(state: HierarchicalState):
            print(f"[{name.upper()} SPECIALIST] Processing request...")
            result = agent.invoke({"messages": state["messages"]})
            agent_response = result["messages"][-1]

            response_with_name = AIMessage(
                content=f"[{name.upper()} SPECIALIST]\n\n{agent_response.content}",
                name=name,
            )

            print(f"[{name.upper()} SPECIALIST] Response complete.")
            return {"messages": [response_with_name]}

        return agent_node

    exercise_hierarchical_node = create_hierarchical_agent_node(
        exercise_agent, "exercise"
    )
    nutrition_hierarchical_node = create_hierarchical_agent_node(
        nutrition_agent, "nutrition"
    )
    sleep_hierarchical_node = create_hierarchical_agent_node(sleep_agent, "sleep")
    stress_hierarchical_node = create_hierarchical_agent_node(stress_agent, "stress")

    hierarchical_workflow = StateGraph(HierarchicalState)

    hierarchical_workflow.add_node("wellness_director", wellness_director_node)
    hierarchical_workflow.add_node("physical_team_lead", physical_team_lead_node)
    hierarchical_workflow.add_node("mental_team_lead", mental_team_lead_node)
    hierarchical_workflow.add_node("exercise", exercise_hierarchical_node)
    hierarchical_workflow.add_node("nutrition", nutrition_hierarchical_node)
    hierarchical_workflow.add_node("sleep", sleep_hierarchical_node)
    hierarchical_workflow.add_node("stress", stress_hierarchical_node)

    hierarchical_workflow.add_edge(START, "wellness_director")

    hierarchical_workflow.add_conditional_edges(
        "wellness_director",
        lambda state: f"{state['current_team']}_team_lead",
        {
            "physical_team_lead": "physical_team_lead",
            "mental_team_lead": "mental_team_lead",
        },
    )

    hierarchical_workflow.add_conditional_edges(
        "physical_team_lead",
        lambda state: state["next_agent"],
        {
            "exercise": "exercise",
            "nutrition": "nutrition",
        },
    )

    hierarchical_workflow.add_conditional_edges(
        "mental_team_lead",
        lambda state: state["next_agent"],
        {
            "sleep": "sleep",
            "stress": "stress",
        },
    )

    hierarchical_workflow.add_edge("exercise", END)
    hierarchical_workflow.add_edge("nutrition", END)
    hierarchical_workflow.add_edge("sleep", END)
    hierarchical_workflow.add_edge("stress", END)

    hierarchical_graph = hierarchical_workflow.compile()

    print("Hierarchical multi-agent system built!")
    print("Flow: User -> Wellness Director -> Team Lead -> Specialist -> END")

    print("\n" + "=" * 70)
    print("TEST 1: Physical Team Question")
    print("=" * 70)

    test_question_1 = "What exercises help with weight loss?"
    response_1 = hierarchical_graph.invoke(
        {
            "messages": [HumanMessage(content=test_question_1)],
            "current_team": "",
            "next_agent": "",
        }
    )
    print(f"\nQuestion: {test_question_1}")
    print("Response:")
    print(response_1["messages"][-1].content)

    print("\n" + "=" * 70)
    print("TEST 2: Mental Team Question")
    print("=" * 70)

    test_question_2 = "How can I improve my sleep when stressed?"
    response_2 = hierarchical_graph.invoke(
        {
            "messages": [HumanMessage(content=test_question_2)],
            "current_team": "",
            "next_agent": "",
        }
    )
    print(f"\nQuestion: {test_question_2}")
    print("Response:")
    print(response_2["messages"][-1].content)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    In this session, we:

    1. **Understood Multi-Agent Systems**: When to use them and key patterns
    2. **Built a Supervisor Pattern**: Central orchestrator routing to specialists
    3. **Implemented Agent Handoffs**: Agents transferring control to each other
    4. **Added Web Search**: SearxNG for current information alongside knowledge base
    5. **Applied Context Engineering**: Managing context for optimal performance

    ### Key Takeaways:

    - **Don't over-engineer**: Only add agents when you truly need specialization
    - **Context is key**: Manage your context window carefully
    - **Patterns matter**: Choose the right pattern for your use case

    **Further Reading:**
    - [Building Effective Agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents)
    - [Don't Build Multi-Agents (Cognition)](https://cognition.ai/blog/dont-build-multi-agents)
    - [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)
    """)
    return


if __name__ == "__main__":
    app.run()
