"""Memory-enabled wellness agent implementation.

This module provides the main agent graph that integrates all 5 memory types
for a comprehensive wellness assistant experience.
"""

from typing import Annotated, Optional
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.store.base import BaseStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from wellness_memory.stores import create_checkpointer, create_memory_store, initialize_wellness_store
from wellness_memory.memory_types import (
    LongTermMemory,
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
)
from wellness_memory.utils import format_memory_context, summarize_conversation


# State definition for the wellness agent
class WellnessState(TypedDict):
    """State for the wellness memory agent.

    Attributes:
        messages: Conversation history (short-term memory via checkpointer).
        user_id: Unique identifier for the user.
        feedback: Optional feedback from the user for procedural updates.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
    feedback: str


def wellness_assistant_node(
    state: WellnessState,
    config: RunnableConfig,
    *,
    store: BaseStore,
) -> dict:
    """Main wellness assistant node that uses all memory types.

    This node:
    1. Retrieves procedural instructions
    2. Loads user profile from long-term memory
    3. Searches for relevant facts using semantic memory
    4. Finds similar past interactions using episodic memory
    5. Generates a personalized response using all context

    Args:
        state: The current graph state.
        config: Runtime configuration.
        store: The memory store for long-term, semantic, and episodic memory.

    Returns:
        Updated state with the assistant's response.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    user_id = state.get("user_id", "default_user")
    user_message = state["messages"][-1].content if state["messages"] else ""

    # 1. PROCEDURAL MEMORY: Get current instructions
    procedural = ProceduralMemory(store)
    instructions, version = procedural.get_instructions()
    if not instructions:
        instructions = "You are a helpful wellness assistant."

    # 2. LONG-TERM MEMORY: Get user profile
    long_term = LongTermMemory(store, user_id)
    profile = long_term.get_profile()
    preferences = long_term.get_preferences()
    combined_profile = {**profile, **preferences}

    # 3. SEMANTIC MEMORY: Search for relevant facts
    semantic = SemanticMemory(store, ("wellness", "knowledge"))
    relevant_facts = semantic.search(user_message, limit=3)

    # 4. EPISODIC MEMORY: Find similar past interactions
    episodic = EpisodicMemory(store)
    similar_episodes = episodic.find_similar(user_message, limit=2)

    # Build comprehensive context
    system_content = format_memory_context(
        profile=combined_profile,
        relevant_facts=relevant_facts,
        similar_episodes=similar_episodes,
        instructions=instructions,
    )

    # 5. SHORT-TERM MEMORY: Use conversation history (managed by checkpointer)
    # Summarize if conversation is getting long
    trimmed_messages = summarize_conversation(state["messages"], max_messages=8, llm=llm)

    # Build final message list
    messages = [SystemMessage(content=system_content)] + trimmed_messages

    # Generate response
    response = llm.invoke(messages)

    return {"messages": [response]}


def feedback_node(
    state: WellnessState,
    config: RunnableConfig,
    *,
    store: BaseStore,
) -> dict:
    """Process user feedback to update procedural memory.

    This node reflects on feedback and updates the agent's instructions
    to improve future interactions.

    Args:
        state: The current graph state.
        config: Runtime configuration.
        store: The memory store.

    Returns:
        Empty dict (no state changes, updates are in the store).
    """
    feedback = state.get("feedback", "")
    if not feedback:
        return {}

    procedural = ProceduralMemory(store)
    new_instructions, new_version = procedural.reflect_and_update(feedback)
    print(f"Procedural memory updated to version {new_version}")

    return {}


def should_process_feedback(state: WellnessState) -> str:
    """Determine if feedback should be processed.

    Args:
        state: The current graph state.

    Returns:
        "feedback" if there's feedback to process, "end" otherwise.
    """
    if state.get("feedback"):
        return "feedback"
    return "end"


def create_wellness_agent(
    store: Optional[BaseStore] = None,
    checkpointer: Optional[MemorySaver] = None,
    initialize_store: bool = True,
    use_local_memory: bool = True,
) -> StateGraph:
    """Create a memory-enabled wellness agent.

    Args:
        store: Optional memory store. Creates one if not provided (and use_local_memory=True).
        checkpointer: Optional checkpointer. Creates one if not provided (and use_local_memory=True).
        initialize_store: Whether to initialize the store with default data.
        use_local_memory: If True, creates local checkpointer/store when not provided.
            Set to False for LangGraph API deployment where persistence is handled by the platform.

    Returns:
        Compiled LangGraph for the wellness agent.
    """
    if use_local_memory:
        if store is None:
            store = create_memory_store(with_embeddings=True)
        if checkpointer is None:
            checkpointer = create_checkpointer()
        if initialize_store and store is not None:
            initialize_wellness_store(store)

    # Build the graph
    builder = StateGraph(WellnessState)

    # Add nodes
    builder.add_node("assistant", wellness_assistant_node)
    builder.add_node("feedback", feedback_node)

    # Add edges
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        should_process_feedback,
        {"feedback": "feedback", "end": END}
    )
    builder.add_edge("feedback", END)

    # Compile with memory (None values are fine for LangGraph API - it injects them)
    return builder.compile(checkpointer=checkpointer, store=store)


# Create graph instance for LangGraph API/Studio
# Note: When running with LangGraph API, checkpointer and store are injected
# automatically by the platform, so we set use_local_memory=False.
wellness_graph = create_wellness_agent(use_local_memory=False)


# Create a local testing graph with in-memory persistence
_local_test_graph = None

def _get_local_test_graph():
    """Get or create a local testing graph with in-memory persistence."""
    global _local_test_graph
    if _local_test_graph is None:
        _local_test_graph = create_wellness_agent(use_local_memory=True)
    return _local_test_graph


# Simple helper for quick testing
def chat(message: str, user_id: str = "default_user", thread_id: str = "default_thread") -> str:
    """Quick chat function for testing the wellness agent.

    Args:
        message: The user's message.
        user_id: The user identifier.
        thread_id: The conversation thread identifier.

    Returns:
        The agent's response.
    """
    graph = _get_local_test_graph()
    config = {"configurable": {"thread_id": thread_id}}
    response = graph.invoke(
        {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "feedback": "",
        },
        config,
    )
    return response["messages"][-1].content


if __name__ == "__main__":
    # Simple test
    print("Testing Wellness Memory Agent")
    print("=" * 50)

    # First message
    response = chat("Hi! I want to start exercising but I have bad knees.", thread_id="test_1")
    print(f"User: Hi! I want to start exercising but I have bad knees.")
    print(f"Assistant: {response}")
    print()

    # Follow-up (tests short-term memory)
    response = chat("What specific exercises do you recommend?", thread_id="test_1")
    print(f"User: What specific exercises do you recommend?")
    print(f"Assistant: {response}")
