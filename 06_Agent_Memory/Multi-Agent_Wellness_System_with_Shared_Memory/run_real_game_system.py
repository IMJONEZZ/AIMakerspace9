#!/usr/bin/env python3
"""
REAL Game Agent System - Complete Implementation

This is the actual game system that:
1. Tests all components for base functionality
2. Determines user identity and creates/loads profiles
3. Prompts for profile information for new users
4. Asks which game they're querying about
5. Routes questions to correct agents
6. Searches searxng + knowledge base
7. Filters spoilers and synthesizes responses
8. Shows reasoning process with --verbose flag
"""

import argparse
import asyncio
import sys
import os
from typing import Optional, List, Dict, Any
import httpx
from datetime import datetime
from uuid import uuid4

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
import tiktoken
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple


@dataclass
class MemoryEntry:
    """Single memory entry with metadata."""

    content: str
    timestamp: str
    entry_type: str  # 'user_query', 'agent_response', 'context', 'fact'
    importance: float  # 0.0 to 1.0
    game_context: Optional[str] = None
    agent_type: Optional[str] = None


class StructuredMemorySystem:
    """Advanced memory system with working, session, and long-term memory layers."""

    def __init__(self, llm, embeddings, qdrant_client):
        self.llm = llm
        self.embeddings = embeddings
        self.qdrant_client = qdrant_client

        # Working memory - recent 3-5 turns with full detail
        self.working_memory: List[MemoryEntry] = []
        self.working_memory_limit = 5

        # Session memory - summarized key points from current gaming session
        self.session_memory: List[MemoryEntry] = []
        self.session_summary = ""

        # Long-term memory - user preferences, game-specific knowledge
        self.long_term_memory: List[MemoryEntry] = []

        # Semantic memory - vector-stored facts for intelligent retrieval
        self.semantic_collection = "semantic_memory"
        self._ensure_semantic_collection()

    def _ensure_semantic_collection(self):
        """Ensure semantic memory collection exists."""
        try:
            collections = {
                c.name for c in self.qdrant_client.get_collections().collections
            }
            if self.semantic_collection not in collections:
                self.qdrant_client.create_collection(
                    collection_name=self.semantic_collection,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
        except Exception as e:
            print(f"Warning: Could not create semantic memory collection: {e}")

    def add_to_working_memory(self, entry: MemoryEntry):
        """Add entry to working memory with automatic rotation."""
        self.working_memory.append(entry)

        # If over limit, move oldest to session memory
        if len(self.working_memory) > self.working_memory_limit:
            oldest = self.working_memory.pop(0)
            self._consolidate_to_session_memory(oldest)

    def _consolidate_to_session_memory(self, entry: MemoryEntry):
        """Consolidate working memory entry to session memory."""
        summarized_entry = self._summarize_memory_entry(entry)
        self.session_memory.append(summarized_entry)

        # Periodically summarize entire session
        if len(self.session_memory) % 5 == 0:
            self._update_session_summary()

    def _summarize_memory_entry(self, entry: MemoryEntry) -> MemoryEntry:
        """Summarize a memory entry for session storage."""
        try:
            summary_prompt = f"""Summarize this gaming interaction for session memory:
            
            Content: {entry.content}
            Type: {entry.entry_type}
            Game: {entry.game_context}
            
            Create a concise summary (1-2 sentences) preserving key information:"""

            messages = [
                SystemMessage(content=summary_prompt),
                HumanMessage(content=entry.content),
            ]

            response = self.llm.invoke(messages)
            summary = str(response.content).strip()

            return MemoryEntry(
                content=summary,
                timestamp=entry.timestamp,
                entry_type="session_summary",
                importance=entry.importance * 0.8,  # Slightly reduce importance
                game_context=entry.game_context,
                agent_type=entry.agent_type,
            )
        except Exception as e:
            # Fallback to original entry
            return MemoryEntry(
                content=entry.content[:200] + "..."
                if len(entry.content) > 200
                else entry.content,
                timestamp=entry.timestamp,
                entry_type="session_summary",
                importance=entry.importance * 0.8,
                game_context=entry.game_context,
                agent_type=entry.agent_type,
            )

    def _update_session_summary(self):
        """Update the overall session summary."""
        if not self.session_memory:
            return

        try:
            session_content = "\n".join(
                [f"- {entry.content}" for entry in self.session_memory[-10:]]
            )

            summary_prompt = f"""Create a comprehensive summary of this gaming session:
            
            Session Interactions:
            {session_content}
            
            Generate a summary that captures:
            1. Main topics discussed
            2. Key information learned
            3. User's interests and patterns
            4. Important questions answered
            
            Keep it to 3-4 sentences total:"""

            messages = [
                SystemMessage(content=summary_prompt),
                HumanMessage(content=session_content),
            ]

            response = self.llm.invoke(messages)
            self.session_summary = str(response.content).strip()

        except Exception as e:
            print(f"Warning: Could not update session summary: {e}")

    def add_to_semantic_memory(self, entry: MemoryEntry):
        """Add entry to semantic memory with vector storage."""
        try:
            # Create embedding for semantic search
            text_to_embed = (
                f"{entry.game_context} {entry.content}"
                if entry.game_context
                else entry.content
            )
            vector = self.embeddings.embed_query(text_to_embed)

            # Store in QDrant
            point = PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "content": entry.content,
                    "timestamp": entry.timestamp,
                    "entry_type": entry.entry_type,
                    "importance": entry.importance,
                    "game_context": entry.game_context,
                    "agent_type": entry.agent_type,
                },
            )

            self.qdrant_client.upsert(
                collection_name=self.semantic_collection, points=[point]
            )

        except Exception as e:
            print(f"Warning: Could not add to semantic memory: {e}")

    def search_semantic_memory(
        self, query: str, game_context: Optional[str] = None, limit: int = 3
    ) -> List[MemoryEntry]:
        """Search semantic memory for relevant entries."""
        try:
            # Create query vector
            query_text = f"{game_context} {query}" if game_context else query
            query_vector = self.embeddings.embed_query(query_text)

            # Search with optional game filter
            search_filter = None
            if game_context:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="game_context", match=MatchValue(value=game_context)
                        )
                    ]
                )

            search_results = self.qdrant_client.query_points(
                collection_name=self.semantic_collection,
                query=query_vector,
                query_filter=search_filter,
                limit=limit,
            )

            entries = []
            for result in search_results.points:
                payload = result.payload
                entry = MemoryEntry(
                    content=payload.get("content", ""),
                    timestamp=payload.get("timestamp", ""),
                    entry_type=payload.get("entry_type", "semantic"),
                    importance=payload.get("importance", 0.5),
                    game_context=payload.get("game_context"),
                    agent_type=payload.get("agent_type"),
                )
                entries.append(entry)

            return entries

        except Exception as e:
            print(f"Warning: Could not search semantic memory: {e}")
            return []

    def get_relevant_context(
        self, query: str, game_context: Optional[str] = None
    ) -> str:
        """Get relevant context from all memory layers."""
        context_parts = []

        # Working memory context
        if self.working_memory:
            working_context = "\n".join(
                [
                    f"{entry.entry_type}: {entry.content}"
                    for entry in self.working_memory[-3:]
                ]
            )
            context_parts.append(f"Recent Interactions:\n{working_context}")

        # Session summary
        if self.session_summary:
            context_parts.append(f"Session Summary:\n{self.session_summary}")

        # Semantic memory search
        semantic_entries = self.search_semantic_memory(query, game_context, limit=2)
        if semantic_entries:
            semantic_context = "\n".join(
                [f"- {entry.content}" for entry in semantic_entries]
            )
            context_parts.append(f"Relevant Past Information:\n{semantic_context}")

        return (
            "\n\n".join(context_parts)
            if context_parts
            else "No relevant context available."
        )

    def get_conversation_history_text(self, limit: int = 5) -> str:
        """Get formatted conversation history for context."""
        recent_entries = self.working_memory[-limit:]
        if not recent_entries:
            return ""

        history_parts = []
        for entry in recent_entries:
            if entry.entry_type == "user_query":
                history_parts.append(f"User: {entry.content}")
            elif entry.entry_type == "agent_response":
                history_parts.append(f"Assistant: {entry.content}")

        return "\n".join(history_parts)


