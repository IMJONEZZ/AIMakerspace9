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
    # Deep Agents: Building Complex Agents for Long-Horizon Tasks

    In this notebook, we'll explore **Deep Agents** - a new approach to building AI agents that can handle complex, multi-step tasks over extended periods. We'll implement all four key elements of Deep Agents while building on our Personal Wellness Assistant use case.

    **Learning Objectives:**
    - Understand the four key elements of Deep Agents: Planning, Context Management, Subagent Spawning, and Long-term Memory
    - Implement each element progressively using the `deepagents` package
    - Learn to use Skills for progressive capability disclosure
    - Use the `deepagents-cli` for interactive agent sessions

    ## Table of Contents:

    - **Breakout Room #1:** Deep Agent Foundations
      - Task 1: Dependencies & Setup
      - Task 2: Understanding Deep Agents
      - Task 3: Planning with Todo Lists
      - Task 4: Context Management with File Systems
      - Task 5: Basic Deep Agent
      - Question #1 & Question #2
      - Activity #1: Build a Research Agent

    - **Breakout Room #2:** Advanced Features & Integration
      - Task 6: Subagent Spawning
      - Task 7: Long-term Memory Integration
      - Task 8: Skills - On-Demand Capabilities
      - Task 9: Using deepagents-cli
      - Task 10: Building a Complete Deep Agent System
      - Question #3 & Question #4
      - Activity #2: Build a Wellness Coach Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🤝 Breakout Room #1
    ## Deep Agent Foundations
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Dependencies & Setup

    Before we begin, make sure you have:

    1. **API Keys** for:
       - Anthropic (default for Deep Agents) or OpenAI
       - LangSmith (optional, for tracing)
       - Tavily (optional, for web search)

    2. **Dependencies installed** via `uv sync`

    3. **For the CLI** (Task 9): `uv pip install deepagents-cli`

    ### Environment Setup

    You can either:
    - Create a `.env` file with your API keys (recommended):
      ```
      ANTHROPIC_API_KEY=your_key_here
      OPENAI_API_KEY=your_key_here
      LANGCHAIN_API_KEY=your_key_here
      ```
    - Or enter them interactively when prompted
    """)
    return


@app.cell
def _():
    # Core imports
    import os
    import getpass
    from uuid import uuid4
    from typing import Annotated, TypedDict, Literal

    import nest_asyncio

    nest_asyncio.apply()  # Required for async operations in Jupyter

    # Load environment variables from .env file
    from dotenv import load_dotenv

    load_dotenv()

    def get_api_key(env_var: str, prompt: str) -> str:
        """Get API key from environment or prompt user."""
        value = os.environ.get(env_var, "")
        if not value:
            value = getpass.getpass(prompt)
            if value:
                os.environ[env_var] = value
        return value
    return Literal, os


@app.cell
def _(os):
    # Verify deepagents installation
    from deepagents import create_deep_agent
    from langchain.chat_models import init_chat_model

    print("deepagents package imported successfully!")

    # Set environment variable for OpenAI-compatible endpoint
    # This will be used by all OpenAI-compatible models including subagents
    os.environ["OPENAI_API_BASE"] = "http://192.168.1.79:8080/v1"
    os.environ["OPENAI_API_KEY"] = (
        "not-needed"  # API key not required for local endpoint
    )

    # Configure model to use open source endpoint
    model = init_chat_model("", model_provider="openai")

    test_agent = create_deep_agent(model=model)
    # Test with a simple agent
    _result = test_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Deep Agents ready!' in exactly those words.",
                }
            ]
        }
    )
    print(_result["messages"][-1].content)
    return create_deep_agent, init_chat_model, model


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 2: Understanding Deep Agents

    **Deep Agents** represent a shift from simple tool-calling loops to sophisticated agents that can handle complex, long-horizon tasks. They address four key challenges:

    ### The Four Key Elements

    | Element | Challenge Addressed | Implementation |
    |---------|---------------------|----------------|
    | **Planning** | "What should I do?" | Todo lists that persist task state |
    | **Context Management** | "What do I know?" | File systems for storing/retrieving info |
    | **Subagent Spawning** | "Who can help?" | Task tool for delegating to specialists |
    | **Long-term Memory** | "What did I learn?" | LangGraph Store for cross-session memory |

    ### Deep Agents vs Traditional Agents

    ```
    Traditional Agent Loop:
    ┌─────────────────────────────────────┐
    │  User Query                         │
    │       ↓                             │
    │  Think → Act → Observe → Repeat     │
    │       ↓                             │
    │  Response                           │
    └─────────────────────────────────────┘
    Problems: Context bloat, no delegation,
              loses track of complex tasks

    Deep Agent Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │                    Deep Agent                           │
    ├─────────────────────────────────────────────────────────┤
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
    │  │   PLANNING   │  │   CONTEXT    │  │   MEMORY     │   │
    │  │              │  │  MANAGEMENT  │  │              │   │
    │  │ write_todos  │  │              │  │   Store      │   │
    │  │ update_todo  │  │  read_file   │  │  namespace   │   │
    │  │ list_todos   │  │  write_file  │  │  get/put     │   │
    │  │              │  │  edit_file   │  │              │   │
    │  └──────────────┘  │  ls          │  └──────────────┘   │
    │                    └──────────────┘                     │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │              SUBAGENT SPAWNING                   │   │
    │  │                                                  │   │
    │  │  task(prompt, tools, model, system_prompt)       │   │
    │  │       ↓              ↓              ↓            │   │
    │  │  ┌────────┐    ┌────────┐    ┌────────┐          │   │
    │  │  │Research│    │Writing │    │Analysis│          │   │
    │  │  │Subagent│    │Subagent│    │Subagent│          │   │
    │  │  └────────┘    └────────┘    └────────┘          │   │
    │  └──────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────┘
    ```

    ### When to Use Deep Agents

    | Use Case | Traditional Agent | Deep Agent |
    |----------|-------------------|------------|
    | Simple Q&A | ✅ | Overkill |
    | Single-step tool use | ✅ | Overkill |
    | Multi-step research | ⚠️ May lose track | ✅ |
    | Complex projects | ❌ Context overflow | ✅ |
    | Parallel task execution | ❌ | ✅ |
    | Long-running sessions | ❌ | ✅ |

    ### Key Insight: "Planning is Context Engineering"

    Deep Agents treat planning not as a separate phase, but as **context engineering**:
    - Todo lists aren't just task trackers—they're **persistent context** about what to do
    - File systems aren't just storage—they're **extended memory** beyond the context window
    - Subagents aren't just helpers—they're **context isolation** to prevent bloat
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 3: Planning with Todo Lists

    The first key element of Deep Agents is **Planning**. Instead of trying to hold all task state in the conversation, Deep Agents use structured todo lists.

    ### Why Todo Lists?

    1. **Persistence**: Tasks survive across conversation turns
    2. **Visibility**: Both agent and user can see progress
    3. **Structure**: Clear tracking of what's done vs pending
    4. **Recovery**: Agent can resume from where it left off

    ### Todo List Tools

    | Tool | Purpose |
    |------|----------|
    | `write_todos` | Create a structured task list |
    | `update_todo` | Mark tasks as complete/in-progress |
    | `list_todos` | View current task state |
    """)
    return


