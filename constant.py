target_words_dict = {
    "battle_option_OCR": [
        # "FIGHT",
        "Select your attack move",
        # "BAG",
        # "Use an Item",
        # "Pokémon",
        # "Switch current Pokémon",
        # "Run",
        # "Escape from battle",
    ],
    "my_name_OCR": ["[JNTM]Hodson"],
    "battle_option_go_back_OCR": ["GO BACK"],
}


game_status_dict = {
    0: "Unknown Game Status",
    404: "Not Active Game Status",
    1: "普通状态",
    21: "战斗选项",
    22: "Battle Go Back Status",
    23: "Battle End Pokemon Caught Status",
    20: "战斗进行中",
}
enemy_hp_positions = {
    2: [(329, 97), (346, 110)],
    3: [(589, 97), (606, 110)],
    4: [(849, 97), (866, 110)],
    5: [(329, 137), (345, 150)],
    6: [(849, 137), (865, 150)],
}


city_info = {
    "SOOTOPOLIS_CITY": {
        "town_map_coords": (836, 414),
        "map_number": (1, 7, 50),
        "112": (43, 32, 1),
        "112_map_number": (1, 2, 65),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(7, 8, 0), (6, 8, 0)],  # 把正对着护士的放在第一个
        "coords_tracking_ready": True,
        "area": "Hoenn",
        "pc_type": "Hoenn_PC",
    },
    "FALLARBOR_TOWN": {
        "town_map_coords": (403, 241),
        "map_number": (1, 13, 50),
        "112": (14, 8, 1),
        "112_map_number": (1, 4, 55),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(7, 8, 0), (6, 8, 0)],
        "coords_tracking_ready": False,
        "area": "Hoenn",
        "pc_type": "Hoenn_PC",
    },
    "PETALBURG_CITY": {
        "town_map_coords": (357, 457),
        "map_number": (1, 0, 50),
        "112": (20, 17, 1),
        "112_map_number": (1, 4, 58),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(7, 8, 0), (6, 8, 0)],
        "area": "Hoenn",
        "pc_type": "Hoenn_PC",
    },
    "BATTLE_FRONTIER": {
        "town_map_coords": (860, 530),
        "map_number": (1, 14, 76),
        "112": (3, 52, 1),
        "112_map_number": (1, 53, 76),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(7, 8, 0), (6, 8, 0)],
        "area": "Hoenn",
        "pc_type": "Hoenn_PC",
    },
    "VERDANTURF_TOWN": {
        "town_map_coords": (424, 383),
        "map_number": (1, 14, 50),
        "112": (16, 4, 1),
        "112_map_number": (1, 4, 56),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(7, 8, 0), (6, 8, 0)],
        "area": "Hoenn",
        "pc_type": "Hoenn_PC",
    },
    "Undella_Town": {
        "town_map_coords": (938, 377),
        "map_number": (2, 2, 156),
        "112": (760, 300, 1),
        "112_map_number": (2, 1, 157),
        "112_nurse": (7, 12, 1),  # x,y,dir
        "112_out": [(7, 19, 0), (6, 19, 0), (8, 19, 0)],
        "area": "Unova",
        "pc_type": "Unova_PC",
    },
    "Icirrus_City": {
        "town_map_coords": (489, 303),
        "map_number": (2, 0, 113),
        "112": (184, 196, 1),
        "112_map_number": (2, 0, 115),
        "112_out": [(7, 19, 0), (6, 19, 0), (8, 19, 0)],
        "112_nurse": (7, 12, 1),  # x,y,dir
        "area": "Unova",
        "pc_type": "Unova_PC",
    },
    "Mistralton_City": {  # 合众飞行到医院前面下面一格不在大门口
        "town_map_coords": (420, 371),
        "map_number": (2, 0, 107),  # 医院门口
        "112": (108, 306, 1),
        "112_map_number": (2, 0, 109),
        "112_out": [(7, 19, 0), (6, 19, 0), (8, 19, 0)],
        "112_nurse": (7, 12, 1),  # x,y,dir
        "area": "Unova",
        "pc_type": "Unova_PC",
    },
    "Cerulean_City": {
        "town_map_coords": (763, 338),
        "map_number": (0, 3, 3),
        "112": (22, 20, 1),
        "112_map_number": (0, 3, 7),
        "112_out": [(7, 8, 0)],
        "112_nurse": (7, 4, 1),  # x,y,dir
        "area": "Kanto",
        "pc_type": "Kanto_PC",
    },
    "Fuchsia_City": {
        "town_map_coords": (721, 554),
        "map_number": (0, 7, 3),
        "112": (25, 32, 1),
        "112_map_number": (0, 5, 11),
        "112_out": [(7, 8, 0)],
        "112_nurse": (7, 4, 1),  # x,y,dir
        "area": "Kanto",
        "pc_type": "Kanto_PC",
    },
}


def test_city_info():
    # Test if all keys in dictionary have no spaces
    for key in city_info.keys():
        assert " " not in key, f"Error: Key {key} has spaces."

    # Test if required keys exist in each dictionary value
    for value in city_info.values():
        assert "town_map_coords" in value, "Error: Missing 'town_map_coords' key."
        assert "map_number" in value, "Error: Missing 'map_number' key."
        assert "112" in value, "Error: Missing '112' key."
        assert "112_map_number" in value, "Error: Missing '112_map_number' key."
        assert "112_nurse" in value, "Error: Missing '112_nurse' key."
        assert "112_out" in value, "Error: Missing '112_out' key."
        assert "area" in value, "Error: Missing 'area' key."
    print("All tests passed.")


if __name__ == "__main__":
    test_city_info()
