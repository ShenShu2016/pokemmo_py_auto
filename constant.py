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
    23: "Battle End Pokemon Caught Status",
    20: "Battle Loading Status",
}
enemy_hp_positions = {
    2: [(329, 97), (346, 110)],
    3: [(589, 97), (606, 110)],
    4: [(849, 97), (866, 110)],
    5: [(329, 137), (345, 150)],
    6: [(849, 137), (865, 150)],
}


def get_enemy_hp_bar_position():
    for i, pos in enemy_hp_positions.items():
        top_left = (pos[0][0] + 20, pos[0][1] + 4)
        bottom_right = (pos[1][0] + 203, pos[1][1] - 5)
        enemy_hp_bar_positions[i] = [top_left, bottom_right]


enemy_hp_bar_positions = {}

enemy_hp_bar_positions = get_enemy_hp_bar_position()


city_info = {
    "SOOTOPOLIS_CITY": {
        "map_number": (1, 7, 50),
        "112": (43, 32, 1),
        "112_map_number": (1, 2, 65),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(6, 8, 0), (7, 8, 0)],
    },
    "FALLARBOR_TOWN": {
        "map_number": (1, 13, 50),
        "112": (14, 8, 1),
        "112_map_number": (1, 4, 55),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(6, 8, 0), (7, 8, 0)],
    },
}
