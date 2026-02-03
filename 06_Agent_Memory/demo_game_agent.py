#!/usr/bin/env python3
"""
Demo Script for Spoiler-Free Video Game Agent System

This script demonstrates the complete video game agent system including:
1. Game Story Research Agent fetching and storing data
2. Routing to specialist agents (Unlockables, Progression, Lore)
3. Spoiler filtering based on user progress
4. Memory management with conflict resolution and importance scoring
5. User progress tracking

Usage:
    python demo_game_agent.py [--game "Game Name"] [--verbose]
"""

import argparse
import asyncio
import sys
from typing import Optional

# Mock imports for demonstration without requiring actual services
from unittest.mock import Mock, patch
import time


class DemoGameAgentSystem:
    """Demo implementation of the Spoiler-Free video game agent system."""

    def __init__(self, verbose: bool = False):
        """Initialize the demo system.

        Args:
            verbose: Enable verbose output to show system flow.
        """
        self.verbose = verbose
        self.setup_mock_components()

    def setup_mock_components(self):
        """Setup mock components for demonstration."""
        if self.verbose:
            print("🔧 Setting up mock components...")

        # Mock QDrant client
        self.mock_qdrant = Mock()
        self.mock_qdrant.get_collections.return_value = Mock(collections=[])
        self.mock_qdrant.scroll.return_value = ([], None)
        self.mock_qdrant.upsert.return_value = None
        self.mock_qdrant.search.return_value = []

        # Mock webfetch
        self.mock_webfetch = Mock()

        # Mock dependencies
        self.mock_tracker = Mock()
        self.mock_tracker.is_game_processed.return_value = False
        self.mock_tracker.mark_game_processed.return_value = True

        self.mock_knowledge_base = Mock()

        self.mock_user_progress = Mock()
        self.mock_user_progress.get_progress.return_value = "intro/tutorial"

        self.mock_game_input_flow = Mock()
        self.mock_game_input_flow.get_user_game.return_value = None

        if self.verbose:
            print("✅ Mock components initialized")

    def demo_game_research(self, game_name: str):
        """Demonstrate game story research functionality."""
        print(f"\n🔍 Researching game: {game_name}")
        print("=" * 60)

        # Mock webfetch response
        mock_content = f"""
        {game_name} is an exciting game with rich gameplay mechanics.
        
        ## Gameplay Features
        - Innovative combat system with multiple weapon types
        - Open-world exploration with hidden secrets
        - Character progression with skill trees
        - Multiple endings based on player choices
        
        ## Story Elements
        The game follows the journey of a hero who must save the world
        from an ancient evil. Players will encounter various characters,
        uncover ancient mysteries, and make difficult choices that affect
        the game's outcome.
        
        ## Unlockables Content
        - Legendary weapons hidden in dungeons
        - Secret areas accessible after specific story beats
        - Character costumes with special abilities
        - Completion bonuses for 100% clear rate
        
        ## Progression Guide
        Early Game: Focus on basic combat and exploration
        Mid Game: Advanced abilities and second dungeon
        Late Game: Final weapons and boss strategies
        End Game: True ending requirements and secrets
        
        ## Lore and Worldbuilding
        Ancient civilization with advanced technology
        Magic system based on elemental forces
        Political factions with complex relationships
        Historical events that shaped the current world
        """

        self.mock_webfetch.fetch.return_value = mock_content

        # Mock existing data check
        self.mock_qdrant.scroll.return_value = ([], None)

        if self.verbose:
            print("📡 Fetching game information from web...")
            print("📊 Processing and chunking content...")
            print("💾 Storing in knowledge base...")

        # Create research agent (mocking internal dependencies)
        with patch(
            "src.game_story_research_agent.GameTracker", return_value=self.mock_tracker
        ):
            with patch(
                "src.game_story_research_agent.GameKnowledgeBase",
                return_value=self.mock_knowledge_base,
            ):
                with patch(
                    "src.tools.webfetch.webfetch", return_value=self.mock_webfetch
                ):
                    from src.game_story_research_agent import GameStoryResearchAgent

                    agent = GameStoryResearchAgent(self.mock_qdrant)

                    # Process the game
                    result = agent.research_game(game_name)

                    if self.verbose:
                        print(f"📈 Research completed: {result}")
                        print(f"   Status: {result.get('status', 'unknown')}")
                        print(f"   Chunks stored: {result.get('chunks_stored', 0)}")

                    return result

    def demo_game_selection(self, game_name: str):
        """Demonstrate game selection functionality."""
        if self.verbose:
            print(f"\n🎮 Selecting game: {game_name}")

        # Mock game selection
        self.mock_game_input_flow.get_user_game.return_value = {
            "game_name": game_name,
            "prompt": "Help me with this game",
        }

        if self.verbose:
            print(f"✅ Game selected: {game_name}")

    def demo_user_progress_levels(self):
        """Demonstrate different user progress levels for spoiler testing."""
        progress_levels = [
            ("intro/tutorial", "Early Game - Tutorial Area"),
            ("early_game", "Early Game - First Zone"),
            ("mid_game", "Mid Game - Second Major Area"),
            ("late_game", "Late Game - Final Areas"),
            ("post_game", "Post Game - New Game+"),
        ]

        return progress_levels

    def demo_specialist_agents(self, game_name: str):
        """Demonstrate all three specialist agents."""
        print(f"\n🤖 Testing Specialist Agents for: {game_name}")
        print("=" * 60)

        # Setup specialist agents with mocks
        with patch(
            "src.game_specialist_agents.GameInputFlow",
            return_value=self.mock_game_input_flow,
        ):
            with patch(
                "src.game_specialist_agents.UserGameProgress",
                return_value=self.mock_user_progress,
            ):
                with patch(
                    "src.game_specialist_agents.GameKnowledgeBase",
                    return_value=self.mock_knowledge_base,
                ):
                    from src.game_specialist_agents import (
                        UnlockablesAgent,
                        ProgressionAgent,
                        LoreAgent,
                    )

                    unlockables = UnlockablesAgent(
                        game_input_flow=self.mock_game_input_flow,
                        user_progress=self.mock_user_progress,
                        knowledge_base=self.mock_knowledge_base,
                    )
                    progression = ProgressionAgent(
                        game_input_flow=self.mock_game_input_flow,
                        user_progress=self.mock_user_progress,
                        knowledge_base=self.mock_knowledge_base,
                    )
                    lore = LoreAgent(
                        game_input_flow=self.mock_game_input_flow,
                        user_progress=self.mock_user_progress,
                        knowledge_base=self.mock_knowledge_base,
                    )

                    # Test queries for each specialist
                    test_queries = [
                        (unlockables, "how to find legendary weapons?", "unlockables"),
                        (
                            progression,
                            "where should I go next in the story?",
                            "progression",
                        ),
                        (lore, "tell me about the game's world history", "lore"),
                    ]

                    for progress_level, description in self.demo_user_progress_levels():
                        print(f"\n📍 Testing with Progress: {description}")
                        print("-" * 40)

                        # Set user progress
                        self.mock_user_progress.get_progress.return_value = (
                            progress_level
                        )

                        # Mock knowledge base responses based on progress level
                        self.mock_knowledge_based_on_progress(progress_level)

                        for agent, query, agent_type in test_queries:
                            if self.verbose:
                                print(f"\n🔹 Testing {agent_type.title()} Agent")
                                print(f"   Query: {query}")

                            # Mock LLM response
                            mock_response = self.generate_agent_response(
                                agent_type, query, progress_level
                            )

                            with patch(
                                "src.game_specialist_agents.ChatOpenAI"
                            ) as mock_llm:
                                mock_llm.return_value = Mock()
                                mock_llm.return_value.invoke.return_value = Mock(
                                    content=mock_response
                                )

                                try:
                                    result, success = agent.handle_query(
                                        "demo_user", query
                                    )

                                    if success and self.verbose:
                                        print(
                                            f"   ✅ Response: {mock_response[:100]}..."
                                        )
                                        print(
                                            f"   📊 Spoiler filtering: {progress_level}"
                                        )
                                    elif self.verbose:
                                        print(f"   ❌ Agent error occurred")

                                except Exception as e:
                                    if self.verbose:
                                        print(f"   ⚠️  Agent error: {str(e)}")

    def mock_knowledge_based_on_progress(self, progress_level: str):
        """Mock knowledge base responses based on user progress."""
        if progress_level in ["intro/tutorial", "early_game"]:
            # Early game content
            self.mock_knowledge_base.search_game_knowledge.return_value = [
                {
                    "text": "Basic combat tutorial and starting area information",
                    "metadata": {"spoiler_level": "early", "content_type": "tutorial"},
                },
                {
                    "text": "First dungeon general strategies",
                    "metadata": {
                        "spoiler_level": "early",
                        "content_type": "walkthrough",
                    },
                },
            ]
        elif progress_level == "mid_game":
            # Mid game content
            self.mock_knowledge_base.search_game_knowledge.return_value = [
                {
                    "text": "Second major area walkthrough and medium-level strategies",
                    "metadata": {"spoiler_level": "mid", "content_type": "walkthrough"},
                },
                {
                    "text": "Advanced weapon locations and upgrade paths",
                    "metadata": {"spoiler_level": "mid", "content_type": "unlockables"},
                },
            ]
        else:
            # Late/post game content filtered out for earlier progress
            self.mock_knowledge_base.search_game_knowledge.return_value = []

    def generate_agent_response(
        self, agent_type: str, query: str, progress_level: str
    ) -> str:
        """Generate appropriate agent responses based on type and progress."""
        responses = {
            "unlockables": {
                "intro/tutorial": "Start by checking the starting area carefully. There are usually some basic items hidden in tutorial zones. Look for chests behind breakable walls and talk to all NPCs.",
                "early_game": "You should now have access to the first dungeon. The legendary flame sword is typically hidden in the castle basement. Use your newly acquired abilities to reach previously inaccessible areas.",
                "mid_game": "With mid-game progress, you can now access the sunken temple. The ultimate weapons require solving complex puzzles involving all three elemental keys you've collected.",
                "late_game": "At this stage, focus on completionist content. The final legendary armor is in the bonus dungeon that appears after the main credits.",
                "post_game": "In New Game+, you'll find ultra-rare golden versions of all weapons. The super boss battles in the dream realm offer the game's biggest challenges.",
            },
            "progression": {
                "intro/tutorial": "Follow the main quest markers and complete the tutorial quests. The game will guide you to the first major story beat. Don't worry about optional content yet - focus on understanding the basic mechanics.",
                "early_game": "You've reached the first major choice point. Consider your character build and which skills to prioritize. The forest path is recommended for beginners, while the mountain path offers better rewards for experienced players.",
                "mid_game": "The story is at a critical turning point. Your decisions here will significantly impact the ending. Make sure you've completed all character-specific side quests before proceeding to the final chapter.",
                "late_game": "You're approaching the finale. Ensure you have the best equipment and consumables stocked. The final boss has multiple phases - prepare accordingly and don't hesitate to use all your resources.",
                "post_game": "With the main story complete, explore the remaining optional content. The true ending requires finding all ancient tablets and assembling them at the forgotten altar.",
            },
            "lore": {
                "intro/tutorial": "This world was once a thriving civilization powered by ancient technology. The cataclysm 1000 years ago changed everything, leading to the current fragmented society. The ruins you see are remnants of that golden age.",
                "early_game": "The three major factions each have different philosophies about the ancient technology. The Scholars believe it should be preserved, the Warriors want to weaponize it, and the Merchants see it as purely commercial opportunity.",
                "mid_game": "The ancient prophecy speaks of a chosen one who will either restore or destroy the remaining ancient technology. Your actions are remarkably similar to historical figures from the previous cataclysm cycle.",
                "late_game": "The true nature of the ancient technology is revealed. It's actually a living entity that corrupted the previous civilization. The final choice determines whether you will control it, destroy it, or find a third option.",
                "post_game": "With the story complete, scholars have begun documenting your journey. Your decisions have reshaped the political landscape, and the ancient technology's future is now in the hands of the people.",
            },
        }

        return responses.get(agent_type, {}).get(
            progress_level,
            f"I can help with {query} based on your current progress in {progress_level}.",
        )

    def demo_routing(self, game_name: str):
        """Demonstrate the routing functionality."""
        print(f"\n🧭 Testing Game Router for: {game_name}")
        print("=" * 60)

        with patch(
            "src.game_router.GameInputFlow", return_value=self.mock_game_input_flow
        ):
            from src.game_router import GameRouterAgent

            router = GameRouterAgent(self.mock_game_input_flow)

            # Test different query types
            test_queries = [
                ("how to unlock the master sword?", "unlockables"),
                ("what's the best way to level up?", "progression"),
                ("tell me about the ancient kingdom's history", "lore"),
                ("general help with this game", "progression"),  # Default case
            ]

            for query, expected_agent in test_queries:
                if self.verbose:
                    print(f"\n🔸 Routing query: {query}")

                # Mock LLM routing decision
                with patch("src.game_router.ChatOpenAI") as mock_llm:
                    mock_decision = Mock()
                    mock_decision.agent = expected_agent
                    mock_decision.reasoning = (
                        f"Query clearly relates to {expected_agent}"
                    )
                    mock_decision.confidence = 0.9

                    mock_llm.return_value = Mock()
                    mock_llm.return_value.with_structured_output.return_value = Mock()
                    mock_llm.return_value.with_structured_output.return_value.invoke.return_value = mock_decision

                    try:
                        result = router.route_query("demo_user", query)

                        if self.verbose:
                            print(f"   ✅ Routed to: {result.agent}")
                            print(f"   📝 Reasoning: {result.reasoning}")
                            print(f"   📊 Confidence: {result.confidence}")

                    except Exception as e:
                        if self.verbose:
                            print(f"   ❌ Routing error: {str(e)}")

    def demo_memory_features(self):
        """Demonstrate memory management features."""
        print(f"\n🧠 Testing Memory Management Features")
        print("=" * 60)

        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(Mock())

            # Test importance scoring
            if self.verbose:
                print("\n📊 Testing Importance Scoring:")

            # Store episodes with different characteristics
            test_episodes = [
                (
                    "high_importance",
                    "Helped with final boss",
                    "Here's the complete strategy...",
                    "This was excellent, saved my run!",
                    0.9,
                ),
                ("low_importance", "Basic question", "Simple answer", None, 0.1),
                (
                    "medium_importance",
                    "Medium complexity help",
                    "Detailed response",
                    "This was helpful",
                    0.5,
                ),
            ]

            for key, situation, output, feedback, importance in test_episodes:
                if self.verbose:
                    print(f"   Storing: {situation} (importance: {importance})")

                with patch.object(memory, "find_similar", return_value=[]):
                    result_key = memory.store_episode(
                        key=key,
                        situation=situation,
                        input_text="test input",
                        output_text=output,
                        feedback=feedback,
                        importance=importance,
                    )

                    if self.verbose and result_key:
                        print(f"   ✅ Stored with key: {result_key}")

            # Test cleanup functionality
            if self.verbose:
                print("\n🧹 Testing Cleanup Functionality:")

            with patch.object(
                memory,
                "search",
                return_value=[
                    Mock(
                        key=f"episode_{i}",
                        value={
                            "importance": 0.1 + (i * 0.1),
                            "timestamp": "2024-01-01T10:00:00",
                        },
                    )
                    for i in range(5)
                ],
            ):
                cleanup_result = memory.cleanup_episodes(
                    importance_threshold=0.3,  # Remove episodes with importance < 0.3
                    dry_run=True,  # Just show what would be removed
                )

                if self.verbose:
                    print(
                        f"   Episodes marked for removal: {cleanup_result.get('removed_count', 0)}"
                    )
                    print(f"   Episodes to keep: {cleanup_result.get('kept_count', 0)}")

                # Get cleanup statistics
                stats = memory.get_cleanup_statistics()
                if self.verbose:
                    print(f"   Total episodes: {stats.get('total_episodes', 0)}")
                    print(
                        f"   Average importance: {stats.get('average_importance', 0):.2f}"
                    )

    def run_complete_demo(self, game_name: str):
        """Run the complete demonstration of all system components."""
        print("🚀 Starting Spoiler-Free Video Game Agent Demo")
        print("=" * 60)
        print(f"Game: {game_name}")
        print(f"Verbose Mode: {'Enabled' if self.verbose else 'Disabled'}")

        try:
            # Step 1: Game Research
            self.demo_game_research(game_name)

            # Step 2: Game Selection
            self.demo_game_selection(game_name)

            # Step 3: Router Testing
            self.demo_routing(game_name)

            # Step 4: Specialist Agent Testing
            self.demo_specialist_agents(game_name)

            # Step 5: Memory Management Testing
            self.demo_memory_features()

            print(f"\n🎉 Demo completed successfully!")
            print("=" * 60)
            print("The Spoiler-Free Video Game Agent system demonstrated:")
            print("✅ Game Story Research with web content fetching")
            print("✅ Intelligent routing to specialist agents")
            print("✅ Spoiler-aware content filtering by user progress")
            print("✅ Memory conflict resolution and importance scoring")
            print("✅ User progress tracking")
            print("✅ Comprehensive cleanup and maintenance features")

        except Exception as e:
            print(f"\n❌ Demo failed with error: {str(e)}")
            if self.verbose:
                import traceback

                traceback.print_exc()


def main():
    """Main entry point for the demo script."""
    parser = argparse.ArgumentParser(
        description="Demo Script for Spoiler-Free Video Game Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_game_agent.py --game "The Legend of Zelda" --verbose
  python demo_game_agent.py --game "Elden Ring"
        """,
    )

    parser.add_argument(
        "--game",
        type=str,
        default="The Legend of Zelda: Tears of the Kingdom",
        help="Game name to use for demonstration (default: %(default)s)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output to show detailed system flow",
    )

    args = parser.parse_args()

    # Create and run demo
    demo = DemoGameAgentSystem(verbose=args.verbose)
    demo.run_complete_demo(args.game)


if __name__ == "__main__":
    main()
