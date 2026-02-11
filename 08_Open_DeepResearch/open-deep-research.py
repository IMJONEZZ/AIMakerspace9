import marimo

__generated_with = "0.19.9"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## LangGraph Open Deep Research - Supervisor-Researcher Architecture

    In this notebook, we'll explore the **supervisor-researcher delegation architecture** for conducting deep research with LangGraph.

    You can visit this repository to see the original application: [Open Deep Research](https://github.com/langchain-ai/open_deep_research)

    Let's jump in!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What We're Building

    This implementation uses a **hierarchical delegation pattern** where:

    1. **User Clarification** - Optionally asks clarifying questions to understand the research scope
    2. **Research Brief Generation** - Transforms user messages into a structured research brief
    3. **Supervisor** - A lead researcher that analyzes the brief and delegates research tasks
    4. **Parallel Researchers** - Multiple sub-agents that conduct focused research simultaneously
    5. **Research Compression** - Each researcher synthesizes their findings
    6. **Final Report** - All findings are combined into a comprehensive report

    ![Architecture Diagram](https://i.imgur.com/Q8HEZn0.png)

    This differs from a section-based approach by allowing dynamic task decomposition based on the research question, rather than predefined sections.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    # 🤝 Breakout Room #1
    ## Deep Research Foundations

    In this breakout room, we'll understand the architecture and components of the Open Deep Research system.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Dependencies

    This system uses open source, self-hosted services:
    - **LMStudio** for LLM inference (at http://192.168.1.79:8080/v1)
    - **SearxNG** for web search (at http://192.168.1.36:4000)
    - **Supabase** for MCP token management (self-hosted)

    No API keys required for local instances!
    """)
    return


@app.cell
def _():
    # No API keys needed for self-hosted open source services
    # LMStudio and SearxNG are configured in the configuration
    # Environment variables for OpenAI client will be set automatically before import
    print("Using self-hosted open source services:")
    print("  - LMStudio: http://192.168.1.79:8080/v1")
    print("  - SearxNG: http://192.168.1.36:4000")
    print(
        "  - OpenAI API Key: Will be set automatically (LMStudio doesn't validate it)"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 2: State Definitions

    The state structure is hierarchical with three levels:

    ### Agent State (Top Level)
    Contains the overall conversation messages, research brief, accumulated notes, and final report.

    ### Supervisor State (Middle Level)
    Manages the research supervisor's messages, research iterations, and coordinating parallel researchers.

    ### Researcher State (Bottom Level)
    Each individual researcher has their own message history, tool call iterations, and research findings.

    We also have structured outputs for tool calling:
    - **ConductResearch** - Tool for supervisor to delegate research to a sub-agent
    - **ResearchComplete** - Tool to signal research phase is done
    - **ClarifyWithUser** - Structured output for asking clarifying questions
    - **ResearchQuestion** - Structured output for the research brief

    Let's import these from our library: [`open_deep_library/state.py`](open_deep_library/state.py)
    """)
    return


@app.cell
def _():
    # Import state definitions from the library
    from open_deep_library.state import (
        AgentInputState,  # Lines 62-63: Input state is just messages
        # Main workflow states
        AgentState,  # Lines 65-72: Top-level agent state with messages, research_brief, notes, final_report
        ClarifyWithUser,  # Lines 30-41: Structured output for user clarification
        # Structured outputs for tool calling
        ConductResearch,  # Lines 15-19: Tool for delegating research to sub-agents
        ResearchComplete,  # Lines 21-22: Tool to signal research completion
        ResearcherOutputState,  # Lines 92-96: Output from researcher (compressed research + raw notes)
        # Researcher states
        ResearcherState,  # Lines 83-90: Individual researcher with messages and tool iterations
        ResearchQuestion,  # Lines 43-48: Structured output for research brief
        # Supervisor states
        SupervisorState,  # Lines 74-81: Supervisor manages research delegation and iterations
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 3: Utility Functions and Tools

    The system uses several key utilities:

    ### Search Tools (Open Source)
    - **searxng_search** - Async web search via self-hosted SearxNG with automatic summarization
    - Supports multiple search engines through SearxNG aggregation

    ### Reflection Tools
    - **think_tool** - Allows researchers to reflect on their progress and plan next steps (ReAct pattern)

    ### Helper Utilities
    - **get_all_tools** - Assembles the complete toolkit (search + MCP + reflection)
    - **get_today_str** - Provides current date context for research
    - Token limit handling utilities for graceful degradation

    These are defined in [`open_deep_library/utils.py`](open_deep_library/utils.py)
    """)
    return


@app.cell
def _():
    # Import utility functions and tools from the library
    from open_deep_library.utils import (
        anthropic_websearch_called,  # Detect Anthropic native search usage
        # Tool assembly - Get all configured tools
        get_all_tools,
        # Supporting utilities for error handling
        get_api_key_for_model,  # Get API keys from config or env
        get_model_token_limit,  # Look up model's token limit
        get_notes_from_tool_calls,  # Extract notes from tool messages
        # Date utility - Get formatted current date
        get_today_str,
        is_token_limit_exceeded,  # Detect token limit errors
        openai_websearch_called,  # Detect OpenAI native search usage
        remove_up_to_last_ai_message,  # Truncate messages for retry
        # Search tool - SearxNG search with automatic summarization
        searxng_search,
        # Reflection tool - Strategic thinking tool for ReAct pattern
        think_tool,
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Configuration System

    The configuration system controls:

    ### Research Behavior
    - **allow_clarification** - Whether to ask clarifying questions before research
    - **max_concurrent_research_units** - How many parallel researchers can run (default: 5)
    - **max_researcher_iterations** - How many times supervisor can delegate research (default: 6)
    - **max_react_tool_calls** - Tool call limit per researcher (default: 10)

    ### Model Configuration (LMStudio OpenAI-compatible)
    - **lmstudio_base_url** - LMStudio API endpoint (default: http://192.168.1.79:8080/v1)
    - **lmstudio_api_key** - API key for LMStudio (typically empty for local instances)
    - **research_model** - Model for research and supervision (openai:glm-4.7)
    - **compression_model** - Model for synthesizing findings (openai:glm-4.7)
    - **final_report_model** - Model for writing the final report (openai:glm-4.7)
    - **summarization_model** - Model for summarizing web search results (openai:glm-4.7)
    - **embedding_model** - Model for embeddings (text-embedding-nomic-embed-text-v2-moe)

    ### Search Configuration (SearxNG Self-Hosted)
    - **search_api** - Which search API to use (SEARXNG, ANTHROPIC, TAVILY, or NONE)
    - **searxng_host** - SearxNG instance URL (default: http://192.168.1.36:4000)
    - **max_content_length** - Character limit before summarization

    Defined in [`open_deep_library/configuration.py`](open_deep_library/configuration.py)
    """)
    return


@app.cell
def _():
    # Import configuration from the library
    from open_deep_library.configuration import (
        Configuration,  # Main configuration class with all settings
        SearchAPI,  # Enum for search API options (SEARXNG, ANTHROPIC, TAVILY, NONE)
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 5: Prompt Templates

    The system uses carefully engineered prompts for each phase:

    ### Phase 1: Clarification
    **clarify_with_user_instructions** - Analyzes if the research scope is clear or needs clarification

    ### Phase 2: Research Brief
    **transform_messages_into_research_topic_prompt** - Converts user messages into a detailed research brief

    ### Phase 3: Supervisor
    **lead_researcher_prompt** - System prompt for the supervisor that manages delegation strategy

    ### Phase 4: Researcher
    **research_system_prompt** - System prompt for individual researchers conducting focused research

    ### Phase 5: Compression
    **compress_research_system_prompt** - Prompt for synthesizing research findings without losing information

    ### Phase 6: Final Report
    **final_report_generation_prompt** - Comprehensive prompt for writing the final report

    All prompts are defined in [`open_deep_library/prompts.py`](open_deep_library/prompts.py)
    """)
    return


@app.cell
def _():
    # Import prompt templates from the library
    from open_deep_library.prompts import (
        clarify_with_user_instructions,  # Lines 3-41: Ask clarifying questions
        compress_research_system_prompt,  # Lines 186-222: Research compression prompt
        final_report_generation_prompt,  # Lines 228-308: Final report generation
        lead_researcher_prompt,  # Lines 79-136: Supervisor system prompt
        research_system_prompt,  # Lines 138-183: Researcher system prompt
        transform_messages_into_research_topic_prompt,  # Lines 44-77: Generate research brief
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #1:

    Explain the interrelationships between the three states (Agent, Supervisor, Researcher). Why don't we just make a single huge state?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### Answer:
    AgentState runs the overall workflow, SupervisorState coordinates research delegation, and ResearcherState handles individual tool-call loops. Splitting them prevents token bloat by only passing relevant context to each level, enables parallel execution, and isolates failures so one researcher crashing doesn't corrupt the entire job.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #2:

    What are the advantages and disadvantages of importing these components instead of including them in the notebook?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### Answer:
    Importing keeps the notebook clean and focused on learning, but you have to switch between files to see implementation details or make quick edits.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🏗️ Activity #1: Explore the Prompts

    Open `open_deep_library/prompts.py` and examine one of the prompt templates in detail.

    **Requirements:**
    1. Choose one prompt template (clarify, brief, supervisor, researcher, compression, or final report)
    2. Explain what the prompt is designed to accomplish
    3. Identify 2-3 key techniques used in the prompt (e.g., structured output, role definition, examples)
    4. Suggest one improvement you might make to the prompt

    **YOUR CODE HERE** - Write your analysis in a markdown cell below
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analysis of `research_system_prompt`

    ### What This Prompt Accomplishes

    The research_system_prompt is designed to guide an AI agent in conducting web research on user-defined topics. It serves as a system prompt for individual researchers who are delegated specific research tasks by a lead researcher agent.

    ### Key Techniques Used

    **1. Structured Sections with XML-Like Tags**
    The prompt uses clear, labeled sections (`<Task>`, `<Available Tools>`, `<Instructions>`, `<Hard Limits>`, `<Show Your Thinking>`). This creates visual hierarchy and makes the prompt easy for both developers and AI models to parse. I'm a big fan of tags, so this is sick.

    **2. Explicit Step-by-Step Instructions**
    The `<Instructions>` section provides a numbered algorithm (1-5) that guides the research process:
    ```
    1. Read question carefully → 2. Start broad → 3. Assess → 4. Narrow down → 5. Stop
    ```
    This creates a reproducible workflow for the AI to follow.

    **3. Hard Constraints with Quantified Limits**
    The `<Hard Limits>` section sets explicit, measurable boundaries:
    - Simple queries: 2-3 search calls max
    - Complex queries: 5 search calls max
    - Stop conditions (comprehensive answer, 3+ sources, duplicate results)

    This prevents the agent from endlessly searching.

    ### Suggested Improvement

    **Add Concrete Examples**

    The current prompt explains what to do but doesn't show how it looks in practice. Adding 1-2 few-shot examples would make the instructions more concrete and reduce ambiguity.

    **Suggested addition:**

    ```
    <Example Workflow>
    User question: "What are the environmental impacts of electric vehicles?"

    Iteration 1:
    - Search: "electric vehicle environmental impact" (broad)
    - Think_tool: Found lifecycle emissions, manufacturing concerns. Missing specific data on battery disposal and comparison with gas vehicles.

    Iteration 2:
    - Search: "electric vehicle vs gasoline car carbon footprint comparison"
    - Think_tool: Have comparison data and lifecycle analysis. Sources are consistent. Stop searching.

    Result: 2 searches, comprehensive answer found.
    </Example Workflow>
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    # 🤝 Breakout Room #2
    ## Building & Running the Researcher

    In this breakout room, we'll explore the node functions, build the graph, and run wellness research.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 6: Node Functions - The Building Blocks

    Now let's look at the node functions that make up our graph. We'll import them from the library and understand what each does.

    ### The Complete Research Workflow

    The workflow consists of 8 key nodes organized into 3 subgraphs:

    1. **Main Graph Nodes:**
       - `clarify_with_user` - Entry point that checks if clarification is needed
       - `write_research_brief` - Transforms user input into structured research brief
       - `final_report_generation` - Synthesizes all research into final report

    2. **Supervisor Subgraph Nodes:**
       - `supervisor` - Lead researcher that plans and delegates
       - `supervisor_tools` - Executes supervisor's tool calls (delegation, reflection)

    3. **Researcher Subgraph Nodes:**
       - `researcher` - Individual researcher conducting focused research
       - `researcher_tools` - Executes researcher's tool calls (search, reflection)
       - `compress_research` - Synthesizes researcher's findings

    All nodes are defined in [`open_deep_library/deep_researcher.py`](open_deep_library/deep_researcher.py)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Node 1: clarify_with_user

    **Purpose:** Analyzes user messages and asks clarifying questions if the research scope is unclear.

    **Key Steps:**
    1. Check if clarification is enabled in configuration
    2. Use structured output to analyze if clarification is needed
    3. If needed, end with a clarifying question for the user
    4. If not needed, proceed to research brief with verification message

    **Implementation:** [`open_deep_library/deep_researcher.py` lines 60-115](open_deep_library/deep_researcher.py#L60-L115)
    """)
    return


@app.cell
def _():
    # Import the clarify_with_user node
    from open_deep_library.deep_researcher import clarify_with_user

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Node 2: write_research_brief

    **Purpose:** Transforms user messages into a structured research brief for the supervisor.

    **Key Steps:**
    1. Use structured output to generate detailed research brief from messages
    2. Initialize supervisor with system prompt and research brief
    3. Set up supervisor messages with proper context

    **Why this matters:** A well-structured research brief helps the supervisor make better delegation decisions.

    **Implementation:** [`open_deep_library/deep_researcher.py` lines 118-175](open_deep_library/deep_researcher.py#L118-L175)
    """)
    return


@app.cell
def _():
    # Import the write_research_brief node
    from open_deep_library.deep_researcher import write_research_brief

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Node 3: supervisor

    **Purpose:** Lead research supervisor that plans research strategy and delegates to sub-researchers.

    **Key Steps:**
    1. Configure model with three tools:
       - `ConductResearch` - Delegate research to a sub-agent
       - `ResearchComplete` - Signal that research is done
       - `think_tool` - Strategic reflection before decisions
    2. Generate response based on current context
    3. Increment research iteration count
    4. Proceed to tool execution

    **Decision Making:** The supervisor uses `think_tool` to reflect before delegating research, ensuring thoughtful decomposition of the research question.

    **Implementation:** [`open_deep_library/deep_researcher.py` lines 178-223](open_deep_library/deep_researcher.py#L178-L223)
    """)
    return


@app.cell
def _():
    # Import the supervisor node (from supervisor subgraph)
    from open_deep_library.deep_researcher import supervisor

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Node 4: supervisor_tools

    **Purpose:** Executes the supervisor's tool calls, including strategic thinking and research delegation.

    **Key Steps:**
    1. Check exit conditions:
       - Exceeded maximum iterations
       - No tool calls made
       - `ResearchComplete` called
    2. Process `think_tool` calls for strategic reflection
    3. Execute `ConductResearch` calls in parallel:
       - Spawn researcher subgraphs for each delegation
       - Limit to `max_concurrent_research_units` (default: 5)
       - Gather all results asynchronously
    4. Aggregate findings and return to supervisor

    **Parallel Execution:** This is where the magic happens - multiple researchers work simultaneously on different aspects of the research question.

    **Implementation:** [`open_deep_library/deep_researcher.py` lines 225-349](open_deep_library/deep_researcher.py#L225-L349)
    """)
    return


@app.cell
def _():
    # Import the supervisor_tools node
    from open_deep_library.deep_researcher import supervisor_tools

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Node 5: researcher

    **Purpose:** Individual researcher that conducts focused research on a specific topic.

    **Key Steps:**
    1. Load all available tools (search, MCP, reflection)
    2. Configure model with tools and researcher system prompt
    3. Generate response with tool calls
    4. Increment tool call iteration count

    **ReAct Pattern:** Researchers use `think_tool` to reflect after each search, deciding whether to continue or provide their answer.

    **Available Tools:**
    - Search tools (Tavily or Anthropic native search)
    - `think_tool` for strategic reflection
    - `ResearchComplete` to signal completion
    - MCP tools (if configured)

    **Implementation:** [`open_deep_library/deep_researcher.py` lines 365-424](open_deep_library/deep_researcher.py#L365-L424)
    """)
    return


@app.cell
def _():
    # Import the researcher node (from researcher subgraph)
    from open_deep_library.deep_researcher import researcher

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Node 6: researcher_tools

    **Purpose:** Executes the researcher's tool calls, including searches and strategic reflection.

    **Key Steps:**
    1. Check early exit conditions (no tool calls, native search used)
    2. Execute all tool calls in parallel:
       - Search tools fetch and summarize web content
       - `think_tool` records strategic reflections
       - MCP tools execute external integrations
    3. Check late exit conditions:
       - Exceeded `max_react_tool_calls` (default: 10)
       - `ResearchComplete` called
    4. Continue research loop or proceed to compression

    **Error Handling:** Safely handles tool execution errors and continues with available results.

    **Implementation:** [`open_deep_library/deep_researcher.py` lines 435-509](open_deep_library/deep_researcher.py#L435-L509)
    """)
    return


@app.cell
def _():
    # Import the researcher_tools node
    from open_deep_library.deep_researcher import researcher_tools

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Node 7: compress_research

    **Purpose:** Compresses and synthesizes research findings into a concise, structured summary.

    **Key Steps:**
    1. Configure compression model
    2. Add compression instruction to messages
    3. Attempt compression with retry logic:
       - If token limit exceeded, remove older messages
       - Retry up to 3 times
    4. Extract raw notes from tool and AI messages
    5. Return compressed research and raw notes

    **Why Compression?** Researchers may accumulate lots of tool outputs and reflections. Compression ensures:
    - All important information is preserved
    - Redundant information is deduplicated
    - Content stays within token limits for the final report

    **Token Limit Handling:** Gracefully handles token limit errors by progressively truncating messages.

    **Implementation:** [`open_deep_library/deep_researcher.py` lines 511-585](open_deep_library/deep_researcher.py#L511-L585)
    """)
    return


@app.cell
def _():
    # Import the compress_research node
    from open_deep_library.deep_researcher import compress_research

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Node 8: final_report_generation

    **Purpose:** Generates the final comprehensive research report from all collected findings.

    **Key Steps:**
    1. Extract all notes from completed research
    2. Configure final report model
    3. Attempt report generation with retry logic:
       - If token limit exceeded, truncate findings by 10%
       - Retry up to 3 times
    4. Return final report or error message

    **Token Limit Strategy:**
    - First retry: Use model's token limit × 4 as character limit
    - Subsequent retries: Reduce by 10% each time
    - Graceful degradation with helpful error messages

    **Report Quality:** The prompt guides the model to create well-structured reports with:
    - Proper headings and sections
    - Inline citations
    - Comprehensive coverage of all findings
    - Sources section at the end

    **Implementation:** [`open_deep_library/deep_researcher.py` lines 607-697](open_deep_library/deep_researcher.py#L607-L697)
    """)
    return


@app.cell
def _():
    # Import the final_report_generation node
    from open_deep_library.deep_researcher import final_report_generation

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 7: Graph Construction - Putting It All Together

    The system is organized into three interconnected graphs:

    ### 1. Researcher Subgraph (Bottom Level)
    Handles individual focused research on a specific topic:
    ```
    START → researcher → researcher_tools → compress_research → END
                   ↑            ↓
                   └────────────┘ (loops until max iterations or ResearchComplete)
    ```

    ### 2. Supervisor Subgraph (Middle Level)
    Manages research delegation and coordination:
    ```
    START → supervisor → supervisor_tools → END
                ↑              ↓
                └──────────────┘ (loops until max iterations or ResearchComplete)

    supervisor_tools spawns multiple researcher_subgraphs in parallel
    ```

    ### 3. Main Deep Researcher Graph (Top Level)
    Orchestrates the complete research workflow:
    ```
    START → clarify_with_user → write_research_brief → research_supervisor → final_report_generation → END
                     ↓                                       (supervisor_subgraph)
                   (may end early if clarification needed)
    ```

    Let's import the compiled graphs from the library.
    """)
    return


@app.cell
def _():
    # Set environment variables for LMStudio OpenAI-compatible endpoint
    # Must be set BEFORE importing the deep_researcher module to ensure
    # the OpenAI client is initialized with the correct configuration
    import os

    os.environ["OPENAI_API_KEY"] = (
        "lm-studio"  # Any value works, LMStudio doesn't validate it
    )
    os.environ["OPENAI_BASE_URL"] = "http://192.168.1.79:8080/v1"

    # Import the pre-compiled graphs from the library
    from open_deep_library.deep_researcher import (
        # Top level: Complete research workflow
        deep_researcher,  # Lines 699-719: Main graph with all phases
        # Bottom level: Individual researcher workflow
        researcher_subgraph,  # Lines 588-605: researcher → researcher_tools → compress_research
        # Middle level: Supervisor coordination
        supervisor_subgraph,  # Lines 351-363: supervisor → supervisor_tools (spawns researchers)
    )

    return (deep_researcher,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why This Architecture?

    ### Advantages of Supervisor-Researcher Delegation

    1. **Dynamic Task Decomposition**
       - Unlike section-based approaches with predefined structure, the supervisor can break down research based on the actual question
       - Adapts to different types of research (comparisons, lists, deep dives, etc.)

    2. **Parallel Execution**
       - Multiple researchers work simultaneously on different aspects
       - Much faster than sequential section processing
       - Configurable parallelism (1-20 concurrent researchers)

    3. **ReAct Pattern for Quality**
       - Researchers use `think_tool` to reflect after each search
       - Prevents excessive searching and improves search quality
       - Natural stopping conditions based on information sufficiency

    4. **Flexible Tool Integration**
       - Easy to add MCP tools for specialized research
       - Supports multiple search APIs (Anthropic, Tavily)
       - Each researcher can use different tool combinations

    5. **Graceful Token Limit Handling**
       - Compression prevents token overflow
       - Progressive truncation in final report generation
       - Research can scale to arbitrary depths

    ### Trade-offs

    - **Complexity:** More moving parts than section-based approach
    - **Cost:** Parallel researchers use more tokens (but faster)
    - **Unpredictability:** Research structure emerges dynamically
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 8: Running the Deep Researcher

    Now let's see the system in action! We'll use it to research wellness strategies for improving sleep quality.

    ### Setup

    We need to:
    1. Set up the wellness research request
    2. Configure the execution with Anthropic settings
    3. Run the research workflow
    """)
    return


@app.cell
def _(deep_researcher):
    # Set up the graph with Anthropic configuration
    import uuid

    from IPython.display import Markdown, display

    # Note: deep_researcher is already compiled from the library
    # For this demo, we'll use it directly without additional checkpointing
    graph = deep_researcher

    print("✓ Graph ready for execution")
    print("  (Note: The graph is pre-compiled from the library)")
    return Markdown, display, graph, uuid


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Configuration for Open Source Stack

    We'll configure the system to use:
    - **LMStudio** with glm-4.7 for all research, supervision, and report generation
    - **SearxNG** for web search (self-hosted at http://192.168.1.36:4000)
    - **Moderate parallelism** (1 concurrent researcher for resource control)
    - **Clarification enabled** (will ask if research scope is unclear)
    """)
    return


@app.cell
def _(uuid):
    # Configure for open source stack with LMStudio and SearxNG
    config = {
        "configurable": {
            # LMStudio Configuration
            "lmstudio_base_url": "http://192.168.1.79:8080/v1",
            "lmstudio_api_key": "",  # Empty for local instances
            "embedding_model": "text-embedding-nomic-embed-text-v2-moe",
            # Model configuration - using glm-4.7 via LMStudio for everything
            "research_model": "openai:glm-4.7",
            "research_model_max_tokens": 20000,
            "compression_model": "openai:glm-4.7",
            "compression_model_max_tokens": 20000,
            "final_report_model": "openai:glm-4.7",
            "final_report_model_max_tokens": 20000,
            "summarization_model": "openai:glm-4.7",
            "summarization_model_max_tokens": 20000,
            # Research behavior
            "allow_clarification": True,
            "max_concurrent_research_units": 1,  # 1 parallel researcher
            "max_researcher_iterations": 2,  # Supervisor can delegate up to 2 times
            "max_react_tool_calls": 3,  # Each researcher can make up to 3 tool calls
            # Search configuration - using self-hosted SearxNG
            "search_api": "searxng",
            "searxng_host": "http://192.168.1.36:4000",
            "max_content_length": 50000,
            # Thread ID for this conversation
            "thread_id": str(uuid.uuid4()),
        }
    }

    print("✓ Configuration ready")
    print(f"  - Research Model: glm-4.7 (via LMStudio)")
    print(f"  - Max Concurrent Researchers: 1")
    print(f"  - Max Iterations: 2")
    print(f"  - Search API: SearxNG (self-hosted)")
    return (config,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Execute the Wellness Research

    Now let's run the research! We'll ask the system to research evidence-based strategies for improving sleep quality.

    The workflow will:
    1. **Clarify** - Check if the request is clear (may skip if obvious)
    2. **Research Brief** - Transform our request into a structured brief
    3. **Supervisor** - Plan research strategy and delegate to researchers
    4. **Parallel Research** - Researchers gather information simultaneously
    5. **Compression** - Each researcher synthesizes their findings
    6. **Final Report** - All findings combined into comprehensive report
    """)
    return


@app.cell
async def _(Markdown, config, display, graph):
    # Create our wellness research request
    research_request = """
    I want to improve my sleep quality. I currently:
    - Go to bed at inconsistent times (10pm-1am)
    - Use my phone in bed
    - Often feel tired in the morning

    Please research the best evidence-based strategies for improving sleep quality and create a comprehensive sleep improvement plan for me.
    """

    # Execute the graph
    async def run_research():
        """Run the research workflow and display results."""
        print("Starting research workflow...\n")

        async for event in graph.astream(
            {"messages": [{"role": "user", "content": research_request}]},
            config,
            stream_mode="updates",
        ):
            # Display each step
            for node_name, node_output in event.items():
                print(f"\n{'=' * 60}")
                print(f"Node: {node_name}")
                print(f"{'=' * 60}")

                if node_name == "clarify_with_user":
                    if "messages" in node_output:
                        last_msg = node_output["messages"][-1]
                        print(f"\n{last_msg.content}")

                elif node_name == "write_research_brief":
                    if "research_brief" in node_output:
                        print(f"\nResearch Brief Generated:")
                        print(f"{node_output['research_brief'][:500]}...")

                elif node_name == "supervisor":
                    print(f"\nSupervisor planning research strategy...")
                    if "supervisor_messages" in node_output:
                        last_msg = node_output["supervisor_messages"][-1]
                        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                            print(f"Tool calls: {len(last_msg.tool_calls)}")
                            for tc in last_msg.tool_calls:
                                print(f"  - {tc['name']}")

                elif node_name == "supervisor_tools":
                    print(f"\nExecuting supervisor's tool calls...")
                    if "notes" in node_output:
                        print(f"Research notes collected: {len(node_output['notes'])}")

                elif node_name == "final_report_generation":
                    if "final_report" in node_output:
                        print(f"\n" + "=" * 60)
                        print("FINAL REPORT GENERATED")
                        print("=" * 60 + "\n")
                        display(Markdown(node_output["final_report"]))

        print("\n" + "=" * 60)
        print("Research workflow completed!")
        print("=" * 60)

    # Run the research
    await run_research()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 9: Understanding the Output

    Let's break down what happened:

    ### Phase 1: Clarification
    The system checked if your request was clear. Since you provided specific details about your sleep issues, it likely proceeded without asking clarifying questions.

    ### Phase 2: Research Brief
    Your request was transformed into a detailed research brief that guides the supervisor's delegation strategy.

    ### Phase 3: Supervisor Delegation
    The supervisor analyzed the brief and decided how to break down the research:
    - Used `think_tool` to plan strategy
    - Called `ConductResearch` to delegate to researchers
    - Each delegation specified a focused research topic (e.g., sleep hygiene, circadian rhythm, blue light effects)

    ### Phase 4: Parallel Research
    Researchers worked on their assigned topics:
    - Each researcher used web search tools to gather information
    - Used `think_tool` to reflect after each search
    - Decided when they had enough information
    - Compressed their findings into clean summaries

    ### Phase 5: Final Report
    All research findings were synthesized into a comprehensive sleep improvement plan with:
    - Well-structured sections
    - Evidence-based recommendations
    - Practical action items
    - Sources for further reading
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 10: Key Takeaways & Next Steps

    ### Architecture Benefits
    1. **Dynamic Decomposition** - Research structure emerges from the question, not predefined
    2. **Parallel Efficiency** - Multiple researchers work simultaneously
    3. **ReAct Quality** - Strategic reflection improves search decisions
    4. **Scalability** - Handles token limits gracefully through compression
    5. **Flexibility** - Easy to add new tools and capabilities

    ### When to Use This Pattern
    - **Complex research questions** that need multi-angle investigation
    - **Comparison tasks** where parallel research on different topics is beneficial
    - **Open-ended exploration** where structure should emerge dynamically
    - **Time-sensitive research** where parallel execution speeds up results

    ### When to Use Section-Based Instead
    - **Highly structured reports** with predefined format requirements
    - **Template-based content** where sections are always the same
    - **Sequential dependencies** where later sections depend on earlier ones
    - **Budget constraints** where token efficiency is critical

    ### Extend the System
    1. **Add MCP Tools** - Integrate specialized tools for your domain
    2. **Custom Prompts** - Modify prompts for specific research types
    3. **Different Models** - Try different models via LMStudio
    4. **Persistence** - Use a real database for checkpointing instead of memory

    ### Learn More
    - [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
    - [Open Deep Research Repo](https://github.com/langchain-ai/open_deep_research)
    - [LMStudio Documentation](https://lmstudio.ai/docs)
    - [SearxNG Documentation](https://docs.searxng.org/)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #3:

    What are the trade-offs of using parallel researchers vs. sequential research? When might you choose one approach over the other?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### Answer:
    Parallel researchers are faster but cost more, while sequential research is cheaper but slower. Choose parallel when speed matters and tasks are independent; choose sequential for tight budgets or dependent tasks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ❓ Question #4:

    How would you adapt this deep research architecture for a production wellness application? What additional components would you need?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### Answer:
    For production, you'd need user authentication and profiles (to track individual wellness goals), a database to persist research history and recommendations, an API layer for frontend integration with rate limiting and caching, monitoring/observability for tracking costs and performance, plus content moderation to filter wellness advice.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🏗️ Activity #2: Custom Wellness Research

    Using what you've learned, run a custom wellness research task.

    **Requirements:**
    1. Create a wellness-related research question (exercise, nutrition, stress, etc.)
    2. Modify the configuration for your use case
    3. Run the research and analyze the output
    4. Document what worked well and what could be improved

    **Experiment ideas:**
    - Research exercise routines for specific conditions (bad knee, lower back pain)
    - Compare different stress management techniques
    - Investigate nutrition strategies for specific goals
    - Explore meditation and mindfulness research

    **YOUR CODE HERE**
    """)
    return


@app.cell
async def _(Markdown, display, graph, uuid):
    # Custom Wellness Research: Stress Management for Working Professionals
    my_wellness_request = """
    I'm a software developer working long hours (50-60 hours/week) and experiencing high stress levels.
    I often feel overwhelmed, have trouble disconnecting from work in the evenings, and my sleep quality has declined.

    Please research evidence-based stress management techniques specifically for working professionals in tech,
    focusing on:
    1. Quick interventions (<5 minutes) that can be done during work hours
    2. Strategies for disconnecting and preventing burnout
    3. Techniques that improve work-life balance without sacrificing productivity

    Create a practical, actionable plan I can implement immediately.
    """

    my_config = {
        "configurable": {
            # LMStudio Configuration
            "lmstudio_base_url": "http://192.168.1.79:8080/v1",
            "lmstudio_api_key": "",
            "embedding_model": "text-embedding-nomic-embed-text-v2-moe",
            # Model configuration using glm-4.7
            "research_model": "openai:glm-4.7",
            "research_model_max_tokens": 20000,
            "compression_model": "openai:glm-4.7",
            "compression_model_max_tokens": 20000,
            "final_report_model": "openai:glm-4.7",
            "final_report_model_max_tokens": 20000,
            "summarization_model": "openai:glm-4.7",
            "summarization_model_max_tokens": 20000,
            # Research behavior - increased iterations for comprehensive coverage
            "allow_clarification": True,
            "max_concurrent_research_units": 2,
            "max_researcher_iterations": 3,
            "max_react_tool_calls": 5,
            # Search configuration - self-hosted SearxNG
            "search_api": "searxng",
            "searxng_host": "http://192.168.1.36:4000",
            "max_content_length": 50000,
            "thread_id": str(uuid.uuid4()),
        }
    }

    async def run_custom_research(request, config):
        """Run custom wellness research workflow."""
        print("\n" + "=" * 60)
        print("CUSTOM WELLNESS RESEARCH: Stress Management")
        print("=" * 60 + "\n")

        async for event in graph.astream(
            {"messages": [{"role": "user", "content": request}]},
            config,
            stream_mode="updates",
        ):
            for node_name, node_output in event.items():
                print(f"\n{'─' * 50}")
                print(f"Node: {node_name}")
                print(f"{'─' * 50}")

                if node_name == "clarify_with_user":
                    if "messages" in node_output:
                        last_msg = node_output["messages"][-1]
                        print(f"\n{last_msg.content}")

                elif node_name == "write_research_brief":
                    if "research_brief" in node_output:
                        print(f"\n✓ Research Brief Generated")
                        brief_preview = node_output["research_brief"][:300]
                        print(f"  Preview: {brief_preview}...")

                elif node_name == "supervisor":
                    print(f"\n📋 Supervisor planning research strategy...")
                    if "supervisor_messages" in node_output:
                        last_msg = node_output["supervisor_messages"][-1]
                        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                            for tc in last_msg.tool_calls:
                                if tc["name"] == "ConductResearch":
                                    topic = tc["args"].get("research_topic", "unknown")[
                                        :60
                                    ]
                                    print(f"  → Researcher assigned: {topic}...")

                elif node_name == "supervisor_tools":
                    if "notes" in node_output:
                        print(
                            f"\n✓ Collected {len(node_output['notes'])} research findings"
                        )

                elif node_name == "final_report_generation":
                    if "final_report" in node_output:
                        print(f"\n{'=' * 60}")
                        print("FINAL REPORT: Stress Management for Tech Professionals")
                        print("=" * 60 + "\n")
                        display(Markdown(node_output["final_report"]))

        print("\n" + "=" * 60)
        print("Research completed successfully!")
        print("=" * 60)

    await run_custom_research(my_wellness_request, my_config)
    return


if __name__ == "__main__":
    app.run()
