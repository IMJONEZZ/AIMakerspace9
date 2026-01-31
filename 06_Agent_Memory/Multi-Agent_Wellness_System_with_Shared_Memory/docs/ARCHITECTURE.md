# Multi-Agent Wellness System - Architecture Design

## Overview

This document describes the architecture of a multi-agent wellness system that demonstrates shared memory and cross-agent learning capabilities using LangGraph.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Router Agent                             │
│  (Routes requests based on user query and profile data)      │
└───────────────────────┬─────────────────────────────────────┘
                        │ Reads: (user_id, "profile")
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Exercise Agent│ │ Nutrition     │ │ Sleep Agent   │
│               │ │ Agent         │ │               │
│ Reads:        │ │ Reads:        │ │ Reads:        │
│ - Profile     │ │ - Profile     │ │ - Profile     │
│ - Episodes    │ │ - Episodes    │ │ - Episodes    │
│ - Knowledge   │ │ - Knowledge   │ │ - Knowledge   │
│ - Exercise    │ │ - Exercise    │ │               │
│   episodes    │ │   episodes    │ │               │
└───────────────┘ └───────────────┘ └───────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
              ┌─────────────────┐
              │ Unified Memory  │
              │     Store       │
              └─────────────────┘
```

## Memory Architecture

### Namespace Strategy

The system uses LangGraph's InMemoryStore with a carefully designed namespace hierarchy:

#### Shared Namespaces (Accessible by All Agents)

**1. User Profile Namespace**
- Pattern: `(user_id, "profile")`
- Purpose: Long-term user demographics, goals, conditions
- Example data:
  ```python
  store.put(("user_123", "profile"), "name", {"value": "Sarah"})
  store.put(("user_123", "profile"), "goals", {"primary": "lose weight"})
  store.put(("user_123", "profile"), "conditions", {"injuries": ["knee injury"]})
  ```

**2. Wellness Knowledge Namespace**
- Pattern: `("wellness", "knowledge")`
- Purpose: Semantic knowledge base for wellness information
- Stores chunks from HealthWellnessGuide.txt with embeddings
- Enables semantic search across all agents

#### Per-Agent Namespaces (Agent-Specific)

**3. Agent Instructions Namespace**
- Pattern: `(agent_name, "instructions")`
- Purpose: Procedural memory - stores agent's current instructions
- Allows self-improvement via instruction updates

**4. Agent Episodes Namespace**
- Pattern: `(agent_name, "episodes")`
- Purpose: Episodic memory - stores successful consultation examples
- Enables few-shot learning from past experiences

### Memory Access Patterns

#### Router Agent Access
```python
# Router reads user profile to understand context
profile = list(store.search((user_id, "profile")))
# Routes query based on user's goals and conditions
```

#### Specialist Agent Access
```python
# Each specialist reads:
1. User profile for personalization
2. Own episodes for few-shot learning
3. Shared wellness knowledge for facts
4. Other agents' episodes (cross-agent learning)
```

### Cross-Agent Learning

Agents can read and learn from each other's episodes:

**Example: Nutrition Agent Learning from Exercise Episodes**
```python
# Nutrition agent can access exercise episodes for injury-aware advice
exercise_episodes = list(store.search(("exercise_agent", "episodes")))
# Uses these to provide nutrition advice that accounts for physical limitations
```

## Memory Types Implemented

Based on the CoALA Framework:

### 1. Short-Term Memory
- **Implementation**: LangGraph checkpointer with thread_id
- **Scope**: Conversation history within a single session

### 2. Long-Term Memory
- **Implementation**: InMemoryStore with namespaces
- **Scope**: User profiles, preferences across sessions

### 3. Semantic Memory
- **Implementation**: Store with embeddings + semantic search
- **Scope**: Wellness knowledge base (HealthWellnessGuide.txt chunks)

### 4. Episodic Memory
- **Implementation**: Per-agent episode storage
- **Scope**: Successful consultation patterns

### 5. Procedural Memory
- **Implementation**: Agent instructions stored and updatable
- **Scope**: Self-improving behavior

## Data Flow Example

### User Query: "I want to lose weight but I have a knee injury"

```
1. Router receives query
   ↓ Reads (user_123, "profile")
   ↓ Detects: knee injury in conditions
   ↓ Routes to Exercise Agent (primary) + Nutrition Agent (secondary)

2. Exercise Agent responds
   ↓ Reads own episodes for injury-appropriate exercise advice
   ↓ Reads wellness knowledge for knee-friendly exercises
   ↓ Generates response with low-impact options

3. Episode stored
   ↓ Stores successful consultation in ("exercise_agent", "episodes")
   ↓ Future queries benefit from this pattern

4. Cross-agent learning
   ↓ Nutrition agent can access Exercise episodes
   ↓ When asked about diet, considers knee injury context
```

## Key Design Decisions

### 1. Shared vs. Private Namespaces
- **Shared**: Profile and knowledge (all agents need access)
- **Private**: Instructions and episodes (maintains agent identity)

### 2. Memory Granularity
- **Coarse-grained**: Profile (user-level)
- **Medium-grained**: Episodes (interaction-level)
- **Fine-grained**: Knowledge chunks (concept-level)

### 3. Cross-Agent Learning Strategy
- **Read-only access**: Agents can read others' episodes but only write their own
- **Semantic relevance**: Episodes retrieved based on query similarity

## Implementation Priorities

1. **Core Infrastructure** (06_Agent_Memory-6od)
   - InMemoryStore initialization
   - Namespace management utilities

2. **Router Agent** (06_Agent_Memory-5gu)
   - Profile reading
   - Query routing logic

3. **Specialist Agents** (06_Agent_Memory-8iq, 7q0, 40e)
   - Exercise Agent
   - Nutrition Agent
   - Sleep Agent

4. **Cross-Agent Learning** (06_Agent_Memory-7ox)
   - Episode sharing mechanism
   - Cross-agent episode reading

5. **Dashboard** (06_Agent_Memory-9i8)
   - Memory state visualization
   - Search interface

## Security & Privacy Considerations

- User profiles isolated by user_id in namespace
- No agent can modify another agent's private memory
- All memory access is logged for auditability

## Performance Considerations

- Semantic search limited to top-k results (k=3)
- Episode retrieval capped to prevent context overflow
- Profile data kept minimal to reduce store size

## Extension Points

1. **Bonus: Memory Conflict Resolution** (06_Agent_Memory-e30)
   - Detect and resolve conflicting information across agents

2. **Bonus: Memory Importance Scoring** (06_Agent_Memory-5fy)
   - Prioritize frequently accessed memories

3. **Bonus: Memory Cleanup Routine** (06_Agent_Memory-36f)
   - Remove stale or low-value memories

## References

- [CoALA Paper](https://arxiv.org/abs/2309.02427)
- [LangGraph Memory Documentation](https://docs.langchain.com/oss/python/langgraph/memory)
- [Multi-Agent Patterns in LangGraph](https://docs.langchain.com/oss/python/langgraph/multi-agent)