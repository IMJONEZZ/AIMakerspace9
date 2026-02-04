# Spoiler-Free Video Game Research Agent System

An advanced multi-agent system that provides intelligent gaming assistance with spoiler-aware content filtering. Built with LangGraph and vector-based knowledge storage, this system routes queries to specialist agents while respecting user progress and spoiler preferences.

## Features

- **Spoiler-Aware Gaming**: Three specialist agents (Gameplay, Lore, Progression) with intelligent content filtering
- **Web Research Integration**: Real-time game content research from search engines
- **Progress Tracking**: User-defined progress levels with granular spoiler filtering
- **Intelligent Routing**: LLM-powered query routing to appropriate specialist agents
- **Vector Knowledge Base**: QDrant-powered semantic search across game content
- **Advanced Memory**: Structured memory system with working, session, and semantic layers
- **Context Compression**: Progressive context optimization for optimal LLM performance

## Architecture

```
User Game Query
       │
       ▼
┌─────────────────┐     Web: searxng (localhost:4000)
│ Game Router      │◄─────────────────────────────────────┐
│    Agent        │                                      │
└───────┬─────────┘                                      │
        │ Routes to:                                      │
    ┌───┼─────────┐                                     │
    ▼   ▼         ▼                                     │
┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│ Gameplay    │ │    Lore     │ │ Progression │          │
│   Agent     │ │   Agent     │ │   Agent     │          │
└─────────────┘ └─────────────┘ └─────────────┘          │
        │               │               │                  │
        └───────────────┴───────────────┴───────────┘
                        ▼
               ┌─────────────────┐
               │ Advanced Memory │
               │ (QDrant +      │
               │  Multi-layer)  │
               └─────────────────┘
```

## Requirements

### System Requirements
- Python 3.10+
- Docker and Docker Compose
- 8GB+ RAM recommended
- Internet connection for web search

### Required Services
- **QDrant Vector Database**: For knowledge storage and semantic search
- **Searxng Search Service**: For web research (already running at localhost:4000)
- **OpenAI-Compatible LLM**: Local LLM server or OpenAI API

## Quick Start

### Step 1: Start Required Services

#### QDrant Vector Database
```bash
# Start QDrant with persistent storage
docker run -d \
  --name qdrant \
  --restart unless-stopped \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Verify QDrant is running
curl http://localhost:6333/collections
```

#### Searxng Search Service
The system expects searxng running at `http://localhost:4000`. If this isn't available, update the URL in the game system configuration.

#### OpenAI-Compatible LLM Server
The system is configured for a local LLM server at `http://localhost:8080/v1`. To use a different endpoint:

```bash
# Option 1: Use OpenAI API (set your key)
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_BASE_URL="https://api.openai.com/v1"

# Option 2: Use local LLM server
# Update the URLs in run_real_game_system.py:
# - base_url="http://your-server:8080/v1"
# - model="your-model-name"
```

### Step 2: Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd Multi-Agent_Spoiler-Free_Video_Game_Research_Agent

# Install Python dependencies
pip install -r requirements.txt

# Key dependencies if manual installation:
pip install langchain>=0.1.0 langchain-openai>=0.1.0
pip install qdrant-client>=1.7.0
pip install langchain-core>=0.1.0
pip install httpx>=0.25.0
pip install tiktoken>=0.5.0
pip install python-dotenv>=1.0.0
```

### Step 3: Verify Services

```bash
# Test QDrant
curl http://localhost:6333/collections

# Test Searxng
curl "http://localhost:4000/search?q=test&format=json"

# Test LLM endpoint (adjust if needed)
curl -H "Content-Type: application/json" \
     -d '{"model":"test","messages":[{"role":"user","content":"test"}]}' \
     http://localhost:8080/v1/chat/completions
```

### Step 4: Run the Game System

```bash
# Run with verbose output to see reasoning process
python run_real_game_system.py --verbose

# Run without verbose for normal operation
python run_real_game_system.py
```

## Usage

### First-Time Setup
When you first run the system, it will:
1. Test all required services
2. Prompt for username (creates user profile)
3. Ask for gaming preferences (genres, playstyle, spoiler sensitivity)
4. Prompt for game selection

### Sample Session
```bash
$ python run_real_game_system.py --verbose

============================================================
INITIALIZING REAL GAME SYSTEM
============================================================
SUCCESS: QDrant connected with 2 collections
SUCCESS: LLM test passed - LLM test successful...
SUCCESS: Web search test passed - 10 results
SUCCESS: Structured memory system initialized
SUCCESS: Tokenizer initialized for context management
SUCCESS: All components initialized and tested

============================================================
USER IDENTIFICATION
============================================================
What is your username? alice
Welcome, alice! Creating your profile...

