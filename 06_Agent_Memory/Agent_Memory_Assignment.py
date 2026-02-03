import marimo

__generated_with = "0.19.7"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Agent Memory: Building Memory-Enabled Agents with LangGraph

    In this notebook, we'll explore **agent memory systems** - the ability for AI agents to remember information across interactions. We'll implement all five memory types from the **CoALA (Cognitive Architectures for Language Agents)** framework while building on our Personal Wellness Assistant use case.

    **Learning Objectives:**
    - Understand the 5 memory types from the CoALA framework
    - Implement short-term memory with checkpointers and thread_id
    - Build long-term memory with InMemoryStore and namespaces
    - Use semantic memory for meaning-based retrieval
    - Apply episodic memory for few-shot learning from past experiences
    - Create procedural memory for self-improving agents
    - Combine all memory types into a unified wellness agent

    ## Table of Contents:

    - **Breakout Room #1:** Memory Foundations
      - Task 1: Dependencies
      - Task 2: Understanding Agent Memory (CoALA Framework)
      - Task 3: Short-Term Memory (MemorySaver, thread_id)
      - Task 4: Long-Term Memory (InMemoryStore, namespaces)
      - Task 5: Message Trimming & Context Management
      - Question #1 & Question #2
      - 🏗️ Activity #1: Store & Retrieve User Wellness Profile

    - **Breakout Room #2:** Advanced Memory & Integration
      - Task 6: Semantic Memory (Embeddings + Search)
      - Task 7: Building Semantic Wellness Knowledge Base
      - Task 8: Episodic Memory (Few-Shot Learning)
      - Task 9: Procedural Memory (Self-Improving Agent)
      - Task 10: Unified Wellness Memory Agent
      - Question #3 & Question #4
      - 🏗️ Activity #2: Wellness Memory Dashboard
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🤝 Breakout Room #1
    ## Memory Foundations
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Dependencies

    Before we begin, make sure you have:

    1. **API Keys** for:
       - OpenAI (for GPT-4o-mini and embeddings)
       - Langfuse (optional, for tracing)

    2. **Dependencies installed** via `uv sync`
    """)
    return


@app.cell
def _():
    # Core imports
    import os
    import getpass
    from uuid import uuid4
    from typing import Annotated, TypedDict

    import nest_asyncio

    nest_asyncio.apply()  # Required for async operations in Jupyter
    return Annotated, TypedDict, getpass, os


@app.cell
def _(getpass, os):
    # Set API Keys
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key: ")
    return


@app.cell
def _(os):
    # Langfuse for tracing (local docker instance)
    os.environ["LANGFUSE_PUBLIC_KEY"] = (
        "pk-lf-b76a11bf-0d3e-4b42-981d-aef04ac7ac80"
    )
    os.environ["LANGFUSE_SECRET_KEY"] = (
        "sk-lf-31d5642a-6af9-436a-a2aa-a3ab1b310995"
    )
    os.environ["LANGFUSE_HOST"] = "http://localhost:3000"

    if not os.environ["LANGFUSE_SECRET_KEY"]:
        print("Langfuse tracing disabled")
    else:
        print("Langfuse tracing enabled at http://localhost:3000")
    return


@app.cell
def _():
    # Initialize LLM
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model="openai/gpt-oss-120b",
        base_url="http://192.168.1.79:8080/v1/",
        temperature=0,
    )
    _response = llm.invoke("Say 'Memory systems ready!' in exactly those words.")
    # Test the connection
    print(_response.content)
    return (llm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 2: Understanding Agent Memory (CoALA Framework)

    The **CoALA (Cognitive Architectures for Language Agents)** framework identifies 5 types of memory that agents can use:

    | Memory Type | Human Analogy | AI Implementation | Wellness Example |
    |-------------|---------------|-------------------|------------------|
    | **Short-term** | What someone just said | Conversation history within a thread | Current consultation conversation |
    | **Long-term** | Remembering a friend's birthday | User preferences stored across sessions | User's goals, allergies, conditions |
    | **Semantic** | Knowing Paris is in France | Facts retrieved by meaning | Wellness knowledge retrieval |
    | **Episodic** | Remembering your first day at work | Learning from past experiences | Past successful advice patterns |
    | **Procedural** | Knowing how to ride a bike | Self-improving instructions | Learned communication preferences |

    ### Memory Architecture Overview

    ```
    ┌─────────────────────────────────────────────────────────────────┐
    │                    LangGraph Wellness Agent                     │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
    │  │  Short-term  │  │  Long-term   │  │   Semantic   │           │
    │  │    Memory    │  │    Memory    │  │    Memory    │           │
    │  │              │  │              │  │              │           │
    │  │ Checkpointer │  │    Store     │  │Store+Embed   │           │
    │  │ + thread_id  │  │ + namespace  │  │  + search()  │           │
    │  └──────────────┘  └──────────────┘  └──────────────┘           │
    │                                                                 │
    │  ┌──────────────┐  ┌──────────────┐                             │
    │  │   Episodic   │  │  Procedural  │                             │
    │  │    Memory    │  │    Memory    │                             │
    │  │              │  │              │                             │
    │  │  Few-shot    │  │Self-modifying│                             │
    │  │  examples    │  │   prompts    │                             │
    │  └──────────────┘  └──────────────┘                             │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
    ```

    ### Key LangGraph Components

    | Component | Memory Type | Scope |
    |-----------|-------------|-------|
    | `MemorySaver` (Checkpointer) | Short-term | Within a single thread |
    | `InMemoryStore` | Long-term, Semantic, Episodic, Procedural | Across all threads |
    | `thread_id` | Short-term | Identifies unique conversations |
    | Namespaces | All store-based | Organizes memories by user/purpose |

    **Documentation:**
    - [CoALA Paper](https://arxiv.org/abs/2309.02427)
    - [LangGraph Memory Concepts](https://langchain-ai.github.io/langgraph/concepts/memory/)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 3: Short-Term Memory (MemorySaver, thread_id)

    **Short-term memory** maintains context within a single conversation thread. Think of it like your working memory during a phone call - you remember what was said earlier, but once the call ends, those details fade.

    In LangGraph, short-term memory is implemented through:
    - **Checkpointer**: Saves the graph state at each step
    - **thread_id**: Uniquely identifies each conversation

    ### How It Works

    ```
    Thread 1: "Hi, I'm Chris_B"          Thread 2: "What's my name?"
         │                                   │
         ▼                                   ▼
    ┌──────────────┐                   ┌──────────────┐
    │ Checkpointer │                   │ Checkpointer │
    │  thread_1    │                   │  thread_2    │
    │              │                   │              │
    │ ["Hi Chris_B"] │                   │ [empty]      │
    └──────────────┘                   └──────────────┘
         │                                   │
         ▼                                   ▼
    "Hi Chris_B!"                        "I don't know your name"
    ```
    """)
    return