@app.cell
def _(Literal):
    from langchain_core.tools import tool
    from typing import List, Optional
    import json

    TODO_STORE = {}
    # Simple in-memory todo storage for demonstration
    # In production, Deep Agents use persistent storage

    @tool
    def write_todos(todos: List[dict]) -> str:
        """Create a list of todos for tracking task progress.

        Args:
            todos: List of todo items, each with 'title' and optional 'description'

        Returns:
            Confirmation message with todo IDs
        """
        created = []
        for i, todo in enumerate(todos):
            todo_id = f"todo_{len(TODO_STORE) + i + 1}"
            TODO_STORE[todo_id] = {
                "id": todo_id,
                "title": todo.get("title", "Untitled"),
                "description": todo.get("description", ""),
                "status": "pending",
            }
            created.append(todo_id)
        return f"Created {len(created)} todos: {', '.join(created)}"

    @tool
    def update_todo(
        todo_id: str, status: Literal["pending", "in_progress", "completed"]
    ) -> str:
        """Update the status of a todo item.

        Args:
            todo_id: The ID of the todo to update
            status: New status (pending, in_progress, completed)

        Returns:
            Confirmation message
        """
        if todo_id not in TODO_STORE:
            return f"Todo {todo_id} not found"
        TODO_STORE[todo_id]["status"] = status
        return f"Updated {todo_id} to {status}"

    @tool
    def list_todos() -> str:
        """List all todos with their current status.

        Returns:
            Formatted list of all todos
        """
        if not TODO_STORE:
            return "No todos found"
        _result = []
        for todo_id, todo in TODO_STORE.items():
            status_emoji = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}
            emoji = status_emoji.get(todo["status"], "❓")
            _result.append(f"{emoji} [{todo_id}] {todo['title']} ({todo['status']})")
        return "\n".join(_result)

    print("Todo tools defined!")
    return TODO_STORE, list_todos, tool, update_todo, write_todos


@app.cell
def _(TODO_STORE, list_todos, write_todos):
    # Test the todo tools
    TODO_STORE.clear()  # Reset for demo
    _result = write_todos.invoke(
        {
            "todos": [
                {
                    "title": "Assess current sleep patterns",
                    "description": "Review user's sleep schedule and quality",
                },
                {
                    "title": "Research sleep improvement strategies",
                    "description": "Find evidence-based techniques",
                },
                {
                    "title": "Create personalized sleep plan",
                    "description": "Combine findings into actionable steps",
                },
            ]
        }
    )
    # Create some wellness todos
    print(_result)
    print("\nCurrent todos:")
    print(list_todos.invoke({}))
    return