Let's set up your gaming profile:
What are your favorite game genres? (comma-separated): RPG, Adventure
What are your preferred playstyles? (e.g., casual, hardcore, completionist): casual, exploration
Spoiler sensitivity (low/medium/high): medium

============================================================
GAME SELECTION
============================================================
Which game would you like to ask about? The Legend of Zelda: Tears of the Kingdom
Selected game: The Legend of Zelda: Tears of the Kingdom

============================================================
PROCESSING QUERY: how do I get to the sky islands?
============================================================
[THINKING] Routing query: 'how do I get to the sky islands?'
[ROUTING] Query routed to: progression agent
[SEARCHING] Searching for: 'Tears of the Kingdom sky islands guide'
[WEB SEARCH QUERY] Tears of the Kingdom sky islands how to reach guide
[WEB SEARCH] Found 5 web results
  1. Zelda Tears of the Kingdom Sky Islands guide...
  2. How to reach Sky Islands TotK complete walkthrough...

[SYNTHESIZING] Creating response for progression query
[CONTEXT COMPRESSION] No compression needed
[RESPONSE] To reach the Sky Islands in Tears of the Kingdom, you'll need to use...
```

### Advanced Features

#### Spoiler Sensitivity Override
Control spoiler level per query:

```bash
# Show all spoilers
"how do I defeat Ganon? --spoiler=none"

# Medium filtering
"what temples should I visit? --spoiler:medium"

# High filtering (no spoilers)
"[high] what abilities do I get?"
```

#### Memory System
The system maintains:
- **Working Memory**: Recent 5 conversations
- **Session Memory**: Summarized key points from current session  
- **Semantic Memory**: Vector-stored facts for future retrieval
- **User Profiles**: Preferences and gaming history

#### Context Optimization
Automatic context compression when content exceeds token limits, preserving most important information.

## Configuration

### Service Endpoints

Edit `run_real_game_system.py` to customize service URLs:

```python
# QDrant Configuration
self.qdrant_client = QdrantClient(host="localhost", port=6333)

# LLM Configuration  
self.llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    base_url="http://localhost:8080/v1",
    api_key="not-needed-for-local-server",
    temperature=0.1,
)

# Web Search Configuration
SEARCH_URL = "http://localhost:4000/search"
```

### Environment Variables

Create `.env` file (optional):

```bash
# OpenAI API (if not using local server)
OPENAI_API_KEY=your_openai_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Custom endpoints
QDRANT_URL=http://localhost:6333
SEARXNG_URL=http://localhost:4000
LLM_BASE_URL=http://localhost:8080/v1
```

## Troubleshooting

### Common Issues

#### QDrant Connection Failed
```bash
# Check if QDrant is running
docker ps | grep qdrant

# Restart QDrant
docker restart qdrant

# Check logs
docker logs qdrant
```

#### LLM Connection Failed
```bash
# Test your LLM endpoint
curl -H "Content-Type: application/json" \
     -d '{"model":"test","messages":[{"role":"user","content":"test"}]}' \
     http://localhost:8080/v1/chat/completions

# If using local server, check if it's running
# Common local servers:
# - Ollama: http://localhost:11434
# - LM Studio: http://localhost:1234
# - Text Generation WebUI: http://localhost:5000
```

#### Web Search Failed
```bash
# Test searxng endpoint
curl "http://localhost:4000/search?q=test&format=json"

# If unavailable, try public alternatives:
# https://searxng.org
# https://search.brave.com
```

### Debug Mode

Run with `--verbose` flag to see:
- Query routing decisions
- Search queries used
- Context compression details
- LLM reasoning process
- Spoiler filtering steps

```bash
python run_real_game_system.py --verbose
```

### Performance Optimization

#### Reduce Memory Usage
- Reduce `working_memory_limit` in `StructuredMemorySystem`
- Lower context window size in `compress_context_pyramid`
- Use smaller embedding models

#### Improve Response Speed
- Use faster LLM models
- Reduce search result count
- Disable verbose mode in production

## Development

### Project Structure
```
Multi-Agent_Spoiler-Free_Video_Game_Research_Agent/
├── run_real_game_system.py    # Main entry point
├── src/                       # Core system components
│   ├── game_router.py           # Query routing logic
│   ├── game_specialist_agents.py # Specialist agents
│   ├── user_game_progress.py    # Progress tracking
│   ├── game_knowledge_base.py   # QDrant integration
│   └── tools/                   # Utility functions
├── demo_game_agent.py         # Demo script
├── test_*.py                  # Test files
└── README.md                  # This file
```

### Adding New Game Specialists
1. Create new agent class in `game_specialist_agents.py`
2. Update routing logic in `GameRouterAgent`
3. Add agent type to routing prompt
4. Test integration

### Customizing Spoiler Rules
Modify `filter_spoilers()` method in `GameSystem` class to implement custom filtering logic.

## License

MIT License