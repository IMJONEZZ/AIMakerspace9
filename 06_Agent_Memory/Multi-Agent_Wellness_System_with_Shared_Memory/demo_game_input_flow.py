"""
Demo: Game Input Flow Conversation

This script demonstrates the initial game input flow where users specify
which game they're asking about before any routing or agent invocation.

Usage:
    python demo_game_input_flow.py
"""

from src.game_input_flow import create_game_input_flow


def simulate_conversation():
    """Simulate a conversation showing the game input flow."""
    print("=" * 70)
    print("SPOILER-FREE VIDEO GAME AGENT SYSTEM - Game Input Flow Demo")
    print("=" * 70)

    # Initialize the game input flow
    game_flow = create_game_input_flow()
    user_id = "demo_user"

    # Step 1: Initial greeting and prompt for game selection
    print("\n--- Step 1: User starts chat ---")
    print("User joins the conversation...")

    # Check if user has a game selected
    if not game_flow.has_user_game(user_id):
        print("\n" + game_flow.prompt_for_game())

    # Step 2: User specifies the game
    print("\n--- Step 2: User responds with game name ---")
    user_response = "I'm playing Elden Ring"

    # Parse the game name from user response (in a real system, this would use NLP)
    # For demo purposes, we'll just extract "Elden Ring"
    if "elden ring" in user_response.lower():
        game_name = "Elden Ring"
        normalized_name = game_flow.normalize_game_name(game_name)

        # Store the user's game selection
        game_flow.set_user_game(user_id, normalized_name, game_name)

        print(f"\nSystem: Great! I've noted that you're playing {game_name}.")
        print("How can I help you with your gameplay?")
    else:
        print("\nSystem: I couldn't identify the game. Please specify again.")
        return

    # Step 3: User asks a question
    print("\n--- Step 3: User asks for help ---")
    user_query = "How do I defeat the first boss?"

    print(f"\nUser: {user_query}")

    # Get the user's selected game
    game_info = game_flow.get_user_game(user_id)

    if game_info:
        print(f"\n[System Context]")
        print(f"  - User has selected: {game_info['display_name']}")
        print(f"  - Normalized name: {game_info['game_name']}")
        print(f"  - Selected at: {game_info['selected_at']}")

        # This game_name would be passed to:
        # 1. Game Story Research Agent (for knowledge base population)
        # 2. All specialist agents (for their queries)

        print(f"\n[System Processing]")
        print(f"  - Routing query to appropriate specialist agent...")
        print(f"  - Passing game_name='{game_info['game_name']}' to specialist")
        print(f"  - Specialist searches knowledge base for: {user_query}")
        print(f"  - Filtering results to avoid spoilers...")

    # Step 4: System response (simulated)
    print(
        f"\nAgent: To defeat the first boss in Elden Ring, head to Stormveil Castle. "
        "The Grafted Knight guards the entrance and can be challenging for newcomers."
    )

    # Step 5: User asks another question
    print("\n--- Step 4: User asks follow-up question ---")
    user_query_2 = "What about the second boss?"

    print(f"\nUser: {user_query_2}")

    # Get the user's selected game (still persists)
    game_info = game_flow.get_user_game(user_id)

    if game_info:
        print(f"\n[System Context]")
        print(f"  - User has selected: {game_info['display_name']} (persisted)")
        print(f"  - No need to re-prompt for game!")

    # Step 6: User asks about a different game
    print("\n--- Step 5: User wants to switch games ---")
    user_response_2 = "Actually, let me ask about Minecraft instead."

    print(f"\nUser: {user_response_2}")

    # Clear the old game and set the new one
    if "minecraft" in user_response_2.lower():
        old_game = game_flow.get_user_game(user_id)["display_name"]
        game_flow.clear_user_game(user_id)
        new_game = "Minecraft"
        normalized_name = game_flow.normalize_game_name(new_game)
        game_flow.set_user_game(user_id, normalized_name, new_game)

        print(f"\nSystem: Got it! Switching from {old_game} to {new_game}.")
        print("How can I help you with Minecraft?")

    # Step 7: User asks a Minecraft question
    print("\n--- Step 6: User asks about Minecraft ---")
    user_query_3 = "How do I craft a pickaxe?"

    print(f"\nUser: {user_query_3}")

    game_info = game_flow.get_user_game(user_id)
    if game_info:
        print(f"\n[System Context]")
        print(f"  - User has selected: {game_info['display_name']}")
        print(f"  - All queries will now search Minecraft knowledge base")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: Game Input Flow Benefits")
    print("=" * 70)
    print("\n1. Eliminates need for game detection in router")
    print("2. Explicit user input ensures accuracy")
    print("3. Game context persists across conversation")
    print("4. Easy to switch games if user changes topics")
    print("5. Game name passed consistently to all agents:")
    print("   - Game Story Research Agent (knowledge base population)")
    print("   - Unlockables Agent")
    print("   - Progression Agent")
    print("   - Lore Agent")


def show_api_usage():
    """Show the API usage for game input flow."""
    print("\n" + "=" * 70)
    print("API USAGE EXAMPLE")
    print("=" * 70)

    print("""
from src.game_input_flow import create_game_input_flow

# Initialize
game_flow = create_game_input_flow()

# Prompt for game (show at start of chat)
prompt = game_flow.prompt_for_game()
print(prompt)

# User responds: "I'm playing Elden Ring"

# Parse and store the game
game_name = "Elden Ring"
normalized_name = game_flow.normalize_game_name(game_name)
game_flow.set_user_game(user_id="user_123", game_name=normalized_name, display_name=game_name)

# Check if user has a game selected
if game_flow.has_user_game("user_123"):
    # Get the game context for routing and agent queries
    game_info = game_flow.get_user_game("user_123")
    print(f"User is playing: {game_info['display_name']}")

    # Pass game_name to all specialist agents
    routing_result = router.route_query(user_id, query)
    agent_response = specialist_agent.handle_query(
        user_id=user_id,
        query=query,
        game_name=game_info['game_name']  # <-- Passed to all agents
    )

# Clear user's game (if they switch)
game_flow.clear_user_game("user_123")
""")


if __name__ == "__main__":
    simulate_conversation()
    show_api_usage()

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
