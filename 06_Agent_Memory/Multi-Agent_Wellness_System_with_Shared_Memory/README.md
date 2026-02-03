# Multi-Agent Wellness & Gaming System with Shared Memory

An advanced multi-agent system built with LangGraph that demonstrates shared memory and cross-agent learning capabilities following the CoALA (Cognitive Architectures for Language Agents) framework. Includes both wellness specialists and spoiler-free video game assistance agents.

## Features

### Wellness System
- **Multi-Agent Architecture**: Three specialist agents (Exercise, Nutrition, Sleep) with unified memory
- **Shared Memory System**: LangGraph InMemoryStore with semantic search capabilities
- **Cross-Agent Learning**: Agents read and learn from each other's successful episodes
- **Memory Persistence**: Short-term (thread) and long-term (user profile, episodes) memory
- **Intelligent Routing**: Router agent selects appropriate specialist based on query and user context
- **Knowledge Base**: Semantic search across wellness documentation
- **Memory Dashboard**: Text-based interface for visualizing system memory state

### Game Agent System (NEW)
- **Spoiler-Free Gaming**: Three specialist agents (Unlockables, Progression, Lore) with content filtering
- **Web Research Integration**: Game Story Research Agent fetches and processes game content from searxng
- **Progress Tracking**: Granular progress markers (intro/tutorial → early_game → mid_game → late_game → post_game)
- **Intelligent Game Routing**: Routes queries to appropriate specialists based on content analysis
- **QDrant Knowledge Base**: Vector-based storage with metadata-aware content filtering
- **Advanced Memory Features**: Conflict resolution, importance scoring, and cleanup routines

## Architecture Overview

### Wellness System
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

### Game Agent System
```
User Game Query
       │
       ▼
┌─────────────────┐     Web: searxng (192.168.1.36:4000)
│ Game Story      │◄─────────────────────────────────────┐
│ Research Agent  │                                      │
└───────┬─────────┘                                      │
        │ Stores in:                                      │
        ▼                                                 │
┌─────────────────┐    QDrant (localhost:6333)           │
│  Game Router    │◄─────────────────────────────────────┘
│    Agent        │    Routes to:
└───────┬─────────┘
        │ ┌─────────────┬─────────────┬─────────────┐
        ▼ ▼             ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Unlockables  │ │ Progression │ │    Lore     │ │ User Game   │
│   Agent     │ │   Agent     │ │   Agent     │ │ Progress    │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
        │               │               │               │
        └───────────────┴───────────────┴───────────────┘
                        ▼
               ┌─────────────────┐
               │ Advanced Memory │
               │ (QDrant + Episodic│
               │  + Conflict Res.)│
               └─────────────────┘
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

### Core Dependencies
- Python 3.10+
- LangGraph + LangChain ecosystem
- OpenAI-compatible LLM endpoint

### External Services Required
- **QDrant Vector Database**: `docker run -p 6333:6333 qdrant/qdrant`
- **Searxng Search Service**: http://192.168.1.36:4000 (web research for game content)
- **OpenAI API**: For LLM responses (or local endpoint)

### Installation

```bash
# Install all dependencies
pip install -r src/wellness_memory.egg-info/requires.txt

# Key packages include:
# - langchain>=1.0.0
# - langchain-openai>=0.3.0
# - qdrant-client>=1.16.2
# - langchain-qdrant>=1.1.0
# - python-dotenv>=1.0.1
# - tiktoken>=0.8.0
```

## Quick Start

### Step 1: Start Required Services

```bash
# Start QDrant Vector Database
docker run -p 6333:6333 qdrant/qdrant

# Ensure Searxng is accessible at http://192.168.1.36:4000
# (This should already be running on your network)
```

### Step 2: Environment Setup

Create `.env` file in project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_key_here
OPENAI_BASE_URL=https://api.openai.com/v1/  # Or local endpoint

# QDrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Leave empty if no authentication

# Web Search Configuration
SEARXNG_URL=http://192.168.1.36:4000

# Optional: Langfuse Tracing
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=http://localhost:3000
```

### Step 3: Run Demo (Mock Mode)