@app.cell
def _(list_todos, update_todo):
    # Simulate progress
    update_todo.invoke({"todo_id": "todo_1", "status": "completed"})
    update_todo.invoke({"todo_id": "todo_2", "status": "in_progress"})

    print("After updates:")
    print(list_todos.invoke({}))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Context Management with File Systems

    The second key element is **Context Management**. Deep Agents use file systems to:

    1. **Offload large content** - Store research, documents, and results to disk
    2. **Persist across sessions** - Files survive beyond conversation context
    3. **Share between subagents** - Subagents can read/write shared files
    4. **Prevent context overflow** - Large tool results automatically saved to disk

    ### Automatic Context Management

    Deep Agents automatically handle context limits:
    - **Large result offloading**: Tool results >20k tokens → saved to disk
    - **Proactive offloading**: At 85% context capacity → agent saves state to disk
    - **Summarization**: Long conversations get summarized while preserving intent

    ### File System Tools

    | Tool | Purpose |
    |------|----------|
    | `ls` | List directory contents |
    | `read_file` | Read file contents |
    | `write_file` | Create/overwrite files |
    | `edit_file` | Make targeted edits |
    """)
    return


@app.cell
def _(tool):
    from pathlib import Path

    WORKSPACE = Path("workspace")
    WORKSPACE.mkdir(exist_ok=True)
    # Create a workspace directory for our agent

    @tool
    def ls(path: str = ".") -> str:
        """List contents of a directory.

        Args:
            path: Directory path to list (default: current directory)

        Returns:
            List of files and directories
        """
        target = WORKSPACE / path
        if not target.exists():
            return f"Directory not found: {path}"
        items = []
        for item in sorted(target.iterdir()):
            prefix = "[DIR]" if item.is_dir() else "[FILE]"
            size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
            items.append(f"{prefix} {item.name}{size}")
        return "\n".join(items) if items else "(empty directory)"

    @tool
    def read_file(path: str) -> str:
        """Read contents of a file.

        Args:
            path: Path to the file to read

        Returns:
            File contents
        """
        target = WORKSPACE / path
        if not target.exists():
            return f"File not found: {path}"
        return target.read_text()

    @tool
    def write_file(path: str, content: str) -> str:
        """Write content to a file (creates or overwrites).

        Args:
            path: Path to the file to write
            content: Content to write to the file

        Returns:
            Confirmation message
        """
        target = WORKSPACE / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"Wrote {len(content)} characters to {path}"

    @tool
    def edit_file(path: str, old_text: str, new_text: str) -> str:
        """Edit a file by replacing text.

        Args:
            path: Path to the file to edit
            old_text: Text to find and replace
            new_text: Replacement text

        Returns:
            Confirmation message
        """
        target = WORKSPACE / path
        if not target.exists():
            return f"File not found: {path}"
        content = target.read_text()
        if old_text not in content:
            return f"Text not found in {path}"
        new_content = content.replace(old_text, new_text, 1)
        target.write_text(new_content)
        return f"Updated {path}"

    print("File system tools defined!")
    print(f"Workspace: {WORKSPACE.absolute()}")
    return Path, WORKSPACE, ls, read_file, write_file


@app.cell
def _(ls):
    # Test the file system tools
    print("Current workspace contents:")
    print(ls.invoke({"path": "."}))
    return


@app.cell
def _(ls, write_file):
    # Create a research notes file
    notes = "# Sleep Research Notes\n\n## Key Findings\n- Adults need 7-9 hours of sleep\n- Consistent sleep schedule is important\n- Blue light affects melatonin production\n\n## TODO\n- [ ] Review individual user needs\n- [ ] Create personalized recommendations\n"
    _result = write_file.invoke({"path": "research/sleep_notes.md", "content": notes})
    print(_result)
    print("\nResearch directory:")
    # Verify it was created
    print(ls.invoke({"path": "research"}))
    return


@app.cell
def _(read_file):
    # Read and edit the file
    print("File contents:")
    print(read_file.invoke({"path": "research/sleep_notes.md"}))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 5: Basic Deep Agent

    Now let's create a basic Deep Agent using the `deepagents` package. This combines:
    - Planning (todo lists)
    - Context management (file system)
    - A capable LLM backbone

    ### Configuring the FilesystemBackend

    Deep Agents come with **built-in file tools** (`ls`, `read_file`, `write_file`, `edit_file`). To control where files are stored, we configure a `FilesystemBackend`:

    ```python
    from deepagents.backends import FilesystemBackend

    backend = FilesystemBackend(
        root_dir="/path/to/workspace",
        virtual_mode=True  # REQUIRED to actually sandbox files!
    )
    ```

    **Critical: `virtual_mode=True`**
    - Without `virtual_mode=True`, agents can still write anywhere on the filesystem!
    - The `root_dir` alone does NOT restrict file access
    - `virtual_mode=True` blocks paths with `..`, `~`, and absolute paths outside root
    """)
    return


@app.cell
def _(Path, create_deep_agent, list_todos, model, update_todo, write_todos):
    from deepagents.backends import FilesystemBackend

    workspace_path = Path("workspace").absolute()
    filesystem_backend = FilesystemBackend(
        root_dir=str(workspace_path), virtual_mode=True
    )
    # Configure the filesystem backend to use our workspace directory
    # IMPORTANT: virtual_mode=True is required to actually restrict paths to root_dir
    # Without it, agents can still write anywhere on the filesystem!
    custom_tools = [write_todos, update_todo, list_todos]
    wellness_agent = create_deep_agent(
        model=model,
        tools=custom_tools,
        backend=filesystem_backend,
        system_prompt="You are a Personal Wellness Assistant that helps users improve their health.\n\nWhen given a complex task:\n1. First, create a todo list to track your progress\n2. Work through each task, updating status as you go\n3. Save important findings to files for reference\n4. Provide a clear summary when complete\n\nBe thorough but concise. Always explain your reasoning.",
    )
    print(f"Basic Deep Agent created!")
    # Combine our custom tools (for todo tracking)
    # Note: Deep Agents has built-in file tools (ls, read_file, write_file, edit_file)
    # that will use the configured FilesystemBackend
    # Create a basic Deep Agent
    print(
        f"File operations sandboxed to: {workspace_path}"
    )  # This is required to sandbox file operations!  # Configure where files are stored
    return filesystem_backend, wellness_agent


