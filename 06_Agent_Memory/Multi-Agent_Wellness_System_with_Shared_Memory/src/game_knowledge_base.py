"""
Game Knowledge Base

Stores and retrieves game content with spoiler-aware filtering.
Uses QDrant for semantic search while maintaining strict metadata controls.

Based on SCHEMA_DESIGN.md - "game_knowledge_base" collection.
"""

from datetime import datetime
from uuid import uuid4
from typing import List, Optional, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from langchain_openai import OpenAIEmbeddings


PROGRESS_ORDER = {
    "intro/tutorial": 0,
    "early_game": 1,
    "mid_game": 2,
    "late_game": 3,
    "endgame": 4,
    "post_game": 5,
    "general": -1,  # Content applicable throughout the game
}


def get_progress_order(progress_marker: str) -> int:
    """
    Get numeric order for progress marker.

    Args:
        progress_marker: Progress marker from PROGRESS_MARKERS

    Returns:
        Integer order value (lower = earlier in game)
    """
    return PROGRESS_ORDER.get(progress_marker, 0)


def is_progress_allowed(content_progress: str, user_progress_marker: str) -> bool:
    """
    Check if content progress is allowed based on user's current progress.

    Args:
        content_progress: Progress marker of the content
        user_progress_marker: User's current progress marker

    Returns:
        True if content is allowed, False otherwise
    """
    content_order = get_progress_order(content_progress)
    user_order = get_progress_order(user_progress_marker)

    # "general" content is always allowed
    if content_progress == "general":
        return True

    # Content is allowed if it's from earlier or same stage as user
    return content_order <= user_order