@app.cell
def _(Annotated, TypedDict, llm):
    from langgraph.graph import StateGraph, START, END
    from langgraph.graph.message import add_messages
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


    # Define the state schema for our graph
    # The `add_messages` annotation tells LangGraph how to update the messages list
    class State(TypedDict):
        messages: Annotated[list, add_messages]


    def wellness_chatbot(state: State):
        # Define our wellness chatbot node
        """Process the conversation and generate a wellness-focused response."""
        system_prompt = SystemMessage(
            content="You are a friendly Personal Wellness Assistant. \nHelp users with exercise, nutrition, sleep, and stress management questions.\nBe supportive and remember details the user shares about themselves."
        )
        messages = [system_prompt] + state["messages"]
        _response = llm.invoke(messages)
        return {"messages": [_response]}


    def _():
        builder = StateGraph(State)
        builder.add_node("chatbot", wellness_chatbot)
        builder.add_edge(START, "chatbot")
        builder.add_edge("chatbot", END)
        checkpointer = MemorySaver()
        wellness_graph = builder.compile(checkpointer=checkpointer)
        return wellness_graph


    # Build the graph
    # Compile with a checkpointer for short-term memory
    print("Wellness chatbot compiled with short-term memory (checkpointing)")
    return (
        AIMessage,
        END,
        HumanMessage,
        MemorySaver,
        START,
        StateGraph,
        SystemMessage,
        add_messages,
    )


@app.cell
def _(HumanMessage, wellness_graph):
    # Test short-term memory within a thread
    config = {"configurable": {"thread_id": "wellness_thread_1"}}
    _response = wellness_graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Hi! My name is Sarah and I want to improve my sleep."
                )
            ]
        },
        config,
    )
    # First message - introduce ourselves
    print("User: Hi! My name is Sarah and I want to improve my sleep.")
    print(f"Assistant: {_response['messages'][-1].content}")
    print()
    return (config,)


@app.cell
def _(HumanMessage, config, wellness_graph):
    # Second message - test if it remembers (same thread)
    _response = wellness_graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What's my name and what am I trying to improve?"
                )
            ]
        },
        config,
    )
    print("User: What's my name and what am I trying to improve?")
    print(
        f"Assistant: {_response['messages'][-1].content}"
    )  # Same config = same thread_id
    return


@app.cell
def _(HumanMessage, wellness_graph):
    # New thread - it won't remember Sarah!
    different_config = {"configurable": {"thread_id": "wellness_thread_2"}}
    _response = wellness_graph.invoke(
        {"messages": [HumanMessage(content="What's my name?")]}, different_config
    )
    print("User (NEW thread): What's my name?")
    print(f"Assistant: {_response['messages'][-1].content}")
    print()  # Different thread_id = no memory of Sarah
    print("Notice: The agent doesn't know our name because this is a new thread!")
    return


@app.cell
def _(HumanMessage, config, wellness_graph):
    # Inspect the state of thread 1
    state = wellness_graph.get_state(config)
    print(f"Thread 1 has {len(state.values['messages'])} messages:")
    for _msg in state.values["messages"]:
        _role = "User" if isinstance(_msg, HumanMessage) else "Assistant"
        _content = (
            _msg.content[:80] + "..." if len(_msg.content) > 80 else _msg.content
        )
        print(f"  {_role}: {_content}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Long-Term Memory (InMemoryStore, namespaces)

    **Long-term memory** stores information across different conversation threads. This is like remembering that your friend prefers tea over coffee - you remember it every time you meet them, regardless of what you're currently discussing.

    In LangGraph, long-term memory uses:
    - **Store**: A persistent key-value store
    - **Namespaces**: Organize memories by user, application, or context

    ### Key Difference from Short-Term Memory

    | Short-Term (Checkpointer) | Long-Term (Store) |
    |---------------------------|-------------------|
    | Scoped to a single thread | Shared across all threads |
    | Automatic (messages) | Explicit (you decide what to store) |
    | Conversation history | User preferences, facts, etc. |
    """)
    return


@app.cell
def _():
    from langgraph.store.memory import InMemoryStore

    # Create a store for long-term memory
    store = InMemoryStore()

    # Namespaces organize memories - typically by user_id and category
    user_id = "user_sarah"
    profile_namespace = (user_id, "profile")
    preferences_namespace = (user_id, "preferences")

    # Store Sarah's wellness profile
    store.put(profile_namespace, "name", {"value": "Sarah"})
    store.put(
        profile_namespace,
        "goals",
        {"primary": "improve sleep", "secondary": "reduce stress"},
    )
    store.put(
        profile_namespace,
        "conditions",
        {"allergies": ["peanuts"], "injuries": ["bad knee"]},
    )

    # Store Sarah's preferences
    store.put(
        preferences_namespace,
        "communication",
        {"style": "friendly", "detail_level": "moderate"},
    )
    store.put(
        preferences_namespace,
        "schedule",
        {
            "preferred_workout_time": "morning",
            "available_days": ["Mon", "Wed", "Fri"],
        },
    )

    print("Stored Sarah's profile and preferences in long-term memory")
    return InMemoryStore, profile_namespace, store


@app.cell
def _(profile_namespace, store):
    # Retrieve specific memories
    name = store.get(profile_namespace, "name")
    print(f"Name: {name.value}")

    goals = store.get(profile_namespace, "goals")
    print(f"Goals: {goals.value}")

    # List all memories in a namespace
    print("\nAll profile items:")
    for item in store.search(profile_namespace):
        print(f"  {item.key}: {item.value}")
    return


@app.cell
def _(
    Annotated,
    END,
    MemorySaver,
    START,
    StateGraph,
    SystemMessage,
    TypedDict,
    add_messages,
    llm,
    store,
):
    from langgraph.store.base import BaseStore
    from langchain_core.runnables import RunnableConfig


    # Define state with user_id for personalization
    class PersonalizedState(TypedDict):
        messages: Annotated[list, add_messages]
        user_id: str


    def personalized_wellness_chatbot(
        state: PersonalizedState, config: RunnableConfig, *, store: BaseStore
    ):
        """A wellness chatbot that uses long-term memory for personalization."""
        user_id = state["user_id"]
        profile_namespace = (user_id, "profile")
        preferences_namespace = (user_id, "preferences")
        profile_items = list(store.search(profile_namespace))
        pref_items = list(store.search(preferences_namespace))
        profile_text = "\n".join(
            [f"- {p.key}: {p.value}" for p in profile_items]
        )  # Retrieve user profile from long-term memory
        pref_text = "\n".join([f"- {p.key}: {p.value}" for p in pref_items])
        system_msg = f"You are a Personal Wellness Assistant. You know the following about this user:\n\nPROFILE:\n{(profile_text if profile_text else 'No profile stored.')}\n\nPREFERENCES:\n{(pref_text if pref_text else 'No preferences stored.')}\n\nUse this information to personalize your responses. Be supportive and helpful."
        messages = [SystemMessage(content=system_msg)] + state["messages"]
        _response = llm.invoke(messages)  # Build context from profile
        return {"messages": [_response]}


    builder2 = StateGraph(PersonalizedState)
    builder2.add_node("chatbot", personalized_wellness_chatbot)
    builder2.add_edge(START, "chatbot")
    builder2.add_edge("chatbot", END)
    personalized_graph = builder2.compile(checkpointer=MemorySaver(), store=store)
    # Build the personalized graph
    # Compile with BOTH checkpointer (short-term) AND store (long-term)
    print("Personalized graph compiled with both short-term and long-term memory")
    return BaseStore, RunnableConfig, personalized_graph


@app.cell
def _(HumanMessage, personalized_graph):
    config_1 = {"configurable": {"thread_id": "personalized_thread_1"}}
    _response = personalized_graph.invoke(
        {
            "messages": [
                HumanMessage(content="What exercises would you recommend for me?")
            ],
            "user_id": "user_sarah",
        },
        config_1,
    )
    print("User: What exercises would you recommend for me?")
    print(f"Assistant: {_response['messages'][-1].content}")
    print()
    print(
        "Notice: The agent knows about Sarah's bad knee without her mentioning it!"
    )
    return


@app.cell
def _(HumanMessage, personalized_graph):
    # Even in a NEW thread, it still knows Sarah's profile
    # because long-term memory is cross-thread!
    new_config = {"configurable": {"thread_id": "personalized_thread_2"}}
    _response = personalized_graph.invoke(
        {
            "messages": [HumanMessage(content="Can you suggest a snack for me?")],
            "user_id": "user_sarah",
        },
        new_config,
    )
    print("User (NEW thread): Can you suggest a snack for me?")
    print(f"Assistant: {_response['messages'][-1].content}")
    print()
    print(
        "Notice: Even in a new thread, the agent knows Sarah has a peanut allergy!"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 5: Message Trimming & Context Management

    Long conversations can exceed the LLM's context window. LangGraph provides utilities to manage message history:

    - **`trim_messages`**: Keeps only recent messages up to a token limit
    - **Summarization**: Compress older messages into summaries

    ### Why Trim Even with 128K Context?

    Even with large context windows:
    1. **Cost**: More tokens = higher API costs
    2. **Latency**: Larger contexts take longer to process
    3. **Quality**: Models can struggle with "lost in the middle" - important info buried in long contexts
    4. **Relevance**: Old messages may not be relevant to current query
    """)
    return


