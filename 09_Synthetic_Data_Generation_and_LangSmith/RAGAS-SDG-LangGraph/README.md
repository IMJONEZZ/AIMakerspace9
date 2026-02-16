# RAGAS-SDG-LangGraph

A synthetic data generation system implementing Evol-Instruct methodology using LangGraph for intelligent orchestration. This project generates diverse, evolved question-answer pairs from source documents with configurable evolution strategies.

## Overview

RAGAS-SDG-LangGraph combines RAG (Retrieval-Augmented Generation) principles with Evol-Instruct to create high-quality synthetic training data. The system uses LangGraph's stateful workflows to orchestrate three evolution types:

- **Simple Evolution**: Paraphrases and rewords questions while maintaining intent
- **Multi-Context Evolution**: Creates questions requiring synthesis across multiple documents  
- **Reasoning Evolution**: Adds complexity through constraints, multi-step reasoning, and analytical requirements

## Features

- **Intelligent Routing**: Automatically selects evolution strategies based on document characteristics
- **Configurable Evolution Modes**: Run all evolutions sequentially or selectively route based on content analysis
- **Vector-Based Context Retrieval**: Uses Qdrant vector store for efficient context retrieval
- **Comprehensive QA Generation**: Produces question-answer pairs with retrieved contexts
- **Flexible Orchestration**: Multiple convenience functions for different use cases

## Installation

### Prerequisites

- Python 3.9+
- Qdrant vector database (local or remote)
- OpenAI-compatible LLM endpoint

### Dependencies

```bash
pip install langgraph langchain langchain-openai langchain-qdrant openai qdrant-client
```

### Setup

1. Configure your LLM endpoint in `evolution_nodes.py` and `qa_context_nodes.py`:
   ```python
   self.client = OpenAI(base_url="YOUR_LLM_ENDPOINT", api_key="your_api_key")
   ```

2. Set up Qdrant vector database:
   ```bash
   # Using Docker
   docker run -p 6333:6333 qdrant/qdrant
   ```

3. Configure embedding model in `evol_instruct_graph.py`:
   ```python
   embeddings = OpenAIEmbeddings(
       model="text-embedding-nomic-embed-text-v2-moe",
       openai_api_base="YOUR_LLM_ENDPOINT"
   )
   ```

## Usage

### Basic Example - Run All Evolutions

```python
from langchain_core.documents import Document
from orchestrator import run_all_evolutions

# Prepare documents with metadata containing base questions
documents = [
    Document(
        page_content="Your document content here...",
        metadata={"question": "What is this about?"}
    )
]

# Run all three evolution types sequentially
result = run_all_evolutions(documents)

print(f"Generated {len(result['evolved_questions'])} questions")
print(f"Created {len(result['q_a_pairs'])} Q&A pairs")
```

### Selective Evolution with Custom Ratios

```python
from orchestrator import run_selective_evolutions

# Configure evolution weights
evolution_ratios = {
    "simple": 0.4,
    "multi_context": 0.3,
    "reasoning": 0.3
}

# Run selective evolution based on document analysis
result = run_selective_evolutions(
    documents=documents,
    evolution_ratios=evolution_ratios
)
```

### Reasoning-Focused Evolution

```python
from orchestrator import run_reasoning_focused_evolutions

# Prioritize reasoning-intensive questions
result = run_reasoning_focused_evolutions(documents)
```

### Multi-Context Focused Evolution

```python
from orchestrator import run_multi_context_focused_evolutions

# Prioritize questions requiring multi-document synthesis
result = run_multi_context_focused_evolutions(documents)
```

### Using the Core Graph Directly

```python
from evol_instruct_graph import run_evol_instruct_sdg

# Full control over evolution parameters
result = run_evol_instruct_sdg(
    documents=documents,
    evolution_mode="selective",
    evolution_ratios={
        "simple": 0.33,
        "multi_context": 0.34,
        "reasoning": 0.33
    }
)

# Access results
evolved_questions = result["evolved_questions"]
qa_pairs = result["q_a_pairs"]
contexts = result["contexts"]
```

## Output Format

The system returns a dictionary with three keys:

```python
{
    "evolved_questions": [
        {
            "id": "q_0",
            "question": "Evolved question text",
            "evolution_type": "reasoning"
        },
        ...
    ],
    "q_a_pairs": [
        {
            "question_id": "q_0",
            "answer": "Generated answer text"
        },
        ...
    ],
    "contexts": [
        {
            "question_id": "q_0",
            "relevant_contexts": ["Context 1", "Context 2", ...]
        },
        ...
    ]
}
```

## Configuration Options

### Evolution Mode (`evolution_mode`)

- `"all"`: Runs all three evolution types sequentially (default)
- `"selective"`: Intelligently routes based on document characteristics

### Evolution Ratios (`evolution_ratios`)

Dictionary mapping evolution types to weights:
- `simple`: Weight for paraphrasing evolution
- `multi_context`: Weight for multi-document synthesis
- `reasoning`: Weight for reasoning-intensive evolution

Ratios must sum to approximately 1.0.

### Document Characteristics Thresholds

- `min_doc_length_for_reasoning`: Minimum average document length for reasoning evolution (default: 300)
- `max_doc_count_for_simple`: Maximum document count to use simple evolution (default: 5)

## File Structure

```
RAGAS-SDG-LangGraph/
├── evol_instruct_graph.py    # Core LangGraph workflow and state management
├── evolution_nodes.py        # Evolution node implementations (simple, multi-context, reasoning)
├── qa_context_nodes.py       # Answer generation and context retrieval nodes
├── orchestrator.py           # High-level orchestration functions
├── test_sdg.py              # Test suite for synthetic data generation
├── ROUTING_LOGIC.md         # Detailed documentation of routing logic
└── README.md                # This file
```

## Architecture

### LangGraph Workflow

The system uses two graph implementations:

1. **Sequential Graph** (`create_evol_instruct_graph`):
   - Runs evolutions in fixed order: simple → multi-context → reasoning
   - Simpler execution path, predictable behavior

2. **Routing Graph** (`create_evol_instruct_graph_with_routing`):
   - Analyzes document characteristics first
   - Routes to appropriate evolution type based on configuration and analysis
   - More efficient, adapts to content

### State Management

The `EvolInstructState` TypedDict manages:
- Input documents
- Accumulated evolved questions
- Generated Q&A pairs
- Retrieved contexts
- Evolution configuration and tracking

## Testing

Run the test suite:

```bash
python test_sdg.py
```

## Advanced Usage

### Custom Evolution Prompts

Modify evolution prompts in `evolution_nodes.py` to customize question generation behavior.

### Document Chunking

For large documents, use the chunking utility:

```python
from evol_instruct_graph import chunk_documents

chunks = chunk_documents(
    documents=large_documents,
    chunk_size=500,
    chunk_overlap=50
)
```

### Vector Store Setup

Set up a persistent vector store:

```python
from evol_instruct_graph import setup_vector_store

vector_store = setup_vector_store(
    documents=documents,
    collection_name="my_collection",
    location="./qdrant_data"
)
```

## Evolution Strategy Details

### Simple Evolution
- Paraphrases questions using different wording
- Maintains original intent and complexity
- Useful for increasing question diversity

### Multi-Context Evolution
- Requires ≥2 documents
- Synthesizes information across document boundaries
- Creates questions that cannot be answered from single sources

### Reasoning Evolution
- Adds constraints and conditions
- Requires multi-step thinking
- Introduces comparative or analytical dimensions
- Best suited for longer, complex documents

## Troubleshooting

### Context Retrieval Fails

Ensure Qdrant is running and collection exists:
```bash
# Check Qdrant status
curl http://localhost:6333/collections/documents
```

### LLM Connection Errors

Verify your endpoint configuration in node files:
```python
self.client = OpenAI(base_url="YOUR_ENDPOINT", api_key="your_key")
```

### Evolution Skipped

Check document characteristics:
- Multi-context requires ≥2 documents
- Reasoning benefits from longer documents (>300 chars)
- Simple evolution works best with ≤5 documents

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style conventions
- Functions include docstrings
- New features include tests
- Documentation is updated

## License

This project is part of the synthetic data generation research initiative.

## References

- [Evol-Instruct: Evolving Instructions for Large Language Models](https://arxiv.org/abs/2304.12244)
- [LangGraph Documentation](https://langgraph.dev/)
- [RAGAS Framework](https://docs.ragas.io/)

## Acknowledgments

Built with:
- LangGraph for workflow orchestration
- Qdrant for vector storage and retrieval
- OpenAI API for LLM interactions