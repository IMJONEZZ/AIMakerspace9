from typing import List, Dict
from langchain_core.documents import Document

from evol_instruct_graph import run_evol_instruct_sdg


def orchestrator(
    documents: List[Document],
    evolution_mode: str = "all",
    evolution_ratios: Dict[str, float] | None = None,
) -> Dict:
    """
    Orchestrator for the EvolInstruct synthetic data generation pipeline.

    Args:
        documents: List of Document objects to generate questions from
        evolution_mode: "all" (run all three evolution types sequentially) or
                       "selective" (route based on document characteristics)
        evolution_ratios: Optional dict with weights for each evolution type:
                         {"simple": 0.33, "multi_context": 0.34, "reasoning": 0.33}

    Returns:
        Dictionary containing evolved questions, Q&A pairs, and retrieved contexts
    """

    if evolution_mode not in ["all", "selective"]:
        raise ValueError(
            f"evolution_mode must be 'all' or 'selective', got '{evolution_mode}'"
        )

    if evolution_ratios:
        valid_types = {"simple", "multi_context", "reasoning"}
        provided_types = set(evolution_ratios.keys())

        if not provided_types.issubset(valid_types):
            invalid = provided_types - valid_types
            raise ValueError(
                f"Invalid evolution types in ratios: {invalid}. "
                f"Valid types are: {valid_types}"
            )

        total = sum(evolution_ratios.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"evolution_ratios must sum to approximately 1.0, got {total}"
            )

    result = run_evol_instruct_sdg(
        documents=documents,
        evolution_mode=evolution_mode,  # type: ignore
        evolution_ratios=evolution_ratios,
    )

    return result


def run_all_evolutions(documents: List[Document]) -> Dict:
    """
    Convenience function to run all three evolution types sequentially.

    This is the default behavior and ensures comprehensive coverage of
    simple paraphrasing, multi-context synthesis, and reasoning-intensive questions.

    Args:
        documents: List of Document objects to generate questions from

    Returns:
        Dictionary containing evolved questions, Q&A pairs, and retrieved contexts
    """
    return orchestrator(documents=documents, evolution_mode="all")


def run_selective_evolutions(
    documents: List[Document],
    evolution_ratios: Dict[str, float] | None = None,
) -> Dict:
    """
    Convenience function to run selective evolution based on document characteristics.

    The routing logic considers:
    - Document length (longer docs favor reasoning evolution)
    - Document count (fewer docs favor simple evolution, more docs favor multi-context)
    - Vocabulary complexity
    - Configurable ratios

    Args:
        documents: List of Document objects to generate questions from
        evolution_ratios: Optional dict with weights for each evolution type

    Returns:
        Dictionary containing evolved questions, Q&A pairs, and retrieved contexts
    """

    if evolution_ratios is None:
        evolution_ratios = {"simple": 0.4, "multi_context": 0.3, "reasoning": 0.3}

    return orchestrator(
        documents=documents,
        evolution_mode="selective",
        evolution_ratios=evolution_ratios,
    )


def run_balanced_evolutions(documents: List[Document]) -> Dict:
    """
    Convenience function for balanced selective evolution.

    Uses equal weights (1/3 each) for all three evolution types when routing.

    Args:
        documents: List of Document objects to generate questions from

    Returns:
        Dictionary containing evolved questions, Q&A pairs, and retrieved contexts
    """
    evolution_ratios = {"simple": 0.33, "multi_context": 0.34, "reasoning": 0.33}

    return orchestrator(
        documents=documents,
        evolution_mode="selective",
        evolution_ratios=evolution_ratios,
    )


def run_reasoning_focused_evolutions(documents: List[Document]) -> Dict:
    """
    Convenience function for reasoning-focused evolution.

    Prioritizes reasoning-intensive questions while still including other types.

    Args:
        documents: List of Document objects to generate questions from

    Returns:
        Dictionary containing evolved questions, Q&A pairs, and retrieved contexts
    """
    evolution_ratios = {"simple": 0.2, "multi_context": 0.3, "reasoning": 0.5}

    return orchestrator(
        documents=documents,
        evolution_mode="selective",
        evolution_ratios=evolution_ratios,
    )


def run_multi_context_focused_evolutions(documents: List[Document]) -> Dict:
    """
    Convenience function for multi-context focused evolution.

    Prioritizes questions that require synthesizing information from multiple documents.

    Args:
        documents: List of Document objects to generate questions from

    Returns:
        Dictionary containing evolved questions, Q&A pairs, and retrieved contexts
    """
    evolution_ratios = {"simple": 0.2, "multi_context": 0.6, "reasoning": 0.2}

    return orchestrator(
        documents=documents,
        evolution_mode="selective",
        evolution_ratios=evolution_ratios,
    )
