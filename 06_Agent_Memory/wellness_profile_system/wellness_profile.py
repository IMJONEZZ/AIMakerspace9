### YOUR CODE HERE ###

# Step 1: Define a wellness profile schema
# Example attributes: name, age, goals, conditions, allergies, fitness_level, preferred_activities

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class WellnessProfile:
    name: str
    age: int
    goals: List[str]
    conditions: List[str]
    allergies: List[str]
    fitness_level: str


# Step 2: Create helper functions to store and retrieve profiles
def store_wellness_profile(store, user_id: str, profile: dict):
    """Store a user's wellness profile."""
    store[user_id] = profile


def get_wellness_profile(store, user_id: str) -> dict:
    """Retrieve a user's wellness profile."""
    return store.get(user_id, {})


# Step 3: Create two different user profiles
profile_store = {}

user1_profile = {
    "name": "Sarah",
    "age": 32,
    "goals": ["lose weight", "build muscle"],
    "conditions": ["asthma"],
    "allergies": ["nuts", "shellfish"],
    "fitness_level": "beginner",
}

user2_profile = {
    "name": "Mike",
    "age": 45,
    "goals": ["improve cardiovascular health", "reduce stress"],
    "conditions": ["hypertension", "diabetes type 2"],
    "allergies": [],
    "fitness_level": "intermediate",
}

store_wellness_profile(profile_store, "user1", user1_profile)
store_wellness_profile(profile_store, "user2", user2_profile)


# Step 4: Build a personalized agent that uses profiles
class WellnessAgent:
    def __init__(self, profile_store: Dict[str, dict]):
        self.profile_store = profile_store

    def get_personalized_advice(self, user_id: str) -> str:
        profile = get_wellness_profile(self.profile_store, user_id)

        if not profile:
            return "No profile found. Please create a wellness profile first."

        name = profile["name"]
        goals = profile["goals"]
        conditions = profile["conditions"]
        allergies = profile["allergies"]
        fitness_level = profile["fitness_level"]

        advice = []
        advice.append(f"Hello {name}! Based on your profile:")

        goal_advice = {
            "lose weight": f"Since you want to lose weight, focus on a caloric deficit with high protein intake.",
            "build muscle": f"To build muscle at your {fitness_level} level, start with compound movements 3x per week.",
            "improve cardiovascular health": f"For heart health, aim for 150 minutes of moderate aerobic activity weekly.",
            "reduce stress": f"Consider practicing mindfulness, meditation, or yoga to help reduce stress.",
        }

        for goal in goals:
            if goal in goal_advice:
                advice.append(goal_advice[goal])

        condition_advice = {
            "asthma": f"With asthma, always carry your inhaler during exercise and avoid high-pollution areas.",
            "hypertension": f"For hypertension, keep exercises moderate in intensity and avoid lifting heavy weights overhead.",
            "diabetes type 2": f"Managing diabetes: monitor blood sugar before and after exercise, carry quick-acting carbs.",
        }

        for condition in conditions:
            if condition in condition_advice:
                advice.append(condition_advice[condition])

        if allergies:
            advice.append(
                f"Be mindful of your allergies to: {', '.join(allergies)} when planning meals."
            )

        fitness_tips = {
            "beginner": f"As a beginner, start with 20-30 minute sessions and gradually increase duration.",
            "intermediate": f"Being at intermediate level, try progressive overload to continue improving.",
            "advanced": f"At an advanced level, focus on periodization and recovery optimization.",
        }

        advice.append(
            fitness_tips.get(fitness_level, "Keep up with your fitness routine!")
        )

        return "\n".join(advice)


# Step 5: Test with different users - they should get different advice
if __name__ == "__main__":
    agent = WellnessAgent(profile_store)

    print("=" * 60)
    print("Testing with user1 (Sarah):")
    print("=" * 60)
    print(agent.get_personalized_advice("user1"))

    print("\n" + "=" * 60)
    print("Testing with user2 (Mike):")
    print("=" * 60)
    print(agent.get_personalized_advice("user2"))

    print("\n" + "=" * 60)
    print("Testing with non-existent user:")
    print("=" * 60)
    print(agent.get_personalized_advice("user3"))