```bash
# Game Agent System Demo (no API calls)
python demo_game_agent.py --game "The Legend of Zelda" --verbose

# Wellness System Demo
python demo.py
```

### Step 4: Run Real System

```bash
# Game Agent with real LLM calls
python -c "
from src.game_router import GameRouterAgent
from src.game_input_flow import GameInputFlow
router = GameRouterAgent(GameInputFlow())
result = router.route_query('user123', 'how do I beat the first boss?')
print(result)
"

# Wellness System with real memory
python -c "
from src import create_wellness_system
system = create_wellness_system()
result = system.handle_query('user123', 'What exercises can I do with a knee injury?')
print(result)
"
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

### System Demos

#### Game Agent System
```bash
# Full system demo with all components
python demo_game_agent.py --game "Elden Ring" --verbose

# Run integration tests
python test_video_game_agent_integration.py

# Test advanced memory features
python test_memory_conflict_resolution.py
python test_memory_importance_scoring.py
python test_memory_cleanup.py
```

#### Wellness System
```bash
# Basic wellness demo
python demo.py

# Comprehensive test scenarios
python tests/test_scenarios.py
```

### Test Coverage

#### Game Agent Tests
- **System Integration**: All components working together
- **Memory Conflict Resolution**: Similarity detection and importance-based merging
- **Memory Importance Scoring**: Automatic and manual importance calculation
- **Memory Cleanup**: Configurable cleanup by importance, age, and limits
- **Spoiler Filtering**: Content filtering across progress levels
- **Routing Intelligence**: Query routing to appropriate specialists

#### Wellness Tests
1. Weight loss with injury (cross-agent learning)
2. Comprehensive wellness journey
3. Cross-agent learning demonstration
4. Multiple users with different profiles
5. Memory persistence across sessions

## Project Structure

```
Multi-Agent_Wellness_System_with_Shared_Memory/
├── src/                          # Core implementation
│   ├── wellness_memory/          # Wellness system components
│   │   ├── memory_types.py       # Advanced memory with conflict resolution
│   │   ├── utils.py             # Token counting and utilities
│   │   └── ...                  # Other wellness components
│   ├── memory_manager.py         # Shared memory infrastructure
│   ├── memory_namespaces.py      # Namespace strategy definition
│   ├── router.py                 # Router agent for query routing
│   ├── specialist_agents.py      # Exercise, Nutrition, Sleep agents
│   ├── cross_agent_learning.py   # Episode management & learning
│   ├── wellness_system.py        # Main wellness system integration
│   ├── game_router.py           # Game query routing agent
│   ├── game_specialist_agents.py # Unlockables, Progression, Lore agents
│   ├── game_story_research_agent.py # Web research integration
│   ├── user_game_progress.py     # User progress tracking
│   ├── game_input_flow.py       # Game selection flow
│   ├── game_knowledge_base.py    # QDrant knowledge storage
│   ├── game_tracker.py           # Game processing tracking
│   └── tools/                    # Tool integrations
│       └── webfetch.py           # Web fetching utilities
├── tests/                        # Test scenarios
│   ├── test_scenarios.py         # Wellness system tests
│   ├── test_video_game_agent_integration.py # Game system integration
│   ├── test_memory_conflict_resolution.py  # Memory conflict handling
│   ├── test_memory_importance_scoring.py  # Importance scoring
│   └── test_memory_cleanup.py    # Memory cleanup routines
├── data/                         # Data files
│   └── HealthWellnessGuide.txt   # Wellness knowledge base
├── docs/                         # Documentation
│   └── ARCHITECTURE.md           # Detailed system design
├── demo.py                       # Wellness demo script
├── demo_game_agent.py           # Game agent demo script
├── dashboard.py                  # Memory dashboard (CLI)
├── src/wellness_memory.egg-info/ # Package metadata and dependencies
├── requirements.txt              # Dependencies (if created)
├── pyproject.toml                # Project configuration
└── README.md                     # This file
```

## Configuration

### Service Endpoints

**Required Services Configuration**:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1/  # Or local endpoint

# QDrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Leave empty if no authentication required

# Web Search Service (Game Research)
SEARXNG_URL=http://192.168.1.36:4000
```

