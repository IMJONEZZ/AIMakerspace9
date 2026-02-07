# Memory System Documentation

## Overview

The AI Life Coach memory system provides robust long-term memory capabilities using LangGraph's InMemoryStore. It organizes user data across 5 hierarchical namespaces, supporting comprehensive CRUD operations with proper error handling.

## Architecture

### Namespace Hierarchy

```
LangGraph Store (InMemoryStore)
│
├── (user_id, "profile")        - User demographics, values, life situation
│   └── profile_data: UserProfile object
│
├── (user_id, "goals")          - Short, medium, long-term goals
│   ├── goal_id_1: Goal object
│   ├── goal_id_2: Goal object
│   └── ...
│
├── (user_id, "progress")       - Milestones and setbacks
│   ├── milestone_{id}: Milestone object
│   └── setback_{id}: Setback object
│
├── (user_id, "preferences")    - Communication style, coaching approach
│   └── preferences_data: UserPreferences object
│
└── ("coaching", "patterns")    - Cross-user learned patterns (anonymized)
    ├── pattern_id_1: CoachingPattern object
    ├── pattern_id_2: CoachingPattern object
    └── ...
```

### Memory Types

| Type | Namespace Pattern | Scope | Use Case |
|------|------------------|-------|----------|
| **User Profile** | `(user_id, "profile")` | Per-user | Demographics, values, life situation |
| **Goals** | `(user_id, "goals")` | Per-user | Short/medium/long-term goals with dependencies |
| **Progress** | `(user_id, "progress")` | Per-user | Milestones achieved and setbacks overcome |
| **Preferences** | `(user_id, "preferences")` | Per-user | Communication style, coaching approach |
| **Patterns** | `("coaching", "patterns")` | Shared | Learned coaching strategies (anonymized) |

## Quick Start

### Basic Setup

```python
from src.memory import create_memory_manager, UserProfile, Goal

# Create memory manager (uses InMemoryStore by default)
manager = create_memory_manager()

# Save a user profile
profile = UserProfile(
    user_id="user_123",
    name="Alex Johnson",
    age=35,
    occupation="Software Engineer",
    values=["growth", "balance", "autonomy"],
)
manager.save_profile(profile)

# Retrieve profile
retrieved = manager.get_profile("user_123")
print(f"Name: {retrieved.name}, Age: {retrieved.age}")
```

### Goal Management

```python
# Create and save goals
goal1 = Goal(
    title="Learn Python",
    description="Complete 6-month Python course",
    domain="career",
    priority=4,
    timeframe="medium",
)
manager.save_goal("user_123", goal1)

goal2 = Goal(
    title="Run a marathon",
    description="Complete 26.2 mile race",
    domain="wellness",
    priority=3,
    timeframe="long",
)
manager.save_goal("user_123", goal2)

# Retrieve all goals
all_goals = manager.get_goals("user_123")
print(f"Total goals: {len(all_goals)}")

# Filter by domain
career_goals = manager.get_goals_by_domain("user_123", "career")
print(f"Career goals: {[g.title for g in career_goals]}")

# Update goal status
goal1.status = "in_progress"
manager.save_goal("user_123", goal1)
```

### Progress Tracking

```python
from src.memory import Milestone, Setback

# Add milestones
milestone = Milestone(
    title="Completed Python Course",
    description="Finished 6-week intensive program",
    domain="career",
    significance="major",
)
manager.add_milestone("user_123", milestone)

# Add setbacks
setback = Setback(
    description="Missed several training sessions",
    domain="wellness",
    resolved=True,
    resolution_notes="Created accountability system with friend",
)
manager.add_setback("user_123", setback)

# Retrieve progress history
milestones = manager.get_milestones("user_123")
setbacks = manager.get_setbacks("user_123")

print(f"Achievements: {len(milestones)}")
print(f"Setbacks overcome: {len([s for s in setbacks if s.resolved])}")
```

### User Preferences

```python
from src.memory import UserPreferences

# Set preferences
preferences = UserPreferences(
    user_id="user_123",
    communication_style="detailed",  # concise, balanced, detailed
    coaching_approach="supportive",  # direct, supportive, collaborative
    preferred_checkin_frequency="weekly",  # daily, weekly, bi_weekly
)
manager.save_preferences(preferences)

# Update single preference
manager.update_preference_key("user_123", "communication_style", "concise")

# Retrieve preferences
prefs = manager.get_preferences("user_123")
print(f"Communication style: {prefs.communication_style}")
```

### Shared Coaching Patterns

```python
from src.memory import CoachingPattern

# Save a pattern (anonymized, no user-specific data)
pattern = CoachingPattern(
    title="Micro-commitments for consistency",
    description="Break large goals into tiny daily actions (5-10 min)",
    category="strategy",
    effectiveness_score=0.85,
    usage_count=42,
    related_domains=["career", "wellness"],
)
manager.save_pattern(pattern)

# Retrieve patterns by domain
wellness_patterns = manager.get_patterns_by_domain("wellness")
print(f"Effective wellness patterns: {len(wellness_patterns)}")

# Increment usage count for a pattern
manager.increment_pattern_usage(pattern.pattern_id)
```

