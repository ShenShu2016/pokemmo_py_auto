def calculate_catch_rate(
    max_hp=30, current_hp=1, catch_rate=255, ball_rate=1, pokemon_condition=1
):
    numerator = (
        (3 * max_hp - 2 * current_hp) * catch_rate * ball_rate * pokemon_condition
    )
    denominator = 3 * max_hp * 255
    final_catch_rate = numerator / denominator
    return final_catch_rate


# Tuple format: (ball_name, rate, price, condition)
balls = [
    ("diveball", 2.5, 960, "water"),
    ("pokeball", 1, 200, None),
    ("healball", 1, 340, None),
    ("greatball", 1.5, 600, None),
    ("luxuryball", 1, 610, None),
    ("premierball", 1.5, 780, None),
    ("nestball", 4, 1300, "lv lower than 30"),
    ("timerball", 4, 1300, "more than 10 rounds"),
    ("ultraball", 2, 1200, None),
    ("quickball", 5, 1350, "first round"),
    ("duskball", 2.5, 1450, "in cave or night"),
    ("netball", 2.5, 1670, "bug or water"),
]

# Example usage
catch_rate = 255
ball_rate = 1

for ball in balls:
    ball_name, rate, price, condition = ball
    final_catch_rate = calculate_catch_rate(catch_rate, ball_rate)
    print(f"Ball: {ball_name}")
    print(f"Final Catch Rate: {final_catch_rate}")
    print(f"Price: {price}")
    print(f"Condition: {condition}")
    print()
