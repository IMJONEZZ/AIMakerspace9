# Multi-Agent Wellness System with Shared Memory

An advanced multi-agent wellness system built with LangGraph that demonstrates shared memory and cross-agent learning capabilities following the CoALA (Cognitive Architectures for Language Agents) framework.

## Features

- **Multi-Agent Architecture**: Three specialist agents (Exercise, Nutrition, Sleep) with unified memory
- **Shared Memory System**: LangGraph InMemoryStore with semantic search capabilities
- **Cross-Agent Learning**: Agents read and learn from each other's successful episodes
- **Memory Persistence**: Short-term (thread) and long-term (user profile, episodes) memory
- **Intelligent Routing**: Router agent selects appropriate specialist based on query and user context
- **Knowledge Base**: Semantic search across wellness documentation
- **Memory Dashboard**: Text-based interface for visualizing system memory state

## Architecture Overview

```
User Query
    │
    ▼
┌─────────────┐     Reads: (user_id, "profile")
│  Router     │
│   Agent     │
└──────┬──────┘
       │ Routes to:
   ┌───┼─────────┐
   ▼   ▼         ▼
┌──────┬─────┐ ┌─────────┐ ┌──────────┐
│Exerc │Nutr │ │  Sleep  │ │ Wellness │
│ Agent│Agent│ │  Agent  │ │Knowledge │
└──────┴─────┘ └─────────┘ └──────────┘
   │      │          │           │
   └──────┴──────────┴───────────┘
          ▼
   ┌─────────────┐
   │ Unified     │
   │ Memory Store│
   └─────────────┘
```

## Memory Architecture (CoALA Framework)

### Shared Namespaces (All Agents Access)
- `(user_id, "profile")` - Long-term user demographics, goals, conditions
- `("wellness", "knowledge")` - Semantic wellness knowledge base (HealthWellnessGuide.txt)

### Per-Agent Namespaces
- `(agent_name, "instructions")` - Procedural memory: Agent's current instructions
- `(agent_name, "episodes")` - Episodic memory: Successful consultation examples

### Memory Types Implemented
1. **Short-Term**: LangGraph checkpointer with thread_id (conversation history)
2. **Long-Term**: InMemoryStore with namespaces (user profiles, preferences)
3. **Semantic**: Store with embeddings + semantic search (wellness knowledge)
4. **Episodic**: Per-agent episode storage for few-shot learning
5. **Procedural**: Agent instructions stored and updatable

## Cross-Agent Learning Pattern

Agents can READ from all agents' episode namespaces but only WRITE to their own:
- ✅ Exercise agent reads: profile, knowledge, exercise episodes, nutrition episodes, sleep episodes
- ✅ Nutrition agent reads: profile, knowledge, own episodes, exercise episodes, sleep episodes
- ✅ Sleep agent reads: profile, knowledge, own episodes, exercise episodes, nutrition episodes

**Example**: Nutrition agent learns from Exercise agent's injury-aware recommendations to provide diet advice that accounts for physical limitations.

## Requirements

- Python 3.10+
- LangGraph
- LangChain (Core, OpenAI, Community)
- OpenAI-compatible LLM endpoint (uses local endpoint by default)

## Installation

```bash
# Using uv (recommended)
cd Multi-Agent_Wellness_System_with_Shared_Memory
uv sync

# Or using pip
pip install langgraph langchain-core langchain-openai langchain-community streamlit
```

## Quick Start

### Basic Usage

```python
from src import create_wellness_system

# Initialize the system (loads knowledge base)
system = create_wellness_system()

# Set up a user profile
system.set_user_profile(
    "user_123",
    {
        "name": "Alex",
        "age": 32,
        "goals": ["lose weight", "improve fitness"],
        "conditions": ["knee injury"]
    }
)

# Handle a query
result = system.handle_query(
    user_id="user_123",
    query="What exercises can I do with my knee injury?"
)

print(f"Agent: {result['agent_used']}")
print(f"Reasoning: {result['routing_reasoning']}")
print(f"Response: {result['response']}")

# Check system statistics
stats = system.get_system_stats()
print(f"Episodes stored: {sum(s['total'] for s in stats['episodes'].values())}")
```

### Memory Dashboard

Interactive text-based dashboard to explore memory state:

```bash
python dashboard.py
```

Features:
- View system statistics (memory, episodes, learning coverage)
- Browse user profiles
- Search knowledge base semantically
- View agent episodes (per-agent or cross-agent search)
- Interactive query mode with real-time routing

### Run Demo Script

```bash
python demo.py
```

