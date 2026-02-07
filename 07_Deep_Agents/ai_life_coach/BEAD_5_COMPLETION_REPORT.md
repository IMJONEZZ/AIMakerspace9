# Bead #5 Completion Report: Planning System with Phases

**Date Completed**: February 5, 2026
**Estimated Time**: 2 hours (Actual: ~3.5 hours including research and testing)
**Dependencies**: Bead #2, #4 ✅ Complete

---

## Executive Summary

Successfully implemented a comprehensive planning system with phase-aware todo management, dependency tracking, and circular dependency validation. The system provides three LangChain tools (`write_todos`, `update_todo`, `list_todos`) that enable AI agents to create structured plans across 4 phases (discovery, planning, execution, review) with automatic dependency validation.

---

## Research Completed

### 1. Todo List Patterns (LangChain Deep Agents)
- **Source**: `Deep_Agents_Assignment.py` lines 255-283 and LangChain documentation
- **Key Findings**:
  - `TodoListMiddleware` provides planning capabilities via `write_todos` and `read_todos` tools
  - Planning tools are "no-op" operations that maintain state for task tracking
  - Tools use `@tool` decorator from `langchain_core.tools`
  - State is managed through shared manager pattern

### 2. Multi-Phase Planning with Dependencies
- **Sources**: searxng web search results on multi-phase todo systems
- **Key Findings**:
  - Tasks organized into logical phases (discovery → planning → execution → review)
  - Dependencies ensure tasks complete in proper sequence
  - Circular dependency detection is critical to prevent impossible plans
  - Status tracking (pending, in_progress, completed) enables progress monitoring

### 3. Dependency Tracking and Validation
- **Sources**: Research on task dependency management systems
- **Key Findings**:
  - Use graph algorithms (DFS) to detect cycles in dependency chains
  - Tasks should be blocked until all dependencies are complete
  - Diamond patterns (A→B, A→C, B→D, C→D) are valid and commonly used
  - Self-dependencies should be detected as cycles

---

## Deliverables Completed

### ✅ 1. Created `src/tools/planning_tools.py`
**Location**: `/home/imjonezz/Desktop/AIE9/07_Deep_Agents/ai_life_coach/src/tools/planning_tools.py`

**Implementation Details**:
- **TodoItem class**: Data model with validation for phases, statuses, dependencies
  - Supports all 4 phases: discovery, planning, execution, review
  - Supports 3 statuses: pending, in_progress, completed
  - Includes optional fields: depends_on (list of indices), notes, timestamps

- **TodoManager class**: Centralized state management with dependency validation
  - `set_todos()`: Replace todo list with circular dependency detection using DFS
  - `update_todo()`: Update status/notes while respecting dependency constraints
  - `list_todos()`: Filter and display todos grouped by phase
  - `_detect_circular_dependencies()`: DFS-based cycle detection with helpful error messages

- **create_planning_tools()**: Factory function returning 3 LangChain tools
  - All functions use `@tool` decorator from `langchain_core.tools`
  - Comprehensive docstrings with Args, Returns, Raises sections
  - User-friendly error messages for validation failures

### ✅ 2. Implemented Todo Data Models with Phase and Dependency Tracking
```python
class TodoItem:
    - title: str (required, non-empty)
    - phase: Literal["discovery", "planning", "execution", "review"]
    - status: Literal["pending", "in_progress", "completed"]
    - depends_on: List[int] (indices of prerequisite tasks)
    - notes: str
    - created_at: str (ISO timestamp)
    - completed_at: Optional[str] (ISO timestamp, set on completion)

class TodoManager:
    - todos: List[TodoItem]
    - Methods for CRUD, filtering, and validation
```

### ✅ 3. Added Validation Logic for Circular Dependencies
**Algorithm**: Depth-First Search (DFS) with recursion stack tracking

**Features**:
- Detects simple cycles: A → B → A
- Detects complex chains: A → B → C → D → A
- Validates diamond patterns (valid): A→B, A→C, B→D, C→D
- Validates self-dependencies (invalid): A → A
- Provides detailed error messages showing the complete cycle path

**Test Results**: All 5 circular dependency tests pass:
- ✅ Simple two-node cycle
- ✅ Three-node chain cycle
- ✅ Self-dependency detection
- ✅ Valid linear dependencies (no false positives)
- ✅ Valid diamond patterns

### ✅ 4. Created Comprehensive Test Suite
**Location**: `/home/imjonezz/Desktop/AIE9/07_Deep_Agents/ai_life_coach/tests/test_planning_tools.py`

**Test Statistics**: 47 tests, 100% pass rate