@app.cell
def _(AIMessage, HumanMessage, SystemMessage):
    from langchain_core.messages import trim_messages
    from langchain_core.messages.utils import count_tokens_approximately

    trimmer = trim_messages(
        max_tokens=500,
        strategy="last",
        token_counter=count_tokens_approximately,
        include_system=True,
        allow_partial=False,
    )
    # Create a trimmer that keeps only recent messages
    long_conversation = [
        SystemMessage(content="You are a wellness assistant."),
        HumanMessage(content="I want to improve my health."),
        AIMessage(
            content="Great goal! Let's start with exercise. What's your current activity level?"
        ),
        HumanMessage(content="I walk about 30 minutes a day."),
        AIMessage(
            content="That's a good foundation. For cardiovascular health, aim for 150 minutes of moderate activity per week."
        ),
        HumanMessage(content="What about nutrition?"),
        AIMessage(
            content="Focus on whole foods: vegetables, lean proteins, whole grains. Limit processed foods and added sugars."
        ),
        HumanMessage(content="And sleep?"),
        AIMessage(
            content="Aim for 7-9 hours. Maintain a consistent sleep schedule and create a relaxing bedtime routine."
        ),
        HumanMessage(
            content="What's the most important change I should make first?"
        ),
    ]
    trimmed = trimmer.invoke(
        long_conversation
    )  # Keep messages up to this token count
    print(
        f"Original: {len(long_conversation)} messages"
    )  # Keep the most recent messages
    print(f"Trimmed: {len(trimmed)} messages")  # Use the LLM to count tokens
    print("\nTrimmed conversation:")  # Always keep system messages
    for _msg in trimmed:  # Don't cut messages in half
        _role = type(_msg).__name__.replace("Message", "")
        _content = (
            _msg.content[:60] + "..." if len(_msg.content) > 60 else _msg.content
        )
        # Example: Create a long conversation
        # Trim to fit context window
        print(f"  {_role}: {_content}")
    return (long_conversation,)