class GameKnowledgeBase:
    """
    Knowledge base for game content with spoiler-aware search.

    Stores chunks of game information with rich metadata:
    - Game identification (name, display name)
    - Content type (walkthrough, lore, spoiler, gameplay_mechanics, controls, tips)
    - Spoiler flag (explicitly marked spoilers)
    - Progress markers (broad stages for filtering)
    - Source information

    Provides semantic search with intelligent filtering:
    - Spoiler-free queries
    - Progress-based filtering
    - Content type filtering
    """

    COLLECTION_NAME = "game_knowledge_base"

    def __init__(
        self, qdrant_client: QdrantClient, embeddings: Optional[OpenAIEmbeddings] = None
    ):
        """
        Initialize the game knowledge base.

        Args:
            qdrant_client: QDrant client instance
            embeddings: Optional embedding model (defaults to text-embedding-nomic-embed-text-v2-moe)
        """
        self.client = qdrant_client
        self.embeddings = embeddings or OpenAIEmbeddings(
            model="text-embedding-nomic-embed-text-v2-moe",
            base_url="http://192.168.1.79:8080/v1",
            check_embedding_ctx_length=False,
        )

        # Ensure collection exists
        self._ensure_collection()

    def _ensure_collection(self):
        """Create the game_knowledge_base collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        existing_names = {c.name for c in collections}

        if self.COLLECTION_NAME not in existing_names:
            # Use known embedding dimension for text-embedding-nomic-embed-text-v2-moe
            vector_dim = 768

            # Create collection with cosine distance for semantic search
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
            )
            print(f"[GameKnowledgeBase] Created collection: {self.COLLECTION_NAME}")

    def _normalize_game_name(self, game_name: str) -> str:
        """
        Normalize game name for consistent storage.

        Args:
            game_name: Game name to normalize

        Returns:
            Normalized game name (lowercase with underscores)
        """
        return game_name.lower().strip().replace(" ", "_")

    def store_game_content(
        self,
        chunks: List[str],
        metadata: Dict[str, Any],
    ) -> bool:
        """
        Store game content chunks with metadata in the knowledge base.

        Args:
            chunks: List of text chunks to store
            metadata: Metadata dictionary with required fields:
                - game_name: str (will be normalized)
                - game_display_name: str
                - content_type: str (one of CONTENT_TYPES)
                - is_spoiler: bool
                - progress_marker: str (one of PROGRESS_MARKERS)
                - source_url: str
                - source_type: str
                Optional fields:
                - chapter: int
                - section_name: str
                - parent_document_id: str
                - quality_score: float

        Returns:
            True if successfully stored, False otherwise
        """
        try:
            # Validate required metadata fields
            required_fields = [
                "game_name",
                "game_display_name",
                "content_type",
                "is_spoiler",
                "progress_marker",
                "source_url",
                "source_type",
            ]

            for field in required_fields:
                if field not in metadata:
                    print(f"[GameKnowledgeBase] Missing required field: {field}")
                    return False

            # Normalize game name
            normalized_game = self._normalize_game_name(metadata["game_name"])

            # Generate embeddings for all chunks
            print(
                f"[GameKnowledgeBase] Generating embeddings for {len(chunks)} chunks..."
            )
            embeddings_list = [self.embeddings.embed_query(chunk) for chunk in chunks]

            # Generate parent document ID if not provided
            parent_document_id = metadata.get(
                "parent_document_id", f"{normalized_game}_{uuid4().hex[:8]}"
            )

            # Prepare points for QDrant
            points = []
            timestamp = datetime.now().isoformat()

            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
                chunk_id = f"{normalized_game}_{metadata['content_type']}_{idx:03d}"

                payload = {
                    "text": chunk,
                    "game_name": normalized_game,
                    "game_display_name": metadata["game_display_name"],
                    "content_type": metadata["content_type"],
                    "is_spoiler": metadata["is_spoiler"],
                    "progress_marker": metadata["progress_marker"],
                    "source_url": metadata["source_url"],
                    "source_type": metadata["source_type"],
                    "timestamp": timestamp,
                    "chunk_id": chunk_id,
                    "parent_document_id": parent_document_id,
                }

                # Add optional fields if provided
                if "chapter" in metadata:
                    payload["chapter"] = metadata["chapter"]
                if "section_name" in metadata:
                    payload["section_name"] = metadata["section_name"]
                if "quality_score" in metadata:
                    payload["quality_score"] = metadata["quality_score"]

                point = PointStruct(id=str(uuid4()), vector=embedding, payload=payload)
                points.append(point)

            # Batch insert into QDrant
            self.client.upsert(collection_name=self.COLLECTION_NAME, points=points)

            print(
                f"[GameKnowledgeBase] Stored {len(chunks)} chunks for game: "
                f"{metadata['game_display_name']}"
            )
            return True

        except Exception as e:
            print(f"[GameKnowledgeBase] Error storing game content: {e}")
            return False

    def search_game_knowledge(
        self,
        query: str,
        game_name: str,
        user_progress_marker: str = "intro/tutorial",
        avoid_spoilers: bool = True,
        content_types: Optional[List[str]] = None,
        limit: int = 5,
        score_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Search game knowledge with spoiler and progress filtering.

        Args:
            query: Search query (semantic search)
            game_name: Game to search within
            user_progress_marker: User's current progress (default: intro/tutorial)
            avoid_spoilers: If True, filter out is_spoiler=True (default: True)
            content_types: Optional list of content types to filter by
            limit: Maximum number of results (default: 5)
            score_threshold: Minimum similarity score (0.0-1.0, default: 0.5)

        Returns:
            List of matching documents with metadata, sorted by relevance
        """
        try:
            # Normalize game name
            normalized_game = self._normalize_game_name(game_name)

            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)

            # Build QDrant filter
            must_conditions = [
                FieldCondition(key="game_name", match=MatchValue(value=normalized_game))
            ]

            # Add content type filter if specified
            if content_types:
                for content_type in content_types:
                    must_conditions.append(
                        FieldCondition(
                            key="content_type", match=MatchValue(value=content_type)
                        )
                    )

            # Add spoiler filter if avoiding spoilers
            must_not_conditions = []
            if avoid_spoilers:
                must_not_conditions.append(
                    FieldCondition(key="is_spoiler", match=MatchValue(value=True))
                )

            # Create filter object
            filter_obj = Filter(
                must=must_conditions if must_conditions else None,
                must_not=must_not_conditions if must_not_conditions else None,
            )

            # Search QDrant
            search_response = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_embedding,
                query_filter=filter_obj,
                limit=limit * 2,  # Fetch more to filter by progress
            )

            # Filter results by progress marker (application-level filtering)
            user_order = get_progress_order(user_progress_marker)
            filtered_results = []

            for result in search_response.points:
                payload = result.payload
                content_progress = payload.get("progress_marker", "early_game")

                # Check if progress allows this content
                if is_progress_allowed(content_progress, user_progress_marker):
                    filtered_results.append(
                        {
                            "text": payload.get("text", ""),
                            "game_name": payload.get("game_display_name", game_name),
                            "content_type": payload.get("content_type"),
                            "is_spoiler": payload.get("is_spoiler", False),
                            "progress_marker": content_progress,
                            "chapter": payload.get("chapter"),
                            "section_name": payload.get("section_name"),
                            "source_url": payload.get("source_url"),
                            "score": result.score,
                        }
                    )

            # Return only requested limit
            return filtered_results[:limit]

        except Exception as e:
            print(f"[GameKnowledgeBase] Error searching game knowledge: {e}")
            return []

    def get_all_spoilers(self, game_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get all marked spoilers for a specific game.

        Args:
            game_name: Game to get spoilers from
            limit: Maximum number of results

        Returns:
            List of spoiler documents with metadata
        """
        try:
            # Normalize game name
            normalized_game = self._normalize_game_name(game_name)

            # Build filter for spoilers only
            filter_obj = Filter(
                must=[
                    FieldCondition(
                        key="game_name", match=MatchValue(value=normalized_game)
                    ),
                    FieldCondition(key="is_spoiler", match=MatchValue(value=True)),
                ]
            )

            # Search with a dummy embedding (just get all matching)
            dummy_vector = [0.0] * 768

            search_results = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=dummy_vector,
                query_filter=filter_obj,
                limit=limit,
            )

            # Format results
            results = []
            for result in search_results.points:
                payload = result.payload
                results.append(
                    {
                        "text": payload.get("text", ""),
                        "game_name": payload.get("game_display_name", game_name),
                        "content_type": payload.get("content_type"),
                        "progress_marker": payload.get("progress_marker"),
                        "chapter": payload.get("chapter"),
                        "section_name": payload.get("section_name"),
                        "source_url": payload.get("source_url"),
                    }
                )

            return results

        except Exception as e:
            print(f"[GameKnowledgeBase] Error getting spoilers: {e}")
            return []

    def get_content_by_type(
        self, game_name: str, content_type: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get content of a specific type for a game.

        Args:
            game_name: Game to search
            content_type: Type of content (e.g., "walkthrough", "lore")
            limit: Maximum number of results

        Returns:
            List of documents with metadata
        """
        try:
            # Normalize game name
            normalized_game = self._normalize_game_name(game_name)

            # Build filter for content type
            filter_obj = Filter(
                must=[
                    FieldCondition(
                        key="game_name", match=MatchValue(value=normalized_game)
                    ),
                    FieldCondition(
                        key="content_type", match=MatchValue(value=content_type)
                    ),
                ]
            )

            # Search with a dummy embedding
            dummy_vector = [0.0] * 768

            search_results = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=dummy_vector,
                query_filter=filter_obj,
                limit=limit,
            )

            # Format results
            results = []
            for result in search_results.points:
                payload = result.payload
                results.append(
                    {
                        "text": payload.get("text", ""),
                        "game_name": payload.get("game_display_name", game_name),
                        "content_type": payload.get("content_type"),
                        "is_spoiler": payload.get("is_spoiler", False),
                        "progress_marker": payload.get("progress_marker"),
                        "chapter": payload.get("chapter"),
                        "section_name": payload.get("section_name"),
                    }
                )

            return results

        except Exception as e:
            print(f"[GameKnowledgeBase] Error getting content by type: {e}")
            return []

    def delete_game_content(self, game_name: str) -> bool:
        """
        Delete all content for a specific game.

        Args:
            game_name: Game to delete

        Returns:
            True if successfully deleted, False otherwise
        """
        try:
            # Normalize game name
            normalized_game = self._normalize_game_name(game_name)

            # Build filter for all game content
            filter_obj = Filter(
                must=[
                    FieldCondition(
                        key="game_name", match=MatchValue(value=normalized_game)
                    )
                ]
            )

            # Delete all matching points
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=filter_obj,
            )

            print(f"[GameKnowledgeBase] Deleted all content for: {game_name}")
            return True

        except Exception as e:
            print(f"[GameKnowledgeBase] Error deleting game content: {e}")
            return False


__all__ = [
    "GameKnowledgeBase",
    "PROGRESS_ORDER",
    "get_progress_order",
    "is_progress_allowed",
]