**Test Categories**:
1. **Tool Creation (3 tests)**: Verify proper decorator usage, docstrings
2. **TodoItem Model (7 tests)**: Validation, serialization, edge cases
3. **TodoManager (4 tests)**: Basic operations, phase counting
4. **Circular Dependency Detection (5 tests)**: Various cycle patterns
5. **write_todos Tool (5 tests)**: Creation, validation, replacement
6. **update_todo Tool (7 tests)**: Status updates, notes, blocking logic
7. **list_todos Tool (6 tests)**: Filtering, display, status icons
8. **Integration Tests (3 tests)**: Full workflows across tools
9. **Edge Cases (7 tests)**: Empty lists, invalid references, all phases

**Coverage Highlights**:
- All 4 phases tested individually and together
- All 3 statuses with state transitions
- Dependency blocking/allowing logic validated
- Circular dependency prevention verified
- Error handling for invalid inputs tested

### ✅ 5. Updated `src/main.py` to Include Planning Tools
**Changes Made**:
```python
# Import planning tools
from src.tools.planning_tools import create_planning_tools

# Create planning tools alongside memory tools
write_todos, update_todo, list_todos = create_planning_tools()

# Combine all tools for the coordinator agent
all_tools = memory_tools + planning_tools

# Updated system prompt with Planning Tools section explaining:
# - 4 phases: discovery, planning, execution, review
# - 3 statuses: pending, in_progress, completed
# - Dependency tracking and blocking behavior
# - Automatic circular dependency detection
```

---

## Technical Requirements Met

### ✅ Use @tool Decorator for All Planning Functions
- `write_todos`: ✅ Uses `@tool` decorator with comprehensive docstring
- `update_todo`: ✅ Uses `@tool` decorator with comprehensive docstring
- `list_todos`: ✅ Uses `@tool` decorator with comprehensive docstring

### ✅ Support Phase Filtering (discovery, planning, execution, review)
- `list_todos` tool accepts optional `phase` parameter
- Validates phase values against `VALID_PHASES = {"discovery", "planning", "execution", "review"}`
- Results grouped by phase in structured output

### ✅ Track Dependencies Between Tasks
- `TodoItem.depends_on` field stores list of prerequisite todo indices
- Dependency status shown in `list_todos` output (e.g., "Dependencies: 1/2 completed")
- Tasks blocked until all dependencies are completed

### ✅ Validate No Circular Dependencies Exist
- DFS algorithm in `TodoManager._detect_circular_dependencies()`
- Run on every `write_todos` operation before state update
- Raises `ValueError` with detailed cycle path if detected

### ✅ Support Todo Status: pending, in_progress, completed
- Validated against `VALID_STATUSES = {"pending", "in_progress", "completed"}`
- Status transitions enforced with dependency checks
- Visual indicators in output: ⏳ pending, 🔄 in_progress, ✅ completed

---

## Test Results Summary

```
============================== 47 passed in 0.27s ==============================

Test Breakdown:
- Tool Creation Tests:      3/3 ✅
- TodoItem Model Tests:     7/7 ✅
- TodoManager Tests:        4/4 ✅
- Circular Dependency:      5/5 ✅
- write_todos Tests:        5/5 ✅
- update_todo Tests:        7/7 ✅
- list_todos Tests:         6/6 ✅
- Integration Tests:        3/3 ✅
- Edge Cases:               7/7 ✅
```

**Key Validations Tested**:
- ✅ Phase filtering works for all 4 phases
- ✅ Dependency tracking prevents invalid state transitions
- ✅ Circular dependencies are detected and rejected
- ✅ Status icons display correctly
- ✅ Notes accumulate properly across updates
- ✅ Invalid inputs are handled gracefully

---

## Demo Verification

Created `demo_planning.py` demonstrating:
1. ✅ Creating structured todo lists across phases
2. ✅ Updating todo status with dependency enforcement
3. ✅ Blocking dependent tasks until prerequisites complete
4. ✅ Phase filtering (showing only discovery phase)
5. ✅ Status filtering (showing only pending todos)
6. ✅ Adding notes to todos
7. ✅ Circular dependency detection with helpful error messages

**Demo Output**: All 10 demonstration steps completed successfully.

---

## Integration Status

### ✅ Planning Tools Integrated into Main Agent
**File Modified**: `src/main.py`

**Integration Points**:
1. Planning tools created alongside memory tools
2. Combined into `all_tools` list for coordinator agent
3. Specialists receive only memory tools (as per design)
4. System prompt updated to explain planning tool capabilities

**Agent Configuration**:
```python
life_coach = create_deep_agent(
    model=model,
    tools=all_tools,  # memory + planning tools
    backend=get_backend(),
    subagents=[career_specialist, relationship_specialist,
               finance_specialist, wellness_specialist],
    system_prompt="...includes Planning Tools section..."
)
```

---

## Key Features Implemented