@app.cell
def _(SystemMessage, llm, long_conversation):
    # Summarization approach for longer conversations
    def summarize_conversation(messages: list, max_messages: int = 6) -> list:
        """Summarize older messages to manage context length."""
        if len(messages) <= max_messages:
            return messages
        system_msg = (
            messages[0] if isinstance(messages[0], SystemMessage) else None
        )
        content_messages = messages[1:] if system_msg else messages
        if (
            len(content_messages) <= max_messages
        ):  # Keep the system message and last few messages
            return messages
        old_messages = content_messages[: -max_messages + 1]
        recent_messages = content_messages[-max_messages + 1 :]
        summary_prompt = f"Summarize this conversation in 2-3 sentences, \ncapturing key wellness topics discussed and any important user information:\n\n{chr(10).join([f'{type(m).__name__}: {m.content[:200]}' for m in old_messages])}"
        summary = llm.invoke(summary_prompt)
        result = []
        if system_msg:
            result.append(system_msg)
        result.append(
            SystemMessage(
                content=f"[Previous conversation summary: {summary.content}]"
            )
        )
        result.extend(recent_messages)  # Summarize old messages
        return result


    summarized = summarize_conversation(long_conversation, max_messages=4)
    print(f"Summarized: {len(summarized)} messages")
    print("\nSummarized conversation:")
    for _msg in summarized:
        _role = type(_msg).__name__.replace("Message", "")
        _content = (
            _msg.content[:80] + "..." if len(_msg.content) > 80 else _msg.content
        )
        # Test summarization
        print(
            f"  {_role}: {_content}"
        )  # Return: system + summary + recent messages
    return (summarize_conversation,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ❓ Question #1:

    What are the trade-offs between **short-term memory** (checkpointer) vs **long-term memory** (store)? When should wellness data move from short-term to long-term?

    Consider:
    - What information should persist across sessions?
    - What are the privacy implications of each?
    - How would you decide what to promote from short-term to long-term?

    ##### Answer:
    *Short-term memory handles automatic conversation tracking within sessions. Long-term memory stores data across sessions. I'd move critical wellness information like allergies, conditions, and long-term goals to long-term storage, but keep temporary conversation details in short-term memory, and I think I might use a tf-idf frequency threshold to decide when to promote from short-term to long-term.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #2:

    Why use message trimming with a 128K context window when HealthWellnessGuide.txt is only ~16KB? What should **always** be preserved when trimming a wellness consultation?

    Consider:
    - The "lost in the middle" phenomenon
    - Cost and latency implications
    - What user information is critical for safety (allergies, conditions, etc.)

    ##### Answer:
    *In my testing and research, I've found that LLMs with our current attention mechanisms have 100% recall up to ~50% of their context window, then a steep drop happens between ~60-80%. So with 128k context, if HealthWellnessGuide contains more than ~64k tokens, we'd already be experiencing a drop in recall, but let's say it's only 20k tokens, there is still a decent chance that we can exceed 40k tokens in our conversation about wellness. We want to extend that 50% context window as far as we possibly can for things to go well.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #1: Store & Retrieve User Wellness Profile

    Build a complete wellness profile system that:
    1. Defines a wellness profile schema (name, goals, conditions, preferences)
    2. Creates functions to store and retrieve profile data
    3. Builds a personalized wellness agent that uses the profile
    4. Tests that different users get different advice

    ### Requirements:
    - Define at least 5 profile attributes
    - Support multiple users with different profiles
    - Agent should reference profile data in responses
    """)
    return


@app.cell
def _(
    Annotated,
    BaseStore,
    END,
    HumanMessage,
    MemorySaver,
    RunnableConfig,
    START,
    StateGraph,
    SystemMessage,
    TypedDict,
    add_messages,
    llm,
    store,
):
    ### YOUR CODE HERE ###

    # Step 1: Define a wellness profile schema
    # Example attributes: name, age, goals, conditions, allergies, fitness_level, preferred_activities

    # Step 2: Create helper functions to store and retrieve profiles
    def store_wellness_profile(store, user_id: str, profile: dict):
        """Store a user's wellness profile."""
        namespace = (user_id, "wellness_profile")
        for key, value in profile.items():
            store.put(namespace, key, {"value": value})


    def get_wellness_profile(store, user_id: str) -> dict:
        """Retrieve a user's wellness profile."""
        namespace = (user_id, "wellness_profile")
        profile_items = list(store.search(namespace))
        return {item.key: item.value["value"] for item in profile_items}


    # Step 3: Create two different user profiles
    Chris_B_profile = {
        "name": "Chris_B",
        "age": 28,
        "goals": ["lose weight", "improve cardiovascular health"],
        "conditions": ["asthma"],
        "allergies": ["shellfish", "dairy"],
        "fitness_level": "beginner",
    }

    Chris_A_profile = {
        "name": "Chris_A",
        "age": 45,
        "goals": ["build muscle", "reduce stress"],
        "conditions": ["high blood pressure"],
        "allergies": ["nuts", "gluten"],
        "fitness_level": "intermediate",
    }

    store_wellness_profile(store, "user_Chris_B", Chris_B_profile)
    store_wellness_profile(store, "user_Chris_A", Chris_A_profile)

    print("Stored Chris_B's and Chris_A's wellness profiles")


    # Step 4: Build a personalized agent that uses profiles
    class ProfileState(TypedDict):
        messages: Annotated[list, add_messages]
        user_id: str


    def profile_wellness_assistant(
        state: ProfileState, config: RunnableConfig, *, store: BaseStore
    ):
        """A wellness assistant that uses user profiles for personalization."""
        user_id = state["user_id"]
        profile = get_wellness_profile(store, user_id)

        if profile:
            profile_text = "\n".join([f"- {k}: {v}" for k, v in profile.items()])
            system_msg = f"You are a Personal Wellness Assistant. You know the following about this user:\n\n{profile_text}\n\nUse this information to personalize your responses. Be supportive and helpful."
        else:
            system_msg = (
                "You are a Personal Wellness Assistant. Be supportive and helpful."
            )

        messages = [SystemMessage(content=system_msg)] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}


    builder = StateGraph(ProfileState)
    builder.add_node("chatbot", profile_wellness_assistant)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)
    profile_graph = builder.compile(checkpointer=MemorySaver(), store=store)

    print("Personalized wellness agent built with profile support")

    # Step 5: Test with different users - they should get different advice
    Chris_B_config = {"configurable": {"thread_id": "Chris_B_test_thread"}}
    Chris_A_config = {"configurable": {"thread_id": "Chris_A_test_thread"}}

    Chris_B_response = profile_graph.invoke(
        {
            "messages": [
                HumanMessage(content="What exercises do you recommend for me?")
            ],
            "user_id": "user_Chris_B",
        },
        Chris_B_config,
    )

    print("\n=== Chris_B's Response ===")
    print(
        f"User (Chris_B, beginner with asthma): What exercises do you recommend for me?"
    )
    print(f"Assistant: {Chris_B_response['messages'][-1].content}")

    Chris_A_response = profile_graph.invoke(
        {
            "messages": [
                HumanMessage(content="What exercises do you recommend for me?")
            ],
            "user_id": "user_Chris_A",
        },
        Chris_A_config,
    )

    print("\n=== Chris_A's Response ===")
    print(
        f"User (Chris_A, intermediate with high blood pressure): What exercises do you recommend for me?"
    )
    print(f"Assistant: {Chris_A_response['messages'][-1].content}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🤝 Breakout Room #2
    ## Advanced Memory & Integration
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 6: Semantic Memory (Embeddings + Search)

    **Semantic memory** stores facts and retrieves them based on *meaning* rather than exact matches. This is like how you might remember "that restaurant with the great pasta" even if you can't remember its exact name.

    In LangGraph, semantic memory uses:
    - **Store with embeddings**: Converts text to vectors for similarity search
    - **`store.search()`**: Finds relevant memories by semantic similarity

    ### How It Works

    ```
    User asks: "What helps with headaches?"
             ↓
    Query embedded → [0.2, 0.8, 0.1, ...]
             ↓
    Compare with stored wellness facts:
      - "Hydration can relieve headaches" → 0.92 similarity ✓
      - "Exercise improves sleep" → 0.35 similarity
             ↓
    Return: "Hydration can relieve headaches"
    ```
    """)
    return


@app.cell
def _(InMemoryStore):
    from langchain_openai import OpenAIEmbeddings

    # Create embeddings model
    embeddings = OpenAIEmbeddings(
        model="text-embedding-nomic-embed-text-v2-moe",
        base_url="http://192.168.1.79:8080/v1",
        check_embedding_ctx_length=False,
    )

    # Create a store with semantic search enabled
    semantic_store = InMemoryStore(
        index={
            "embed": embeddings,
            "dims": 1536,  # Dimension of text-embedding-3-small
        }
    )

    print("Semantic memory store created with embedding support")
    return (semantic_store,)


@app.cell
def _(semantic_store):
    # Store various wellness facts as semantic memories
    namespace = ("wellness", "facts")

    wellness_facts = [
        (
            "fact_1",
            {
                "text": "Drinking water can help relieve headaches caused by dehydration"
            },
        ),
        (
            "fact_2",
            {
                "text": "Regular exercise improves sleep quality and helps you fall asleep faster"
            },
        ),
        (
            "fact_3",
            {
                "text": "Deep breathing exercises can reduce stress and anxiety within minutes"
            },
        ),
        (
            "fact_4",
            {
                "text": "Eating protein at breakfast helps maintain steady energy levels throughout the day"
            },
        ),
        (
            "fact_5",
            {
                "text": "Blue light from screens can disrupt your circadian rhythm and sleep"
            },
        ),
        (
            "fact_6",
            {
                "text": "Walking for 30 minutes daily can improve cardiovascular health"
            },
        ),
        (
            "fact_7",
            {
                "text": "Magnesium-rich foods like nuts and leafy greens can help with muscle cramps"
            },
        ),
        (
            "fact_8",
            {
                "text": "A consistent sleep schedule, even on weekends, improves overall sleep quality"
            },
        ),
    ]

    for key, value in wellness_facts:
        semantic_store.put(namespace, key, value)

    print(f"Stored {len(wellness_facts)} wellness facts in semantic memory")
    return (namespace,)


@app.cell
def _(namespace, semantic_store):
    # Search semantically - notice we don't need exact matches!

    queries = [
        "My head hurts, what should I do?",
        "How can I get better rest at night?",
        "I'm feeling stressed and anxious",
        "What should I eat in the morning?",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        results = semantic_store.search(namespace, query=query, limit=2)
        for r in results:
            print(f"   {r.value['text']} (score: {r.score:.3f})")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 7: Building Semantic Wellness Knowledge Base

    Let's load the HealthWellnessGuide.txt and create a semantic knowledge base that our agent can search.

    This is similar to RAG from Session 4, but now using LangGraph's Store API instead of a separate vector database.
    """)
    return


