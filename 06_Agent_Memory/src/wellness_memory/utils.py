"""Utility functions for the wellness memory agent.

This module provides helper functions for message trimming,
conversation summarization, and other memory-related operations.
"""

from typing import Optional
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    trim_messages,
)
from langchain_openai import ChatOpenAI


def trim_conversation(
    messages: list[BaseMessage],
    max_tokens: int = 4000,
    llm: Optional[ChatOpenAI] = None,
    include_system: bool = True,
    preserve_first: bool = True,
) -> list[BaseMessage]:
    """Trim a conversation to fit within a token limit.

    This function uses LangGraph's trim_messages utility to intelligently
    reduce the conversation length while preserving important context.

    Args:
        messages: The list of messages to trim.
        max_tokens: Maximum number of tokens to keep.
        llm: The LLM to use for token counting. Defaults to gpt-4o-mini.
        include_system: Whether to always keep system messages.
        preserve_first: Whether to always keep the first human message.

    Returns:
        The trimmed list of messages.

    Example:
        >>> messages = [SystemMessage(content="..."), HumanMessage(content="..."), ...]
        >>> trimmed = trim_conversation(messages, max_tokens=2000)
    """
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini")

    trimmer = trim_messages(
        max_tokens=max_tokens,
        strategy="last",
        token_counter=llm,
        include_system=include_system,
        allow_partial=False,
    )

    trimmed = trimmer.invoke(messages)

    # Optionally preserve the first human message for context
    if preserve_first and messages:
        first_human = None
        for msg in messages:
            if isinstance(msg, HumanMessage):
                first_human = msg
                break

        if first_human and first_human not in trimmed:
            # Insert after system message if present
            insert_idx = 1 if trimmed and isinstance(trimmed[0], SystemMessage) else 0
            trimmed.insert(insert_idx, first_human)

    return trimmed


def summarize_conversation(
    messages: list[BaseMessage],
    max_messages: int = 6,
    llm: Optional[ChatOpenAI] = None,
    summary_prefix: str = "[Previous conversation summary]",
) -> list[BaseMessage]:
    """Summarize older messages to manage context length.

    This function keeps recent messages intact while summarizing
    older parts of the conversation into a condensed summary.

    Args:
        messages: The list of messages to potentially summarize.
        max_messages: Keep this many recent messages without summarizing.
        llm: The LLM to use for summarization. Defaults to gpt-4o-mini.
        summary_prefix: Prefix for the summary message.

    Returns:
        List of messages with older content summarized.

    Example:
        >>> messages = [...long conversation...]
        >>> condensed = summarize_conversation(messages, max_messages=4)
    """
    if len(messages) <= max_messages:
        return messages

    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Separate system message if present
    system_msg = None
    content_messages = messages
    if messages and isinstance(messages[0], SystemMessage):
        system_msg = messages[0]
        content_messages = messages[1:]

    if len(content_messages) <= max_messages:
        return messages

    # Split into old and recent
    old_messages = content_messages[: -max_messages + 1]
    recent_messages = content_messages[-max_messages + 1:]

    # Create summary of old messages
    summary_prompt = f"""Summarize this conversation history in 2-3 sentences,
capturing the key topics discussed, any important decisions made, and user preferences revealed:

{chr(10).join([f'{type(m).__name__.replace("Message", "")}: {m.content[:300]}{"..." if len(m.content) > 300 else ""}' for m in old_messages])}"""

    summary_response = llm.invoke(summary_prompt)
    summary_text = f"{summary_prefix}: {summary_response.content}"

    # Reconstruct message list
    result = []
    if system_msg:
        result.append(system_msg)
    result.append(SystemMessage(content=summary_text))
    result.extend(recent_messages)

    return result


def extract_wellness_topics(
    message: str,
    llm: Optional[ChatOpenAI] = None,
) -> list[str]:
    """Extract wellness-related topics from a message.

    This function identifies which wellness domains (exercise, nutrition,
    sleep, stress, etc.) are relevant to a user's message.

    Args:
        message: The user's message.
        llm: The LLM to use for extraction. Defaults to gpt-4o-mini.

    Returns:
        List of relevant wellness topics.
    """
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""Analyze this message and identify which wellness topics it relates to.
Return only the topic names from this list, separated by commas:
exercise, nutrition, sleep, stress, hydration, habits, mental_health, general

Message: {message}

Topics:"""

    response = llm.invoke(prompt)
    topics = [t.strip().lower() for t in response.content.split(",")]

    valid_topics = {"exercise", "nutrition", "sleep", "stress", "hydration", "habits", "mental_health", "general"}
    return [t for t in topics if t in valid_topics]


def format_profile_for_context(profile: dict) -> str:
    """Format a user profile for inclusion in agent context.

    Args:
        profile: Dictionary containing profile data.

    Returns:
        Formatted string suitable for inclusion in prompts.
    """
    if not profile:
        return "No profile information available."

    sections = []
    for key, value in profile.items():
        if isinstance(value, dict):
            formatted = ", ".join([f"{k}: {v}" for k, v in value.items()])
            sections.append(f"- {key.replace('_', ' ').title()}: {formatted}")
        elif isinstance(value, list):
            sections.append(f"- {key.replace('_', ' ').title()}: {', '.join(str(v) for v in value)}")
        else:
            sections.append(f"- {key.replace('_', ' ').title()}: {value}")

    return "\n".join(sections)


def format_memory_context(
    profile: dict,
    relevant_facts: list,
    similar_episodes: list,
    instructions: str,
) -> str:
    """Format all memory types into a comprehensive context string.

    Args:
        profile: User's long-term profile data.
        relevant_facts: Semantically retrieved facts.
        similar_episodes: Episodic memories (past experiences).
        instructions: Procedural instructions.

    Returns:
        Formatted context string for the agent's system message.
    """
    context_parts = [instructions]

    # Add user profile
    if profile:
        profile_text = format_profile_for_context(profile)
        context_parts.append(f"\n=== USER PROFILE ===\n{profile_text}")

    # Add relevant facts
    if relevant_facts:
        facts_text = "\n".join([f"- {f.get('text', str(f))}" for f in relevant_facts])
        context_parts.append(f"\n=== RELEVANT KNOWLEDGE ===\n{facts_text}")

    # Add episodic examples
    if similar_episodes:
        examples = []
        for i, ep in enumerate(similar_episodes, 1):
            example = f"Example {i}:\n  User: {ep.get('input', 'N/A')}\n  Assistant: {ep.get('output', 'N/A')[:200]}..."
            examples.append(example)
        context_parts.append(f"\n=== SUCCESSFUL PAST INTERACTIONS ===\n" + "\n".join(examples))

    return "\n".join(context_parts)
