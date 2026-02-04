"""
QDrant Knowledge Base Schema Design for Spoiler-Free Video Game Agent System

This document defines the schema and metadata structure for storing game content
in QDrant, optimized for spoiler-free querying and efficient filtering.
"""

# ============================================================================
# COLLECTION STRUCTURE
# ============================================================================

"""
Collection Name: "game_knowledge_base"

Description: Stores all game-related content including walkthroughs, lore,
spoilers, gameplay mechanics, controls, and tips. All content is embedded
for semantic search while maintaining strict metadata for spoiler filtering.

Vector Configuration:
- Vector size: 1536 (matches text-embedding-nomic-embed-text-v2-moe)
- Distance metric: Cosine
"""

# ============================================================================
# PAYLOAD SCHEMA (Metadata Structure)
# ============================================================================

"""
Each document in QDrant will have the following payload structure:

{
    # Core content fields
    "text": str,                    # Main text content (chunked game information)
    
    # Game identification
    "game_name": str,                # Normalized game name (e.g., "elden_ring", "minecraft")
                                    # Use lowercase with underscores for consistency
    "game_display_name": str,       # Display name (e.g., "Elden Ring", "Minecraft")
    
    # Content classification
    "content_type": str,            # Type of content - see CONTENT_TYPES enum
    "is_spoiler": bool,             # Explicit spoiler flag (True/False)
    
    # Progress tracking for spoiler control
    "progress_marker": str,         # Broad progress stage - see PROGRESS_MARKERS enum
    "chapter": Optional[int],       # Optional chapter number (for games with chapters)
    "section_name": Optional[str],  # Optional section/area name (e.g., "Leyndell", "Limgrave")
    
    # Source information
    "source_url": str,              # URL where content was fetched from
    "source_type": str,             # How source was obtained (e.g., "searxng", "manual")
    
    # Metadata
    "timestamp": str,               # ISO 8601 timestamp (e.g., "2026-02-02T13:00:00Z")
    "chunk_id": str,                # Unique chunk identifier (e.g., "elden_ring_walkthrough_001")
    "parent_document_id": str,     # ID of the source document this chunk belongs to
    
    # Quality/Relevance scores (optional)
    "quality_score": Optional[float],  # Relevance/quality score (0.0-1.0)
    "confidence": Optional[float],     # Confidence in spoiler classification (0.0-1.0)
}
"""

# ============================================================================
# ENUMERATIONS / VALID VALUES
# ============================================================================

CONTENT_TYPES = [
    "walkthrough",           # Step-by-step game completion guides
    "lore",                  # Story, world-building, character backgrounds
    "spoiler",               # Explicit story spoilers (plot points, endings)
    "gameplay_mechanics",   # Game systems, mechanics (can be spoiler territory!)
    "controls",              # Controls and input methods (can be spoiler territory!)
    "tips",                  # General tips and tricks
]

"""
IMPORTANT: All content types can potentially contain spoilers!

Examples of spoilers in unexpected categories:
- gameplay_mechanics: "To unlock the Dark Blade, you must first defeat Malenia"
- controls: "After chapter 5, you gain access to flight using the X button"
- tips: "Use this strategy for the final boss fight"

Therefore, is_spoiler flag must be carefully set based on content analysis.
"""

PROGRESS_MARKERS = [
    "intro/tutorial",        # Tutorial area, beginning of game
    "early_game",           # First few hours/chapters
    "mid_game",             # Mid-game content, around 30-60% through
    "late_game",            # Late game content, approaching finale
    "endgame",              # Final boss, ending sequence
    "post_game",            # Post-game content, New Game+, secrets
    "general",              # Content applicable throughout the game
]

"""
Progress markers are deliberately broad to err on NOT knowing rather than revealing too much.

For example:
- "early_game": Contains content from the first 30% of the game
- "mid_game": Content from 30-70% of the game
- "late_game": Content from 70-95% of the game

If progress is unknown or ambiguous, default to "early_game" to be safe.
"""

# ============================================================================
# NAMESPACE STRUCTURE FOR ORGANIZATION
# ============================================================================

"""
While QDrant uses collections rather than namespaces, we can organize data using:

1. Primary Collection: "game_knowledge_base"
   - All game content lives here
   - Filtered by metadata (game_name, content_type, is_spoiler, progress_marker)

2. Tracking Collection: "game_tracking"
   - Tracks which games have been processed
   - Prevents redundant web fetching
   
   Schema:
   {
       "game_name": str,              # Normalized game name
       "processed_at": str,          # ISO timestamp of processing
       "chunk_count": int,           # Number of chunks stored
       "source_urls": list[str],     # List of URLs fetched from
       "last_updated": str,          # ISO timestamp of last update
   }

3. User Progress Collection: "user_game_progress"
   - Tracks each user's progress for specific games
   - Enables personalized spoiler filtering
   
   Schema:
   {
       "user_id": str,               # Unique user identifier
       "game_name": str,             # Normalized game name
       "progress_marker": str,       # Current progress (from PROGRESS_MARKERS)
       "last_updated": str,          # ISO timestamp of last update
   }
"""

# ============================================================================
# FILTERING STRATEGIES
# ============================================================================