@app.cell
def _():
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    # Load and chunk the wellness document
    loader = TextLoader("data/HealthWellnessGuide.txt")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)

    print(f"Loaded and split into {len(chunks)} chunks")
    print(f"\nSample chunk:\n{chunks[0].page_content[:200]}...")
    return (chunks,)


@app.cell
def _(chunks, semantic_store):
    # Store chunks in semantic memory
    knowledge_namespace = ("wellness", "knowledge")
    for _i, chunk in enumerate(chunks):
        semantic_store.put(
            knowledge_namespace,
            f"chunk_{_i}",
            {"text": chunk.page_content, "source": "HealthWellnessGuide.txt"},
        )
    print(f"Stored {len(chunks)} chunks in semantic knowledge base")
    return


@app.cell
def _(
    Annotated,
    BaseStore,
    END,
    MemorySaver,
    RunnableConfig,
    START,
    StateGraph,
    SystemMessage,
    TypedDict,
    add_messages,
    llm,
    semantic_store,
):
    # Build a semantic search wellness chatbot
    class SemanticState(TypedDict):
        messages: Annotated[list, add_messages]
        user_id: str


    def semantic_wellness_chatbot(
        state: SemanticState, config: RunnableConfig, *, store: BaseStore
    ):
        """A wellness chatbot that retrieves relevant facts using semantic search."""
        user_message = state["messages"][-1].content
        knowledge_results = store.search(
            ("wellness", "knowledge"), query=user_message, limit=3
        )
        if knowledge_results:
            knowledge_text = "\n\n".join(
                [f"- {r.value['text']}" for r in knowledge_results]
            )
            system_msg = f"You are a Personal Wellness Assistant with access to a wellness knowledge base.\n\nRelevant information from your knowledge base:\n{knowledge_text}\n\nUse this information to answer the user's question. If the information doesn't directly answer their question, use your general knowledge but mention what you found."  # Search for relevant knowledge
        else:
            system_msg = "You are a Personal Wellness Assistant. Answer wellness questions helpfully."
        messages = [SystemMessage(content=system_msg)] + state["messages"]
        _response = llm.invoke(messages)
        return {"messages": [_response]}


    builder3 = StateGraph(SemanticState)
    builder3.add_node(
        "chatbot", semantic_wellness_chatbot
    )  # Build context from retrieved knowledge
    builder3.add_edge(START, "chatbot")
    builder3.add_edge("chatbot", END)
    semantic_graph = builder3.compile(
        checkpointer=MemorySaver(), store=semantic_store
    )
    # Build and compile
    print("Semantic wellness chatbot ready")
    return (semantic_graph,)


@app.cell
def _(HumanMessage, semantic_graph):
    config_2 = {"configurable": {"thread_id": "semantic_thread_1"}}
    questions = [
        "What exercises can help with lower back pain?",
        "How can I improve my sleep quality?",
        "What should I eat for better gut health?",
    ]
    for q in questions:
        _response = semantic_graph.invoke(
            {"messages": [HumanMessage(content=q)], "user_id": "test_user"},
            config_2,
        )
        print(f"\nUser: {q}")
        print(f"Assistant: {_response['messages'][-1].content[:500]}...")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 8: Episodic Memory (Few-Shot Learning)

    **Episodic memory** stores past experiences and uses them as examples for future tasks. In humans, this is like remembering the first time you successfully gave someone good advice and using that experience to guide future interactions.

    For AI agents, episodic memory is often implemented as **few-shot examples** - showing the model examples of correct behavior so it can learn patterns.

    ### The CoALA Framework Perspective

    > "Facts can be written to semantic memory, whereas **experiences** can be written to episodic memory."

    Key insight: Sometimes it's easier to **show** than **tell**. LLMs learn well from examples!
    """)
    return


@app.cell
def _(semantic_store):
    # Create episodic memory with past successful interactions
    episodic_namespace = ("agent", "episodes")
    successful_episodes = [
        {
            "situation": "User asked about starting exercise with joint pain",
            "input": "I want to start exercising but my knees hurt. What should I do?",
            "output": "For knee-friendly exercise, I'd recommend starting with low-impact activities:\n\n1. **Swimming or water aerobics** - Water supports your joints while providing great cardio\n2. **Cycling** - Either stationary or regular bikes are gentle on knees\n3. **Elliptical machine** - Provides cardio without impact\n\nStart slowly with 15-20 minutes and gradually increase. If you experience pain, stop and consult a healthcare provider. Would you like specific exercises for any of these?",
            "feedback": "User appreciated the specific alternatives and safety advice",
        },
        {
            "situation": "User struggling with sleep and stress",
            "input": "I can't fall asleep because I'm always thinking about work. Help!",
            "output": 'Racing thoughts at bedtime is common, especially with work stress. Here\'s a proven approach:\n\n**Before bed:**\n- Write down tomorrow\'s to-do list (gets thoughts out of your head)\n- Set a "worry time" earlier in the evening - not at bedtime\n\n**At bedtime:**\n- Try the 4-7-8 breathing technique: Inhale 4 counts, hold 7, exhale 8\n- Use the "cognitive shuffle" - think of random, unrelated objects (apple, guitar, mountain...)\n\nWhich of these would you like to try first?',
            "feedback": "User found the structured approach and specific techniques helpful",
        },
        {
            "situation": "User asking about healthy eating on a budget",
            "input": "How can I eat healthy when I don't have much money?",
            "output": "Eating healthy on a budget is absolutely possible! Here are practical strategies:\n\n**Budget-friendly nutritious foods:**\n- Eggs, beans, lentils (cheap protein)\n- Frozen vegetables (same nutrition as fresh, longer lasting)\n- Oats, rice, whole grain bread\n- Canned fish (tuna, salmon)\n\n**Money-saving tips:**\n- Buy in bulk when possible\n- Plan meals around sales\n- Cook in batches and freeze portions\n\nWhat's your typical weekly food budget? I can help you create a specific meal plan.",
            "feedback": "User valued the practical, actionable advice without judgment",
        },
    ]
    for _i, episode in enumerate(successful_episodes):
        semantic_store.put(
            episodic_namespace,
            f"episode_{_i}",
            {"text": episode["situation"], **episode},
        )
    print(
        f"Stored {len(successful_episodes)} episodic memories (past successful interactions)"
    )  # Used for semantic search
    return


@app.cell
def _(
    Annotated,
    BaseStore,
    END,
    MemorySaver,
    RunnableConfig,
    START,
    StateGraph,
    SystemMessage,
    TypedDict,
    add_messages,
    llm,
    semantic_store,
):
    class EpisodicState(TypedDict):
        messages: Annotated[list, add_messages]


    def episodic_wellness_chatbot(
        state: EpisodicState, config: RunnableConfig, *, store: BaseStore
    ):
        """A chatbot that learns from past successful interactions."""
        user_question = state["messages"][-1].content
        similar_episodes = store.search(
            ("agent", "episodes"), query=user_question, limit=1
        )
        if similar_episodes:
            episode = similar_episodes[
                0
            ].value  # Search for similar past experiences
            few_shot_example = f"Here's an example of a similar wellness question I handled well:\n\nUser asked: {episode['input']}\n\nMy response was:\n{episode['output']}\n\nThe user feedback was: {episode['feedback']}\n\nUse this as inspiration for the style, structure, and tone of your response, but tailor it to the current question."
            system_msg = f"You are a Personal Wellness Assistant. Learn from your past successes:\n\n{few_shot_example}"
        else:
            system_msg = "You are a Personal Wellness Assistant. Be helpful, specific, and supportive."
        messages = [SystemMessage(content=system_msg)] + state["messages"]
        _response = llm.invoke(messages)
        return {
            "messages": [_response]
        }  # Build few-shot examples from past episodes


    builder4 = StateGraph(EpisodicState)
    builder4.add_node("chatbot", episodic_wellness_chatbot)
    builder4.add_edge(START, "chatbot")
    builder4.add_edge("chatbot", END)
    episodic_graph = builder4.compile(
        checkpointer=MemorySaver(), store=semantic_store
    )
    # Build the episodic memory graph
    print("Episodic memory chatbot ready")
    return (episodic_graph,)


@app.cell
def _(HumanMessage, episodic_graph):
    config_3 = {"configurable": {"thread_id": "episodic_thread_1"}}
    _response = episodic_graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="I want to exercise more but I have a bad hip. What can I do?"
                )
            ]
        },
        config_3,
    )
    print("User: I want to exercise more but I have a bad hip. What can I do?")
    print(f"\nAssistant: {_response['messages'][-1].content}")
    print(
        "\nNotice: The response structure mirrors the successful knee pain episode!"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 9: Procedural Memory (Self-Improving Agent)

    **Procedural memory** stores the rules and instructions that guide behavior. In humans, this is like knowing *how* to give good advice - it's internalized knowledge about performing tasks.

    For AI agents, procedural memory often means **self-modifying prompts**. The agent can:
    1. Store its current instructions in the memory store
    2. Reflect on feedback from interactions
    3. Update its own instructions to improve

    ### The Reflection Pattern

    ```
    User feedback: "Your advice is too long and complicated"
             ↓
    Agent reflects on current instructions
             ↓
    Agent updates instructions: "Keep advice concise and actionable"
             ↓
    Future responses use updated instructions
    ```
    """)
    return


