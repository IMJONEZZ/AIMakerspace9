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
    # Agentic RAG From Scratch: Building with LangGraph and Open-Source Models

    In this notebook, we'll look under the hood of `create_agent` and build an agentic RAG application **from scratch** using LangGraph's low-level primitives and locally-hosted open-source models.

    **Learning Objectives:**
    - Understand LangGraph's core constructs: StateGraph, nodes, edges, and conditional routing
    - Build a ReAct agent from scratch without high-level abstractions
    - Use Ollama to run open-source models locally (gpt-oss:20b + embeddinggemma)
    - Transition from `aimakerspace` utilities to the LangChain ecosystem

    ## Table of Contents:

    - **Breakout Room #1:** LangGraph Fundamentals & Building Agents from Scratch
      - Task 1: Dependencies & Ollama Setup
      - Task 2: LangGraph Core Concepts (StateGraph, Nodes, Edges)
      - Task 3: Building a ReAct Agent from Scratch
      - Task 4: Adding Tools to Your Agent
      - Question #1 & Question #2
      - Activity #1: Implement a Custom Routing Function

    - **Breakout Room #2:** Agentic RAG with Local Models
      - Task 5: Loading & Chunking with LangChain
      - Task 6: Setting up Qdrant with Local Embeddings
      - Task 7: Creating a RAG Tool
      - Task 8: Building Agentic RAG from Scratch
      - Question #3 & Question #4
      - Activity #2: Extend the Agent with Memory
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Breakout Room #1
    ## LangGraph Fundamentals & Building Agents from Scratch
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Dependencies & Ollama Setup

    Before we begin, make sure you have:

    1. **Ollama installed** - Download from [ollama.com](https://ollama.com/)
    2. **Ollama running** - Start with `ollama serve` in a terminal
    3. **Models pulled** - Run these commands:

    ```bash
    # Chat model for reasoning and generation (~12GB)
    ollama pull gpt-oss:20b

    # Embedding model for RAG (~622MB)
    ollama pull embeddinggemma
    ```

    > **Note**: If you don't have enough RAM/VRAM for `gpt-oss:20b` (requires 16GB+ VRAM or 24GB+ RAM), you can substitute with `llama3.2:3b` or another smaller model.

    **📚 Documentation:**
    - [Ollama Installation Guide](https://ollama.com/download)
    - [gpt-oss Model Card](https://ollama.com/library/gpt-oss)
    - [EmbeddingGemma Model Card](https://ollama.com/library/embeddinggemma)
    - [langchain-ollama Integration](https://python.langchain.com/docs/integrations/providers/ollama/)
    """)
    return


@app.cell
def _():
    # Core imports we'll use throughout the notebook
    import os
    import getpass
    import json
    from uuid import uuid4
    from typing import Annotated, TypedDict, Literal

    import nest_asyncio

    nest_asyncio.apply()  # Required for async operations in Jupyter
    return Annotated, Literal, TypedDict


@app.cell
def _():
    # Verify Ollama is running and models are available
    from langchain_ollama import ChatOllama, OllamaEmbeddings

    # Test connection to Ollama
    try:
        test_llm = ChatOllama(model="gpt-oss:20b", temperature=0)
        test_response = test_llm.invoke(
            "Say 'Ollama is working!' in exactly 3 words."
        )
        print(f"Chat Model Test: {test_response.content}")

        test_embeddings = OllamaEmbeddings(model="embeddinggemma")
        test_vector = test_embeddings.embed_query("test")
        print(f"Embedding Model Test: Vector dimension = {len(test_vector)}")
        print("\nOllama is ready!")
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        print("\nMake sure:")
        print("1. Ollama is installed: https://ollama.com/")
        print("2. Ollama is running: 'ollama serve'")
        print(
            "3. Models are pulled: 'ollama pull gpt-oss:20b' and 'ollama pull embeddinggemma'"
        )
    return ChatOllama, OllamaEmbeddings


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 2: LangGraph Core Concepts

    In Session 3, we used `create_agent` which abstracts away the complexity. Now let's understand what's happening under the hood!

    ### LangGraph models workflows as **graphs** with three key components:

    ### 1. State
    A shared data structure that represents the current snapshot of your application:

    ```python
    class AgentState(TypedDict):
        messages: Annotated[list, add_messages]  # Conversation history
    ```

    The `add_messages` **reducer** ensures new messages are appended (not replaced) when the state updates.

    ### 2. Nodes
    Python functions that encode the logic of your agent:
    - Receive the current state
    - Perform computation or side-effects
    - Return an updated state

    ### 3. Edges
    Functions that determine which node to execute next:
    - **Normal edges**: Always go to a specific node
    - **Conditional edges**: Choose the next node based on state

    **📚 Documentation:**
    - [LangGraph Low-Level Concepts](https://langchain-ai.github.io/langgraph/concepts/low_level/)
    - [LangGraph Quickstart](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
    - [StateGraph API Reference](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.StateGraph)
    """)
    return


@app.cell
def _(Annotated, TypedDict):
    # Let's build our first LangGraph workflow - a simple echo graph
    from langgraph.graph import StateGraph, START, END
    from langgraph.graph.message import add_messages
    from langchain_core.messages import HumanMessage, AIMessage


    # Step 1: Define the State
    class SimpleState(TypedDict):
        messages: Annotated[list, add_messages]


    # Step 2: Define Nodes (functions that process state)
    def echo_node(state: SimpleState):
        """A simple node that echoes the last message."""
        last_message = state["messages"][-1]
        echo_response = AIMessage(content=f"You said: {last_message.content}")
        return {"messages": [echo_response]}


    # Step 3: Build the Graph
    echo_graph = StateGraph(SimpleState)

    # Add nodes
    echo_graph.add_node("echo", echo_node)

    # Add edges (START -> echo -> END)
    echo_graph.add_edge(START, "echo")
    echo_graph.add_edge("echo", END)

    # Compile the graph
    echo_app = echo_graph.compile()

    print("Simple echo graph created!")
    return END, HumanMessage, START, StateGraph, add_messages, echo_app


@app.cell
def _(echo_app):
    # Visualize the graph structure
    try:
        from IPython.display import display, Image

        display(Image(echo_app.get_graph().draw_mermaid_png()))
    except Exception as e:
        print(f"Could not display graph image: {e}")
        print("\nGraph structure (ASCII):")
        print(echo_app.get_graph().draw_ascii())
    return Image, display


@app.cell
def _(HumanMessage, echo_app):
    def test_echo_graph():
        # Test the echo graph
        result = echo_app.invoke(
            {"messages": [HumanMessage(content="Hello, LangGraph!")]}
        )
        print("Conversation:")
        for _msg in result["messages"]:
            role = "Human" if isinstance(_msg, HumanMessage) else "AI"
        return print(f"  [{role}]: {_msg.content}")


    test_echo_graph()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 3: Building a ReAct Agent from Scratch

    Now let's build something more sophisticated: a **ReAct agent** that can:
    1. **Reason** about what to do
    2. **Act** by calling tools
    3. **Observe** results
    4. **Repeat** until done

    This is exactly what `create_agent` does under the hood. Let's build it ourselves!

    ### The Agent Loop Architecture

    ```
                        ┌──────────────┐
                        │    START     │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                 ┌─────►│    agent     │◄────────┐
                 │      │  (call LLM)  │         │
                 │      └──────┬───────┘         │
                 │             │                 │
                 │             ▼                 │
                 │      ┌──────────────┐         │
                 │      │ should_      │         │
                 │      │ continue?    │         │
                 │      └──────┬───────┘         │
                 │             │                 │
                 │    tool_calls?                │
                 │     │           │             │
                 │    YES         NO             │
                 │     │           │             │
                 │     ▼           ▼             │
                 │ ┌────────┐  ┌───────┐         │
                 │ │ tools  │  │  END  │         │
                 └─┤(execute│  └───────┘         │
                   │ tools) ├────────────────────┘
                   └────────┘
    ```

    **📚 Documentation:**
    - [How to create a ReAct agent from scratch](https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/)
    - [ReAct Agent Conceptual Guide](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/#react-agent)
    """)
    return


@app.cell
def _(Annotated, TypedDict, add_messages):
    from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
    from langchain_core.tools import tool
    from langgraph.prebuilt import ToolNode


    # Step 1: Define the Agent State
    class AgentState(TypedDict):
        """The state of our agent - just a list of messages."""

        messages: Annotated[list[BaseMessage], add_messages]


    print("AgentState defined with messages field")
    return AgentState, BaseMessage, SystemMessage, ToolNode, tool


@app.cell
def _(ChatOllama):
    # Step 2: Initialize our local LLM with Ollama
    llm = ChatOllama(
        model="gpt-oss:20b",
        temperature=0,  # Deterministic for reproducibility
        reasoning=True,  # Enable reasoning/thinking mode to capture model's thought process
    )

    print(f"LLM initialized: {llm.model} with reasoning enabled")
    return (llm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Adding Tools to Your Agent

    Tools are functions that the agent can call. We use the `@tool` decorator and **bind** them to the LLM.

    **📚 Documentation:**
    - [LangChain Tools Conceptual Guide](https://python.langchain.com/docs/concepts/tools/)
    - [@tool Decorator Reference](https://python.langchain.com/api_reference/core/tools/langchain_core.tools.convert.tool.html)
    - [ToolNode Prebuilt](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.tool_node.ToolNode)
    """)
    return


@app.cell
def _(llm, tool):
    # Step 3: Define Tools
    @tool
    def calculate(expression: str) -> str:
        """Evaluate a mathematical expression. Use this for any math calculations.

        Args:
            expression: A mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')
        """
        try:
            result = eval(
                expression, {"__builtins__": {}}, {}
            )  # Using eval with restricted globals for safety
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"Error evaluating expression: {e}"


    @tool
    def get_current_time() -> str:
        """Get the current date and time. Use this when the user asks about the current time or date."""
        from datetime import datetime

        return f"The current date and time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


    tools = [calculate, get_current_time]
    llm_with_tools = llm.bind_tools(tools)
    # Create our tool list
    print("Tools defined and bound to LLM:")
    for _t in tools:
        # Bind tools to the LLM - this tells the LLM about available tools
        print(f"  - {_t.name}: {_t.description[:50]}...")
    return calculate, get_current_time, llm_with_tools, tools


@app.cell
def _(AgentState, SystemMessage, llm_with_tools):
    # Step 4: Define the Agent Node (calls the LLM)
    SYSTEM_PROMPT = "You are a helpful assistant that can perform calculations and tell the time.\nAlways use the available tools when appropriate.\nBe concise in your responses."


    def agent_node(state: AgentState):
        """The agent node - calls the LLM with the current conversation."""
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        _response = llm_with_tools.invoke(messages)
        return {"messages": [_response]}  # Prepare messages with system prompt


    print(
        "Agent node defined"
    )  # Call the LLM  # Return the response to be added to state
    return (agent_node,)


@app.cell
def _(ToolNode, tools):
    # Step 5: Define the Tool Node (executes tools)
    # We can use LangGraph's prebuilt ToolNode for convenience
    tool_node = ToolNode(tools)

    print("Tool node created using ToolNode prebuilt")
    return (tool_node,)


@app.cell
def _(AgentState, Literal):
    # Step 6: Define the Conditional Edge (routing logic)
    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Determine whether to call tools or end the conversation."""
        last_message = state["messages"][-1]

        # If the LLM made tool calls, route to tools node
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        # Otherwise, end the conversation
        return "end"


    print("Conditional routing function defined")
    return (should_continue,)


@app.cell
def _(
    AgentState,
    END,
    START,
    StateGraph,
    agent_node,
    should_continue,
    tool_node,
):
    # Step 7: Build the Graph!
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Set the entry point
    workflow.add_edge(START, "agent")

    # Add conditional edge from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  # If should_continue returns "tools", go to tools node
            "end": END,  # If should_continue returns "end", finish
        },
    )

    # Add edge from tools back to agent (the loop!)
    workflow.add_edge("tools", "agent")

    # Compile the graph
    agent = workflow.compile()

    print("ReAct agent built from scratch!")
    return (agent,)


@app.cell
def _(Image, agent, display):
    # Visualize our agent
    try:
        display(Image(agent.get_graph().draw_mermaid_png()))
    except Exception as e:
        print(f"Could not display graph image: {e}")
        print("\nGraph structure (ASCII):")
        print(agent.get_graph().draw_ascii())
    return


@app.cell
def _(HumanMessage, agent):
    # Test our agent!
    print("Testing our from-scratch agent:")
    print("=" * 50)
    _response = agent.invoke(
        {"messages": [HumanMessage(content="What is 25 * 48?")]}
    )
    print("\nConversation:")
    for _msg in _response["messages"]:
        msg_type = type(_msg).__name__
        content = (
            _msg.content
            if _msg.content
            else f"[Tool calls: {_msg.tool_calls}]"
            if hasattr(_msg, "tool_calls") and _msg.tool_calls
            else "[No content]"
        )
        print(f"  [{msg_type}]: {content[:200]}")
    return


@app.cell
def _(HumanMessage, agent):
    # Test with multiple tools
    print("Testing with multiple tool calls:")
    print("=" * 50)
    _response = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What time is it, and what is 100 divided by the current hour?"
                )
            ]
        }
    )
    print("\nFinal response:")
    print(_response["messages"][-1].content)
    return


@app.cell
def _(HumanMessage, agent):
    # Stream the agent's execution to see it step by step
    print("Streaming agent execution:")
    print("=" * 50)
    for chunk in agent.stream(
        {"messages": [HumanMessage(content="Calculate 15% of 200")]},
        stream_mode="updates",
    ):
        for node_name, values in chunk.items():
            print(f"\n[Node: {node_name}]")
            if "messages" in values:
                for _msg in values["messages"]:
                    if hasattr(_msg, "content") and _msg.content:
                        print(f"  Content: {_msg.content[:200]}")
                    if hasattr(_msg, "tool_calls") and _msg.tool_calls:
                        print(
                            f"  Tool calls: {[tc['name'] for tc in _msg.tool_calls]}"
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ❓ Question #1:

    In our from-scratch agent, we defined a `should_continue` function that returns either `"tools"` or `"end"`. How does this compare to how `create_agent` handles the same decision? What additional logic might `create_agent` include that we didn't implement?

    ##### Answer:
    *Both check for tool calls to decide whether to execute tools or end, but `create_agent` wraps this in a more robust implementation that handles edge cases we naive builders didn't bother thinking about.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #2:

    We used `ToolNode` from `langgraph.prebuilt` to execute tools. Looking at the tool execution flow, what would happen if we wanted to add logging, error handling, or rate limiting to tool execution? How would building our own tool node give us more control?

    ##### Answer:
    Building your own tool node lets you wrap tool calls with logging, error handling, and rate limiting middleware - capabilities ToolNode keeps locked away.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #1: Implement a Custom Routing Function

    Extend the agent by implementing a **custom routing function** that adds more sophisticated logic.

    Ideas:
    - Add a maximum iteration limit to prevent infinite loops
    - Route to different nodes based on the type of tool being called
    - Add a "thinking" step before tool execution

    Requirements:
    1. Modify the `should_continue` function or create a new one
    2. Add any new nodes if needed
    3. Rebuild and test the agent

    **📚 Documentation:**
    - [Conditional Edges](https://langchain-ai.github.io/langgraph/concepts/low_level/#conditional-edges)
    - [How to create branches for parallel node execution](https://langchain-ai.github.io/langgraph/how-tos/branching/)
    """)
    return


@app.cell
def _(
    Annotated,
    BaseMessage,
    END,
    Literal,
    START,
    StateGraph,
    SystemMessage,
    ToolNode,
    TypedDict,
    add_messages,
    calculate,
    get_current_time,
    llm_with_tools,
):
    ### YOUR CODE HERE ###

    MAX_ITERATIONS = 25

    CUSTOM_ROUTING_SYSTEM_PROMPT = "You are a helpful assistant that can perform calculations and tell the time.\nAlways use the available tools when appropriate.\nBe concise in your responses."


    class AgentStateWithCounter(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]
        iteration_count: int


    def custom_should_continue(
        state: AgentStateWithCounter,
    ) -> Literal["thinking", "end"]:
        """Custom routing with iteration limit."""
        last_message = state["messages"][-1]

        if state["iteration_count"] >= MAX_ITERATIONS:
            print(
                f"\n[Iteration limit reached ({MAX_ITERATIONS}). Ending conversation to prevent infinite loop.]"
            )
            return "end"

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "thinking"

        return "end"


    def route_by_tool_type(
        state: AgentStateWithCounter,
    ) -> Literal["calculation_tools", "info_tools"]:
        """Route to different tool nodes based on tool type."""
        last_message = state["messages"][-1]

        if not (hasattr(last_message, "tool_calls") and last_message.tool_calls):
            return "info_tools"

        tool_names = [tc["name"] for tc in last_message.tool_calls]

        if any("calculate" in name.lower() for name in tool_names):
            return "calculation_tools"
        else:
            return "info_tools"


    def agent_node_with_counter(state: AgentStateWithCounter):
        """Agent node that updates iteration counter."""
        messages = [SystemMessage(content=CUSTOM_ROUTING_SYSTEM_PROMPT)] + state[
            "messages"
        ]
        response = llm_with_tools.invoke(messages)

        new_iteration_count = state.get("iteration_count", 0) + 1

        return {"messages": [response], "iteration_count": new_iteration_count}


    def thinking_node(state: AgentStateWithCounter):
        """Thinking step before tool execution - extracts and displays model's actual reasoning."""
        last_message = state["messages"][-1]

        if not (hasattr(last_message, "tool_calls") and last_message.tool_calls):
            return {"messages": []}

        reasoning_content = None

        if (
            hasattr(last_message, "additional_kwargs")
            and last_message.additional_kwargs
        ):
            reasoning_content = last_message.additional_kwargs.get(
                "reasoning_content"
            )

        if not reasoning_content:
            return {"messages": []}

        from langchain_core.messages import AIMessage

        thinking_message = AIMessage(content=f"[Thinking] {reasoning_content}")

        return {"messages": [thinking_message]}


    calc_tools = [calculate]
    info_tools = [get_current_time]

    calc_tool_node = ToolNode(calc_tools)
    info_tool_node = ToolNode(info_tools)

    counter_workflow = StateGraph(AgentStateWithCounter)

    counter_workflow.add_node("agent", agent_node_with_counter)
    counter_workflow.add_node("thinking", thinking_node)
    counter_workflow.add_node("calculation_tools", calc_tool_node)
    counter_workflow.add_node("info_tools", info_tool_node)

    counter_workflow.add_edge(START, "agent")

    counter_workflow.add_conditional_edges(
        "agent", custom_should_continue, {"thinking": "thinking", "end": END}
    )

    counter_workflow.add_conditional_edges(
        "thinking",
        route_by_tool_type,
        {"calculation_tools": "calculation_tools", "info_tools": "info_tools"},
    )

    counter_workflow.add_edge("calculation_tools", "agent")
    counter_workflow.add_edge("info_tools", "agent")

    custom_agent = counter_workflow.compile()

    print(f"Custom agent built with:")
    print(f"  - Iteration limit: {MAX_ITERATIONS}")
    print(f"  - Thinking step before tool execution")
    print(f"  - Tool-type aware routing (calculation vs info tools)")
    return (custom_agent,)


@app.cell
def _(HumanMessage, custom_agent):
    print("Testing Custom Agent with Advanced Routing:")
    print("=" * 70)

    queries = [
        "What is 25 * 48 + 130 / 10?",
        "What time is it right now?",
        "Calculate 15% of 200 and tell me the current hour",
    ]

    for idx, query in enumerate(queries, 1):
        print(f"\n{'-' * 70}")
        print(f"Query {idx}: {query}")
        print("-" * 70)

        result = custom_agent.invoke(
            {
                "messages": [HumanMessage(content=query)],
                "iteration_count": 0,
            }
        )

        print(f"Final iteration count: {result['iteration_count']}")
        print("\nExecution flow:")
        for msg in result["messages"]:
            msg_content = (
                msg.content
                if msg.content
                else f"[Tool calls: {msg.tool_calls}]"
                if hasattr(msg, "tool_calls") and msg.tool_calls
                else "[No content]"
            )
            print(f"  [{type(msg).__name__}]: {msg_content[:200]}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Breakout Room #2
    ## Agentic RAG with Local Models
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now let's build a full **Agentic RAG** system from scratch using our local models!

    We'll transition from the `aimakerspace` utilities to the **LangChain ecosystem**:

    | Task | aimakerspace | LangChain |
    |------|--------------|----------|
    | Load Documents | `TextFileLoader` | `TextLoader` |
    | Split Text | `CharacterTextSplitter` | `RecursiveCharacterTextSplitter` |
    | Embeddings | Custom | `OllamaEmbeddings` |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 5: Loading & Chunking with LangChain

    Let's use LangChain's document loaders and text splitters.

    **📚 Documentation:**
    - [Document Loaders Conceptual Guide](https://python.langchain.com/docs/concepts/document_loaders/)
    - [TextLoader Reference](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.text.TextLoader.html)
    - [RecursiveCharacterTextSplitter](https://python.langchain.com/docs/how_to/recursive_text_splitter/)
    - [Text Splitters Conceptual Guide](https://python.langchain.com/docs/concepts/text_splitters/)
    """)
    return


@app.cell
def _():
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    # Load the document using LangChain's TextLoader
    loader = TextLoader("data/HealthWellnessGuide.txt")
    documents = loader.load()

    print(f"Loaded {len(documents)} document(s)")
    print(f"Total characters: {sum(len(doc.page_content) for doc in documents):,}")
    print(f"\nDocument metadata: {documents[0].metadata}")
    return RecursiveCharacterTextSplitter, documents


@app.cell
def _(RecursiveCharacterTextSplitter, documents):
    # Split documents using RecursiveCharacterTextSplitter
    # This is more sophisticated than simple character splitting!

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        # Default separators: ["\n\n", "\n", " ", ""]
        # Tries to keep paragraphs, then sentences, then words together
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Split into {len(chunks)} chunks")
    print(f"\nSample chunk (first 300 chars):")
    print("-" * 50)
    print(chunks[0].page_content[:300] + "...")
    return (chunks,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 6: Setting up Qdrant with Local Embeddings

    Now we'll use **OllamaEmbeddings** with the `embeddinggemma` model - completely local!

    **📚 Documentation:**
    - [OllamaEmbeddings Reference](https://python.langchain.com/api_reference/ollama/embeddings/langchain_ollama.embeddings.OllamaEmbeddings.html)
    - [Qdrant Vector Store Integration](https://python.langchain.com/docs/integrations/vectorstores/qdrant/)
    - [Embedding Models Conceptual Guide](https://python.langchain.com/docs/concepts/embedding_models/)
    - [EmbeddingGemma Overview (Google)](https://ai.google.dev/gemma/docs/embeddinggemma)
    """)
    return


@app.cell
def _(OllamaEmbeddings):
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams

    embedding_model = OllamaEmbeddings(model="embeddinggemma")
    sample_embedding = embedding_model.embed_query("test")
    # Initialize local embedding model
    embedding_dim = len(sample_embedding)
    print(f"Embedding dimension: {embedding_dim}")
    # Get embedding dimension
    print(f"Using local model: embeddinggemma")
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
    collection_name = "wellness_knowledge_base_local"

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
    # Create vector store and add documents
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embedding_model,
    )

    # Add documents to the vector store
    print(
        "Adding documents to vector store (this may take a moment with local embeddings)..."
    )
    vector_store.add_documents(chunks)
    print(f"Added {len(chunks)} documents to vector store")
    return (vector_store,)


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
    ## Task 7: Creating a RAG Tool

    Now let's wrap our retriever as a tool that the agent can use.
    """)
    return


@app.cell
def _(retriever, tool):
    @tool
    def search_wellness_knowledge(query: str) -> str:
        """Search the wellness knowledge base for information about health, fitness, nutrition, sleep, and mental wellness.

        Use this tool when the user asks questions about:
        - Physical health and fitness
        - Nutrition and diet
        - Sleep and rest
        - Mental health and stress management
        - General wellness tips

        Args:
            query: The search query to find relevant wellness information
        """
        results = retriever.invoke(query)

        if not results:
            return "No relevant information found in the wellness knowledge base."

        # Format the results
        formatted_results = []
        for i, doc in enumerate(results, 1):
            formatted_results.append(f"[Source {i}]:\n{doc.page_content}")

        return "\n\n".join(formatted_results)


    print(f"RAG tool created: {search_wellness_knowledge.name}")
    return (search_wellness_knowledge,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 8: Building Agentic RAG from Scratch

    Now let's put it all together - a complete agentic RAG system built from scratch!
    """)
    return


@app.cell
def _(calculate, get_current_time, llm, search_wellness_knowledge):
    # Define all tools for our RAG agent
    rag_tools = [search_wellness_knowledge, calculate, get_current_time]
    rag_llm_with_tools = llm.bind_tools(rag_tools)
    # Bind tools to the LLM
    print("Tools for RAG agent:")
    for _t in rag_tools:
        print(f"  - {_t.name}")
    return rag_llm_with_tools, rag_tools


@app.cell
def _(AgentState, SystemMessage, ToolNode, rag_llm_with_tools, rag_tools):
    # Define the RAG agent components
    RAG_SYSTEM_PROMPT = "You are a helpful wellness assistant with access to a comprehensive health and wellness knowledge base.\n\nYour role is to:\n1. Answer questions about health, fitness, nutrition, sleep, and mental wellness\n2. ALWAYS search the knowledge base when the user asks wellness-related questions\n3. Provide accurate, helpful information based on the retrieved context\n4. Be supportive and encouraging in your responses\n5. If you cannot find relevant information, say so honestly\n\nRemember: Always cite information from the knowledge base when applicable."


    def rag_agent_node(state: AgentState):
        """The RAG agent node - calls the LLM with wellness system prompt."""
        messages = [SystemMessage(content=RAG_SYSTEM_PROMPT)] + state["messages"]
        _response = rag_llm_with_tools.invoke(messages)
        return {"messages": [_response]}


    rag_tool_node = ToolNode(rag_tools)
    # Create tool node for RAG tools
    print("RAG agent node defined")
    return rag_agent_node, rag_tool_node


@app.cell
def _(
    AgentState,
    END,
    START,
    StateGraph,
    rag_agent_node,
    rag_tool_node,
    should_continue,
):
    # Build the RAG agent graph
    rag_workflow = StateGraph(AgentState)

    # Add nodes
    rag_workflow.add_node("agent", rag_agent_node)
    rag_workflow.add_node("tools", rag_tool_node)

    # Set entry point
    rag_workflow.add_edge(START, "agent")

    # Add conditional edge
    rag_workflow.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", "end": END}
    )

    # Add edge from tools back to agent
    rag_workflow.add_edge("tools", "agent")

    # Compile
    rag_agent = rag_workflow.compile()

    print("Agentic RAG built from scratch!")
    return rag_agent, rag_workflow


@app.cell
def _(Image, display, rag_agent):
    # Visualize the RAG agent
    try:
        display(Image(rag_agent.get_graph().draw_mermaid_png()))
    except Exception as e:
        print(f"Could not display graph image: {e}")
        print("\nGraph structure:")
        print(rag_agent.get_graph().draw_ascii())
    return


@app.cell
def _(HumanMessage, rag_agent):
    # Test the RAG agent
    print("Testing Agentic RAG (with local models):")
    print("=" * 50)
    _response = rag_agent.invoke(
        {
            "messages": [
                HumanMessage(content="What are some tips for better sleep?")
            ]
        }
    )
    print("\nFinal Response:")
    print("=" * 50)
    print(_response["messages"][-1].content)
    return


@app.cell
def _(HumanMessage, rag_agent):
    # Test with a complex query requiring both RAG and calculation
    print("Testing with complex query:")
    print("=" * 50)
    _response = rag_agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="I'm stressed and sleeping poorly. What should I do? Also, if I sleep 6 hours a night for a week, how many total hours is that?"
                )
            ]
        }
    )
    print("\nFinal Response:")
    print("=" * 50)
    print(_response["messages"][-1].content)
    return


