# Developer Documentation

## Getting Started

Welcome to the AI Life Coach developer documentation. This comprehensive guide will help you understand, extend, and maintain our multi-agent life coaching system.

## Quick Start

### Prerequisites
- Python 3.9+
- OpenAI-compatible LLM endpoint (we use GLM-4.7)
- Git for version control

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai_life_coach
```

2. **Set up virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
# OR with uv (recommended)
pip install uv
uv pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API endpoint and keys
```

5. **Initialize workspace**
```bash
mkdir -p workspace/{user_profile,assessments,plans,progress,resources}
```

### Basic Usage

```python
from src.main import create_life_coach

# Create the AI Life Coach
coach = create_life_coach()

# Start a coaching session
result = coach.invoke({
    "messages": [{
        "role": "user",
        "content": "I need help with my career development"
    }]
})

print(result["messages"][-1].content)
```

## Architecture Overview

The AI Life Coach is built on the **Deep Agents** pattern, combining:

- **4 Domain Specialists**: Career, Relationships, Finance, Wellness
- **Central Coordinator**: Orchestrates specialists and integrates insights
- **Memory System**: LangGraph Store for persistent user data
- **Context Management**: Filesystem backend for documents and plans
- **Planning System**: Phase-based goal tracking with dependencies

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│                  (CLI or Web Interface)                      │
└────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              LIFE COACH COORDINATOR                         │
│          (Main Agent - LLM Model)                           │
├─────────────────────────────────────────────────────────────┤
│  Responsibilities:                                           │
│  • Multi-domain assessment & prioritization                 │
│  • Phase-based planning (discovery → execution)            │
│  • Subagent coordination & delegation                      │
│  • Cross-domain insight synthesis                           │
└───────┬─────────┬───────────────┬─────────────┬──────────────┘
        │         │               │             │
        ▼         ▼               ▼             ▼
┌───────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   CAREER  │ │ RELATIONSHIP │ │ FINANCE  │ │  WELLNESS    │
│  SPECIAL- │ │   SPECIALIST  │ │SPECIAL-  │ │  SPECIALIST  │
│    IST    │ └──────────────┘ │   IST    │ └──────────────┘
└───────────┘                  └──────────┘
    │                              │             │
    ◄─────── SPECIALIST TOOLS ───────────────────┘

                ▼
┌─────────────────────────────────────┐
│        INTEGRATED PLAN              │
│  • Unified recommendations          │
│  • Cross-domain connections         │
│  • Prioritized action items         │
└─────────────────────────────────────┘
```

## Core Components

### 1. Coordinator Agent

**File**: `src/agents/coordinator.py`

The coordinator is the central intelligence that:
- Analyzes user requests across all life domains
- Determines when to delegate to specialists
- Integrates specialist outputs into cohesive guidance
- Manages multi-user sessions with proper authentication

**Key Responsibilities**:
- Request analysis and domain identification
- Subagent coordination (parallel/sequential)
- Cross-domain conflict resolution
- Priority-based task management
- Emergency protocol activation

### 2. Domain Specialists

Each specialist has:
- Domain-specific system prompt
- Curated tool set for their expertise
- Access to shared memory and context tools
- Ability to identify cross-domain implications

#### Career Specialist
- **File**: `src/agents/specialists.py` (get_career_specialist)
- **Tools**: Skill gap analysis, career path planning, resume optimization
- **Expertise**: Professional development, job search strategy, market research

#### Relationship Specialist  
- **File**: `src/agents/specialists.py` (get_relationship_specialist)
- **Tools**: Communication analysis, boundary setting, conflict resolution
- **Expertise**: Interpersonal relationships, social skills, emotional intelligence

#### Finance Specialist
- **File**: `src/agents/specialists.py` (get_finance_specialist)  
- **Tools**: Budget analysis, financial planning, debt payoff strategies
- **Expertise**: Personal finance, investment basics, financial wellness

#### Wellness Specialist
- **File**: `src/agents/specialists.py` (get_wellness_specialist)
- **Tools**: Health assessment, habit formation, stress management
- **Expertise**: Physical health, mental wellness, work-life balance

### 3. Memory System

**File**: `src/memory.py`

Uses LangGraph's InMemoryStore with organized namespaces:

```python
# Namespace structure
(user_id, "profile")      # Demographics, values, life situation
(user_id, "goals")        # Short, medium, long-term goals
(user_id, "progress")     # Milestones, setbacks, achievements
(user_id, "preferences")  # Communication style, coaching approach
("coaching", "patterns")  # Cross-user learned patterns (anonymized)
```

### 4. Context Management

**File**: `src/tools/context_tools.py`

FilesystemBackend manages persistent documents:

```
workspace/
├── user_profile/{user_id}/     # Profile data and preferences
├── assessments/{user_id}/       # Assessment results and reports  
├── plans/{user_id}/            # Action plans and goal documents
├── progress/{user_id}/          # Weekly progress tracking
└── resources/                  # Curated articles and tools
```

## Tool System

### Tool Categories

1. **Memory Tools** (`src/tools/memory_tools.py`)
   - `get_user_profile()` - Retrieve user background and goals
   - `save_user_preference()` - Store user communication preferences
   - `update_milestone()` - Track achievements and progress
   - `get_progress_history()` - Review past sessions and patterns

2. **Planning Tools** (`src/tools/planning_tools.py`)
   - `write_todos()` - Create structured task lists with phases
   - `update_todo()` - Update task status and add notes
   - `list_todos()` - Review progress and dependencies

3. **Context Tools** (`src/tools/context_tools.py`)
   - `save_assessment()` - Document user assessments
   - `get_active_plan()` - Retrieve current plans
   - `save_weekly_progress()` - Track progress over time
   - `save_curated_resource()` - Save helpful resources

4. **Domain-Specific Tools**
   - Career: `src/tools/career_tools.py`
   - Relationship: `src/tools/relationship_tools.py`
   - Finance: `src/tools/finance_tools.py`
   - Wellness: `src/tools/wellness_tools.py`

### Creating New Tools

All tools follow this pattern:

```python
from langchain_core.tools import tool
from typing import Any, Dict, List, Optional