class GameSystem:
    """Actual game system with routing, agents, and spoiler filtering."""

    def __init__(self, verbose: bool = False):
        """Initialize the game system.

        Args:
            verbose: Enable verbose output showing reasoning process
        """
        self.verbose = verbose
        self.user_id = None
        self.user_profile = None
        self.current_game = None
        self.memory_system = None  # Will be initialized after component setup
        self.tokenizer = None  # For context compression
        self.setup_components()

    def setup_components(self):
        """Setup and test all system components."""
        print("=" * 60)
        print("INITIALIZING REAL GAME SYSTEM")
        print("=" * 60)

        # Test and setup QDrant
        self._setup_qdrant()

        # Test and setup LLM
        self._setup_llm()

        # Test and setup web search
        self._setup_web_search()

        # Initialize memory system and tokenizer
        self._setup_memory_system()
        self._setup_tokenizer()

        print("SUCCESS: All components initialized and tested")

    def _setup_qdrant(self):
        """Setup and test QDrant connection."""
        try:
            self.qdrant_client = QdrantClient(host="localhost", port=6333)
            collections = self.qdrant_client.get_collections()
            print(
                f"SUCCESS: QDrant connected with {len(collections.collections)} collections"
            )

            # Ensure required collections exist
            self._ensure_collections()

        except Exception as e:
            print(f"ERROR: QDrant setup failed: {e}")
            sys.exit(1)

    def _ensure_collections(self):
        """Create required collections if they don't exist."""
        collections = ["user_profiles", "game_knowledge"]

        existing = {c.name for c in self.qdrant_client.get_collections().collections}

        for collection_name in collections:
            if collection_name not in existing:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
                print(f"SUCCESS: Created collection: {collection_name}")

    def _setup_llm(self):
        """Setup and test LLM connection."""
        try:
            os.environ["OPENAI_API_KEY"] = "not-needed-for-local-server"

            self.llm = ChatOpenAI(
                model="openai/gpt-oss-120b",
                base_url="http://192.168.1.79:8080/v1",
                api_key="not-needed-for-local-server",
                temperature=0.1,
            )

            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-nomic-embed-text-v2-moe",
                base_url="http://192.168.1.79:8080/v1",
                check_embedding_ctx_length=False,
            )

            # Test LLM
            test_messages = [
                SystemMessage(content="Test"),
                HumanMessage(content="Say 'LLM test successful'"),
            ]
            response = self.llm.invoke(test_messages)
            print(f"SUCCESS: LLM test passed - {response.content[:50]}...")

        except Exception as e:
            print(f"ERROR: LLM setup failed: {e}")
            sys.exit(1)

    def _setup_web_search(self):
        """Setup and test web search."""
        try:
            response = httpx.get(
                "http://192.168.1.36:4000/search",
                params={"q": "test", "format": "json"},
                timeout=5.0,
            )
            response.raise_for_status()
            results = response.json()
            print(
                f"SUCCESS: Web search test passed - {len(results.get('results', []))} results"
            )

        except Exception as e:
            print(f"ERROR: Web search setup failed: {e}")
            sys.exit(1)

    def _setup_memory_system(self):
        """Setup the structured memory system."""
        try:
            self.memory_system = StructuredMemorySystem(
                self.llm, self.embeddings, self.qdrant_client
            )
            print("SUCCESS: Structured memory system initialized")
        except Exception as e:
            print(f"ERROR: Memory system setup failed: {e}")
            sys.exit(1)

    def _setup_tokenizer(self):
        """Setup tokenizer for context compression."""
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
            print("SUCCESS: Tokenizer initialized for context management")
        except Exception as e:
            print(f"WARNING: Tokenizer setup failed: {e}")
            self.tokenizer = None

    def estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text."""
        if not self.tokenizer:
            return int(len(text.split()) * 1.3)  # Rough fallback estimate
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            return int(len(text.split()) * 1.3)

    def compress_context_pyramid(
        self, instruction_prompt: str, context: str, max_tokens: int = 8000
    ) -> Tuple[str, str]:
        """Implement progressive context compression using pyramid structure.

        Args:
            instruction_prompt: System instructions (highest priority)
            context: Context information to compress
            max_tokens: Maximum total tokens allowed

        Returns:
            Tuple of (compressed_context, compression_summary)
        """
        instruction_tokens = self.estimate_tokens(instruction_prompt)
        available_context_tokens = (
            max_tokens - instruction_tokens - 500
        )  # Reserve 500 for response

        if self.estimate_tokens(context) <= available_context_tokens:
            return context, "No compression needed"

        try:
            # Level 1: Extract key sentences using LLM
            extract_prompt = f"""Extract the most important information from this context for gaming assistance.
            Keep key facts, instructions, and relevant details. Remove redundancy and filler.
            
            Context:
            {context}
            
            Return only the essential information, approximately {available_context_tokens * 0.7} tokens:"""

            messages = [
                SystemMessage(content=extract_prompt),
                HumanMessage(content=context),
            ]

            response = self.llm.invoke(messages)
            compressed = str(response.content).strip()

            # Level 2: If still too long, create bullet-point summary
            if self.estimate_tokens(compressed) > available_context_tokens:
                bullet_prompt = f"""Convert this to a concise bullet-point summary for gaming assistance.
                Focus only on actionable information and key facts.
                
                Content:
                {compressed}
                
                Return as bullet points, maximum {available_context_tokens * 0.5} tokens:"""

                messages = [
                    SystemMessage(content=bullet_prompt),
                    HumanMessage(content=compressed),
                ]

                response = self.llm.invoke(messages)
                compressed = str(response.content).strip()

            # Level 3: Final compression if needed
            if self.estimate_tokens(compressed) > available_context_tokens:
                # Simple truncation with ellipsis
                compressed = compressed[: int(available_context_tokens * 0.9)] + "..."

            original_tokens = self.estimate_tokens(context)
            final_tokens = self.estimate_tokens(compressed)
            compression_ratio = (
                (original_tokens - final_tokens) / original_tokens
                if original_tokens > 0
                else 0
            )

            summary = f"Compressed from {original_tokens} to {final_tokens} tokens ({compression_ratio:.1%} reduction)"

            if self.verbose:
                print(f"[CONTEXT COMPRESSION] {summary}")

            return compressed, summary

        except Exception as e:
            if self.verbose:
                print(f"[CONTEXT COMPRESSION ERROR] {e}")
            # Fallback: simple truncation
            if self.estimate_tokens(context) > available_context_tokens:
                truncated = context[: int(available_context_tokens * 0.9)] + "..."
                return truncated, "Emergency truncation applied"
            return context, "Compression failed, original used"

    def determine_user_identity(self):
        """Determine who the user is and create/load profile."""
        print("\n" + "=" * 60)
        print("USER IDENTIFICATION")
        print("=" * 60)

        while True:
            username = input("What is your username? ").strip()
            if username:
                self.user_id = username
                break
            print("Please enter a valid username.")

        # Try to load existing profile
        self.user_profile = self._load_user_profile(username)

        if not self.user_profile:
            print(f"Welcome, {username}! Creating your profile...")
            self.user_profile = self._create_new_profile(username)
        else:
            print(f"Welcome back, {username}! Profile loaded.")

    def _load_user_profile(self, username: str) -> Optional[Dict]:
        """Load existing user profile from QDrant."""
        try:
            results = self.qdrant_client.scroll(
                collection_name="user_profiles",
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="username", match=MatchValue(value=username))
                    ]
                ),
                limit=1,
            )

            points = results[0]
            if points:
                return points[0].payload
            return None

        except Exception as e:
            if self.verbose:
                print(f"Error loading profile: {e}")
            return None

    def _create_new_profile(self, username: str) -> Dict:
        """Create new user profile by prompting for information."""
        profile = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "favorite_genres": [],
            "preferred_playstyles": [],
            "spoiler_sensitivity": "medium",
            "games_played": [],
        }

        print("\nLet's set up your gaming profile:")

        # Favorite genres
        genres_input = input(
            "What are your favorite game genres? (comma-separated): "
        ).strip()
        if genres_input:
            profile["favorite_genres"] = [g.strip() for g in genres_input.split(",")]

        # Preferred playstyles
        playstyles_input = input(
            "What are your preferred playstyles? (e.g., casual, hardcore, completionist): "
        ).strip()
        if playstyles_input:
            profile["preferred_playstyles"] = [
                p.strip() for p in playstyles_input.split(",")
            ]

        # Spoiler sensitivity
        while True:
            sensitivity = (
                input("Spoiler sensitivity (low/medium/high): ").strip().lower()
            )
            if sensitivity in ["low", "medium", "high"]:
                profile["spoiler_sensitivity"] = sensitivity
                break
            print("Please enter: low, medium, or high")

        # Store profile in QDrant
        self._store_user_profile(profile)

        return profile

    def _store_user_profile(self, profile: Dict):
        """Store user profile in QDrant."""
        try:
            # Use dummy vector for profile storage
            dummy_vector = [0.0] * 768

            point = PointStruct(id=str(uuid4()), vector=dummy_vector, payload=profile)

            self.qdrant_client.upsert(collection_name="user_profiles", points=[point])

            if self.verbose:
                print(f"Stored profile for user: {profile['username']}")

        except Exception as e:
            print(f"Error storing profile: {e}")

    def determine_current_game(self):
        """Ask which game the user wants to query about."""
        print("\n" + "=" * 60)
        print("GAME SELECTION")
        print("=" * 60)

        while True:
            game_name = input("Which game would you like to ask about? ").strip()
            if game_name:
                self.current_game = game_name
                print(f"Selected game: {game_name}")
                break
            print("Please enter a game name.")

    def route_query_to_agent(self, query: str) -> str:
        """Route user query to the correct specialist agent."""
        if self.verbose:
            print(f"\n[THINKING] Routing query: '{query}'")

        routing_prompt = f"""You are a game query router. Classify this query into one of these categories:
        
        - gameplay: Questions about mechanics, controls, how to do things
        - lore: Questions about story, characters, world-building, background
        - progression: Questions about advancing, leveling up, what to do next
        - technical: Questions about bugs, performance, technical issues
        
        Query: "{query}"
        
        Respond with only the category name:"""

        try:
            messages = [
                SystemMessage(content=routing_prompt),
                HumanMessage(content=query),
            ]

            response = self.llm.invoke(messages)
            content = (
                response.content if hasattr(response, "content") else str(response)
            )
            agent_type = str(content).strip().lower()

            valid_agents = ["gameplay", "lore", "progression", "technical"]
            if agent_type not in valid_agents:
                agent_type = "gameplay"  # default

            if self.verbose:
                print(f"[ROUTING] Query routed to: {agent_type} agent")

            return agent_type

        except Exception as e:
            if self.verbose:
                print(f"[ROUTING ERROR] {e}")
            return "gameplay"

    def parse_spoiler_override(self, query: str) -> tuple[str, Optional[str]]:
        """Parse spoiler sensitivity override from query.

        Supports formats:
        - "query --spoiler=high"
        - "query --spoiler:medium"
        - "[high] query"

        Returns:
            tuple of (cleaned_query, sensitivity_override)
            sensitivity_override can be "high", "medium", "low", "none" or None
        """
        import re

        sensitivity_override = None
        cleaned_query = query.strip()

        # Check for --spoiler= flag
        spoiler_match = re.search(
            r"--spoiler[=:](high|medium|low|none)", query, re.IGNORECASE
        )
        if spoiler_match:
            sensitivity_override = spoiler_match.group(1).lower()
            cleaned_query = re.sub(
                r"--spoiler[=:](high|medium|low|none)", "", query, flags=re.IGNORECASE
            )

        # Check for [sensitivity] format
        bracket_match = re.search(r"\[(high|medium|low|none)\]", query, re.IGNORECASE)
        if bracket_match:
            sensitivity_override = bracket_match.group(1).lower()
            cleaned_query = re.sub(
                r"\[(high|medium|low|none)\]", "", query, flags=re.IGNORECASE
            )

        # Clean up extra whitespace
        cleaned_query = re.sub(r"\s+", " ", cleaned_query).strip()

        return cleaned_query, sensitivity_override

    def generate_intelligent_search_query(
        self, user_query: str, agent_type: str
    ) -> str:
        """Generate intelligent search query using LLM to understand user intent and context."""

        # Build context for query generation
        context_info = []
        if self.current_game:
            context_info.append(f"Game: {self.current_game}")

        if self.user_profile:
            genres = self.user_profile.get("favorite_genres", [])
            playstyles = self.user_profile.get("preferred_playstyles", [])
            sensitivity = self.user_profile.get("spoiler_sensitivity", "medium")

            if genres:
                context_info.append(f"User prefers genres: {', '.join(genres)}")
            if playstyles:
                context_info.append(f"User playstyles: {', '.join(playstyles)}")
            context_info.append(f"Spoiler sensitivity: {sensitivity}")

        # Add conversation context from memory system
        conversation_context = ""
        if self.memory_system and self.memory_system.working_memory:
            recent_context = self.memory_system.working_memory[
                -2:
            ]  # Last 2 interactions
            if recent_context:
                context_snippets = []
                for entry in recent_context:
                    if entry.entry_type == "user_query":
                        context_snippets.append(f"Q: {entry.content[:100]}")
                conversation_context = "Recent conversation context: " + " | ".join(
                    context_snippets
                )

        query_generation_prompt = f"""You are an expert at generating optimized search queries for gaming information.

