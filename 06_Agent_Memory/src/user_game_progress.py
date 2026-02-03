"""
User Game Progress Tracking

Tracks individual user progress in games for spoiler-aware responses.
Uses QDrant for persistent storage of user-game progress pairs.
"""

from datetime import datetime
from typing import Optional, List

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


PROGRESS_MARKERS = [
    "intro/tutorial",
    "early_game",
    "mid_game",
    "late_game",
    "endgame",
    "post_game",
]


class UserGameProgress:
    """
    Tracks user progress in games for spoiler control.

    Stores per-user, per-game progress markers to enable
    spoiler-aware responses from specialist agents.
    """

    COLLECTION_NAME = "user_game_progress"

    def __init__(
        self, qdrant_client: QdrantClient, embeddings: Optional[OpenAIEmbeddings] = None
    ):
        """
        Initialize the user game progress tracker.

        Args:
            qdrant_client: QDrant client instance
            embeddings: Optional embedding model (not needed for tracking)
        """
        self.client = qdrant_client
        self.embeddings = embeddings or OpenAIEmbeddings(
            model="text-embedding-nomic-embed-text-v2-moe",
            base_url="http://192.168.1.79:8080/v1",
            check_embedding_ctx_length=False,
        )

        self._ensure_collection()

    def _ensure_collection(self):
        """Create the user_game_progress collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        existing_names = {c.name for c in collections}

        if self.COLLECTION_NAME not in existing_names:
            vector_dim = 768

            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
            )
            print(f"[UserGameProgress] Created collection: {self.COLLECTION_NAME}")

    def _normalize_game_name(self, game_name: str) -> str:
        """
        Normalize game name for consistent storage.

        Args:
            game_name: Game name to normalize

        Returns:
            Normalized game name (lowercase with underscores)
        """
        return game_name.lower().strip().replace(" ", "_")

    def _validate_progress_marker(self, progress_marker: str) -> bool:
        """
        Validate that a progress marker is in the allowed list.

        Args:
            progress_marker: Progress marker to validate

        Returns:
            True if valid, False otherwise
        """
        return progress_marker in PROGRESS_MARKERS

    def update_progress(
        self,
        user_id: str,
        game_name: str,
        progress_marker: Optional[str] = None,
    ) -> bool:
        """
        Update or create user progress for a game.

        Args:
            user_id: Unique identifier for the user
            game_name: Name of the game
            progress_marker: Current progress marker (defaults to 'intro/tutorial')

        Returns:
            True if successfully updated, False otherwise
        """
        normalized_name = self._normalize_game_name(game_name)

        if progress_marker is None:
            progress_marker = "intro/tutorial"

        if not self._validate_progress_marker(progress_marker):
            print(
                f"[UserGameProgress] Invalid progress marker: {progress_marker}. "
                f"Must be one of: {PROGRESS_MARKERS}"
            )
            return False

        try:
            from uuid import uuid4

            results = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                        FieldCondition(
                            key="game_name", match=MatchValue(value=normalized_name)
                        ),
                    ]
                ),
                limit=1,
            )

            points = results[0]

            payload = {
                "user_id": user_id,
                "game_name": normalized_name,
                "game_display_name": game_name.strip(),
                "progress_marker": progress_marker,
                "last_updated": datetime.now().isoformat(),
            }

            if len(points) > 0:
                point_id = points[0].id
                self.client.set_payload(
                    collection_name=self.COLLECTION_NAME,
                    payload=payload,
                    points=[point_id],
                )
                print(
                    f"[UserGameProgress] Updated progress for user {user_id} in {game_name}: {progress_marker}"
                )
            else:
                dummy_vector = [0.0] * 768
                point = PointStruct(
                    id=str(uuid4()), vector=dummy_vector, payload=payload
                )
                self.client.upsert(collection_name=self.COLLECTION_NAME, points=[point])
                print(
                    f"[UserGameProgress] Created progress for user {user_id} in {game_name}: {progress_marker}"
                )

            return True

        except Exception as e:
            print(f"[UserGameProgress] Error updating progress: {e}")
            return False

    def get_progress(self, user_id: str, game_name: str) -> Optional[str]:
        """
        Get current progress marker for a user in a game.

        Args:
            user_id: Unique identifier for the user
            game_name: Name of the game

        Returns:
            Progress marker string, or None if not found
        """
        normalized_name = self._normalize_game_name(game_name)

        try:
            results = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                        FieldCondition(
                            key="game_name", match=MatchValue(value=normalized_name)
                        ),
                    ]
                ),
                limit=1,
            )

            points = results[0]

            if len(points) > 0:
                return points[0].payload.get("progress_marker")

            return None

        except Exception as e:
            print(f"[UserGameProgress] Error getting progress: {e}")
            return None

    def get_all_user_progress(self, user_id: str) -> List[dict]:
        """
        Get all game progress for a specific user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            List of dictionaries with game_name and progress_marker
        """
        try:
            results = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="user_id", match=MatchValue(value=user_id))
                    ]
                ),
                limit=100,
            )

            points = results[0]

            games = []
            for point in points:
                games.append(
                    {
                        "game_name": point.payload.get("game_display_name", "Unknown"),
                        "progress_marker": point.payload.get("progress_marker", ""),
                        "last_updated": point.payload.get("last_updated"),
                    }
                )

            return games

        except Exception as e:
            print(f"[UserGameProgress] Error getting all progress: {e}")
            return []

    def remove_progress(self, user_id: str, game_name: str) -> bool:
        """
        Remove progress tracking for a user-game pair.

        Args:
            user_id: Unique identifier for the user
            game_name: Name of the game

        Returns:
            True if successfully removed, False otherwise
        """
        normalized_name = self._normalize_game_name(game_name)

        try:
            results = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                        FieldCondition(
                            key="game_name", match=MatchValue(value=normalized_name)
                        ),
                    ]
                ),
                limit=1,
            )

            points = results[0]

            if len(points) > 0:
                point_id = points[0].id
                self.client.delete(
                    collection_name=self.COLLECTION_NAME, points_selector=[point_id]
                )
                print(
                    f"[UserGameProgress] Removed progress for user {user_id} in {game_name}"
                )
                return True

            return False

        except Exception as e:
            print(f"[UserGameProgress] Error removing progress: {e}")
            return False


__all__ = ["UserGameProgress", "PROGRESS_MARKERS"]