@app.cell
def _(semantic_store):
    # Initialize procedural memory with base instructions
    procedural_namespace = ("agent", "instructions")

    initial_instructions = """You are a Personal Wellness Assistant.

    Guidelines:
    - Be supportive and non-judgmental
    - Provide evidence-based wellness information
    - Ask clarifying questions when needed
    - Encourage healthy habits without being preachy"""

    semantic_store.put(
        procedural_namespace,
        "wellness_assistant",
        {"instructions": initial_instructions, "version": 1},
    )

    print("Initialized procedural memory with base instructions")
    print(f"\nCurrent Instructions (v1):\n{initial_instructions}")
    return


@app.cell
def _(
    Annotated,
    BaseStore,
    END,
    HumanMessage,
    MemorySaver,
    RunnableConfig,
    START,
    StateGraph,
    SystemMessage,
    TypedDict,
    add_messages,
    llm,
    semantic_store,
):
    class ProceduralState(TypedDict):
        messages: Annotated[list, add_messages]
        feedback: str  # Optional feedback from user


    def get_instructions(store: BaseStore) -> tuple[str, int]:
        """Retrieve current instructions from procedural memory."""
        item = store.get(("agent", "instructions"), "wellness_assistant")
        if item is None:
            return ("You are a helpful wellness assistant.", 0)
        return (item.value["instructions"], item.value["version"])


    def procedural_assistant_node(
        state: ProceduralState, config: RunnableConfig, *, store: BaseStore
    ):
        """Respond using current procedural instructions."""
        instructions, version = get_instructions(store)
        messages = [SystemMessage(content=instructions)] + state["messages"]
        _response = llm.invoke(messages)
        return {"messages": [_response]}


    def reflection_node(
        state: ProceduralState, config: RunnableConfig, *, store: BaseStore
    ):
        """Reflect on feedback and update instructions if needed."""
        feedback = state.get("feedback", "")
        if not feedback:
            return {}
        current_instructions, version = get_instructions(store)
        reflection_prompt = f"You are improving a wellness assistant's instructions based on user feedback.\n\nCurrent Instructions:\n{current_instructions}\n\nUser Feedback:\n{feedback}\n\nBased on this feedback, provide improved instructions. Keep the same general format but incorporate the feedback.\nOnly output the new instructions, nothing else."
        _response = llm.invoke([HumanMessage(content=reflection_prompt)])
        new_instructions = _response.content
        store.put(
            ("agent", "instructions"),
            "wellness_assistant",
            {"instructions": new_instructions, "version": version + 1},
        )  # No feedback, no update needed
        print(f"\nInstructions updated to version {version + 1}")
        return {}  # Get current instructions


    def should_reflect(state: ProceduralState) -> str:
        """Decide whether to reflect on feedback."""  # Ask the LLM to reflect and improve instructions
        if state.get("feedback"):
            return "reflect"
        return "end"


    builder5 = StateGraph(ProceduralState)
    builder5.add_node("assistant", procedural_assistant_node)
    builder5.add_node("reflect", reflection_node)
    builder5.add_edge(START, "assistant")
    builder5.add_conditional_edges(
        "assistant", should_reflect, {"reflect": "reflect", "end": END}
    )
    builder5.add_edge("reflect", END)
    procedural_graph = builder5.compile(
        checkpointer=MemorySaver(), store=semantic_store
    )
    # Build the procedural memory graph
    print(
        "Procedural memory graph ready (with self-improvement capability)"
    )  # Update procedural memory with new instructions
    return get_instructions, procedural_graph


@app.cell
def _(HumanMessage, procedural_graph):
    config_4 = {"configurable": {"thread_id": "procedural_thread_1"}}
    _response = procedural_graph.invoke(
        {
            "messages": [HumanMessage(content="How can I reduce stress?")],
            "feedback": "",
        },
        config_4,
    )
    print("User: How can I reduce stress?")
    print(f"\nAssistant (v1 instructions):\n{_response['messages'][-1].content}")
    return


@app.cell
def _(HumanMessage, procedural_graph):
    # Now provide feedback - the agent will update its own instructions!
    _response = procedural_graph.invoke(
        {
            "messages": [HumanMessage(content="How can I reduce stress?")],
            "feedback": "Your responses are too long. Please be more concise and give me 3 actionable tips maximum.",
        },
        {"configurable": {"thread_id": "procedural_thread_2"}},
    )
    return


@app.cell
def _(get_instructions, semantic_store):
    # Check the updated instructions
    new_instructions, version = get_instructions(semantic_store)
    print(f"Updated Instructions (v{version}):\n")
    print(new_instructions)
    return (version,)