**Optional Services**:
```bash
# Langfuse Tracing (for monitoring)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=http://localhost:3000
```

### Docker Services Required

#### QDrant Vector Database
```bash
# Start QDrant for game knowledge storage
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

#### Searxng Search Service
- **URL**: http://192.168.1.36:4000
- **Purpose**: Game content research and web fetching
- **Status**: Should be running on network (external service)

### Model Configuration

**Wellness System Default**:
- **LLM Model**: `gpt-3.5-turbo` (via OpenAI API)
- **Embedding Model**: `text-embedding-ada-002` (via OpenAI API)

**Game System Default**:
- **LLM Model**: `gpt-4` (via OpenAI API)
- **Vector Storage**: QDrant with custom embeddings

Note: The system automatically handles API key management for local endpoints. For production OpenAI usage, provide valid API keys.

## Key Components

### Wellness System Components

#### MemoryManager
Central memory management with InMemoryStore, semantic search, and namespace handling.

#### RouterAgent
Routes queries to appropriate specialist agents based on user profile and query content.

#### Specialist Agents (BaseSpecialistAgent)
- **ExerciseAgent**: Fitness, workouts, physical activity
- **NutritionAgent**: Diet, meal planning, healthy eating
- **SleepAgent**: Sleep quality, insomnia, rest

All wellness agents:
- Read user profiles for personalization
- Access wellness knowledge base semantically
- Use own episodes for few-shot learning
- Read other agents' episodes (cross-agent learning)
- Store successful consultations as new episodes

#### CrossAgentLearner
Enables knowledge transfer between wellness agents through episode access.

### Game System Components

#### GameStoryResearchAgent
- Fetches game information from web search (searxng)
- Processes and chunks content for storage
- Integrates with QDrant for semantic search

#### GameRouterAgent
- Routes game queries to appropriate specialists
- Analyzes query content for intelligent routing
- Handles user game selection and context

#### Game Specialist Agents
- **UnlockablesAgent**: Secrets, achievements, hidden content
- **ProgressionAgent**: Walkthroughs, level guidance, story progression
- **LoreAgent**: Story background, world-building, game history

#### UserGameProgress
- Tracks player progress across game stages
- Provides spoiler-aware content filtering
- Supports progress transitions

#### Advanced Memory Features
- **Conflict Resolution**: Similarity-based duplicate detection
- **Importance Scoring**: Automatic importance calculation
- **Cleanup Routines**: Configurable memory maintenance

### Shared Infrastructure
- **QDrant Integration**: Vector-based knowledge storage for game content
- **WebFetch Integration**: Real-time game research from web sources
- **Memory Types**: Unified episodic and semantic memory across both systems

## Examples

### Wellness System Examples

#### Multi-Turn Conversation

```python
queries = [
    "I want to lose weight but I have a knee injury",
    "What should I eat?",
    "I'm not sleeping well"
]

responses = system.multi_turn_conversation("user_123", queries)
```

#### Cross-Agent Learning Verification

```python
# Exercise agent handles injury-aware query
result1 = system.handle_query("user_123", "Knee-friendly exercises")

# Nutrition agent should know about the injury
result2 = system.handle_query("user_123", "Diet for weight loss")

# Verify nutrition agent considered the injury
if "injury" in result2['response'].lower():
    print("✅ Cross-agent learning successful!")
```

#### Memory Inspection

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

### Game System Examples

#### Basic Game Query Processing

```python
from src.game_router import GameRouterAgent
from src.game_input_flow import GameInputFlow

# Initialize game system
router = GameRouterAgent(GameInputFlow())

# Handle user query
result = router.route_query("user123", "how do I find the master sword?")
print(f"Routed to: {result.agent}")
print(f"Reasoning: {result.reasoning}")
```

#### Game Research and Knowledge Storage

```python
from src.game_story_research_agent import GameStoryResearchAgent
from qdrant_client import QdrantClient

# Initialize research agent
qdrant_client = QdrantClient(url="http://localhost:6333")
researcher = GameStoryResearchAgent(qdrant_client)

