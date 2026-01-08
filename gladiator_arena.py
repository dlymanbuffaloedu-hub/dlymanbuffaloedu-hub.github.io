import random
from dataclasses import dataclass, field


@dataclass
class Gladiator:
    name: str
    level: int = 1
    power: int = 12
    max_health: int = 90
    gold: int = 0
    wins: int = 0
    losses: int = 0
    xp: int = 0
    xp_to_next: int = 10
    equipment: dict = field(default_factory=dict)

    @property
    def total_power(self) -> int:
        return self.power + sum(item["power"] for item in self.equipment.values())

    @property
    def total_health(self) -> int:
        return self.max_health + sum(item["health"] for item in self.equipment.values())

    @property
    def treasure_collected(self) -> int:
        return self.gold


@dataclass
class Enemy:
    title: str
    tier: int
    power: int
    max_health: int
    bounty: int


@dataclass
class BattleRecord:
    number: int
    opponent: str
    result: str
    bounty: int
    rounds: int


EQUIPMENT_SHOP = {
    "Bronze Sword": {"cost": 30, "power": 3, "health": 0},
    "Iron Shield": {"cost": 45, "power": 1, "health": 12},
    "Gladiator Helm": {"cost": 60, "power": 2, "health": 18},
    "Champion Spear": {"cost": 80, "power": 5, "health": 0},
    "Titan Plate": {"cost": 120, "power": 2, "health": 30},
}

ENEMY_TITLES = [
    "Bronze Spear",
    "Crimson Blade",
    "Sandstorm Duelist",
    "Steel Lotus",
    "Lionheart",
    "Obsidian Guard",
    "Phantom Strike",
]


def random_between(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)