@app.cell
def _(HumanMessage, procedural_graph, version):
    # Test with updated instructions - should be more concise now!
    _response = procedural_graph.invoke(
        {
            "messages": [HumanMessage(content="How can I sleep better?")],
            "feedback": "",
        },
        {"configurable": {"thread_id": "procedural_thread_3"}},
    )
    print(f"User: How can I sleep better?")
    print(f"\nAssistant (v{version} instructions - after feedback):")
    print(_response["messages"][-1].content)  # No feedback this time
    print(
        "\nNotice: The response should now be more concise based on the feedback!"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 10: Unified Wellness Memory Agent

    Now let's combine **all 5 memory types** into a unified wellness agent:

    1. **Short-term**: Remembers current conversation (checkpointer)
    2. **Long-term**: Stores user profile across sessions (store + namespace)
    3. **Semantic**: Retrieves relevant wellness knowledge (store + embeddings)
    4. **Episodic**: Uses past successful interactions as examples (store + search)
    5. **Procedural**: Adapts behavior based on feedback (store + reflection)

    ### Memory Retrieval Flow

    ```
    User Query: "What exercises can help my back pain?"
                  │
                  ▼
    ┌─────────────────────────────────────────────────┐
    │  1. PROCEDURAL: Get current instructions         │
    │  2. LONG-TERM: Load user profile (conditions)    │
    │  3. SEMANTIC: Search wellness knowledge          │
    │  4. EPISODIC: Find similar past interactions     │
    │  5. SHORT-TERM: Include conversation history     │
    └─────────────────────────────────────────────────┘
                  │
                  ▼
            Generate personalized, informed response
    ```
    """)
    return


@app.cell
def _(
    Annotated,
    BaseStore,
    END,
    HumanMessage,
    MemorySaver,
    RunnableConfig,
    START,
    StateGraph,
    SystemMessage,
    TypedDict,
    add_messages,
    llm,
    semantic_store,
    summarize_conversation,
):
    class UnifiedState(TypedDict):
        messages: Annotated[list, add_messages]
        user_id: str
        feedback: str


    def unified_wellness_assistant(
        state: UnifiedState, config: RunnableConfig, *, store: BaseStore
    ):
        """An assistant that uses all five memory types."""
        user_id = state["user_id"]
        user_message = state["messages"][-1].content
        instructions_item = store.get(
            ("agent", "instructions"), "wellness_assistant"
        )
        base_instructions = (
            instructions_item.value["instructions"]
            if instructions_item
            else "You are a helpful wellness assistant."
        )
        profile_items = list(
            store.search((user_id, "profile"))
        )  # 1. PROCEDURAL: Get current instructions
        pref_items = list(store.search((user_id, "preferences")))
        profile_text = (
            "\n".join([f"- {p.key}: {p.value}" for p in profile_items])
            if profile_items
            else "No profile stored."
        )
        relevant_knowledge = store.search(
            ("wellness", "knowledge"), query=user_message, limit=2
        )
        knowledge_text = (
            "\n".join(
                [f"- {r.value['text'][:200]}..." for r in relevant_knowledge]
            )
            if relevant_knowledge
            else "No specific knowledge found."
        )  # 2. LONG-TERM: Get user profile
        similar_episodes = store.search(
            ("agent", "episodes"), query=user_message, limit=1
        )
        if similar_episodes:
            ep = similar_episodes[0].value
            episode_text = f"Similar past interaction:\nUser: {ep.get('input', 'N/A')}\nResponse style: {ep.get('feedback', 'N/A')}"
        else:  # 3. SEMANTIC: Search for relevant knowledge
            episode_text = "No similar past interactions found."
        system_message = f"{base_instructions}\n\n=== USER PROFILE ===\n{profile_text}\n\n=== RELEVANT WELLNESS KNOWLEDGE ===\n{knowledge_text}\n\n=== LEARNING FROM EXPERIENCE ===\n{episode_text}\n\nUse all of this context to provide the best possible personalized response."
        trimmed_messages = summarize_conversation(
            state["messages"], max_messages=6
        )
        messages = [
            SystemMessage(content=system_message)
        ] + trimmed_messages  # 4. EPISODIC: Find similar past interactions
        _response = llm.invoke(messages)
        return {"messages": [_response]}


    def unified_feedback_node(
        state: UnifiedState, config: RunnableConfig, *, store: BaseStore
    ):
        """Update procedural memory based on feedback."""
        feedback = state.get("feedback", "")
        if not feedback:
            return {}  # Build comprehensive system message
        item = store.get(("agent", "instructions"), "wellness_assistant")
        if item is None:
            return {}
        current = item.value
        reflection_prompt = f"Update these instructions based on feedback:\n\nCurrent: {current['instructions']}\nFeedback: {feedback}\n\nOutput only the updated instructions."
        _response = llm.invoke([HumanMessage(content=reflection_prompt)])
        store.put(
            ("agent", "instructions"),
            "wellness_assistant",
            {"instructions": _response.content, "version": current["version"] + 1},
        )
        print(f"Procedural memory updated to v{current['version'] + 1}")
        return {}


    def unified_route(state: UnifiedState) -> str:
        return "feedback" if state.get("feedback") else "end"


    unified_builder = StateGraph(UnifiedState)
    unified_builder.add_node(
        "assistant", unified_wellness_assistant
    )  # 5. SHORT-TERM: Full conversation history is automatically managed by the checkpointer
    unified_builder.add_node(
        "feedback", unified_feedback_node
    )  # Use summarization for long conversations
    unified_builder.add_edge(START, "assistant")
    unified_builder.add_conditional_edges(
        "assistant", unified_route, {"feedback": "feedback", "end": END}
    )
    unified_builder.add_edge("feedback", END)
    unified_graph = unified_builder.compile(
        checkpointer=MemorySaver(), store=semantic_store
    )
    # Build the unified graph
    # Compile with both checkpointer (short-term) and store (all other memory types)
    print("Unified wellness assistant ready with all 5 memory types!")
    return (unified_graph,)


@app.cell
def _(HumanMessage, unified_graph):
    config_5 = {"configurable": {"thread_id": "unified_thread_1"}}
    _response = unified_graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What exercises would you recommend for my back?"
                )
            ],
            "user_id": "user_sarah",
            "feedback": "",
        },
        config_5,
    )
    print("User: What exercises would you recommend for my back?")
    print(f"\nAssistant: {_response['messages'][-1].content}")
    print("\n" + "=" * 60)
    print("Memory types used:")
    print("  Long-term: Knows Sarah has a bad knee")
    print("  Semantic: Retrieved back exercise info from knowledge base")
    print("  Episodic: May use similar joint pain episode as reference")
    print("  Procedural: Following current instructions")
    print("  Short-term: Will remember this in follow-up questions")
    return (config_5,)


@app.cell
def _(HumanMessage, config_5, unified_graph):
    _response = unified_graph.invoke(
        {
            "messages": [
                HumanMessage(content="Can you show me how to do the first one?")
            ],
            "user_id": "user_sarah",
            "feedback": "",
        },
        config_5,
    )
    print("User: Can you show me how to do the first one?")
    print(f"\nAssistant: {_response['messages'][-1].content}")
    print("\nNotice: The agent remembers the context from the previous message!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ❓ Question #3:

    How would you decide what constitutes a **"successful" wellness interaction** worth storing as an episode? What metadata should you store alongside the episode?

    Consider:
    - Explicit feedback (thumbs up) vs implicit signals
    - User engagement (did they ask follow-up questions?)
    - Objective outcomes vs subjective satisfaction
    - Privacy implications of storing interaction data

    ##### Answer:
    *I don't think there's a silver bullet that exists, but we can store episodes when users give positive feedback, ask follow-up questions, or report progress. These signals show the advice was actually helpful. Keep metadata like timestamp, topic category, feedback score (if provided), engagement metrics (follow-up count, conversation duration), and anonymized user ID for privacy while avoiding any personal health details. This starts getting tricky the same way that bag of words lead to tf-idf, but neither solved the frequency-signal relationship.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #4:

    For a **production wellness assistant**, which memory types need persistent storage (PostgreSQL) vs in-memory? How would you handle memory across multiple agent instances (e.g., Exercise Agent, Nutrition Agent, Sleep Agent)?

    Consider:
    - Which memories are user-specific vs shared?
    - Consistency requirements across agents
    - Memory expiration and cleanup policies
    - Namespace strategy for multi-agent systems

    ##### Answer:
    *User profiles, semantic (relational) knowledge, episodic examples, and procedural instructions should likely be persistent in PostgreSQL. Keep short-term conversation context in-memory with a TTL, namespace by user_id for privacy and agent_type for specialist data.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #2: Wellness Memory Dashboard

    Build a wellness tracking system that:
    1. Tracks wellness metrics over time (mood, energy, sleep quality)
    2. Uses semantic memory to find relevant advice
    3. Uses episodic memory to recall what worked before
    4. Uses procedural memory to adapt advice style
    5. Provides a synthesized "wellness summary"

    ### Requirements:
    - Store at least 3 wellness metrics per user
    - Track metrics over multiple "days" (simulated)
    - Agent should reference historical data in responses
    - Generate a personalized wellness summary
    """)
    return