### 1. Phase-Aware Organization
- **Discovery**: Assess current state, identify problems
- **Planning**: Create action plans, set strategies
- **Execution**: Implement actions, track progress
- **Review**: Evaluate results, reflect on outcomes

### 2. Smart Dependency Management
- Tasks can depend on multiple other tasks
- Automatic blocking of incomplete prerequisites
- Clear feedback about which tasks are blocking progress

### 3. Circular Dependency Protection
- DFS algorithm detects cycles of any complexity
- Detailed error messages show the complete cycle path
- Prevents creation of impossible task sequences

### 4. Comprehensive Filtering
- Filter by phase (single or all)
- Filter by status (pending, in_progress, completed)
- Combine filters for precise queries

### 5. Rich Output Formatting
- Status icons (⏳ 🔄 ✅) for quick scanning
- Grouped by phase with counts
- Shows dependency completion progress
- Displays notes when present

---

## Examples of Usage

### Creating a Structured Plan
```python
write_todos({"todos": [
    {"title": "Initial life assessment", "phase": "discovery"},
    {"title": "Identify top 3 priorities", "phase": "discovery", "depends_on": [0]},
    {"title": "Create 90-day action plan", "phase": "planning", "depends_on": [1]},
    {"title": "Weekly check-in system", "phase": "execution"}
]})
```

### Updating with Dependency Enforcement
```python
# This will be blocked until todo_id 0 is completed
update_todo({"todo_id": 1, "status": "in_progress"})
# Returns: "Cannot set 'Identify top 3 priorities' to in_progress
#          because it depends on incomplete tasks: Initial life assessment"

# After completing dependency, this works
update_todo({"todo_id": 0, "status": "completed"})
update_todo({"todo_id": 1, "status": "in_progress"})  # Now succeeds
```

### Filtering Todos
```python
# Show only discovery phase tasks
list_todos({"phase": "discovery"})

# Show all pending tasks across phases
list_todos({"status": "pending"})
```

---

## Challenges and Solutions

### Challenge 1: LangChain Tool Invocation Pattern
**Issue**: Initially invoked tools with direct parameters, but LangChain `StructuredTool` expects dictionary-wrapped arguments.

**Solution**: Updated all tests to wrap parameters in dictionaries (e.g., `{"todos": [...]}` instead of `[...]`).

### Challenge 2: Circular Dependency Algorithm
**Issue**: Needed to detect cycles in potentially disconnected graphs.

**Solution**: Implemented DFS with recursion stack tracking that checks all nodes (not just connected components) and returns detailed cycle paths for debugging.

### Challenge 3: Global State Management
**Issue**: Tests were creating new TodoManager instances, causing state isolation issues.

**Solution**: Used `get_todo_manager()` to access the shared global instance, ensuring tools maintain state across operations.

---

## Files Created/Modified

### Created:
1. `src/tools/planning_tools.py` (390 lines)
2. `tests/test_planning_tools.py` (660 lines, 47 tests)
3. `demo_planning.py` (106 lines)

### Modified:
1. `src/main.py`
   - Added import for planning tools
   - Created planning tool instances
   - Combined with memory tools in `all_tools`
   - Updated system prompt with planning tool documentation

---

## Next Steps / Future Enhancements

### Potential Improvements:
1. **Time Estimation**: Add estimated_duration field to todos for time tracking
2. **Priority Levels**: Add priority (high, medium, low) for better task ordering
3. **Subtasks**: Support hierarchical todo structure (task → subtasks)
4. **Due Dates**: Add deadline tracking with alerts
5. **Tags/Categories**: Enable cross-phase filtering by category
6. **Progress Metrics**: Calculate percentage complete across phases
7. **Archive System**: Move completed todos to archive rather than deleting

### Integration Possibilities:
1. Connect with memory system to persist plans across sessions
2. Enable saving/loading todo lists from files
3. Create specialized subagent for complex plan creation
4. Add AI-assisted todo breakdown (LLM analyzes goal, suggests tasks)

---

## Conclusion

Bead #5 has been successfully completed with all requirements met:

✅ **Three planning tools implemented** (`write_todos`, `update_todo`, `list_todos`) with proper `@tool` decorators
✅ **Phase filtering working** for all 4 phases (discovery, planning, execution, review)
✅ **Dependency tracking functional** with automatic blocking and progress display
✅ **Circular dependency validation complete** using DFS algorithm
✅ **Comprehensive test suite** with 47 tests, 100% pass rate
✅ **Integration with main agent** completed in `src/main.py`
✅ **Demo script validates** all functionality works as expected

The planning system is production-ready and provides a solid foundation for AI agents to create, track, and manage structured todo lists with smart dependency enforcement.

---

**Bead #5 Status**: ✅ COMPLETE