@app.cell
def _(TODO_STORE, wellness_agent):
    # Reset todo store for fresh demo
    TODO_STORE.clear()
    _result = wellness_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I want to improve my sleep quality. I currently:\n- Go to bed at inconsistent times (10pm-1am)\n- Use my phone in bed\n- Often feel tired in the morning\n\nPlease create a personalized sleep improvement plan for me and save it to a file.",
                }
            ]
        }
    )
    # Test with a multi-step wellness task
    print("Agent response:")
    print(_result["messages"][-1].content)
    return


@app.cell
def _(WORKSPACE, list_todos):
    # Check what the agent created
    print("Todo list after task:")
    print(list_todos.invoke({}))
    print("\n" + "=" * 50)
    print("\nWorkspace contents:")
    for _f in sorted(WORKSPACE.iterdir()):
        # List files in the workspace directory
        if _f.is_file():
            print(f"  [FILE] {_f.name} ({_f.stat().st_size} bytes)")
        else:
            print(f"  [DIR] {_f.name}/")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ❓ Question #1:

    What are the **trade-offs** of using todo lists for planning? Consider:
    - When might explicit planning overhead slow things down?
    - How granular should todo items be?
    - What happens if the agent creates todos but never completes them?

    ##### Answer:
    *Explicit planning slows down simple one-step tasks and wastes time when items are too granular. Unfinished todos pile up into clutter that gets in the way of actual priorities. The overhead isn't worth it for quick tasks, but without consistent cleanup, the list becomes noise.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #2:

    How would you design a **context management strategy** for a wellness agent that:
    - Needs to reference a large health document (16KB)
    - Tracks user metrics over time
    - Must remember user conditions (allergies, medications) for safety

    What goes in files vs. in the prompt? What should never be offloaded?

    ##### Answer:
    *Store the 16KB document and user metrics in files or long-term memory, but never offload allergies and medications—keep those in the prompt for instant access since missing them could be dangerous.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #1: Build a Research Agent

    Build a Deep Agent that can research a wellness topic and produce a structured report.

    ### Requirements:
    1. Create todos for the research process
    2. Read from the HealthWellnessGuide.txt in the data folder
    3. Save findings to a structured markdown file
    4. Update todo status as tasks complete

    ### Test prompt:
    "Research stress management techniques and create a comprehensive guide with at least 5 evidence-based strategies."
    """)
    return


@app.cell
def _():
    ### YOUR CODE HERE ###

    # Step 1: Create a research agent with appropriate tools
    # Hint: You'll need file tools to read the wellness guide

    # Step 2: Add a tool to read from the data folder
    # Hint: Use Path("data/HealthWellnessGuide.txt")

    # Step 3: Create the agent with a research-focused system prompt

    # Step 4: Test with the stress management research task
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🤝 Breakout Room #2
    ## Advanced Features & Integration
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 6: Subagent Spawning

    The third key element is **Subagent Spawning**. This allows a Deep Agent to delegate tasks to specialized subagents.

    ### Why Subagents?

    1. **Context Isolation**: Each subagent has its own context window, preventing bloat
    2. **Specialization**: Different subagents can have different tools/prompts
    3. **Parallelism**: Multiple subagents can work simultaneously
    4. **Cost Optimization**: Use cheaper models for simpler subtasks

    ### How Subagents Work

    ```
    Main Agent
        ├── task("Research sleep science", model="gpt-4o-mini")
        │       └── Returns: Summary of findings
        │
        ├── task("Analyze user's sleep data", tools=[analyze_tool])
        │       └── Returns: Analysis results
        │
        └── task("Write recommendations", system_prompt="Be concise")
                └── Returns: Final recommendations
    ```

    Key benefit: The main agent only receives **summaries**, not all the intermediate context!
    """)
    return


@app.cell
def _():
    research_subagent = {
        "name": "research-agent",
        "description": "Use this agent to research wellness topics in depth. It can read documents and synthesize information.",
        "system_prompt": "You are a wellness research specialist. Your job is to:\n1. Find relevant information in provided documents\n2. Synthesize findings into clear summaries\n3. Cite sources when possible\n\nBe thorough but concise. Focus on evidence-based information.",
        "tools": [],
        "model": "openai:glm-4.7",
    }
    writing_subagent = {
        "name": "writing-agent",
        "description": "Use this agent to create well-structured documents, plans, and guides.",
        "system_prompt": "You are a wellness content writer. Your job is to:\n1. Take research findings and turn them into clear, actionable content\n2. Structure information for easy understanding\n3. Use formatting (headers, bullets, etc.) effectively\n\nWrite in a supportive, encouraging tone.",
        "tools": [],
        "model": "openai:glm-4.7",
    }
    # Define specialized subagent configurations
    # Note: Subagents inherit the backend from the parent agent
    print(
        "Subagent configurations defined!"
    )  # Uses built-in file tools from backend  # Cheaper model for research  # Uses built-in file tools from backend
    return research_subagent, writing_subagent