# Research a game
result = researcher.research_game("The Legend of Zelda")
print(f"Status: {result['status']}")
print(f"Chunks stored: {result['chunks_stored']}")
```

#### Progress-Aware Content Filtering

```python
from src.user_game_progress import UserGameProgress
from src.game_specialist_agents import UnlockablesAgent

# Track user progress
progress = UserGameProgress()
progress.set_progress("user123", "mid_game")

# Get spoiler-filtered help
agent = UnlockablesAgent(...)
response, success = agent.handle_query("user123", "secret items")
# Response will be filtered for mid_game progress (no late/post game spoilers)
```

#### Advanced Memory Management

```python
from src.wellness_memory.memory_types import EpisodicMemory

# Initialize advanced memory
memory = EpisodicMemory(store)

# Store with automatic importance scoring
memory.store_episode(
    key="boss_help",
    situation="Help with final boss",
    input_text="how to defeat final boss",
    output_text="Complete boss strategy...",
    feedback="This saved my run!",
    importance=0.9  # High importance
)

# Check for conflicts
conflicts = memory.find_similar("new_episode", threshold=0.85)

# Cleanup old episodes
cleanup_result = memory.cleanup_episodes(
    importance_threshold=0.3,
    dry_run=False
)
```

## Production Deployment

### Required Services Checklist

Before running the full system in production, ensure these services are running:

#### ✅ External Services
- [ ] **QDrant Vector Database**: `docker run -p 6333:6333 qdrant/qdrant`
- [ ] **Searxng Search**: Accessible at `http://192.168.1.36:4000`
- [ ] **OpenAI API**: Valid API key configured

#### ✅ Environment Configuration
- [ ] **.env file** created with all required variables
- [ ] **Dependencies installed** via requirements
- [ ] **Service health checks** passed

### Complete System Demo

```bash
# Step 1: Start all services
docker run -d -p 6333:6333 qdrant/qdrant
# Verify searxng at http://192.168.1.36:4000

# Step 2: Run complete game agent demo
python demo_game_agent.py --game "Elden Ring" --verbose

# Step 3: Test wellness system integration
python demo.py

# Step 4: Run memory dashboard
python dashboard.py

# Step 5: Verify with integration tests
python test_video_game_agent_integration.py
python tests/test_scenarios.py
```

### System Monitoring

#### Memory Statistics
```python
# Game system memory stats
from src.wellness_memory.memory_types import EpisodicMemory
memory = EpisodicMemory(store)
stats = memory.get_cleanup_statistics()
print(f"Total episodes: {stats['total_episodes']}")
print(f"Average importance: {stats['average_importance']:.2f}")

# Wellness system stats
stats = system.get_system_stats()
print(f"Cross-agent learning coverage: {stats['learning_coverage']}")
```

#### Service Health
```bash
# Check QDrant
curl http://localhost:6333/collections

# Check searxng
curl http://192.168.1.36:4000/search?q=test

# Test OpenAI API
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

## Submitting the Advanced Build

### Required Deliverables
- ✅ Multi-agent wellness implementation with shared memory
- ✅ Game agent system with spoiler filtering and web research
- ✅ Advanced memory features (conflict resolution, importance scoring, cleanup)
- ✅ Memory architecture diagram (see docs/ARCHITECTURE.md)
- ✅ Complete system documentation and setup guide
- ✅ Integration tests for both systems
- ✅ Memory dashboard and demo scripts

### For Submission
1. **Video demonstration** showing:
   - Both wellness and game systems working
   - Game content research from web
   - Spoiler-aware content filtering
   - Cross-agent learning in wellness system
   - Advanced memory management features

2. **GitHub URL** to this repository

3. **Screenshots/Documentation**:
   - Service configuration and health checks
   - Memory state across both systems
   - Cross-agent learning examples
   - Game agent routing and spoiler filtering

4. **Performance Benchmarks**:
   - Memory cleanup effectiveness
   - Cross-agent learning coverage
   - Game content retrieval accuracy
   - System response times

## Documentation

- **docs/ARCHITECTURE.md**: Detailed system design, memory architecture, data flows, and implementation priorities
- **src/memory_namespaces.py**: Namespace strategy with access control rules
- **tests/test_scenarios.py**: Comprehensive test scenarios demonstrating all features

## License

MIT