"""
Text-based Memory Dashboard for Multi-Agent Wellness System

This dashboard provides a simple command-line interface to view and search
the system's memory state, including:
- User profiles
- Knowledge base chunks
- Agent episodes
- Cross-agent learning statistics
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import create_wellness_system


class MemoryDashboard:
    """Text-based dashboard for memory visualization."""

    def __init__(self):
        """Initialize the memory dashboard."""
        print("Initializing wellness system...")
        self.system = create_wellness_system()
        self.running = True

    def show_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 60)
        print("Multi-Agent Wellness System - Memory Dashboard")
        print("=" * 60)
        print("\nAvailable Commands:")
        print("1. View System Statistics")
        print("2. List User Profiles")
        print("3. View User Profile Details")
        print("4. Search Knowledge Base")
        print("5. View Agent Episodes")
        print("6. Search Episodes")
        print("7. View Cross-Agent Learning Coverage")
        print("8. Interactive Query Mode")
        print("q. Quit")
        print("=" * 60)

    def show_system_stats(self):
        """Display system-wide statistics."""
        print("\n" + "-" * 60)
        print("System Statistics")
        print("-" * 60)

        stats = self.system.get_system_stats()

        print("\n📊 Memory Statistics:")
        for key, value in stats["memory"].items():
            print(f"   {key}: {value}")

        print("\n📚 Episode Statistics:")
        for agent, agent_stats in stats["episodes"].items():
            print(f"\n   {agent}:")
            for stat_key, stat_value in agent_stats.items():
                if isinstance(stat_value, float):
                    print(f"      {stat_key}: {stat_value:.2f}")
                else:
                    print(f"      {stat_key}: {stat_value}")

        print("\n🧠 Learning Coverage:")
        for agent, topics in stats["coverage"].items():
            if topics:
                print(f"   {agent}:")
                topic_str = ", ".join(topics[:5])
                if len(topics) > 5:
                    topic_str += f" ... and {len(topics) - 5} more"
                print(f"      Topics: {topic_str}")
            else:
                print(f"   {agent}: No episodes yet")

    def list_user_profiles(self):
        """List all user profiles in the system."""
        print("\n" + "-" * 60)
        print("User Profiles")
        print("-" * 60)

        try:
            all_items = list(self.system.memory.store.search(()))
            profiles = {}

            for item in all_items:
                if len(item.namespace) >= 2 and item.namespace[1] == "profile":
                    user_id = item.namespace[0]
                    if user_id not in profiles:
                        profiles[user_id] = {}
                    profiles[user_id][item.key] = item.value.get("value")

            if not profiles:
                print("\n  No user profiles found.")
            else:
                for user_id, profile in profiles.items():
                    print(f"\n  👤 User: {user_id}")
                    for key, value in profile.items():
                        if isinstance(value, list):
                            print(f"     {key}: {', '.join(str(v) for v in value)}")
                        else:
                            print(f"     {key}: {value}")
        except Exception as e:
            print(f"\n  Error listing profiles: {e}")

    def view_user_profile(self):
        """View details for a specific user profile."""
        print("\n" + "-" * 60)
        print("View User Profile Details")
        print("-" * 60)

        user_id = input("\nEnter user ID: ").strip()

        if not user_id:
            print("User ID cannot be empty.")
            return

        try:
            profile = self.system.get_user_profile(user_id)

            if not profile:
                print(f"\n  No profile found for user: {user_id}")
            else:
                print(f"\n  👤 Profile for: {user_id}")
                for key, value in profile.items():
                    if isinstance(value, list):
                        print(f"     {key}:")
                        for item in value:
                            print(f"        - {item}")
                    else:
                        print(f"     {key}: {value}")
        except Exception as e:
            print(f"\n  Error retrieving profile: {e}")

    def search_knowledge_base(self):
        """Search the wellness knowledge base."""
        print("\n" + "-" * 60)
        print("Search Knowledge Base")
        print("-" * 60)

        query = input("\nEnter search query: ").strip()

        if not query:
            print("Query cannot be empty.")
            return

        try:
            results = self.system.memory.search_knowledge_base(query, limit=5)

            if not results:
                print("\n  No matching knowledge found.")
            else:
                print(f"\n  Found {len(results)} relevant results:")
                for i, result in enumerate(results, 1):
                    text = result.value.get("text", "")
                    print(f"\n  {i}. (Score: {result.score:.3f})")
                    print(f"     {text[:200]}...")
        except Exception as e:
            print(f"\n  Error searching knowledge base: {e}")

    def view_agent_episodes(self):
        """View episodes for a specific agent."""
        print("\n" + "-" * 60)
        print("View Agent Episodes")
        print("-" * 60)

        agents = ["exercise", "nutrition", "sleep"]
        print("\nAvailable agents:", ", ".join(agents))

        agent_name = input("\nEnter agent name: ").strip().lower()

        if agent_name not in agents:
            print(f"Invalid agent. Please choose from: {', '.join(agents)}")
            return

        try:
            full_agent_name = f"{agent_name}_agent"
            episodes = self.system.memory.get_agent_episodes(full_agent_name)

            if not episodes:
                print(f"\n  No episodes found for {agent_name}_agent")
            else:
                print(f"\n  Found {len(episodes)} episodes:")
                for i, ep in enumerate(episodes, 1):
                    print(f"\n  {i}. Situation: {ep.get('situation', 'N/A')[:80]}...")
                    print(f"     Input: {ep.get('input', 'N/A')[:60]}...")
                    print(f"     Output: {ep.get('output', 'N/A')[:60]}...")
                    if ep.get("feedback"):
                        print(f"     Feedback: {ep['feedback'][:60]}...")
        except Exception as e:
            print(f"\n  Error retrieving episodes: {e}")

    def search_episodes(self):
        """Search across all agent episodes."""
        print("\n" + "-" * 60)
        print("Search Episodes")
        print("-" * 60)

        query = input("\nEnter search query: ").strip()

        if not query:
            print("Query cannot be empty.")
            return

        try:
            cross_agent_episodes = self.system.memory.get_cross_agent_episodes(
                query=query, exclude_agent=None, limit_per_agent=2
            )

            if not cross_agent_episodes:
                print("\n  No matching episodes found.")
            else:
                print(f"\n  Found episodes from {len(cross_agent_episodes)} agents:")
                for agent_name, episodes in cross_agent_episodes.items():
                    print(f"\n  📦 {agent_name}:")
                    for i, ep in enumerate(episodes, 1):
                        print(
                            f"     {i}. Situation: {ep.get('situation', 'N/A')[:60]}..."
                        )
        except Exception as e:
            print(f"\n  Error searching episodes: {e}")

    def view_cross_agent_coverage(self):
        """View cross-agent learning coverage."""
        print("\n" + "-" * 60)
        print("Cross-Agent Learning Coverage")
        print("-" * 60)

        try:
            stats = self.system.get_system_stats()
            coverage = stats["coverage"]

            print("\n  Topics each agent has learned about:")
            for agent, topics in coverage.items():
                print(f"\n  🤖 {agent}:")
                if topics:
                    for topic in topics[:10]:
                        print(f"     • {topic}")
                else:
                    print("     No episodes yet")

            print("\n  💡 Cross-agent learning enables agents to:")
            print("     • Learn from each other's successful interactions")
            print("     • Provide context-aware recommendations")
            print("     • Avoid repeating mistakes made by other agents")

        except Exception as e:
            print(f"\n  Error retrieving coverage: {e}")

    def interactive_query_mode(self):
        """Interactive mode to send queries to the system."""
        print("\n" + "-" * 60)
        print("Interactive Query Mode")
        print("-" * 60)
        print("\nEnter a user ID to start (or 'back' to return to menu)")

        while True:
            user_id = input("\nUser ID: ").strip()

            if user_id.lower() == "back":
                break

            if not user_id:
                print("Please enter a valid user ID.")
                continue

            while True:
                query = input("\nQuery (or 'back' to change user): ").strip()

                if query.lower() == "back":
                    break

                if not query:
                    print("Please enter a valid query.")
                    continue

                try:
                    result = self.system.handle_query(user_id, query)

                    print(f"\n🎯 Routed to: {result['agent_used']}")
                    print(f"💭 Reasoning: {result['routing_reasoning']}")
                    print(f"\n📝 Response:")
                    print(result["response"])
                except Exception as e:
                    print(f"\n❌ Error: {e}")

    def run(self):
        """Run the main dashboard loop."""
        while self.running:
            try:
                self.show_menu()
                choice = input("\nEnter your choice: ").strip().lower()

                if choice == "1":
                    self.show_system_stats()
                elif choice == "2":
                    self.list_user_profiles()
                elif choice == "3":
                    self.view_user_profile()
                elif choice == "4":
                    self.search_knowledge_base()
                elif choice == "5":
                    self.view_agent_episodes()
                elif choice == "6":
                    self.search_episodes()
                elif choice == "7":
                    self.view_cross_agent_coverage()
                elif choice == "8":
                    self.interactive_query_mode()
                elif choice in ["q", "quit", "exit"]:
                    print("\nThank you for using the Memory Dashboard!")
                    self.running = False
                else:
                    print("\nInvalid choice. Please try again.")

            except KeyboardInterrupt:
                print("\n\nInterrupted by user.")
                self.running = False
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                input("\nPress Enter to continue...")


def main():
    """Main entry point for the dashboard."""
    print("=" * 60)
    print("Multi-Agent Wellness System")
    print("Text-based Memory Dashboard")
    print("=" * 60)

    dashboard = MemoryDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