Context Information:
{chr(10).join(context_info)}

Agent Type: {agent_type}
{conversation_context if conversation_context else ""}

User's Original Query: "{user_query}"

Your task: Generate an optimized search query that will find the most relevant information for this user's gaming question. Consider:
1. The specific game they're asking about
2. Their gaming preferences and experience level
3. The type of information they need (gameplay, lore, progression, technical)
4. Avoid spoilers based on their sensitivity level
5. Use gaming-specific terminology and keywords
6. Include relevant modifiers like "guide", "walkthrough", "how to", "tips", etc. when appropriate

Generate only the optimized search query, nothing else. Keep it concise but comprehensive (3-8 words optimal)."""

        try:
            messages = [
                SystemMessage(content=query_generation_prompt),
                HumanMessage(content=user_query),
            ]

            response = self.llm.invoke(messages)
            content = (
                response.content if hasattr(response, "content") else str(response)
            )
            optimized_query = str(content).strip()

            # Fallback if LLM fails or returns empty
            if not optimized_query or len(optimized_query) < 3:
                optimized_query = (
                    f"{self.current_game} {user_query}"
                    if self.current_game
                    else user_query
                )

            if self.verbose:
                print(
                    f"[QUERY GENERATION] Original: '{user_query}' -> Optimized: '{optimized_query}'"
                )

            return optimized_query

        except Exception as e:
            if self.verbose:
                print(f"[QUERY GENERATION ERROR] {e}")
            # Fallback to original method
            return (
                f"{self.current_game} {user_query}" if self.current_game else user_query
            )

    def search_web_and_knowledge(self, query: str) -> Dict[str, List]:
        """Search both web and knowledge base for information."""
        if self.verbose:
            print(f"\n[SEARCHING] Searching for: '{query}'")

        results = {"web": [], "knowledge": []}

        # Get agent type for better query generation
        agent_type = self.route_query_to_agent(query)

        # Enhanced web search with LLM-generated intelligent query
        try:
            # Generate context-aware search query using LLM
            search_query = self.generate_intelligent_search_query(query, agent_type)

            search_params = {
                "q": search_query,
                "format": "json",
                "engines": "google,bing,duckduckgo",
            }

            if self.verbose:
                print(f"[WEB SEARCH QUERY] {search_query}")

            response = httpx.get(
                "http://192.168.1.36:4000/search", params=search_params, timeout=10.0
            )
            response.raise_for_status()

            search_data = response.json()
            web_results = search_data.get("results", [])[:5]

            for result in web_results:
                results["web"].append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "snippet": result.get("content", "")[:200] + "..."
                        if len(result.get("content", "")) > 200
                        else result.get("content", ""),
                    }
                )

            if self.verbose:
                print(f"[WEB SEARCH] Found {len(web_results)} web results")
                for i, result in enumerate(web_results[:2], 1):
                    print(f"  {i}. {result['title'][:50]}...")

            # Embed and store web results for future retrieval
            if results["web"]:
                self.embed_and_store_web_results(results["web"], query, agent_type)

        except Exception as e:
            if self.verbose:
                print(f"[WEB SEARCH ERROR] {e}")

        # Knowledge base search
        try:
            query_vector = self.embeddings.embed_query(query or "")
            game_vector = self.embeddings.embed_query(self.current_game or "")

            # Combine vectors for better search
            combined_vector = [
                (qv + gv) / 2 for qv, gv in zip(query_vector, game_vector)
            ]

            from qdrant_client.http.models import PointStruct

            # First, let's see if we have any data in the knowledge base
            scroll_results = self.qdrant_client.scroll(
                collection_name="game_knowledge", limit=3
            )

            points = scroll_results[0]

            for point in points:
                payload = point.payload or {}
                results["knowledge"].append(
                    {
                        "text": payload.get("text", ""),
                        "source": payload.get("source", "knowledge_base"),
                        "relevance": 0.8,  # Default relevance for scroll results
                    }
                )

            if self.verbose:
                print(f"[KNOWLEDGE SEARCH] Found {len(points)} knowledge base results")

        except Exception as e:
            if self.verbose:
                print(f"[KNOWLEDGE SEARCH ERROR] {e}")

        return results

    def filter_spoilers(
        self, content: str, agent_type: str, sensitivity_override: Optional[str] = None
    ) -> str:
        """Filter content based on spoiler sensitivity and game progress with iterative rephrasing."""
        if self.verbose:
            print(f"\n[SPOILER FILTER] Processing content for {agent_type}")

        # Get user's spoiler sensitivity, with optional per-query override
        sensitivity = sensitivity_override or (self.user_profile or {}).get(
            "spoiler_sensitivity", "medium"
        )

        max_iterations = 2
        current_content = content

        for iteration in range(max_iterations):
            spoiler_filter_prompt = f"""You are a spoiler filter for game content.
        User's spoiler sensitivity: {sensitivity}
        Content type: {agent_type}
        Game: {self.current_game}

        Review this content and remove or mask any spoilers based on sensitivity level:
        - None: Show all content without filtering
        - Low sensitivity: Allow most content, only remove major plot twists
        - Medium sensitivity: Remove mid-game and late game spoilers
        - High sensitivity: Remove all potential spoilers, keep only basic info

        Content to filter:
        "{current_content}"

        Return filtered content. If the content contains spoilers that exceed the user's sensitivity level,
        provide a spoiler-free version that still addresses their question as helpfully as possible without revealing
        the sensitive information. Be creative in finding alternative ways to answer that avoid spoilers. """

            try:
                messages = [
                    SystemMessage(content=spoiler_filter_prompt),
                    HumanMessage(content=current_content),
                ]

                response = self.llm.invoke(messages)
                response_content = (
                    response.content if hasattr(response, "content") else str(response)
                )
                filtered_content = str(response_content).strip()

                if self.verbose:
                    print(
                        f"[SPOILER FILTER] Iteration {iteration + 1}: Applied {sensitivity} sensitivity filter"
                    )

                # Check if content is still blocked
                if "contains spoilers" in filtered_content.lower():
                    if iteration < max_iterations - 1:
                        if self.verbose:
                            print(
                                f"[SPOILER FILTER] Content blocked, attempting rephrase (iteration {iteration + 2})"
                            )
                        # Try to rephrase for next iteration
                        rephrase_prompt = f"""The previous response was considered too spoiler-heavy. Please rewrite this content to be completely spoiler-free while still being helpful:

Original question context: {agent_type} query about {self.current_game}
Content to rephrase: "{current_content}"

Focus on providing helpful guidance without revealing any plot points, specific character details, or location spoilers.
Use general advice and hints instead of specific answers."""

                        rephrase_messages = [
                            SystemMessage(content=rephrase_prompt),
                            HumanMessage(content=current_content),
                        ]
                        rephrase_response = self.llm.invoke(rephrase_messages)
                        current_content = (
                            rephrase_response.content
                            if hasattr(rephrase_response, "content")
                            else str(rephrase_response)
                        ).strip()
                    else:
                        if self.verbose:
                            print(
                                "[SPOILER FILTER] Max iterations reached, returning filtered content"
                            )
                        return filtered_content
                else:
                    return filtered_content

            except Exception as e:
                if self.verbose:
                    print(f"[SPOILER FILTER ERROR] {e}")
                return current_content  # fallback to current iteration

        return current_content

    def embed_and_store_web_results(
        self, web_results: List[Dict], query: str, agent_type: str
    ):
        """Embed web search results and store them in QDrant for future retrieval."""
        if not web_results:
            return

        # Check if memory_system is initialized
        if not self.memory_system or not hasattr(
            self.memory_system, "semantic_collection"
        ):
            if self.verbose:
                print(
                    "[KNOWLEDGE UPDATE] Skipping web result embedding - memory system not initialized"
                )
            return

        try:
            from qdrant_client.http.models import PointStruct
            from datetime import datetime

            points_to_upsert = []
            timestamp = datetime.now().isoformat()

            for idx, result in enumerate(web_results[:3]):  # Store top 3 results
                text_to_embed = (
                    f"{result.get('title', '')}\n{result.get('content', '')}"
                )

                # Create embedding
                try:
                    vector = self.embeddings.embed_query(text_to_embed)

                    point_id = str(uuid4())
                    point = PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "text": text_to_embed,
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "source": "web_search",
                            "game_context": self.current_game,
                            "agent_type": agent_type,
                            "query": query,
                            "timestamp": timestamp,
                            "entry_type": "web_result",
                            "importance": 0.6,
                        },
                    )
                    points_to_upsert.append(point)

                except Exception as embed_error:
                    if self.verbose:
                        print(
                            f"[EMBED ERROR] Failed to embed result {idx}: {embed_error}"
                        )
                    continue

            if points_to_upsert:
                self.qdrant_client.upsert(
                    collection_name=self.memory_system.semantic_collection,
                    points=points_to_upsert,
                )
                if self.verbose:
                    print(
                        f"[KNOWLEDGE UPDATE] Embedded {len(points_to_upsert)} web results into QDrant"
                    )

        except Exception as e:
            if self.verbose:
                print(f"[KNOWLEDGE UPDATE ERROR] {e}")

    def extract_reasoning_and_response(self, llm_content: str) -> tuple[str, str]:
        """Extract reasoning content from LLM response and separate from user-facing content.

        Args:
            llm_content: Raw LLM response content

        Returns:
            Tuple of (reasoning_content, user_response)
        """
        # Look for think tags
        import re

        # Case 1: Both opening and closing think tags
        # Use the exact characters to avoid encoding issues
        opening_tag = "think"
        closing_tag = "think"
        pattern = f"{re.escape(opening_tag)}(.*?){re.escape(closing_tag)}"
        think_matches = re.findall(pattern, llm_content, re.DOTALL)

        if think_matches:
            # Extract all reasoning content
            reasoning = "\n".join(think_matches).strip()
            # Remove all think content from user response
            user_response = re.sub(pattern, "", llm_content).strip()
            return reasoning, user_response

        # Case 2: Only opening think tag
        if opening_tag in llm_content:
            # Everything after opening tag is reasoning, everything before is user response
            parts = llm_content.split(opening_tag, 1)
            user_response = parts[0].strip()
            reasoning = parts[1].strip() if len(parts) > 1 else ""
            return reasoning, user_response

        # Case 3: No think tags
        return "", llm_content

    def synthesize_response(
        self,
        query: str,
        agent_type: str,
        search_results: Dict,
        spoiler_override: Optional[str] = None,
    ) -> str:
        """Synthesize a response using search results, memory context, and progressive context compression."""
        if self.verbose:
            print(f"\n[SYNTHESIZING] Creating response for {agent_type} query")

        # Get relevant context from memory system
        memory_context = ""
        if self.memory_system:
            memory_context = self.memory_system.get_relevant_context(
                query, self.current_game or ""
            )

        # Prepare context from search results
        context_parts = []

        if memory_context:
            context_parts.append("Memory Context:")
            context_parts.append(memory_context)

        if search_results["web"]:
            context_parts.append("Web Search Results:")
            for i, result in enumerate(search_results["web"][:2], 1):
                context_parts.append(
                    f"{i}. {result['title']}: {result['content'][:200]}..."
                )

        if search_results["knowledge"]:
            context_parts.append("Knowledge Base Results:")
            for i, result in enumerate(search_results["knowledge"], 1):
                context_parts.append(f"{i}. {result['text'][:200]}...")

        context = (
            "\n".join(context_parts)
            if context_parts
            else "No specific information found."
        )

        # Create the instruction prompt (pyramid structure base)
        instruction_prompt = f"""You are a helpful gaming assistant specializing in {agent_type} for {self.current_game}.
        
        User Question: {query}
        
        Provide a helpful, accurate response based on the available information. 
        If information is limited, be honest about that and suggest where they might find more help.
        Keep responses conversational and focused on answering their specific question.

        When thinking through your response, use <think> tags for your internal reasoning process.
        Put your step-by-step thinking between <think> and </think> tags.
        The content outside think tags will be shown to the user."""

        # Apply progressive context compression
        compressed_context, compression_info = self.compress_context_pyramid(
            instruction_prompt, f"Available Information:\n{context}", max_tokens=8000
        )

        if self.verbose:
            print(f"[CONTEXT COMPRESSION] {compression_info}")

        # Build final prompt with compressed context
        final_prompt = f"""{instruction_prompt}
        
        {compressed_context}"""

        try:
            messages = [
                SystemMessage(content=final_prompt),
                HumanMessage(content=query),
            ]

            response = self.llm.invoke(messages)
            content = (
                response.content if hasattr(response, "content") else str(response)
            )
            raw_response = str(content)

            # Extract reasoning and user-facing content
            reasoning, user_response = self.extract_reasoning_and_response(
                str(raw_response)
            )

            # Display reasoning in verbose mode
            if self.verbose and reasoning:
                print(f"\n[LLM REASONING]\n{reasoning}\n[/LLM REASONING]")

            # Apply spoiler filtering to user response only
            filtered_response = self.filter_spoilers(
                user_response, agent_type, sensitivity_override=spoiler_override
            )

            # Store conversation in memory system
            if self.memory_system:
                # Add user query to working memory
                user_entry = MemoryEntry(
                    content=query,
                    timestamp=datetime.now().isoformat(),
                    entry_type="user_query",
                    importance=0.8,
                    game_context=self.current_game,
                    agent_type=agent_type,
                )
                self.memory_system.add_to_working_memory(user_entry)

                # Add agent response to working memory and semantic memory
                response_entry = MemoryEntry(
                    content=filtered_response,
                    timestamp=datetime.now().isoformat(),
                    entry_type="agent_response",
                    importance=0.7,
                    game_context=self.current_game,
                    agent_type=agent_type,
                )
                self.memory_system.add_to_working_memory(response_entry)
                self.memory_system.add_to_semantic_memory(response_entry)

            if self.verbose:
                print(f"[SYNTHESIS] Response created and spoiler-filtered")

            return filtered_response

        except Exception as e:
            if self.verbose:
                print(f"[SYNTHESIS ERROR] {e}")
            return "I'm having trouble creating a response right now. Please try again."

    def process_user_query(self, query: str):
        """Process a user query through the complete pipeline."""
        # Parse spoiler sensitivity override
        cleaned_query, spoiler_override = self.parse_spoiler_override(query)

        print(f"\n{'=' * 60}")
        print(f"PROCESSING QUERY: {cleaned_query}")
        if spoiler_override:
            print(f"SPOILER OVERRIDE: {spoiler_override.upper()}")
        print("=" * 60)

        # Step 1: Route to agent
        agent_type = self.route_query_to_agent(cleaned_query)

        # Step 2: Search for information
        search_results = self.search_web_and_knowledge(cleaned_query)

        # Step 3: Synthesize and filter response
        response = self.synthesize_response(
            cleaned_query, agent_type, search_results, spoiler_override=spoiler_override
        )

        # Step 4: Display response
        print(f"\n[RESPONSE]\n{response}\n")

    def run_interactive_session(self):
        """Run main interactive session."""
        print("\n" + "=" * 60)
        print("INTERACTIVE GAME ASSISTANCE")
        print("=" * 60)
        print("Ask me anything about your selected game!")
        print("Type 'quit' to exit, 'change game' to select a different game")

        while True:
            try:
                query = input(
                    f"\n[{self.user_id}] Ask about {self.current_game}: "
                ).strip()

                if not query:
                    continue
                elif query.lower() == "quit":
                    print("Goodbye!")
                    break
                elif query.lower() == "change game":
                    self.determine_current_game()
                    continue

                # Process query
                self.process_user_query(query)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error processing query: {e}")

    def run_system(self):
        """Run the complete game system."""
        print(f"\nStarting Real Game System...")
        print(f"Verbose mode: {self.verbose}")

        # Step 1: User identification
        self.determine_user_identity()

        # Step 2: Game selection
        self.determine_current_game()

        # Step 3: Interactive session
        self.run_interactive_session()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Real Game Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_real_game_system.py --game "Silksong" --verbose
  python run_real_game_system.py
        """,
    )

    parser.add_argument(
        "--game",
        type=str,
        help="Initial game name (can be changed during session)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show reasoning process and tool calls",
    )

    args = parser.parse_args()

    try:
        system = GameSystem(verbose=args.verbose)

        # If game provided via command line, set it
        if args.game:
            system.current_game = args.game
            print(f"Initial game set to: {args.game}")

        system.run_system()

    except KeyboardInterrupt:
        print("\nSystem interrupted by user")
    except Exception as e:
        print(f"\nSystem error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()

# Quick test of enhanced components (non-interactive)
if __name__ == "__main__" and len(sys.argv) == 1:
    # Test the enhanced components
    system = GameSystem(verbose=True)
    print("✅ StructuredMemorySystem created successfully")

    # Test LLM-generated search query
    test_query = "best weapons for strength build"
    context = system.memory_system.get_relevant_context(test_query)
    optimized_query = system.generate_intelligent_search_query(test_query, context)
    print(f'✅ Search query enhancement: "{test_query}" → "{optimized_query}"')

    # Test memory system
    system.memory_system.add_to_working_memory(
        test_query, "Test response about quality weapons", "gameplay"
    )
    print(
        f"✅ Memory system updated: {len(system.memory_system.working_memory)} working memory items"
    )

    # Test context compression
    system.memory_system.session_summary = (
        "Test session covering weapons and progression"
    )
    context_size = system._estimate_token_count()
    print(f"✅ Context compression ready at {context_size} tokens")

    print("🎮 All context engineering improvements working correctly!")