@app.cell
def _(semantic_store):
    ### YOUR CODE HERE ###

    # Step 1: Define wellness metrics schema and storage functions
    def log_wellness_metric(
        store,
        user_id: str,
        date: str,
        metric_type: str,
        value: float,
        notes: str = "",
    ):
        """Log a wellness metric for a user."""
        namespace = (user_id, "metrics")
        key = f"{date}_{metric_type}"
        store.put(namespace, key, {"value": value, "notes": notes, "date": date})


    def get_wellness_history(
        store, user_id: str, metric_type: str = None, days: int = 7
    ) -> list:
        """Get wellness history for a user."""
        namespace = (user_id, "metrics")
        all_metrics = list(store.search(namespace))
        if metric_type:
            filtered = [m for m in all_metrics if metric_type in m.key]
        else:
            filtered = all_metrics
        sorted_metrics = sorted(filtered, key=lambda x: x.key, reverse=True)
        return sorted_metrics[:days]


    # Step 2: Create sample wellness data for a user (simulate a week)
    test_user = "user_dashboard_test"
    dates = ["Day1", "Day2", "Day3", "Day4", "Day5"]
    for i, day in enumerate(dates):
        log_wellness_metric(
            semantic_store, test_user, day, "mood", 6 + i * 0.5 if i < 4 else 5
        )
        log_wellness_metric(semantic_store, test_user, day, "energy", 5 + (i % 3))
        log_wellness_metric(
            semantic_store, test_user, day, "sleep_quality", 7 - (i % 2)
        )
    print("Sample wellness data created for test user")

    # Step 3: Build a wellness dashboard agent that:
    #   - Retrieves user's wellness history
    #   - Searches for relevant advice based on patterns
    #   - Uses episodic memory for what worked before
    #   - Generates a personalized summary


    def generate_wellness_summary(store, user_id: str) -> dict:
        """Generate a summary of wellness metrics."""
        history = get_wellness_history(store, user_id, days=7)
        mood_vals = [m.value["value"] for m in history if "mood" in m.key]
        energy_vals = [m.value["value"] for m in history if "energy" in m.key]
        sleep_vals = [m.value["value"] for m in history if "sleep" in m.key]
        summary = {
            "avg_mood": sum(mood_vals) / len(mood_vals) if mood_vals else 0,
            "avg_energy": sum(energy_vals) / len(energy_vals)
            if energy_vals
            else 0,
            "avg_sleep": sum(sleep_vals) / len(sleep_vals) if sleep_vals else 0,
            "trend": "improving"
            if mood_vals and mood_vals[0] > mood_vals[-1]
            else "stable",
        }
        return summary


    def wellness_dashboard(store, user_id: str, query: str) -> str:
        """Main dashboard function."""
        summary = generate_wellness_summary(store, user_id)
        relevant_advice = store.search(("wellness", "facts"), query=query, limit=2)
        similar_episodes = store.search(
            ("agent", "episodes"), query=query, limit=1
        )

        response = f"Wellness Summary for {user_id}:\n"
        response += f"- Average Mood: {summary['avg_mood']:.1f}/10\n"
        response += f"- Average Energy: {summary['avg_energy']:.1f}/10\n"
        response += f"- Average Sleep: {summary['avg_sleep']:.1f}/10\n"
        response += f"- Trend: {summary['trend']}\n"

        if relevant_advice:
            response += f"\nRelevant Advice:\n{relevant_advice[0].value['text']}"

        return response


    # Step 4: Test the dashboard
    print("\n" + "=" * 50)
    print("Test 1: Weekly Summary")
    print("=" * 50)
    print(wellness_dashboard(semantic_store, test_user, "give me a summary"))

    print("\n" + "=" * 50)
    print("Test 2: Tiredness Query")
    print("=" * 50)
    print(
        wellness_dashboard(
            semantic_store, test_user, "I've been feeling tired lately"
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    In this session, we explored the **5 memory types** from the CoALA framework:

    | Memory Type | LangGraph Component | Scope | Wellness Use Case |
    |-------------|---------------------|-------|-------------------|
    | **Short-term** | `MemorySaver` + `thread_id` | Within thread | Current consultation |
    | **Long-term** | `InMemoryStore` + namespaces | Across threads | User profile, goals |
    | **Semantic** | Store + embeddings + `search()` | Across threads | Knowledge retrieval |
    | **Episodic** | Store + few-shot examples | Across threads | Past successful interactions |
    | **Procedural** | Store + self-reflection | Across threads | Self-improving instructions |

    ### Key Takeaways:

    1. **Memory transforms chatbots into assistants** - Persistence enables personalization
    2. **Different memory types serve different purposes** - Choose based on your use case
    3. **Context management is critical** - Trim and summarize to stay within limits
    4. **Episodic memory enables learning** - Show, don't just tell
    5. **Procedural memory enables adaptation** - Agents can improve themselves

    ### Production Considerations:

    - Use `PostgresSaver` instead of `MemorySaver` for persistent checkpoints
    - Use `PostgresStore` instead of `InMemoryStore` for persistent long-term memory
    - Consider TTL (Time-to-Live) policies for automatic memory cleanup
    - Implement proper access controls for user data

    ### Further Reading:

    - [LangGraph Memory Documentation](https://langchain-ai.github.io/langgraph/concepts/memory/)
    - [CoALA Paper](https://arxiv.org/abs/2309.02427) - Cognitive Architectures for Language Agents
    - [LangGraph Platform](https://docs.langchain.com/langgraph-platform/) - Managed infrastructure for production
    """)
    return


if __name__ == "__main__":
    app.run()