@app.cell
def _(
    create_deep_agent,
    filesystem_backend,
    list_todos,
    model,
    research_subagent,
    update_todo,
    write_todos,
    writing_subagent,
):
    # Create a coordinator agent that can spawn subagents
    coordinator_agent = create_deep_agent(
        model=model,
        tools=[write_todos, update_todo, list_todos],
        backend=filesystem_backend,  # Use the same backend - subagents inherit it
        subagents=[research_subagent, writing_subagent],
        system_prompt="""You are a Wellness Project Coordinator. Your role is to:
    1. Break down complex wellness requests into subtasks
    2. Delegate research to the research-agent
    3. Delegate content creation to the writing-agent
    4. Coordinate the overall workflow using todos

    Use subagents for specialized work rather than doing everything yourself.
    This keeps the work organized and the results high-quality.""",
    )

    print("Coordinator agent created with subagent capabilities!")
    return (coordinator_agent,)


@app.cell
def _(TODO_STORE, coordinator_agent):
    # Reset for demo
    TODO_STORE.clear()
    _result = coordinator_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Create a comprehensive morning routine guide for better energy.\n        \nThe guide should:\n1. Research the science behind morning routines\n2. Include practical steps for exercise, nutrition, and mindset\n3. Be saved as a well-formatted markdown file",
                }
            ]
        }
    )
    # Test the coordinator with a complex task
    print("Coordinator response:")
    print(_result["messages"][-1].content)
    return


@app.cell
def _(WORKSPACE, list_todos):
    # Check the results
    print("Final todo status:")
    print(list_todos.invoke({}))
    print("\nGenerated files in workspace:")
    for _f in sorted(WORKSPACE.iterdir()):
        if _f.is_file():
            print(f"  [FILE] {_f.name} ({_f.stat().st_size} bytes)")
        elif _f.is_dir():
            print(f"  [DIR] {_f.name}/")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 7: Long-term Memory Integration

    The fourth key element is **Long-term Memory**. Deep Agents integrate with LangGraph's Store for persistent memory across sessions.

    ### Memory Types in Deep Agents

    | Type | Scope | Use Case |
    |------|-------|----------|
    | **Thread Memory** | Single conversation | Current session context |
    | **User Memory** | Across threads, per user | User preferences, history |
    | **Shared Memory** | Across all users | Common knowledge, learned patterns |

    ### Integration with LangGraph Store

    Deep Agents can use the same `InMemoryStore` (or `PostgresStore`) we learned in Session 6:
    """)
    return


@app.cell
def _():
    from langgraph.store.memory import InMemoryStore

    # Create a memory store
    memory_store = InMemoryStore()

    # Store user profile
    user_id = "user_alex"
    profile_namespace = (user_id, "profile")

    memory_store.put(profile_namespace, "name", {"value": "Alex"})
    memory_store.put(
        profile_namespace,
        "goals",
        {"primary": "improve energy levels", "secondary": "better sleep"},
    )
    memory_store.put(
        profile_namespace,
        "conditions",
        {"dietary": ["vegetarian"], "medical": ["mild anxiety"]},
    )
    memory_store.put(
        profile_namespace,
        "preferences",
        {"exercise_time": "morning", "communication_style": "detailed"},
    )

    print(f"Stored profile for {user_id}")

    # Retrieve and display
    for item in memory_store.search(profile_namespace):
        print(f"  {item.key}: {item.value}")
    return (memory_store,)


@app.cell
def _(memory_store, tool):
    # Create memory-aware tools
    from langgraph.store.base import BaseStore

    @tool
    def get_user_profile(user_id: str) -> str:
        """Retrieve a user's wellness profile from long-term memory.

        Args:
            user_id: The user's unique identifier

        Returns:
            User profile as formatted text
        """
        namespace = (user_id, "profile")
        items = list(memory_store.search(namespace))
        if not items:
            return f"No profile found for {user_id}"
        _result = [f"Profile for {user_id}:"]
        for item in items:
            _result.append(f"  {item.key}: {item.value}")
        return "\n".join(_result)

    @tool
    def save_user_preference(user_id: str, key: str, value: str) -> str:
        """Save a user preference to long-term memory.

        Args:
            user_id: The user's unique identifier
            key: The preference key
            value: The preference value

        Returns:
            Confirmation message
        """
        namespace = (user_id, "preferences")
        memory_store.put(namespace, key, {"value": value})
        return f"Saved preference '{key}' for {user_id}"

    print("Memory tools defined!")
    return get_user_profile, save_user_preference


@app.cell
def _(
    create_deep_agent,
    filesystem_backend,
    get_user_profile,
    init_chat_model,
    list_todos,
    save_user_preference,
    update_todo,
    write_todos,
):
    # Create a memory-enhanced agent
    memory_tools = [
        get_user_profile,
        save_user_preference,
        write_todos,
        update_todo,
        list_todos,
    ]

    memory_agent = create_deep_agent(
        model=init_chat_model("openai:glm-4.7"),
        tools=memory_tools,
        backend=filesystem_backend,  # Use workspace for file operations
        system_prompt="""You are a Personal Wellness Assistant with long-term memory.

    At the start of each conversation:
    1. Check the user's profile to understand their goals and conditions
    2. Personalize all advice based on their profile
    3. Save any new preferences they mention

    Always reference stored information to show you remember the user.""",
    )

    print("Memory-enhanced agent created!")
    return (memory_agent,)


@app.cell
def _(TODO_STORE, memory_agent):
    # Test the memory agent
    TODO_STORE.clear()
    _result = memory_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Hi! My user_id is user_alex. What exercise routine would you recommend for me?",
                }
            ]
        }
    )
    print("Agent response:")
    print(_result["messages"][-1].content)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 8: Skills - On-Demand Capabilities

    **Skills** are a powerful feature for progressive capability disclosure. Instead of loading all tools upfront, agents can load specialized capabilities on demand.

    ### Why Skills?

    1. **Context Efficiency**: Don't waste context on unused tool descriptions
    2. **Specialization**: Skills can include detailed instructions for specific tasks
    3. **Modularity**: Easy to add/remove capabilities
    4. **Discoverability**: Agent can browse available skills

    ### SKILL.md Format

    Skills are defined in markdown files with YAML frontmatter:

    ```markdown
    ---
    name: skill-name
    description: What this skill does
    version: 1.0.0
    tools:
      - tool1
      - tool2
    ---

    # Skill Instructions

    Detailed steps for how to use this skill...
    ```
    """)
    return


