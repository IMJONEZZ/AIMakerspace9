"""
Test script for GameTracker
"""

import sys

sys.path.insert(0, "/home/imjonezz/Desktop/AIE9/06_Agent_Memory/src")

from qdrant_client import QdrantClient
from game_tracker import GameTracker


def test_game_tracker():
    """Test the game tracker functionality"""

    print("=" * 60)
    print("Testing GameTracker")
    print("=" * 60)

    # Initialize QDrant client (in-memory for testing)
    qdrant_client = QdrantClient(":memory:")

    # Initialize game tracker
    tracker = GameTracker(qdrant_client)

    print("\n✓ GameTracker initialized")

    # Test 1: Check unprocessed game
    print("\nTest 1: Checking if 'Elden Ring' is processed (should be False)")
    result = tracker.check_game_processed("Elden Ring")
    print(f"Result: {result}")
    assert result == False, "Expected False for unprocessed game"
    print("✓ Test 1 passed")

    # Test 2: Mark a game as processed
    print("\nTest 2: Marking 'Elden Ring' as processed")
    success = tracker.mark_game_processed(
        game_name="Elden Ring",
        chunk_count=1500,
        source_urls=[
            "https://example.com/elden-ring-walkthrough",
            "https://example.com/elden-ring-lore",
        ],
        metadata={"status": "complete", "version": 1.0},
    )
    print(f"Success: {success}")
    assert success == True, "Expected True for successful mark"
    print("✓ Test 2 passed")

    # Test 3: Check processed game
    print("\nTest 3: Checking if 'Elden Ring' is processed (should be True)")
    result = tracker.check_game_processed("Elden Ring")
    print(f"Result: {result}")
    assert result == True, "Expected True for processed game"
    print("✓ Test 3 passed")

    # Test 4: Get all processed games
    print("\nTest 4: Getting all processed games")
    games = tracker.get_processed_games()
    print(f"Found {len(games)} processed game(s):")
    for game in games:
        print(f"  - {game['game_name']} ({game['chunk_count']} chunks)")
    assert len(games) == 1, "Expected 1 processed game"
    print("✓ Test 4 passed")

    # Test 5: Get specific game metadata
    print("\nTest 5: Getting metadata for 'Elden Ring'")
    metadata = tracker.get_game_metadata("Elden Ring")
    print(f"Metadata: {metadata}")
    assert metadata is not None, "Expected metadata to exist"
    assert metadata["chunk_count"] == 1500, "Chunk count mismatch"
    assert len(metadata["source_urls"]) == 2, "Source URLs count mismatch"
    print("✓ Test 5 passed")

    # Test 6: Update existing game
    print("\nTest 6: Updating 'Elden Ring' with new metadata")
    success = tracker.mark_game_processed(
        game_name="Elden Ring",
        chunk_count=2000,  # Updated
        source_urls=["https://new-source.com/elden-ring"],  # Updated
    )
    print(f"Success: {success}")

    metadata = tracker.get_game_metadata("Elden Ring")
    print(f"Updated chunk count: {metadata['chunk_count']}")
    assert metadata["chunk_count"] == 2000, "Chunk count not updated"
    print("✓ Test 6 passed")

    # Test 7: Add another game
    print("\nTest 7: Marking 'Minecraft' as processed")
    success = tracker.mark_game_processed(
        game_name="Minecraft",
        chunk_count=500,
        source_urls=["https://example.com/minecraft-guide"],
    )
    print(f"Success: {success}")
    assert success == True, "Expected True for successful mark"

    games = tracker.get_processed_games()
    print(f"Found {len(games)} processed game(s):")
    for game in games:
        print(f"  - {game['game_name']} ({game['chunk_count']} chunks)")
    assert len(games) == 2, "Expected 2 processed games"
    print("✓ Test 7 passed")

    # Test 8: Remove a game
    print("\nTest 8: Removing 'Minecraft' from tracking")
    success = tracker.remove_game("Minecraft")
    print(f"Success: {success}")

    games = tracker.get_processed_games()
    print(f"After removal, found {len(games)} processed game(s):")
    for game in games:
        print(f"  - {game['game_name']}")
    assert len(games) == 1, "Expected 1 processed game after removal"
    print("✓ Test 8 passed")

    # Test 9: Case insensitivity
    print("\nTest 9: Testing case insensitivity")
    success = tracker.mark_game_processed(
        game_name="THE LEGEND OF ZELDA", chunk_count=100
    )

    # Check with different case
    result = tracker.check_game_processed("the legend of zelda")
    print(f"Check with lowercase: {result}")

    result = tracker.check_game_processed("THE LEGEND OF ZELDA")
    print(f"Check with uppercase: {result}")

    result = tracker.check_game_processed("The Legend of Zelda")
    print(f"Check with title case: {result}")

    assert all([r, r, r]), "Expected True for all case variations"
    print("✓ Test 9 passed")

    # Test 10: Normalized name handling
    print("\nTest 10: Testing normalized name handling")
    success = tracker.mark_game_processed(
        game_name="God of War Ragnarök", chunk_count=300
    )

    metadata = tracker.get_game_metadata("God of War Ragnarök")
    print(f"Normalized name: {metadata['normalized_name']}")
    assert metadata["normalized_name"] == "god_of_war_ragnarök", (
        "Normalized name mismatch"
    )
    print("✓ Test 10 passed")

    print("\n" + "=" * 60)
    print("All GameTracker tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_game_tracker()