"""
Query 1: Spoiler-free search for a specific game
-----------------------------------------------
Filter conditions:
- Must match: game_name = target_game
- Must not have: is_spoiler = True
- Progress filtering: progress_marker <= user_progress_marker

QDrant filter:
{
    "must": [
        {"key": "game_name", "match": {"value": target_game}}
    ],
    "must_not": [
        {"key": "is_spoiler", "match": {"value": True}}
    ],
    # Progress marker filtering handled in application layer (not QDrant filter)
}

Query 2: Get all spoilers for a specific game
---------------------------------------------
Filter conditions:
- Must match: game_name = target_game
- Must have: is_spoiler = True

QDrant filter:
{
    "must": [
        {"key": "game_name", "match": {"value": target_game}},
        {"key": "is_spoiler", "match": {"value": True}}
    ]
}

Query 3: Get specific content type for a game
----------------------------------------------
Filter conditions:
- Must match: game_name = target_game
- Must match: content_type = specific_type

QDrant filter:
{
    "must": [
        {"key": "game_name", "match": {"value": target_game}},
        {"key": "content_type", "match": {"value": specific_type}}
    ]
}

Query 4: Get content up to a certain progress point
--------------------------------------------------
Filter conditions:
- Must match: game_name = target_game
- Progress filtering: progress_marker in ['intro/tutorial', 'early_game']

Note: Progress marker ordering is handled in application layer:
Ordering: intro/tutorial < early_game < mid_game < late_game < endgame < post_game
"""

# ============================================================================
# EMBEDDING STRATEGY
# ============================================================================

"""
Embedding Model: text-embedding-nomic-embed-text-v2-moe
- Dimension: 1536
- Base URL: http://192.168.1.79:8080/v1

Chunking Strategy:
- Chunk size: 500 tokens
- Chunk overlap: 100 tokens
- Use RecursiveCharacterTextSplitter

Each chunk's "text" field is embedded for semantic search.
"""

# ============================================================================
# EXAMPLE DOCUMENTS
# ============================================================================

EXAMPLE_WALKTHROUGH_EARLY_GAME = {
    "text": "To defeat the first boss in Elden Ring, head to Stormveil Castle. "
            "The Grafted Knight guards the entrance and can be challenging for newcomers.",
    "game_name": "elden_ring",
    "game_display_name": "Elden Ring",
    "content_type": "walkthrough",
    "is_spoiler": False,
    "progress_marker": "early_game",
    "chapter": 1,
    "section_name": "Stormveil Castle",
    "source_url": "https://example.com/elden-ring-walkthrough",
    "source_type": "searxng",
    "timestamp": "2026-02-02T13:00:00Z",
    "chunk_id": "elden_ring_walkthrough_001",
    "parent_document_id": "walkthrough_20240202",
}

EXAMPLE_SPOILER_ENDGAME = {
    "text": "In the final battle against Lord Mohg, use the Bloodhound's Fang "
            "and dodge his blood flame attacks. After defeating him, you unlock "
            "the path to Erdtree.",
    "game_name": "elden_ring",
    "game_display_name": "Elden Ring",
    "content_type": "spoiler",
    "is_spoiler": True,
    "progress_marker": "endgame",
    "source_url": "https://example.com/elden-ring-spoilers",
    "source_type": "searxng",
    "timestamp": "2026-02-02T13:00:00Z",
    "chunk_id": "elden_ring_spoiler_042",
    "parent_document_id": "spoilers_20240202",
}

EXAMPLE_GAMEPLAY_MECHANICS_MID_GAME = {
    "text": "In God of War Ragnarök, you unlock the Draupnir Spear after "
            "completing the main quest in Vanaheim. This weapon allows you to "
            "create magical spears that can be detonated for area damage.",
    "game_name": "god_of_war_ragnarok",
    "game_display_name": "God of War Ragnarök",
    "content_type": "gameplay_mechanics",
    "is_spoiler": True,  # This reveals a mid-game unlock!
    "progress_marker": "mid_game",
    "source_url": "https://example.com/gow-ragnarok-mechanics",
    "source_type": "searxng",
    "timestamp": "2026-02-02T13:00:00Z",
    "chunk_id": "gow_ragnarok_mechanics_015",
    "parent_document_id": "mechanics_20240202",
}

# ============================================================================
# IMPLEMENTATION CHECKLIST
# ============================================================================

"""
[ ] Create QDrant client initialization with collection setup
[ ] Implement collection creation with proper vector configuration
[ ] Create document insertion function with metadata validation
[ ] Implement search functions with filtering:
    [ ] Spoiler-free search by game and user progress
    [ ] Get all spoilers for a game
    [ ] Search by content type
[ ] Create progress marker ordering utility function
[ ] Implement game tracking collection (prevent re-fetching)
[ ] Create user progress tracking functions
[ ] Add document update/delete operations
[ ] Implement batch insertion for efficiency

"""

# ============================================================================
# FILES TO CREATE
# ============================================================================

"""
1. src/game_knowledge_base.py
   - Main QDrant knowledge base implementation
   - Search functions with spoiler filtering
   - Document management operations

2. src/game_tracker.py
   - Game tracking system (prevent re-fetching)
   - Processed games metadata

3. src/user_progress.py
   - User progress tracking
   - Progress marker management

4. tests/test_game_knowledge_base.py
   - Unit tests for QDrant operations
   - Spoiler filtering validation

"""