@app.cell
def _(Path):
    # Let's look at the skills we created
    skills_dir = Path("skills")

    print("Available skills:")
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                # Extract name and description from frontmatter
                lines = content.split("\n")
                name = ""
                desc = ""
                for line in lines:
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip()
                    if line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip()
                print(f"  - {name}: {desc}")
    return


@app.cell
def _(Path):
    # Read the wellness-assessment skill
    skill_content = Path("skills/wellness-assessment/SKILL.md").read_text()
    print(skill_content)
    return


@app.cell
def _(Path, tool):
    # Create a skill-aware tool
    @tool
    def load_skill(skill_name: str) -> str:
        """Load a skill's instructions for a specialized task.

        Available skills:
        - wellness-assessment: Assess user wellness and create recommendations
        - meal-planning: Create personalized meal plans

        Args:
            skill_name: Name of the skill to load

        Returns:
            Skill instructions
        """
        skill_path = Path(f"skills/{skill_name}/SKILL.md")
        if not skill_path.exists():
            available = [d.name for d in Path("skills").iterdir() if d.is_dir()]
            return f"Skill '{skill_name}' not found. Available: {', '.join(available)}"

        return skill_path.read_text()

    print("Skill loader defined!")
    return (load_skill,)


@app.cell
def _(
    create_deep_agent,
    filesystem_backend,
    init_chat_model,
    list_todos,
    load_skill,
    update_todo,
    write_todos,
):
    # Create an agent that can load and use skills
    skill_agent = create_deep_agent(
        model=init_chat_model("openai:glm-4.7"),
        tools=[
            load_skill,
            write_todos,
            update_todo,
            list_todos,
        ],
        backend=filesystem_backend,  # Use workspace for file operations
        system_prompt="""You are a wellness assistant with access to specialized skills.

    When a user asks for something that matches a skill:
    1. Load the appropriate skill using load_skill()
    2. Follow the skill's instructions carefully
    3. Save outputs as specified in the skill

    Available skills:
    - wellness-assessment: For comprehensive wellness evaluations
    - meal-planning: For creating personalized meal plans

    If no skill matches, use your general wellness knowledge.""",
    )

    print("Skill-aware agent created!")
    return (skill_agent,)


@app.cell
def _(TODO_STORE, skill_agent):
    # Test with a skill-appropriate request
    TODO_STORE.clear()
    _result = skill_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I'd like a wellness assessment. I'm a 35-year-old office worker who sits most of the day, has trouble sleeping, and wants to lose 15 pounds. I'm vegetarian and have no major health conditions.",
                }
            ]
        }
    )
    print("Agent response:")
    print(_result["messages"][-1].content)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 9: Using deepagents-cli

    The `deepagents-cli` provides an interactive terminal interface for working with Deep Agents.

    ### Installation

    ```bash
    uv pip install deepagents-cli
    # or
    pip install deepagents-cli
    ```

    ### Key Features

    | Feature | Description |
    |---------|-------------|
    | **Interactive Sessions** | Chat with your agent in the terminal |
    | **Conversation Resume** | Pick up where you left off |
    | **Human-in-the-Loop** | Approve or reject agent actions |
    | **File System Access** | Agent can read/write to your filesystem |
    | **Remote Sandboxing** | Run in isolated Docker containers |

    ### Basic Usage

    ```bash
    # Start an interactive session
    deepagents

    # Resume a previous conversation
    deepagents --resume

    # Use a specific model
    deepagents --model openai:glm-4.7

    # Enable human-in-the-loop approval
    deepagents --approval-mode full
    ```

    ### Example Session

    ```
    $ deepagents

    Welcome to Deep Agents CLI!

    You: Create a 7-day meal plan for a vegetarian athlete

    Agent: I'll create a comprehensive meal plan for you. Let me:
    1. Research vegetarian athlete nutrition needs
    2. Design balanced daily menus
    3. Save the plan to a file

    [Agent uses tools...]

    Agent: I've created your meal plan! You can find it at:
    workspace/vegetarian_athlete_meal_plan.md

    You: /exit
    ```
    """)
    return


@app.cell
def _():
    # Check if CLI is installed
    import subprocess

    try:
        _result = subprocess.run(
            ["deepagents", "--version"], capture_output=True, text=True
        )
        print(f"deepagents-cli version: {_result.stdout.strip()}")
    except FileNotFoundError:
        print("deepagents-cli not installed. Install with:")
        print("  uv pip install deepagents-cli")
        print("  # or")
        print("  pip install deepagents-cli")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Try It Yourself!

    After installing the CLI, try these commands in your terminal:

    ```bash
    # Basic interactive session
    deepagents

    # With a specific working directory
    deepagents --workdir ./workspace

    # See all options
    deepagents --help
    ```

    Sample prompts to try:
    1. "Create a weekly workout plan and save it to a file"
    2. "Research the health benefits of meditation and summarize in a report"
    3. "Analyze my current diet and suggest improvements" (then provide details)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 10: Building a Complete Deep Agent System

    Now let's bring together all four elements to build a comprehensive "Wellness Coach" system:

    1. **Planning**: Track multi-week wellness programs
    2. **Context Management**: Store session notes and progress
    3. **Subagent Spawning**: Delegate to specialists (exercise, nutrition, mindfulness)
    4. **Long-term Memory**: Remember user preferences and history
    """)
    return


