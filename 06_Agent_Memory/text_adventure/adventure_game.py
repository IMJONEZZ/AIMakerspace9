import random
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class CharacterStats:
    health: int = 100
    strength: int = 10
    intelligence: int = 10
    charisma: int = 10
    gold: int = 50


@dataclass
class WorldState:
    current_location: str = "village"
    visited_locations: List[str] = None
    met_npcs: List[str] = None
    items_collected: List[str] = None

    def __post_init__(self):
        if self.visited_locations is None:
            self.visited_locations = ["village"]
        if self.met_npcs is None:
            self.met_npcs = []
        if self.items_collected is None:
            self.items_collected = []


@dataclass
class GameState:
    character: CharacterStats
    world: WorldState
    plot_progression: int = 0
    flags: Dict[str, bool] = None

    def __post_init__(self):
        if self.flags is None:
            self.flags = {}


class TextAdventureGame:
    def __init__(self):
        self.state = GameState(character=CharacterStats(), world=WorldState())

    def display_stats(self):
        print("\n" + "=" * 50)
        print(f"Health: {self.state.character.health}")
        print(f"Strength: {self.state.character.strength}")
        print(f"Intelligence: {self.state.character.intelligence}")
        print(f"Charisma: {self.state.character.charisma}")
        print(f"Gold: {self.state.character.gold}")
        print("=" * 50)

    def display_world_state(self):
        print(f"\nLocation: {self.state.world.current_location}")
        print(f"Locations visited: {', '.join(self.state.world.visited_locations)}")
        if self.state.world.items_collected:
            print(f"Items: {', '.join(self.state.world.items_collected)}")
        if self.state.world.met_npcs:
            print(f"People met: {', '.join(self.state.world.met_npcs)}")

    def get_user_choice(self, options: List[str]) -> int:
        while True:
            try:
                choice = input("\nYour choice: ").strip()
                return int(choice)
            except ValueError:
                print("Please enter a valid number.")

    def modify_stat(self, stat: str, amount: int):
        old_value = getattr(self.state.character, stat)
        setattr(self.state.character, stat, max(0, old_value + amount))
        change = "increased" if amount > 0 else "decreased"
        print(f"\n{stat.capitalize()} {change} by {abs(amount)}!")

    def check_game_over(self) -> bool:
        if self.state.character.health <= 0:
            print("\n💀 GAME OVER - You have died!")
            return False
        if self.state.plot_progression >= 100:
            print("\n🎉 VICTORY - You have completed the adventure!")
            return False
        return True

    def scene_village(self):
        print("\n" + "=" * 50)
        print("🏘️ VILLAGE SQUARE")
        print("=" * 50)
        print("You stand in the village square. The morning sun illuminates")
        print("the cobblestone streets. A few villagers go about their business.")

        self.state.world.visited_locations.append("village")

        print("\nWhat do you want to do?")
        print("1. Visit the blacksmith")
        print("2. Talk to the village elder")
        print("3. Head to the forest edge")

        choice = self.get_user_choice([1, 2, 3])

        if choice == 1:
            self.scene_blacksmith()
        elif choice == 2:
            self.scene_village_elder()
        elif choice == 3:
            if "forest" not in self.state.world.visited_locations:
                self.scene_forest_edge()
            else:
                print("\nYou head to the familiar forest edge...")

        return self.check_game_over()

    def scene_blacksmith(self):
        print("\n" + "=" * 50)
        print("🔨 BLACKSMITH")
        print("=" * 50)

        if "blacksmith" not in self.state.world.met_npcs:
            print("A burly man hammers at a glowing piece of metal.")
            self.state.world.met_npcs.append("blacksmith")
        else:
            print("The blacksmith looks up from his work.")

        if self.state.character.gold >= 20:
            print("\n'Want a new sword? It'll cost you 20 gold.'")
            print("1. Buy the sword (20 gold)")
            print("2. Decline and leave")

            choice = self.get_user_choice([1, 2])

            if choice == 1:
                self.state.character.gold -= 20
                self.modify_stat("strength", 5)
                self.state.world.items_collected.append("sword")
                print("\nThe blacksmith hands you a sturdy sword.")
        else:
            print("\n'Come back when you have more gold!'")

    def scene_village_elder(self):
        print("\n" + "=" * 50)
        print("👴 VILLAGE ELDER")
        print("=" * 50)

        if "elder" not in self.state.world.met_npcs:
            print("An old man with wise eyes sits on a stone bench.")
            self.state.world.met_npcs.append("elder")
        else:
            print("The elder smiles at your return.")

        if not self.state.flags.get("elder_quest_given"):
            print("\n'Ah, young one. There is darkness growing in the forest.")
            print("Will you investigate it for me?'")
            print("1. Accept the quest")
            print("2. Ask for more information first")

            choice = self.get_user_choice([1, 2])

            if choice == 1:
                self.state.flags["elder_quest_given"] = True
                self.modify_stat("intelligence", 3)
                print("\n'Thank you! Return to me when you learn more.'")
            elif choice == 2:
                print(
                    "\n'Strange creatures have been seen. Villagers vanish at night.'"
                )
        else:
            print("\n'Any news from the forest?'")

    def scene_forest_edge(self):
        print("\n" + "=" * 50)
        print("🌲 FOREST EDGE")
        print("=" * 50)

        if "forest" not in self.state.world.visited_locations:
            print("The forest looms ahead, dark and mysterious.")
            self.state.world.visited_locations.append("forest")
        else:
            print("The forest edge looks as ominous as before.")

        print("\nWhat do you want to do?")
        print("1. Enter the forest")
        print("2. Search the area")
        print("3. Return to village")

        choice = self.get_user_choice([1, 2, 3])

        if choice == 1:
            self.state.plot_progression = min(100, self.state.plot_progression + 20)
            if "sword" in self.state.world.items_collected:
                print("\nYou venture into the forest, sword at the ready...")
            else:
                damage = random.randint(5, 15)
                self.modify_stat("health", -damage)
                print("\nWithout a weapon, you take damage exploring the forest!")
        elif choice == 3:
            self.state.world.current_location = "village"

        return self.check_game_over()

    def run(self):
        print("\n" + "=" * 50)
        print("⚔️ TEXT ADVENTURE: THE DARK FOREST")
        print("=" * 50)
        print("\nYour journey begins...")

        while True:
            if not self.check_game_over():
                break

            self.display_stats()

            if self.state.world.current_location == "village":
                continue_game = self.scene_village()
            else:
                continue_game = self.scene_forest_edge()

            if not continue_game:
                break

        print("\nThanks for playing!")


if __name__ == "__main__":
    game = TextAdventureGame()
    game.run()