def arena_tier(battle_number: int) -> int:
    return min(6, (battle_number - 1) // 4 + 1)


def build_enemy(battle_number: int) -> Enemy:
    tier = arena_tier(battle_number)
    power = 8 + tier * 3 + battle_number
    max_health = 70 + tier * 18 + battle_number * 4
    bounty = 12 + tier * 8 + battle_number * 3
    title = ENEMY_TITLES[(battle_number - 1) % len(ENEMY_TITLES)]
    return Enemy(title=title, tier=tier, power=power, max_health=max_health, bounty=bounty)


def display_scoreboard(gladiator: Gladiator, records: list[BattleRecord]) -> None:
    print("\n=== SCOREBOARD ===")
    print(f"Gladiator: {gladiator.name}")
    print(f"Level {gladiator.level} | Wins {gladiator.wins} | Losses {gladiator.losses}")
    print(f"Power {gladiator.total_power} | Max Health {gladiator.total_health}")
    print(f"Treasure Collected: {gladiator.treasure_collected} gold")
    print("\nRecent Battles:")
    if not records:
        print("  No battles yet. Head to the arena!")
        return
    for record in records[-5:][::-1]:
        print(
            f"  #{record.number} vs {record.opponent} - {record.result} "
            f"(+{record.bounty} gold, {record.rounds} rounds)"
        )


def show_shop(gladiator: Gladiator) -> None:
    print("\n=== GLADIATOR ARMORY ===")
    print(f"Gold: {gladiator.gold}")
    for idx, (name, stats) in enumerate(EQUIPMENT_SHOP.items(), start=1):
        owned = "(owned)" if name in gladiator.equipment else ""
        print(
            f"{idx}. {name} - Cost {stats['cost']} | "
            f"Power +{stats['power']} | Health +{stats['health']} {owned}"
        )
    print("0. Return to arena")

    choice = input("Choose equipment to buy: ").strip()
    if choice == "0":
        return
    if not choice.isdigit() or int(choice) not in range(1, len(EQUIPMENT_SHOP) + 1):
        print("Invalid choice. Returning to arena.")
        return

    selected_name = list(EQUIPMENT_SHOP.keys())[int(choice) - 1]
    if selected_name in gladiator.equipment:
        print("You already own this equipment.")
        return

    item = EQUIPMENT_SHOP[selected_name]
    if gladiator.gold < item["cost"]:
        print("Not enough gold. Win more battles to afford this item.")
        return

    gladiator.gold -= item["cost"]
    gladiator.equipment[selected_name] = item
    print(f"Purchased {selected_name}! Your stats improved for the next fight.")


def resolve_battle(gladiator: Gladiator, enemy: Enemy) -> tuple[bool, int, int]:
    glad_health = gladiator.total_health
    enemy_health = enemy.max_health
    rounds = 0

    while glad_health > 0 and enemy_health > 0 and rounds < 6:
        rounds += 1
        glad_strike = random_between(gladiator.total_power - 2, gladiator.total_power + 4)
        enemy_strike = random_between(enemy.power - 3, enemy.power + 3)
        enemy_health -= glad_strike
        glad_health -= enemy_strike

    win = glad_health > enemy_health
    gold_earned = max(0, enemy.bounty + gladiator.wins * 2)
    return win, gold_earned, rounds


def apply_battle_results(
    gladiator: Gladiator,
    enemy: Enemy,
    win: bool,
    gold_earned: int,
    battle_number: int,
    rounds: int,
) -> BattleRecord:
    if win:
        gladiator.wins += 1
        gladiator.gold += gold_earned
        gladiator.xp += 6 + enemy.tier * 2
        while gladiator.xp >= gladiator.xp_to_next:
            gladiator.xp -= gladiator.xp_to_next
            gladiator.level += 1
            gladiator.xp_to_next = int(gladiator.xp_to_next * 1.25 + 6)
            gladiator.power += 2 + gladiator.level // 2
            gladiator.max_health += 10 + gladiator.level * 2
    else:
        gladiator.losses += 1
        gladiator.wins = 0
        gladiator.gold = max(0, gladiator.gold - enemy.bounty // 2)

    return BattleRecord(
        number=battle_number,
        opponent=enemy.title,
        result="Victory" if win else "Defeat",
        bounty=gold_earned if win else 0,
        rounds=rounds,
    )


def display_stats(gladiator: Gladiator, enemy: Enemy) -> None:
    print("\n=== ARENA MATCHUP ===")
    print(f"Enemy: {enemy.title} (Tier {enemy.tier})")
    print(f"Enemy Power: {enemy.power} | Enemy Health: {enemy.max_health}")
    print("\nYour Gladiator")
    print(f"Name: {gladiator.name} | Level: {gladiator.level}")
    print(f"Power: {gladiator.total_power} | Health: {gladiator.total_health}")
    print(f"Gold: {gladiator.gold} | Win Streak: {gladiator.wins}")


def arena_loop() -> None:
    gladiator = Gladiator(name="Valeria the Bold")
    records: list[BattleRecord] = []
    battle_number = 1

    print("Welcome to the Gladiator Arena!")

    while True:
        enemy = build_enemy(battle_number)
        display_stats(gladiator, enemy)
        print("\nChoose an action:")
        print("1. Fight the next battle")
        print("2. Visit the armory")
        print("3. View scoreboard")
        print("4. Rest (+5 gold, reset streak)")
        print("5. Retire")

        choice = input("Selection: ").strip()

        if choice == "1":
            win, gold_earned, rounds = resolve_battle(gladiator, enemy)
            record = apply_battle_results(
                gladiator, enemy, win, gold_earned, battle_number, rounds
            )
            records.append(record)
            outcome = "Victory!" if win else "Defeat..."
            print(
                f"\n{outcome} {enemy.title} battle completed in {rounds} rounds. "
                f"Gold earned: {record.bounty}."
            )
            battle_number += 1
        elif choice == "2":
            show_shop(gladiator)
        elif choice == "3":
            display_scoreboard(gladiator, records)
        elif choice == "4":
            gladiator.wins = 0
            gladiator.gold += 5
            print("You rest between battles, regain focus, and collect 5 gold tribute.")
        elif choice == "5":
            print("You retire from the arena. Your legend lives on!")
            break
        else:
            print("Invalid option. Choose a number from the menu.")


if __name__ == "__main__":
    arena_loop()