@app.cell
def _():
    # Define specialized wellness subagents
    # Subagents inherit the backend from the parent, so they use the same workspace
    exercise_specialist = {
        "name": "exercise-specialist",
        "description": "Expert in exercise science, workout programming, and physical fitness. Use for exercise-related questions and plan creation.",
        "system_prompt": """You are an exercise specialist with expertise in:
    - Workout programming for different fitness levels
    - Exercise form and safety
    - Progressive overload principles
    - Recovery and injury prevention

    Always consider the user's fitness level and any physical limitations.
    Provide clear, actionable exercise instructions.""",
        "tools": [],  # Uses built-in file tools from backend
        "model": "openai:glm-4.7",
    }

    nutrition_specialist = {
        "name": "nutrition-specialist",
        "description": "Expert in nutrition science, meal planning, and dietary optimization. Use for food-related questions and meal plans.",
        "system_prompt": """You are a nutrition specialist with expertise in:
    - Macro and micronutrient balance
    - Meal planning and preparation
    - Dietary restrictions and alternatives
    - Nutrition timing for performance

    Always respect dietary restrictions and preferences.
    Focus on practical, achievable meal suggestions.""",
        "tools": [],  # Uses built-in file tools from backend
        "model": "openai:glm-4.7",
    }

    mindfulness_specialist = {
        "name": "mindfulness-specialist",
        "description": "Expert in stress management, sleep optimization, and mental wellness. Use for stress, sleep, and mental health questions.",
        "system_prompt": """You are a mindfulness and mental wellness specialist with expertise in:
    - Stress reduction techniques
    - Sleep hygiene and optimization
    - Meditation and breathing exercises
    - Work-life balance strategies

    Be supportive and non-judgmental.
    Provide practical techniques that can be implemented immediately.""",
        "tools": [],  # Uses built-in file tools from backend
        "model": "openai:glm-4.7",
    }

    print("Specialist subagents defined!")
    return exercise_specialist, mindfulness_specialist, nutrition_specialist


@app.cell
def _(
    create_deep_agent,
    exercise_specialist,
    filesystem_backend,
    get_user_profile,
    init_chat_model,
    list_todos,
    load_skill,
    mindfulness_specialist,
    nutrition_specialist,
    save_user_preference,
    update_todo,
    write_todos,
):
    # Create the Wellness Coach coordinator
    wellness_coach = create_deep_agent(
        model=init_chat_model("openai:glm-4.7"),
        tools=[
            # Planning
            write_todos,
            update_todo,
            list_todos,
            # Long-term Memory
            get_user_profile,
            save_user_preference,
            # Skills
            load_skill,
        ],
        backend=filesystem_backend,  # All file ops go to workspace
        subagents=[exercise_specialist, nutrition_specialist, mindfulness_specialist],
        system_prompt="""You are a Personal Wellness Coach that coordinates comprehensive wellness programs.

    ## Your Role
    - Understand each user's unique goals, constraints, and preferences
    - Create personalized, multi-week wellness programs
    - Coordinate between exercise, nutrition, and mindfulness specialists
    - Track progress and adapt recommendations

    ## Workflow
    1. **Initial Assessment**: Get user profile and understand their situation
    2. **Planning**: Create a todo list for the program components
    3. **Delegation**: Use specialists for domain-specific content:
       - exercise-specialist: Workout plans and fitness guidance
       - nutrition-specialist: Meal plans and dietary advice
       - mindfulness-specialist: Stress and sleep optimization
    4. **Integration**: Combine specialist outputs into a cohesive program
    5. **Documentation**: Save all plans and recommendations to files

    ## Important
    - Always check user profile first for context
    - Respect any medical conditions or dietary restrictions
    - Provide clear, actionable recommendations
    - Save progress to files so users can reference later""",
    )

    print("Wellness Coach created with all 4 Deep Agent elements!")
    return (wellness_coach,)