Runs a simple demonstration with test queries and shows system statistics.

### Run Test Scenarios

```bash
python tests/test_scenarios.py
```

Comprehensive test suite demonstrating:
1. Weight loss with injury (cross-agent learning)
2. Comprehensive wellness journey
3. Cross-agent learning demonstration
4. Multiple users with different profiles
5. Memory persistence across sessions

## Project Structure

```
Multi-Agent_Wellness_System_with_Shared_Memory/
├── src/                          # Core implementation
│   ├── __init__.py
│   ├── memory_manager.py         # Shared memory infrastructure
│   ├── memory_namespaces.py      # Namespace strategy definition
│   ├── router.py                 # Router agent for query routing
│   ├── specialist_agents.py      # Exercise, Nutrition, Sleep agents
│   ├── cross_agent_learning.py   # Episode management & learning
│   └── wellness_system.py        # Main system integration
├── tests/                        # Test scenarios
│   └── test_scenarios.py         # Comprehensive test suite
├── data/                         # Data files
│   └── HealthWellnessGuide.txt   # Wellness knowledge base
├── docs/                         # Documentation
│   └── ARCHITECTURE.md           # Detailed system design
├── demo.py                       # Simple demo script
├── dashboard.py                  # Memory dashboard (CLI)
├── pyproject.toml                # Project configuration
└── README.md                     # This file
```

## Configuration

Environment variables (optional, uses defaults):

```bash
# LLM endpoint configuration
OPENAI_API_KEY=dummy-key-for-local-endpoint
OPENAI_BASE_URL=http://192.168.1.79:8080/v1/
OPENAI_MODEL=openai/gpt-oss-120b

# Langfuse tracing (optional)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=http://localhost:3000
```

## Key Components

### MemoryManager
Central memory management with InMemoryStore, semantic search, and namespace handling.

### RouterAgent
Routes queries to appropriate specialist agents based on user profile and query content.

### Specialist Agents (BaseSpecialistAgent)
- **ExerciseAgent**: Fitness, workouts, physical activity
- **NutritionAgent**: Diet, meal planning, healthy eating
- **SleepAgent**: Sleep quality, insomnia, rest

All agents:
- Read user profiles for personalization
- Access wellness knowledge base semantically
- Use own episodes for few-shot learning
- Read other agents' episodes (cross-agent learning)
- Store successful consultations as new episodes

### CrossAgentLearner
Enables knowledge transfer between agents through episode access.

## Examples

### Multi-Turn Conversation

```python
queries = [
    "I want to lose weight but I have a knee injury",
    "What should I eat?",
    "I'm not sleeping well"
]

responses = system.multi_turn_conversation("user_123", queries)
```

### Cross-Agent Learning Verification

```python
# Exercise agent handles injury-aware query
result1 = system.handle_query("user_123", "Knee-friendly exercises")

# Nutrition agent should know about the injury
result2 = system.handle_query("user_123", "Diet for weight loss")

# Verify nutrition agent considered the injury
if "injury" in result2['response'].lower():
    print("✅ Cross-agent learning successful!")
```

### Memory Inspection

```python
# Get user profile
profile = system.get_user_profile("user_123")

# Search knowledge base
results = system.memory.search_knowledge_base("knee pain", limit=3)

# Get agent episodes
episodes = system.memory.get_agent_episodes("exercise_agent", query="injury")

# Get cross-agent episodes
cross_ep = system.memory.get_cross_agent_episodes("asthma", limit_per_agent=2)
```

## Submitting the Advanced Build

### Required Deliverables
- ✅ Multi-agent implementation with shared memory
- ✅ Memory architecture diagram (see docs/ARCHITECTURE.md)
- ✅ Namespace strategy documentation
- ✅ Cross-agent learning demonstration (tests/test_scenarios.py)
- ✅ Memory dashboard (dashboard.py)

### For Submission
1. Loom video demonstration showing:
   - System initialization and knowledge base loading
   - Multi-turn conversation with injury-aware routing
   - Cross-agent learning (nutrition agent knowing about exercise context)
   - Memory dashboard showing episodes and statistics

2. GitHub URL to this repository

3. Screenshots of memory state at different points:
   - User profile with conditions
   - Agent episodes after queries
   - Cross-agent learning coverage

## Documentation

- **docs/ARCHITECTURE.md**: Detailed system design, memory architecture, data flows, and implementation priorities
- **src/memory_namespaces.py**: Namespace strategy with access control rules
- **tests/test_scenarios.py**: Comprehensive test scenarios demonstrating all features

## License

MIT