@tool
def my_new_tool(param1: str, param2: Optional[int] = None) -> str:
    """
    Tool description for the agent.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (optional)
    
    Returns:
        Description of what the tool returns
        
    Example:
        >>> result = my_new_tool("hello", 42)
        >>> print(result)
    """
    try:
        # Your tool logic here
        return "Success message"
    except Exception as e:
        return f"Error: {str(e)}"
```

**Best Practices**:
- Always include type hints
- Provide clear docstrings with Args and Returns
- Handle errors gracefully with try/catch
- Return user-friendly messages
- Include validation for inputs

## Subagent Development

### Subagent Configuration Template

```python
def get_my_specialist(tools: List[Any] = None) -> dict:
    """
    Get my domain specialist configuration.
    
    Args:
        tools: List of tools available to this specialist
        
    Returns:
        dict: Specialist configuration
    """
    return {
        "name": "my-specialist",
        "description": "Expert in my domain with deep knowledge of...",
        "system_prompt": """
# My Domain Specialist

## Your Role
Expert in [domain] with deep knowledge of...

## Core Competencies
- ...

## Workflow
1. Analyze the user's [domain] situation
2. Identify key challenges and opportunities  
3. Generate specific, actionable recommendations
4. Provide resources for implementation

## Important
- Always consider cross-domain impacts
- Note any synergies or conflicts with other life areas
- Provide concrete next steps, not just general advice
        """,
        "tools": tools or [],
        "model": "openai:glm-4.7"
    }
```

### Adding New Specialists

1. **Create specialist function** in `src/agents/specialists.py`
2. **Design system prompt** following the template above
3. **Allocate appropriate tools** from shared pools
4. **Update main coordinator** in `src/main.py` to include new specialist
5. **Update coordinator prompt** to know when to delegate
6. **Test specialist** independently before integration

## Planning and Dependencies

### Phase-Based Planning

The system uses 4 phases:

1. **Discovery**: Assessment and goal identification
2. **Planning**: Action plan creation with dependencies  
3. **Execution**: Task implementation and tracking
4. **Review**: Progress evaluation and adaptation

### Goal Dependencies

Goals can have these relationships:

| Type | Description | Example |
|------|-------------|---------|
| **Enables** | Goal A makes Goal B possible | "Get promotion" → "Buy house" |
| **Requires** | Goal A needs Goal B to succeed | "Run marathon" → "6 months training" |
| **Conflicts** | Goals compete for resources | "Work 60h/week" ↔ "Family time" |
| **Supports** | Goal A helps but doesn't require Goal B | "Exercise" → "Better sleep" |

### Todo Structure

```python
todos = [
    {
        "id": "unique_task_id",
        "title": "Task description",
        "phase": "discovery|planning|execution|review",
        "status": "pending|in_progress|completed",
        "depends_on": ["task_id1", "task_id2"],
        "domain": "career|relationship|finance|wellness",
        "priority": 1-5,
        "due_date": "YYYY-MM-DD" (optional)
    }
]
```

## Memory Management

### Best Practices

1. **Use appropriate namespaces** for data isolation
2. **Include user_id in all user-specific operations**
3. **Store structured data** as JSON for consistency
4. **Use semantic search** for pattern discovery
5. **Clean up old data** to maintain performance

### Memory Operations

```python
# Write to memory
store.put((user_id, "profile"), "demographics", {"name": "Alex", "age": 35})

# Read from memory  
items = list(store.search((user_id, "profile")))