@app.cell
def _(TODO_STORE, wellness_coach):
    # Test the complete system
    TODO_STORE.clear()
    _result = wellness_coach.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Hi! My user_id is user_alex. I'd like you to create a 2-week wellness program for me.\n\nI want to focus on:\n1. Building a consistent exercise routine (I can exercise 3x per week for 30 mins)\n2. Improving my diet (remember I'm vegetarian)\n3. Better managing my work stress and improving my sleep\n\nPlease create comprehensive plans for each area and save them as separate files I can reference.",
                }
            ]
        }
    )
    print("Wellness Coach response:")
    print(_result["messages"][-1].content)
    return


@app.cell
def _(WORKSPACE, list_todos):
    # Review what was created
    print("=" * 60)
    print("FINAL TODO STATUS")
    print("=" * 60)
    print(list_todos.invoke({}))
    print("\n" + "=" * 60)
    print("GENERATED FILES")
    print("=" * 60)
    for _f in sorted(WORKSPACE.iterdir()):
        if _f.is_file():
            print(f"  [FILE] {_f.name} ({_f.stat().st_size} bytes)")
        elif _f.is_dir():
            print(f"  [DIR] {_f.name}/")
    return


@app.cell
def _(WORKSPACE):
    # Read one of the generated files
    files = list(WORKSPACE.glob("*.md"))
    if files:
        print(f"\nContents of {files[0].name}:")
        print("=" * 60)
        print(
            files[0].read_text()[:2000] + "..."
            if len(files[0].read_text()) > 2000
            else files[0].read_text()
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ❓ Question #3:

    What are the key considerations when designing **subagent configurations**?

    Consider:
    - When should subagents share tools vs have distinct tools?
    - How do you decide which model to use for each subagent?
    - What's the right granularity for subagent specialization?

    ##### Answer:
    *Your answer here*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #4:

    For a **production wellness application** using Deep Agents, what would you need to add?

    Consider:
    - Safety guardrails for health advice
    - Persistent storage (not in-memory)
    - Multi-user support and isolation
    - Monitoring and observability
    - Cost management with subagents

    ##### Answer:
    *Your answer here*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Activity #2: Build a Wellness Coach Agent

    Build your own wellness coach that uses all 4 Deep Agent elements.

    ### Requirements:
    1. **Planning**: Create todos for a 30-day wellness challenge
    2. **Context Management**: Store daily check-in notes
    3. **Subagents**: At least 2 specialized subagents
    4. **Memory**: Remember user preferences across interactions

    ### Challenge:
    Create a "30-Day Wellness Challenge" system that:
    - Generates a personalized 30-day plan
    - Tracks daily progress
    - Adapts recommendations based on feedback
    - Saves a weekly summary report
    """)
    return


@app.cell
def _():
    ### YOUR CODE HERE ###

    # Step 1: Define your subagent configurations

    # Step 2: Create any additional tools you need

    # Step 3: Build the main coordinator agent

    # Step 4: Test with a user creating their 30-day challenge

    # Step 5: Simulate a daily check-in and adaptation
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    In this session, we explored **Deep Agents** and their four key elements:

    | Element | Purpose | Implementation |
    |---------|---------|----------------|
    | **Planning** | Track complex tasks | `write_todos`, `update_todo`, `list_todos` |
    | **Context Management** | Handle large contexts | File system tools, automatic offloading |
    | **Subagent Spawning** | Delegate to specialists | `task` tool with custom configs |
    | **Long-term Memory** | Remember across sessions | LangGraph Store integration |

    ### Key Takeaways:

    1. **Deep Agents handle complexity** - Unlike simple tool loops, they can manage long-horizon, multi-step tasks
    2. **Planning is context engineering** - Todo lists and files aren't just organization—they're extended memory
    3. **Subagents prevent context bloat** - Delegation keeps the main agent focused and efficient
    4. **Skills enable progressive disclosure** - Load capabilities on-demand instead of upfront
    5. **The CLI makes interaction natural** - Interactive sessions with conversation resume

    ### Deep Agents vs Traditional Agents

    | Aspect | Traditional Agent | Deep Agent |
    |--------|-------------------|------------|
    | Task complexity | Simple, single-step | Complex, multi-step |
    | Context management | All in conversation | Files + summaries |
    | Delegation | None | Subagent spawning |
    | Memory | Within thread | Across sessions |
    | Planning | Implicit | Explicit (todos) |

    ### When to Use Deep Agents

    **Use Deep Agents when:**
    - Tasks require multiple steps or phases
    - Context would overflow in a simple loop
    - Specialization would improve quality
    - Users need to resume sessions
    - Long-term memory is valuable

    **Use Simple Agents when:**
    - Tasks are straightforward Q&A
    - Single tool call suffices
    - Context fits easily
    - No need for persistence

    ### Further Reading

    - [Deep Agents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
    - [Deep Agents GitHub](https://github.com/langchain-ai/deepagents)
    - [Context Management Blog Post](https://www.blog.langchain.com/context-management-for-deepagents/)
    - [Building Multi-Agent Applications](https://www.blog.langchain.com/building-multi-agent-applications-with-deep-agents/)
    - [LangGraph Memory Concepts](https://langchain-ai.github.io/langgraph/concepts/memory/)
    """)
    return


if __name__ == "__main__":
    app.run()
