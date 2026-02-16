# Conditional Routing Logic for EvolInstruct SDG

## Summary

I have implemented intelligent conditional routing logic for the EvolInstruct synthetic data generation workflow in `evol_instruct_graph.py` and added an orchestrator module with convenient configuration functions.

## Key Components

### 1. Document Characterization (`analyze_document_characteristics`)

Analyzes documents to extract key metrics used for routing decisions:
- **Document Count**: Number of document chunks
- **Average Length**: Mean length of all documents in characters
- **Total Length**: Sum of all document lengths
- **Vocabulary Complexity**: Unique word ratio (unique words / total words)

### 2. Conditional Edge Functions

#### `select_evolution_type(state)`
Routes to the appropriate evolution node based on:
- **Evolution Mode** ("all" or "selective")
- **Document characteristics**
- **Configurable evolution ratios**

**In "all" mode**: Runs all three evolutions sequentially (simple → multi_context → reasoning)

**In "selective" mode**: Uses weighted random selection with dynamic adjustment:
- **Reasoning evolution** weight reduced by 70% if avg doc length < min_threshold (300 chars)
- **Simple evolution** weight reduced by 50% if doc count > max_threshold (5 docs)
- **Multi-context evolution** weight reduced by 90% if doc count < 2

#### `should_continue_evolution(state)`
Determines whether to continue evolving or proceed to answer generation:
- **In "all" mode**: Continues until all three evolutions are completed
- **In "selective" mode**:
  - Continues if available evolutions exist and less than 2 types completed
  - Stops after completing 1-2 evolution types based on document suitability

### 3. Graph Structure

#### Original Graph (`create_evol_instruct_graph`)
```
START → simple_evolution → multi_context_evolution → reasoning_evolution 
      → generate_answers → retrieve_contexts → END
```

#### New Routing Graph (`create_evol_instruct_graph_with_routing`)
```
START → analyze_docs
        ↓ (select_evolution_type)
    ┌───┴─────┬───────────┐
simple      multi_     reasoning
evolution  context    evolution
    └────┬───┴─────────┘
         ↓ (should_continue_evolution)
    ┌────┴─────┐
continue  generate_answers
   ↑          ↓
analyze_docs → retrieve_contexts → END
```

### 4. Configuration Parameters

#### `EvolutionConfig`
- `evolution_mode`: "all" (default) or "selective"
- `evolution_ratios`: Dict with weights for each type (default: 0.33, 0.34, 0.33)
- `min_doc_length_for_reasoning`: Minimum avg length for reasoning evolution (default: 300)
- `max_doc_count_for_simple`: Maximum doc count to favor simple evolution (default: 5)

### 5. Orchestrator Module (`orchestrator.py`)

Provides convenient functions for different use cases:

#### `orchestrator(documents, evolution_mode="all", evolution_ratios=None)`
Main orchestrator with full configuration control

#### `run_all_evolutions(documents)`
Runs all three evolution types sequentially (default behavior)

#### `run_selective_evolutions(documents, evolution_ratios=None)`
Routes based on document characteristics with custom ratios

#### `run_balanced_evolutions(documents)`
Selective mode with equal weights (1/3 each)

#### `run_reasoning_focused_evolutions(documents)`
Prioritizes reasoning evolution (simple: 0.2, multi_context: 0.3, reasoning: 0.5)

#### `run_multi_context_focused_evolutions(documents)`
Prioritizes multi-context evolution (simple: 0.2, multi_context: 0.6, reasoning: 0.2)

## Usage Examples

```python
from langchain_core.documents import Document
from orchestrator import (
    run_all_evolutions,
    run_selective_evolutions,
    run_reasoning_focused_evolutions
)

documents = [Document(page_content="...")]

# Option 1: Run all evolutions (default)
result = run_all_evolutions(documents)

# Option 2: Selective routing with custom ratios
result = run_selective_evolutions(
    documents,
    evolution_ratios={"simple": 0.5, "multi_context": 0.3, "reasoning": 0.2}
)

# Option 3: Focus on reasoning questions
result = run_reasoning_focused_evolutions(documents)
```

## Routing Logic Flow

1. **Analysis Phase**: Document characteristics are computed
2. **Selection Phase**: Based on mode and config, select next evolution type
3. **Execution Phase**: Run selected evolution node
4. **Continuation Check**: Determine if more evolutions needed
5. **Loop** or **Proceed**: Return to analysis or continue to answer generation

## Benefits

- **Adaptive**: Routing adapts to document characteristics
- **Configurable**: Flexible ratio thresholds and weights
- **Efficient**: Selective mode conserves compute for unsuitable evolution types
- **Backward Compatible**: Default "all" mode preserves original behavior