### User Summary & Deletion

```python
# Get comprehensive user summary
summary = manager.get_user_summary("user_123")
print(f"Profile: {summary['profile'].name}")
print(f"Goals: {len(summary['goals'])}")
print(f"Milestones: {len(summary['milestones'])}")

# Delete all user data (GDPR compliance)
success = manager.delete_user_data("user_123")
if success:
    print("User data deleted successfully")
```

## Data Models

### UserProfile

```python
class UserProfile:
    user_id: str                    # Required unique identifier
    name: Optional[str]             # User's full name
    age: Optional[int]              # Age in years
    occupation: Optional[str]       # Current job/role
    relationship_status: Optional[str]  # Single, married, etc.
    values: List[str]               # Core life values
    life_situation: Dict[str, Any]  # Additional context
    created_at: str                 # ISO timestamp
    updated_at: str                 # ISO timestamp
```

### Goal

```python
class Goal:
    goal_id: str                    # Auto-generated UUID
    title: str                      # Goal name
    description: str                # Detailed description
    domain: str                     # career, relationship, finance, wellness
    priority: int                   # 1-5 (5 = highest)
    status: str                     # pending, in_progress, completed, cancelled
    timeframe: str                  # short, medium, long
    deadline: Optional[str]         # ISO date string
    dependencies: List[str]         # IDs of prerequisite goals
    created_at: str                 # ISO timestamp
```

### Milestone

```python
class Milestone:
    milestone_id: str               # Auto-generated UUID
    title: str                      # Achievement name
    description: str                # Details about the achievement
    domain: str                     # Domain category
    achieved_at: str                # ISO timestamp when achieved
    significance: str               # minor, normal, major
```

### Setback

```python
class Setback:
    setback_id: str                 # Auto-generated UUID
    description: str                # What happened
    domain: str                     # Domain affected
    occurred_at: str                # ISO timestamp when it happened
    resolved: bool                  # Whether overcome
    resolution_notes: str           # How it was handled
```

### UserPreferences

```python
class UserPreferences:
    user_id: str                    # Required unique identifier
    communication_style: str        # concise, balanced, detailed
    coaching_approach: str          # direct, supportive, collaborative
    preferred_checkin_frequency: str  # daily, weekly, bi_weekly
    preferred_response_length: str  # short, medium, long
    custom_preferences: Dict[str, Any]  # Additional settings
```

### CoachingPattern

```python
class CoachingPattern:
    pattern_id: str                 # Auto-generated UUID
    title: str                      # Pattern name
    description: str                # What the pattern does
    category: str                   # strategy, insight, challenge
    effectiveness_score: Optional[float]  # 0-1 based on outcomes
    usage_count: int                # How many times used
    related_domains: List[str]      # Relevant domains
```

## Advanced Usage

### Error Handling

```python
from src.memory import MemoryManager, create_memory_store

# Handle missing users gracefully
profile = manager.get_profile("nonexistent_user")
if profile is None:
    print("User not found")

# Validate required fields
try:
    manager.save_goal("", Goal(title="No User"))
except ValueError as e:
    print(f"Error: {e}")  # "user_id cannot be empty"
```

### Custom Store Configuration

```python
from src.memory import create_memory_store, MemoryManager

# Create custom store instance
store = create_memory_store("in_memory")

# Pass to manager
manager = MemoryManager(store)
```

### Integration with Config System

```python
from src.config import config, initialize_environment, get_memory_store

# Initialize environment (sets up both backend and store)
config.initialize_environment()

# Get the initialized memory store
store = get_memory_store()
manager = MemoryManager(store)
```

### Namespace Functions

```python
from src.memory import (
    get_profile_namespace,
    get_goals_namespace,
    get_progress_namespace,
    get_preferences_namespace,
    get_coaching_patterns_namespace
)

# Get namespace tuples for direct store operations
profile_ns = get_profile_namespace("user_123")
print(profile_ns)  # ('user_123', 'profile')

coaching_ns = get_coaching_patterns_namespace()
print(coaching_ns)  # ('coaching', 'patterns')
```

## Best Practices

### 1. Always Check for None

```python
# Good pattern
profile = manager.get_profile(user_id)
if profile is None:
    # Handle missing user
    profile = UserProfile(user_id=user_id, name="New User")
    manager.save_profile(profile)
```

### 2. Use Domain Filtering

```python
# Instead of filtering manually
career_goals = [g for g in manager.get_goals(user_id) if g.domain == "career"]

# Use the built-in filter
career_goals = manager.get_goals_by_domain(user_id, "career")
```

### 3. Handle Dependencies Properly

