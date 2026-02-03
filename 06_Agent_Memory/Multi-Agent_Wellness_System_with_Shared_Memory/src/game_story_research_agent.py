"""
Game Story Research Agent

Orchestrates web searching and content extraction to populate the knowledge base
with game information (walkthroughs, lore, spoilers) from searxng search results.

This agent:
1. Uses searxng to find URLs for game content
2. Fetches content using webfetch tool
3. Chunks and adds metadata to the content
4. Stores in GameKnowledgeBase
5. Uses GameTracker to avoid reprocessing games
"""

from typing import Optional, List, Dict, Any
import httpx

from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .game_tracker import GameTracker
from .game_knowledge_base import GameKnowledgeBase


class GameStoryResearchAgent:
    """
    Research agent that populates the knowledge base with game content.

    Uses searxng search to find URLs, then fetches and processes content.
    """

    SEARXNG_URL = "http://192.168.1.36:4000/search"

    def __init__(
        self,
        qdrant_client: Optional[QdrantClient] = None,
        embeddings: Optional[OpenAIEmbeddings] = None,
    ):
        """
        Initialize the Game Story Research Agent.

        Args:
            qdrant_client: QDrant client instance
            embeddings: Embedding model for content chunking
        """
        self.qdrant_client = qdrant_client or QdrantClient(":memory:")
        self.embeddings = embeddings or OpenAIEmbeddings(
            model="text-embedding-nomic-embed-text-v2-moe",
            base_url="http://192.168.1.79:8080/v1",
            check_embedding_ctx_length=False,
        )

        # Initialize dependencies
        self.game_tracker = GameTracker(self.qdrant_client, self.embeddings)
        self.knowledge_base = GameKnowledgeBase(self.qdrant_client, self.embeddings)

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
        )

    def _search_searxng(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search searxng for URLs.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of dicts with 'url' and 'title' keys
        """
        try:
            params = {
                "q": query,
                "format": "json",
                "engines": "google,bing,duckduckgo",
            }

            response = httpx.get(
                self.SEARXNG_URL,
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()

            results = response.json()
            urls = []

            for result in results.get("results", [])[:num_results]:
                urls.append({"url": result["url"], "title": result.get("title", "")})

            return urls

        except Exception as e:
            print(f"[GameStoryResearchAgent] Error searching searxng: {e}")
            return []

    def _fetch_content(self, url: str) -> Optional[str]:
        """
        Fetch content from a URL using webfetch.

        Args:
            url: URL to fetch

        Returns:
            Markdown content or None if error
        """
        try:
            from src.tools.webfetch import webfetch

            content = webfetch(url, format="markdown")
            return content
        except Exception as e:
            print(f"[GameStoryResearchAgent] Error fetching {url}: {e}")
            return None

    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into smaller pieces for storage.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        return self.text_splitter.split_text(text)

    def _classify_progress_marker(self, text: str) -> str:
        """
        Classify content progress marker based on keywords.

        Args:
            text: Content to classify

        Returns:
            Progress marker (intro/tutorial, early_game, mid_game, late_game, endgame, post_game, general)
        """
        text_lower = text.lower()

        # Check for progress markers (order matters - more specific first)
        if any(
            keyword in text_lower
            for keyword in ["tutorial", "beginning", "start", "intro"]
        ):
            return "intro/tutorial"
        elif any(
            keyword in text_lower for keyword in ["early game", "first boss", "initial"]
        ):
            return "early_game"
        elif any(
            keyword in text_lower for keyword in ["mid game", "middle", "halfway"]
        ):
            return "mid_game"
        elif any(keyword in text_lower for keyword in ["endgame", "final boss"]):
            return "endgame"
        elif any(keyword in text_lower for keyword in ["late game", "final"]):
            return "late_game"
        elif any(
            keyword in text_lower for keyword in ["post game", "new game+", "after"]
        ):
            return "post_game"

        # Default to general
        return "general"

    def _classify_content_type(self, search_query: str) -> str:
        """
        Classify content type based on search query.

        Args:
            search_query: The original search query

        Returns:
            Content type (walkthrough, lore, spoiler, tips)
        """
        query_lower = search_query.lower()

        if "spoiler" in query_lower:
            return "spoiler"
        elif "lore" in query_lower or "story" in query_lower:
            return "lore"
        elif any(keyword in query_lower for keyword in ["walkthrough", "guide"]):
            return "walkthrough"
        else:
            return "tips"

    def _is_spoiler_content(self, content_type: str, text: str) -> bool:
        """
        Determine if content should be marked as spoiler.

        Args:
            content_type: Content type
            text: Content text

        Returns:
            True if spoiler, False otherwise
        """
        if content_type == "spoiler":
            return True

        # Check for spoiler keywords in text
        spoiler_keywords = [
            "ending",
            "final boss",
            "plot twist",
            "reveals that",
            "actually is",
            "secret ending",
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in spoiler_keywords)

    def research_game(
        self,
        game_name: str,
        display_name: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Research a game and populate the knowledge base.

        Args:
            game_name: Normalized game name
            display_name: Display name (e.g., "Elden Ring")
            force_refresh: If True, re-fetch even if already processed

        Returns:
            Dict with results summary
        """
        display_name = display_name or game_name.replace("_", " ").title()

        print(f"[GameStoryResearchAgent] Starting research for: {display_name}")

        # Check if already processed
        if not force_refresh and self.game_tracker.check_game_processed(game_name):
            print(f"[GameStoryResearchAgent] Game already processed: {display_name}")
            return {
                "success": True,
                "message": f"Game {display_name} already processed",
                "game_name": game_name,
            }

        # Search for different types of content
        search_queries = [
            f"{display_name} walkthrough guide",
            f"{display_name} lore story background",
            f"{display_name} spoilers ending plot",
        ]

        all_urls = []
        content_type_map = {}

        for query in search_queries:
            print(f"[GameStoryResearchAgent] Searching: {query}")
            urls = self._search_searxng(query, num_results=3)
            content_type = self._classify_content_type(query)

            for url_dict in urls:
                all_urls.append(url_dict)
                content_type_map[url_dict["url"]] = {
                    "type": content_type,
                    "query": query,
                }

        print(f"[GameStoryResearchAgent] Found {len(all_urls)} URLs to fetch")

        # Fetch and process content
        total_chunks = 0
        processed_urls = []

        for url_dict in all_urls:
            url = url_dict["url"]
            content_type_info = content_type_map[url]

            print(f"[GameStoryResearchAgent] Fetching: {url}")
            content = self._fetch_content(url)

            if not content or len(content) < 100:
                print(f"[GameStoryResearchAgent] Skipping (too short or error): {url}")
                continue

            # Chunk the content
            chunks = self._chunk_text(content)
            print(f"[GameStoryResearchAgent] Split into {len(chunks)} chunks")

            # Classify progress marker for this content
            progress_marker = self._classify_progress_marker(content)

            # Determine if spoiler
            is_spoiler = self._is_spoiler_content(content_type_info["type"], content)

            # Store in knowledge base
            metadata = {
                "game_name": game_name,
                "game_display_name": display_name,
                "content_type": content_type_info["type"],
                "is_spoiler": is_spoiler,
                "progress_marker": progress_marker,
                "source_url": url,
                "source_type": "searxng",
            }

            success = self.knowledge_base.store_game_content(chunks, metadata)

            if success:
                total_chunks += len(chunks)
                processed_urls.append(url)

        # Mark game as processed
        if total_chunks > 0:
            self.game_tracker.mark_game_processed(
                game_name,
                chunk_count=total_chunks,
                source_urls=processed_urls,
            )

        print(f"[GameStoryResearchAgent] Research complete for {display_name}")
        print(f"  - Total chunks stored: {total_chunks}")
        print(f"  - URLs processed: {len(processed_urls)}")

        return {
            "success": total_chunks > 0,
            "message": f"Processed {len(processed_urls)} URLs with {total_chunks} chunks",
            "game_name": game_name,
            "display_name": display_name,
            "total_chunks": total_chunks,
            "urls_processed": processed_urls,
        }


def create_game_story_research_agent(
    qdrant_client: Optional[QdrantClient] = None,
    embeddings: Optional[OpenAIEmbeddings] = None,
) -> GameStoryResearchAgent:
    """
    Factory function to create a Game Story Research Agent.

    Args:
        qdrant_client: QDrant client instance
        embeddings: Embedding model

    Returns:
        New GameStoryResearchAgent instance
    """
    return GameStoryResearchAgent(qdrant_client, embeddings)


__all__ = [
    "GameStoryResearchAgent",
    "create_game_story_research_agent",
]
