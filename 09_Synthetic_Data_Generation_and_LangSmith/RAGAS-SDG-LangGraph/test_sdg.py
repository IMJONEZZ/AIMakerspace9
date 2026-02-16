import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from evol_instruct_graph import run_evol_instruct_sdg


def load_and_split_documents(data_dir: str, chunk_size: int = 500, overlap: int = 50):
    loader = TextLoader(data_dir)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)

    for i, chunk in enumerate(chunks[:10]):
        chunk.metadata["question"] = f"What is described in section {i + 1}?"

    return chunks


def display_results(results):
    print("\n" + "=" * 80)
    print("EVOL INSTRUCT SYNTHETIC DATA GENERATION RESULTS")
    print("=" * 80)

    evolved_questions = results.get("evolved_questions", [])
    q_a_pairs = results.get("q_a_pairs", [])
    contexts = results.get("contexts", [])

    print(f"\n✓ Total Evolved Questions: {len(evolved_questions)}")
    print(f"✓ Total Q&A Pairs: {len(q_a_pairs)}")
    print(f"✓ Total Contexts Retrieved: {len(contexts)}")

    evolution_counts = {}
    for q in evolved_questions:
        evo_type = q.get("evolution_type", "unknown")
        evolution_counts[evo_type] = evolution_counts.get(evo_type, 0) + 1

    print("\n" + "-" * 80)
    print("EVOLVED QUESTIONS BY TYPE:")
    print("-" * 80)
    for evo_type, count in evolution_counts.items():
        print(f"  {evo_type}: {count}")

    print("\n" + "-" * 80)
    print("SAMPLE QUESTIONS BY EVOLUTION TYPE:")
    print("-" * 80)

    for evo_type in evolution_counts.keys():
        sample = next(
            (q for q in evolved_questions if q.get("evolution_type") == evo_type), None
        )
        if sample:
            print(f"\n  [{evo_type.upper()}]")
            print(f"  Question: {sample.get('question', 'N/A')}")
            if "original_question" in sample:
                print(f"  Original: {sample.get('original_question', 'N/A')}")

    print("\n" + "-" * 80)
    print("SAMPLE Q&A PAIRS:")
    print("-" * 80)

    for i, qa in enumerate(q_a_pairs[:2]):
        print(f"\n  [Pair {i + 1}]")
        question_id = qa.get("question_id", "unknown")

        matched_question = next(
            (q for q in evolved_questions if q.get("id") == question_id), None
        )
        print(
            f"  Question: {matched_question.get('question') if matched_question else 'N/A'}"
        )
        print(f"  Answer: {qa.get('answer', 'N/A')[:200]}...")

    print("\n" + "-" * 80)
    print("SAMPLE CONTEXTS:")
    print("-" * 80)

    for i, ctx in enumerate(contexts[:2]):
        print(f"\n  [Context {i + 1}]")
        print(f"  Question ID: {ctx.get('question_id', 'unknown')}")
        relevant_contexts = ctx.get("relevant_contexts", [])
        print(f"  Number of Contexts Retrieved: {len(relevant_contexts)}")
        if relevant_contexts:
            print(f"  Sample Context: {relevant_contexts[0][:150]}...")


def verify_structure(results):
    print("\n" + "-" * 80)
    print("STRUCTURE VERIFICATION:")
    print("-" * 80)

    required_keys = ["evolved_questions", "q_a_pairs", "contexts"]
    all_present = True

    for key in required_keys:
        present = key in results
        status = "✓" if present else "✗"
        print(f"  {status} {key}: {'present' if present else 'missing'}")
        if not present:
            all_present = False
        elif isinstance(results[key], list):
            print(f"    Type: list")
            print(f"    Length: {len(results[key])}")
        else:
            print(f"    Type: {type(results[key]).__name__}")
            all_present = False

    print(
        f"\n  {'✓' if all_present else '✗'} Structure verification: {'PASSED' if all_present else 'FAILED'}"
    )

    return all_present


def main():
    print("\n" + "=" * 80)
    print("TEST SCRIPT: EVOL INSTRUCT LANGGRAPH SDG PIPELINE")
    print("=" * 80)

    data_dir = Path(__file__).parent.parent / "data"

    health_file = data_dir / "HealthWellnessGuide.txt"
    mental_health_file = data_dir / "MentalHealthGuide.txt"

    print(f"\n✓ Loading documents from: {data_dir}")
    print(f"  - HealthWellnessGuide.txt")
    print(f"  - MentalHealthGuide.txt")

    try:
        health_docs = load_and_split_documents(str(health_file))
        mental_health_docs = load_and_split_documents(str(mental_health_file))

        all_chunks = health_docs + mental_health_docs
        print(f"✓ Total document chunks created: {len(all_chunks)}")

    except Exception as e:
        print(f"\n✗ Error loading documents: {e}")
        return

    try:
        print("\n" + "-" * 80)
        print("RUNNING EVOL INSTRUCT LANGGRAPH PIPELINE")
        print("-" * 80)

        results = run_evol_instruct_sdg(all_chunks)

        print("✓ Pipeline execution completed")

    except Exception as e:
        print(f"\n✗ Error running pipeline: {e}")
        import traceback

        traceback.print_exc()
        return

    display_results(results)
    verify_structure(results)

    print("\n" + "=" * 80)
    print("TEST SCRIPT COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