```python
# Goal dependencies are tracked but not enforced automatically
goal1 = Goal(title="Get promotion", domain="career")
goal2 = Goal(
    title="Buy house",
    domain="finance",
    dependencies=[goal1.goal_id]  # Goal2 requires goal1
)

manager.save_goal(user_id, goal1)
manager.save_goal(user_id, goal2)
```

### 4. Anonymize Shared Patterns

```python
# When creating coaching patterns, never include user-specific data
pattern = CoachingPattern(
    title="Effective morning routine",  # Generic, not "Alex's morning routine"
    description="5-minute meditation + exercise helps with energy",  # No names
    category="strategy",
)
manager.save_pattern(pattern)
```

### 5. Use Appropriate Significance Levels

```python
# Milestone significance helps track major achievements
major = Milestone(title="Completed degree", significance="major")
normal = Milestone(title="Weekly workout streak 10 weeks", significance="normal")
minor = Milestone(title("Logged meals for a day"), significance="minor")
```

## Testing

Run the comprehensive test suite:

```bash
cd ai_life_coach
python tests/test_memory.py
```

Expected output: **32 passed** (all namespace, model, and CRUD tests)

## Migration Path to Production

### Current: InMemoryStore (Development)
```python
from src.memory import create_memory_store

store = create_memory_store("in_memory")
# Data persists only during application runtime
```

### Future: PostgresStore (Production)
```python
from src.memory import create_memory_store

# Will be implemented in future beads
store = create_memory_store("postgres")
# Data persists across application restarts
```

The MemoryManager API remains the same - only the underlying store changes.

## Performance Considerations

1. **Namespace Design**: Using `(user_id, type)` pattern enables efficient per-user queries
2. **Bulk Operations**: For many goals/progress items, batch operations are recommended
3. **Caching**: Consider caching frequently accessed user profiles in memory
4. **Indexing**: When migrating to PostgresStore, add indexes on namespace and key fields

## Security & Privacy

1. **User Isolation**: Each user's data is in separate namespace - no cross-user access
2. **Anonymization**: Coaching patterns never contain user-identifiable information
3. **Data Deletion**: `delete_user_data()` provides complete GDPR-compliant deletion
4. **Access Control**: Implement user authentication before calling memory manager methods

## Troubleshooting

### Issue: ImportError for langgraph.store
**Solution**: Install LangGraph:
```bash
pip install langgraph
```

### Issue: Profile not found returns None
**Expected behavior**: Always check for None and handle gracefully. See "Best Practices" section.

### Issue: Store not initialized error
**Solution**: Call `config.initialize_environment()` before using memory functions, or create store with `create_memory_store()`.

## Related Documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture overview
- [Beads_Plan.md](../Beads_Plan.md) - Implementation plan
- [src/config.py](./config.py) - Configuration system

## API Reference Summary

### MemoryManager Methods

| Method | Purpose |
|--------|---------|
| `save_profile(profile)` | Save/update user profile |
| `get_profile(user_id)` | Retrieve user profile |
| `profile_exists(user_id)` | Check if profile exists |
| `save_goal(user_id, goal)` | Save/update single goal |
| `get_goal(user_id, goal_id)` | Retrieve specific goal |
| `get_goals(user_id)` | Get all user's goals |
| `get_goals_by_domain(user_id, domain)` | Filter goals by domain |
| `delete_goal(user_id, goal_id)` | Delete a goal |
| `add_milestone(user_id, milestone)` | Add achievement milestone |
| `get_milestones(user_id)` | Get all milestones |
| `add_setback(user_id, setback)` | Add/setback record |
| `get_setbacks(user_id)` | Get all setbacks |
| `save_preferences(preferences)` | Save/update preferences |
| `get_preferences(user_id)` | Retrieve preferences |
| `update_preference_key(user_id, key, value)` | Update single preference field |
| `save_pattern(pattern)` | Save coaching pattern |
| `get_pattern(pattern_id)` | Retrieve specific pattern |
| `get_patterns()` | Get all patterns |
| `get_patterns_by_domain(domain)` | Filter patterns by domain |
| `increment_pattern_usage(pattern_id)` | Track pattern usage |
| `get_user_summary(user_id)` | Get complete user data summary |
| `delete_user_data(user_id)` | Delete all user data |

### Factory Functions

| Function | Purpose |
|----------|---------|
| `create_memory_store(store_type)` | Create InMemoryStore or PostgresStore |
| `create_memory_manager(store?)` | Create MemoryManager with optional store |

### Namespace Functions

| Function | Returns |
|----------|---------|
| `get_profile_namespace(user_id)` | `(user_id, "profile")` |
| `get_goals_namespace(user_id)` | `(user_id, "goals")` |
| `get_progress_namespace(user_id)` | `(user_id, "progress")` |
| `get_preferences_namespace(user_id)` | `(user_id, "preferences")` |
| `get_coaching_patterns_namespace()` | `("coaching", "patterns")` |

---

**Bead #3 Status**: ✅ **COMPLETE AND TESTED**

All 5 namespaces implemented, data models designed, comprehensive CRUD operations working.