# Semantic search (if vector store added)
items = list(store.search(("coaching", "patterns"), query="procrastination"))
```

## Configuration

### Environment Variables

```bash
# .env file
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=http://192.168.1.79:8080/v1
MODEL_NAME=glm-4.7
WORKSPACE_PATH=./workspace
LOG_LEVEL=INFO
```

### Model Configuration

The system uses OpenAI-compatible endpoints. Update `src/config.py`:

```python
def get_model_config() -> dict:
    return {
        "model": os.getenv("MODEL_NAME", "glm-4.7"),
        "model_provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
        "temperature": 0.7,
        "max_tokens": 2000
    }
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_career_tools.py

# Run with coverage
pytest --cov=src tests/
```

### Test Structure

```
tests/
├── test_career_tools.py      # Tool functionality tests
├── test_agents.py            # Agent behavior tests  
├── test_memory.py            # Memory operations tests
├── test_integration.py       # End-to-end scenarios
└── fixtures/                # Test data and scenarios
```

### Writing Tests

```python
import pytest
from src.tools.career_tools import analyze_skill_gap

def test_analyze_skill_gap_basic():
    """Test basic skill gap analysis functionality."""
    result = analyze_skill_gap(
        current_skills=["Python", "SQL"],
        target_role="Data Scientist"
    )
    
    assert isinstance(result, str)
    assert "missing skills" in result.lower() or "all skills covered" in result.lower()
```

## Performance Optimization

### Optimization Targets

- **Response Time**: < 30 seconds for simple queries, < 2 minutes for complex multi-domain requests
- **Parallelization**: Specialists work in parallel when possible  
- **Caching**: Frequently accessed data cached to reduce memory calls
- **Context Management**: Offload large documents to filesystem

### Bottleneck Prevention

1. **Tool Calls**: Batch related operations; avoid redundant calls
2. **Memory Access**: Use efficient namespace organization; minimize search scope
3. **Subagent Coordination**: Limit back-and-forth between coordinator and specialists
4. **File Operations**: Minimize I/O; aggregate writes where possible

## Extension Guidelines

### Adding New Domains

1. **Create specialist configuration** in `src/agents/specialists.py`
2. **Implement domain-specific tools** in `src/tools/your_tools.py`
3. **Add to coordinator's subagent list** in `src/main.py`
4. **Update assessment workflow** if needed
5. **Create comprehensive tests**

### Adding New Features

1. **Plan the feature** with use cases and acceptance criteria
2. **Design the architecture** considering existing patterns
3. **Implement incrementally** with tests at each step
4. **Update documentation** as you build
5. **Test integration** with existing system

### Code Style

- Follow PEP 8 for Python code
- Use type hints for all functions
- Include comprehensive docstrings
- Keep functions focused and single-purpose
- Handle errors gracefully
- Write tests for new functionality

## Troubleshooting

### Common Issues

**1. Agent Not Responding**
- Check model configuration in `.env`
- Verify API endpoint is accessible
- Check logs for error messages

**2. Memory Not Persisting**
- Ensure InMemoryStore is properly initialized
- Check namespace usage in memory operations
- Verify user_id is included in memory calls

**3. Tools Not Available**
- Confirm tools are properly registered
- Check import statements in `src/main.py`
- Verify tool decorators are applied

**4. Subagent Not Responding**
- Check subagent configuration
- Verify tools are allocated correctly
- Review system prompt for clarity

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check individual components:

```python
# Test memory store
from src.memory import create_memory_store
store = create_memory_store()
store.put(("test", "debug"), "test", {"data": "test"})

# Test tools
from src.tools.career_tools import analyze_skill_gap
result = analyze_skill_gap(["Python"], "Developer")
print(result)
```

## API Reference

### Core Functions

#### `create_life_coach() -> CompiledStateGraph`
Creates the complete AI Life Coach system with all specialists and tools.

#### `create_memory_store() -> InMemoryStore`  
Initializes the persistent memory store with namespace management.

#### Tool Functions
Each tool module exports a `create_*_tools()` function that returns a tuple of LangChain tools.

### Configuration

#### `get_model_config() -> dict`
Returns model configuration for LLM initialization.

#### `get_backend() -> FilesystemBackend`  
Returns configured filesystem backend for context management.

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/my-feature`
3. **Make changes** with tests
4. **Run tests**: `pytest tests/`
5. **Commit changes**: `git commit -m "Add my feature"`
6. **Push to fork**: `git push origin feature/my-feature`
7. **Create pull request**

### Code Review Process

- All changes must pass tests
- Documentation updated for new features
- Code follows style guidelines
- Performance impact considered
- Security implications reviewed

## Support

### Documentation

- This developer guide
- API documentation inline with code
- Architecture documentation in `ARCHITECTURE.md`
- User documentation in `README.md`

### Community

- Issues and discussions on GitHub
- Regular code reviews and pair programming
- Knowledge sharing sessions

---

## Development Status

This is a comprehensive multi-agent system actively maintained and extended. We welcome contributions and feedback from the developer community.

**Last Updated**: February 2025
**Version**: 1.0.0
**Maintainers**: AI Development Team