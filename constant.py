target_words_dict = {
    "battle_option_ORC": [
        # "FIGHT",
        "Select your attack move",
        # "BAG",
        # "Use an Item",
        # "Pokémon",
        # "Switch current Pokémon",
        # "Run",
        # "Escape from battle",
    ],
    "my_name_ORC": ["[JNTM]Hodson"],
    "battle_option_go_back_ORC": ["GO BACK"],
}


game_status_dict = {
    0: "Unknown Game Status",
    404: "Not Active Game Status",
    1: "Normal Game Status",
    21: "Battle Option Status",
    22: "Battle Go Back Status",
    20: "Battle Loading Status",
}
enemy_hp_positions = {
    2: [(329, 97), (346, 110)],
    3: [(589, 97), (606, 110)],
    4: [(849, 97), (866, 110)],
    5: [(329, 137), (345, 150)],
    6: [(849, 137), (865, 150)],
}

enemy_hp_bar_positions = {}

for i, pos in enemy_hp_positions.items():
    top_left = (pos[0][0] + 20, pos[0][1] + 4)
    bottom_right = (pos[1][0] + 203, pos[1][1] - 5)
    enemy_hp_bar_positions[i] = [top_left, bottom_right]

print(enemy_hp_bar_positions)
