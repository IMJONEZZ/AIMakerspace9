"""
Game Tracking System

Tracks which games have been processed to avoid redundant web fetching.
Uses QDrant for persistent storage of game processing metadata.

Based on SCHEMA_DESIGN.md - "game_tracking" collection.
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


class GameTracker:
    """
    Tracks processed games to prevent redundant web fetching.

    Stores metadata about processed games including:
    - Processing timestamps
    - Number of chunks stored in knowledge base
    - Source URLs where content was fetched from
    - Last update timestamps

    Uses QDrant for persistent storage.
    """

    COLLECTION_NAME = "game_tracking"

    def __init__(
        self, qdrant_client: QdrantClient, embeddings: Optional[OpenAIEmbeddings] = None
    ):
        """
        Initialize the game tracker.

        Args:
            qdrant_client: QDrant client instance
            embeddings: Optional embedding model (not needed for tracking but kept for consistency)
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
        """Create the game_tracking collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        existing_names = {c.name for c in collections}

        if self.COLLECTION_NAME not in existing_names:
            # Use known embedding dimension for text-embedding-nomic-embed-text-v2-moe
            vector_dim = 768

            # Create collection
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
            )
            print(f"[GameTracker] Created collection: {self.COLLECTION_NAME}")

    def _normalize_game_name(self, game_name: str) -> str:
        """
        Normalize game name for consistent storage.

        Args:
            game_name: Game name to normalize

        Returns:
            Normalized game name (lowercase with underscores)
        """
        return game_name.lower().strip().replace(" ", "_")

    def check_game_processed(self, game_name: str) -> bool:
        """
        Check if a game has already been processed.

        Args:
            game_name: Game name to check

        Returns:
            True if game has been processed, False otherwise
        """
        normalized_name = self._normalize_game_name(game_name)

        try:
            # Search for the game by filtering on game_name
            filter_query = Filter(
                must=[
                    FieldCondition(
                        key="game_name", match=MatchValue(value=normalized_name)
                    )
                ]
            )

            results = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=filter_query,
                limit=1,
            )

            # results[0] contains the points, results[1] is the offset
            points = results[0]

            return len(points) > 0

        except Exception as e:
            print(f"[GameTracker] Error checking if {game_name} is processed: {e}")
            return False

    def mark_game_processed(
        self,
        game_name: str,
        chunk_count: int = 0,
        source_urls: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Mark a game as processed with metadata.

        Args:
            game_name: Game name to mark as processed
            chunk_count: Number of chunks stored in knowledge base
            source_urls: List of URLs where content was fetched from
            metadata: Additional metadata (optional)

        Returns:
            True if successfully marked, False otherwise
        """
        normalized_name = self._normalize_game_name(game_name)

        try:
            # Check if already exists
            if self.check_game_processed(game_name):
                # Update existing record
                results = self.client.scroll(
                    collection_name=self.COLLECTION_NAME,
                    scroll_filter={
                        "must": [
                            {"key": "game_name", "match": {"value": normalized_name}}
                        ]
                    },
                    limit=1,
                )

                points = results[0]
                if len(points) > 0:
                    point_id = points[0].id
                    current_payload = points[0].payload

                    # Update the existing point
                    self.client.set_payload(
                        collection_name=self.COLLECTION_NAME,
                        payload={
                            "chunk_count": chunk_count
                            if chunk_count > 0
                            else current_payload.get("chunk_count", 0),
                            "source_urls": source_urls
                            if source_urls
                            else current_payload.get("source_urls", []),
                            **(metadata or {}),
                            "last_updated": datetime.now().isoformat(),
                        },
                        points=[point_id],
                    )

                    print(f"[GameTracker] Updated processed game: {game_name}")
                    return True

            # Create new point
            point_id = f"{normalized_name}_tracking"

            payload = {
                "game_name": normalized_name,
                "game_display_name": game_name.strip(),
                "processed_at": datetime.now().isoformat(),
                "chunk_count": chunk_count,
                "source_urls": source_urls or [],
                "last_updated": datetime.now().isoformat(),
            }

            # Add custom metadata
            if metadata:
                payload.update(metadata)

            # Create a dummy vector (not used for search, but required by QDrant)
            # Use zeros since we don't need semantic search for tracking
            dummy_vector = [0.0] * 768

            point = PointStruct(id=str(uuid4()), vector=dummy_vector, payload=payload)

            points = results[0]

            games = []
            for point in points:
                games.append(
                    {
                        "game_name": point.payload.get("game_display_name", "Unknown"),
                        "normalized_name": point.payload.get("game_name", ""),
                        "processed_at": point.payload.get("processed_at"),
                        "chunk_count": point.payload.get("chunk_count", 0),
                        "source_urls": point.payload.get("source_urls", []),
                        "last_updated": point.payload.get("last_updated"),
                    }
                )

            return games

        except Exception as e:
            print(f"[GameTracker] Error getting processed games: {e}")
            return []

    def get_game_metadata(self, game_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed metadata for a specific processed game.

        Args:
            game_name: Game name to look up

        Returns:
            Dictionary with game metadata, or None if not found
        """
        normalized_name = self._normalize_game_name(game_name)

        try:
            results = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter={
                    "must": [{"key": "game_name", "match": {"value": normalized_name}}]
                },
                limit=1,
            )

            points = results[0]

            if len(points) > 0:
                return points[0].payload

            return None

        except Exception as e:
            print(f"[GameTracker] Error getting metadata for {game_name}: {e}")
            return None

    def remove_game(self, game_name: str) -> bool:
        """
        Remove a game from tracking (e.g., for re-processing).

        Args:
            game_name: Game name to remove

        Returns:
            True if successfully removed, False otherwise
        """
        normalized_name = self._normalize_game_name(game_name)

        try:
            results = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter={
                    "must": [{"key": "game_name", "match": {"value": normalized_name}}]
                },
                limit=1,
            )

            points = results[0]

            if len(points) > 0:
                point_id = points[0].id
                self.client.delete(
                    collection_name=self.COLLECTION_NAME, points_selector=[point_id]
                )

                print(f"[GameTracker] Removed game from tracking: {game_name}")
                return True

            return False

        except Exception as e:
            print(f"[GameTracker] Error removing {game_name}: {e}")
            return False


__all__ = ["GameTracker"]