@app.cell
def _(HumanMessage, rag_agent):
    # Test that the agent knows when NOT to use RAG
    print("Testing agent decision-making (should NOT use RAG):")
    print("=" * 50)
    _response = rag_agent.invoke(
        {"messages": [HumanMessage(content="What is 125 * 8?")]}
    )
    print("\nFinal Response:")
    print(_response["messages"][-1].content)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ❓ Question #3:

    Compare the experience of building an agent from scratch with LangGraph versus using `create_agent` from Session 3. What are the trade-offs between control and convenience? When would you choose one approach over the other?

    ##### Answer:
    *Building from scratch gives you complete control and visibility but requires writing every component yourself, while `create_agent` gets you running quickly with the convenient trade-off that debugging becomes an exercise in guessing what's happening behind the abstraction.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #4:

    We used local models (gpt-oss:20b and embeddinggemma) instead of cloud APIs. What are the advantages and disadvantages of this approach?

    ##### Answer:
    *Local models keep your data private and avoid API costs, though you'll pay for it with slower inference and the hardware requirements that make your laptop sound like a jet engine.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #2: Extend the Agent with Memory

    LangGraph supports **checkpointing** which enables conversation memory across invocations.

    Your task: Add memory to the RAG agent so it can:
    1. Remember previous questions in the conversation
    2. Reference past context when answering new questions
    3. Build on previous answers

    Hint: Use `MemorySaver` from `langgraph.checkpoint.memory` and pass a `thread_id` in the config.

    **📚 Documentation:**
    - [LangGraph Persistence & Memory](https://langchain-ai.github.io/langgraph/concepts/persistence/)
    - [How to add memory to your graph](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
    - [MemorySaver Reference](https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.memory.MemorySaver)
    """)
    return


@app.cell
def _(HumanMessage, rag_workflow):
    ### YOUR CODE HERE ###

    from langgraph.checkpoint.memory import MemorySaver

    # Create a memory saver
    memory = MemorySaver()

    # Recompile the agent with checkpointing
    rag_agent_with_memory = rag_workflow.compile(checkpointer=memory)

    # Test with a conversation that requires memory
    # Use config={"configurable": {"thread_id": "conversation-1"}}

    print("RAG agent with memory compiled successfully!")
    print("Memory enables conversation context across multiple invocations.")

    # First interaction
    config = {"configurable": {"thread_id": "conversation-1"}}

    print("\n" + "=" * 70)
    print("Interaction 1: Asking about wellness tips")
    print("=" * 70)

    response1 = rag_agent_with_memory.invoke(
        {
            "messages": [
                HumanMessage(content="What are some tips for better sleep?")
            ]
        },
        config,
    )

    print("Response 1:", response1["messages"][-1].content)

    # Second interaction - builds on the first
    print("\n" + "=" * 70)
    print("Interaction 2: Following up with a related question")
    print("=" * 70)

    response2 = rag_agent_with_memory.invoke(
        {"messages": [HumanMessage(content="What about morning routines?")]},
        config,
    )

    print("Response 2:", response2["messages"][-1].content)

    # Third interaction - tests memory retention
    print("\n" + "=" * 70)
    print("Interaction 3: Referencing both previous topics")
    print("=" * 70)

    response3 = rag_agent_with_memory.invoke(
        {
            "messages": [
                HumanMessage(
                    content="How can I combine the sleep tips with morning routines?"
                )
            ]
        },
        config,
    )

    print("Response 3:", response3["messages"][-1].content)

    print("\n" + "=" * 70)
    print("Memory Test: Using a different thread_id (should NOT have context)")
    print("=" * 70)

    config2 = {"configurable": {"thread_id": "conversation-2"}}
    response4 = rag_agent_with_memory.invoke(
        {"messages": [HumanMessage(content="What did we discuss about sleep?")]},
        config2,
    )

    print("Response with new thread:", response4["messages"][-1].content)
    return (rag_agent_with_memory,)


@app.cell
def _(HumanMessage, rag_agent_with_memory):
    # Test your memory-enabled agent with a multi-turn conversation

    print("\n" + "=" * 70)
    print("Extended Memory Test: Multi-turn Wellness Consultation")
    print("=" * 70)

    config3 = {"configurable": {"thread_id": "wellness-consultation"}}

    # Turn 1: Initial question
    print("\n--- Turn 1 ---")
    response = rag_agent_with_memory.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What are 3 things I can do to improve my sleep quality?"
                )
            ]
        },
        config3,
    )
    print("Question: What are 3 things I can do to improve my sleep quality?")
    print("Answer:", response["messages"][-1].content)

    # Turn 2: Follow-up question (tests memory of turn 1)
    print("\n--- Turn 2 ---")
    response = rag_agent_with_memory.invoke(
        {
            "messages": [
                HumanMessage(
                    content="How about nutrition? What foods help with sleep?"
                )
            ]
        },
        config3,
    )
    print("Question: How about nutrition? What foods help with sleep?")
    print("Answer:", response["messages"][-1].content)

    # Turn 3: Synthesis question (tests memory of both previous turns)
    print("\n--- Turn 3 ---")
    response = rag_agent_with_memory.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Can you create a simple evening routine combining the sleep tips and nutrition advice?"
                )
            ]
        },
        config3,
    )
    print(
        "Question: Can you create a simple evening routine combining the sleep tips and nutrition advice?"
    )
    print("Answer:", response["messages"][-1].content)

    # Turn 4: Clarification (tests context retention)
    print("\n--- Turn 4 ---")
    response = rag_agent_with_memory.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What was the first tip you mentioned about sleep?"
                )
            ]
        },
        config3,
    )
    print("Question: What was the first tip you mentioned about sleep?")
    print("Answer:", response["messages"][-1].content)

    print("\n" + "=" * 70)
    print("Memory Test Complete!")
    print("=" * 70)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    In this session, we:

    1. **Built agents from scratch** using LangGraph's low-level primitives (StateGraph, nodes, edges)
    2. **Used local open-source models** with Ollama (gpt-oss:20b + embeddinggemma)
    3. **Transitioned to LangChain** for document loading and text splitting
    4. **Created an Agentic RAG system** that intelligently decides when to retrieve information

    ### Key Takeaways:

    - **StateGraph** gives you full control over agent architecture
    - **Conditional edges** enable dynamic routing based on LLM decisions
    - **Local models** provide privacy and cost savings, with trade-offs in performance
    - **LangSmith** provides crucial visibility regardless of where your models run

    ### What's Next?

    Now that you understand the fundamentals, you can:
    - Add more sophisticated routing logic
    - Implement human-in-the-loop patterns
    - Build multi-agent systems
    - Deploy to production with LangGraph Platform

    **📚 Further Reading:**
    - [LangGraph How-To Guides](https://langchain-ai.github.io/langgraph/how-tos/)
    - [Human-in-the-Loop Patterns](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/)
    - [Multi-Agent Architectures](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
    - [LangGraph Platform](https://langchain-ai.github.io/langgraph/concepts/langgraph_platform/)
    """)
    return


if __name__ == "__main__":
    app.run()
