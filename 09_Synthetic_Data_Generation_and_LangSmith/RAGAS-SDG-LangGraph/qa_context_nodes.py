from typing import Dict, List
import json

from langchain_core.messages import HumanMessage, SystemMessage
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore


class QAContextNode:
    def __init__(self):
        self.client = OpenAI(base_url="http://192.168.1.79:8080/v1", api_key="dummy")
        self.model = "glm-4.7"
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-nomic-embed-text-v2-moe",
            openai_api_base="http://192.168.1.79:8080/v1",
            openai_api_key="dummy",
        )


def generate_answers_node(state: Dict) -> Dict:
    node = QAContextNode()

    evolved_questions = state.get("evolved_questions", [])
    q_a_pairs = state.get("q_a_pairs", [])

    if not evolved_questions:
        return {**state, "current_step": "answer_generation_skipped"}

    prompt = """You are an expert question answering system. Your task is to provide accurate, comprehensive answers based on the given context.

Instructions:
1. Read the question carefully
2. If provided, use the context information to formulate your answer
3. Provide a clear, detailed, and accurate response
4. If the information is not in the context, state that clearly
5. Be specific and concise while covering all relevant points

Return ONLY a valid JSON object with this structure:
{{
    "question_id": "{question_id}",
    "answer": "your comprehensive answer to the question"
}}

Question:
{question}"""

    new_qa_pairs = []

    for idx, question_data in enumerate(evolved_questions):
        question_text = question_data.get("question", "")
        question_id = f"q_{idx}"

        response = node.client.chat.completions.create(
            model=node.model,
            messages=[
                SystemMessage(
                    content="You are a helpful assistant that provides accurate, detailed answers to questions."
                ),
                HumanMessage(
                    content=prompt.format(
                        question_id=question_id, question=question_text
                    )
                ),
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        try:
            result = json.loads(response.choices[0].message.content)

            qa_pair = {
                "question_id": question_id,
                "answer": result.get("answer", ""),
                "question": question_text,
            }
            new_qa_pairs.append(qa_pair)
        except (json.JSONDecodeError, KeyError):
            qa_pair = {
                "question_id": question_id,
                "answer": response.choices[0].message.content,
                "question": question_text,
            }
            new_qa_pairs.append(qa_pair)

    return {
        **state,
        "q_a_pairs": q_a_pairs + new_qa_pairs,
        "current_step": "answer_generation_complete",
    }


def retrieve_contexts_node(state: Dict) -> Dict:
    node = QAContextNode()

    evolved_questions = state.get("evolved_questions", [])
    contexts = state.get("contexts", [])

    if not evolved_questions:
        return {**state, "current_step": "context_retrieval_skipped"}

    try:
        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=node.embeddings,
            collection_name="documents",
            url="http://localhost:6333",
        )
    except Exception:
        try:
            vector_store = QdrantVectorStore.from_existing_collection(
                embedding=node.embeddings,
                collection_name="my_documents",
                url="http://localhost:6333",
            )
        except Exception as e:
            return {
                **state,
                "current_step": f"context_retrieval_failed: {str(e)}",
            }

    new_contexts = []

    for idx, question_data in enumerate(evolved_questions):
        question_text = question_data.get("question", "")
        question_id = f"q_{idx}"

        try:
            retrieved_docs = vector_store.similarity_search(question_text, k=5)

            relevant_contexts = [doc.page_content for doc in retrieved_docs]

            context_entry = {
                "question_id": question_id,
                "relevant_contexts": relevant_contexts,
            }
            new_contexts.append(context_entry)
        except Exception as e:
            context_entry = {
                "question_id": question_id,
                "relevant_contexts": [],
                "error": str(e),
            }
            new_contexts.append(context_entry)

    return {
        **state,
        "contexts": contexts + new_contexts,
        "current_step": "context_retrieval_complete",
    }
