#!/usr/bin/env python3
"""
Real Game System Test - Non-Interactive Test Suite

Tests all components without requiring user input:
1. User identification (simulated)
2. Profile loading from QDrant
3. Searxng web search
4. LLM calls with real responses
5. QDrant read/write operations
"""

import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from uuid import uuid4

import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams


class RealGameSystemTest:
    """Test all real components without mocks."""

    def __init__(self):
        """Initialize test system."""
        self.test_user = "test_user_123"
        self.test_game = "Elden Ring"
        self.setup_components()

    def setup_components(self):
        """Setup all real components."""
        print("=" * 60)
        print("INITIALIZING REAL GAME SYSTEM TEST")
        print("=" * 60)

        # Setup QDrant
        self.qdrant_client = QdrantClient(host="localhost", port=6333)

        # Setup collections
        self._setup_collections()

        # Setup LLM
        os.environ["OPENAI_API_KEY"] = "not-needed"

        self.llm = ChatOpenAI(
            model="openai/gpt-oss-120b",
            base_url="http://192.168.1.79:8080/v1",
            api_key="not-needed",
            temperature=0.1,
        )

        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-nomic-embed-text-v2-moe",
            base_url="http://192.168.1.79:8080/v1",
            check_embedding_ctx_length=False,
        )

        print("SUCCESS: All components initialized")

    def _setup_collections(self):
        """Setup required QDrant collections."""
        collections_to_setup = ["user_game_progress", "game_knowledge_base"]

        existing_collections = {
            c.name for c in self.qdrant_client.get_collections().collections
        }

        for collection_name in collections_to_setup:
            if collection_name not in existing_collections:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
                print(f"SUCCESS: Created collection {collection_name}")
            else:
                print(f"SUCCESS: Collection {collection_name} exists")

    def test_user_identification(self) -> bool:
        """Test user identification (simulated)."""
        print(f"\n{'=' * 40}")
        print("TEST 1: USER IDENTIFICATION")
        print(f"{'=' * 40}")

        try:
            print(f"Simulated username: {self.test_user}")
            print("SUCCESS: User identification completed")
            return True
        except Exception as e:
            print(f"ERROR: User identification failed: {e}")
            return False

    def test_profile_loading(self) -> bool:
        """Test user profile loading from QDrant."""
        print(f"\n{'=' * 40}")
        print("TEST 2: PROFILE LOADING FROM QDRANT")
        print(f"{'=' * 40}")

        try:
            # First, store a test profile
            test_vector = [0.0] * 768
            test_point = PointStruct(
                id=str(uuid4()),
                vector=test_vector,
                payload={
                    "user_id": self.test_user,
                    "game_name": "elden_ring",
                    "game_display_name": "Elden Ring",
                    "progress_marker": "early_game",
                    "last_updated": datetime.now().isoformat(),
                },
            )

            self.qdrant_client.upsert(
                collection_name="user_game_progress", points=[test_point]
            )
            print("SUCCESS: Stored test user profile")

            # Now read it back
            from qdrant_client.http.models import FieldCondition, Filter, MatchValue

            results = self.qdrant_client.scroll(
                collection_name="user_game_progress",
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id", match=MatchValue(value=self.test_user)
                        )
                    ]
                ),
                limit=10,
            )

            points = results[0]
            if points:
                print(f"SUCCESS: Loaded profile for {self.test_user}")
                print(f"Found {len(points)} game entries")
                for point in points:
                    payload = point.payload or {}
                    game = payload.get("game_display_name", "Unknown")
                    progress = payload.get("progress_marker", "Unknown")
                    print(f"  - {game}: {progress}")
                return True
            else:
                print("ERROR: No profile data found")
                return False

        except Exception as e:
            print(f"ERROR: Profile loading failed: {e}")
            return False

    def test_searxng_search(self) -> bool:
        """Test searxng web search."""
        print(f"\n{'=' * 40}")
        print("TEST 3: SEARXNG WEB SEARCH")
        print(f"{'=' * 40}")

        try:
            search_url = "http://192.168.1.36:4000/search"
            params = {
                "q": f"{self.test_game} walkthrough guide",
                "format": "json",
                "engines": "google,bing,duckduckgo",
            }

            print(f"Searching: {params['q']}")

            response = httpx.get(search_url, params=params, timeout=10.0)
            response.raise_for_status()

            results = response.json()
            results_count = len(results.get("results", []))

            print(f"SUCCESS: Searxng returned {results_count} results")

            if results_count > 0:
                for i, result in enumerate(results["results"][:2]):
                    title = result.get("title", "No title")
                    print(f"  {i + 1}. {title}")
                return True
            else:
                print("ERROR: No search results")
                return False

        except Exception as e:
            print(f"ERROR: Searxng search failed: {e}")
            return False

    def test_llm_calls(self) -> bool:
        """Test LLM system with real calls."""
        print(f"\n{'=' * 40}")
        print("TEST 4: LLM SYSTEM CALLS")
        print(f"{'=' * 40}")

        try:
            test_queries = [
                f"What is {self.test_game} about?",
                f"Help me get started in {self.test_game}",
                f"What are the main classes in {self.test_game}?",
            ]

            for i, query in enumerate(test_queries, 1):
                print(f"\nQuery {i}: {query}")

                messages = [
                    SystemMessage(
                        content=f"You are a helpful gaming assistant specializing in {self.test_game}."
                    ),
                    HumanMessage(content=query),
                ]

                response = self.llm.invoke(messages)
                response_length = len(response.content)

                print(f"SUCCESS: LLM responded with {response_length} characters")
                print(f"Response preview: {response.content[:100]}...")

            return True

        except Exception as e:
            print(f"ERROR: LLM calls failed: {e}")
            return False

    def test_qdrant_operations(self) -> bool:
        """Test QDrant read/write operations."""
        print(f"\n{'=' * 40}")
        print("TEST 5: QDRANT READ/WRITE OPERATIONS")
        print(f"{'=' * 40}")

        try:
            # Test write
            test_content = f"Game knowledge for {self.test_game} at {datetime.now()}"
            print(f"Writing: {test_content[:50]}...")

            test_vector = self.embeddings.embed_query(test_content)

            test_point = PointStruct(
                id=str(uuid4()),
                vector=test_vector,
                payload={
                    "text": test_content,
                    "user_id": self.test_user,
                    "game_name": self.test_game.lower().replace(" ", "_"),
                    "content_type": "test",
                    "timestamp": datetime.now().isoformat(),
                },
            )

            self.qdrant_client.upsert(
                collection_name="game_knowledge_base", points=[test_point]
            )
            print("SUCCESS: Wrote content to QDrant")

            # Test read
            from qdrant_client.http.models import FieldCondition, Filter, MatchValue

            search_results = self.qdrant_client.search(
                collection_name="game_knowledge_base",
                query_vector=test_vector,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id", match=MatchValue(value=self.test_user)
                        )
                    ]
                ),
                limit=3,
            )

            if search_results:
                print(f"SUCCESS: Found {len(search_results)} matching results")
                for i, result in enumerate(search_results):
                    payload = result.payload or {}
                    text = payload.get("text", "No text")
                    score = result.score
                    print(f"  {i + 1}. Score: {score:.3f}, Text: {text[:50]}...")
                return True
            else:
                print("ERROR: No search results found")
                return False

        except Exception as e:
            print(f"ERROR: QDrant operations failed: {e}")
            return False

    def run_all_tests(self):
        """Run all tests and report results."""
        print(f"\n{'=' * 60}")
        print("STARTING COMPREHENSIVE SYSTEM TESTS")
        print(f"Test User: {self.test_user}")
        print(f"Test Game: {self.test_game}")
        print(f"{'=' * 60}")

        tests = [
            ("User Identification", self.test_user_identification),
            ("Profile Loading", self.test_profile_loading),
            ("Searxng Search", self.test_searxng_search),
            ("LLM Calls", self.test_llm_calls),
            ("QDrant Operations", self.test_qdrant_operations),
        ]

        results = []

        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"CRITICAL ERROR in {test_name}: {e}")
                results.append((test_name, False))

        # Final summary
        print(f"\n{'=' * 60}")
        print("FINAL TEST RESULTS")
        print(f"{'=' * 60}")

        passed = 0
        total = len(results)

        for test_name, success in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status}: {test_name}")
            if success:
                passed += 1

        print(f"\nSummary: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 ALL TESTS PASSED - SYSTEM IS FULLY OPERATIONAL!")
        else:
            print("⚠️  Some tests failed - check errors above")

        return passed == total


def main():
    """Main entry point."""
    try:
        tester = RealGameSystemTest()
        success = tester.run_all_tests()

        if success:
            print("\n✓ Real Game System is ready for production use!")
            sys.exit(0)
        else:
            print("\n✗ System needs fixes before production use")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nCritical test failure: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
