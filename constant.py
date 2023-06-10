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


city_info = {
    "SOOTOPOLIS_CITY": {
        "town_map_coords": (836, 414),
        "map_number": (1, 7, 50),
        "112": (43, 32, 1),
        "112_map_number": (1, 2, 65),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [
            (7, 8, 0),
            (6, 8, 0),
        ],  # 把正对着护士的放在第一个
        "coords_tracking_ready": True,
    },
    "FALLARBOR_TOWN": {
        "town_map_coords": (403, 241),
        "map_number": (1, 13, 50),
        "112": (14, 8, 1),
        "112_map_number": (1, 4, 55),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(7, 8, 0), (6, 8, 0)],
        "coords_tracking_ready": False,
    },
    "PETALBURG_CITY": {
        "town_map_coords": (357, 457),
        "map_number": (1, 0, 50),
        "112": (20, 17, 1),
        "112_map_number": (1, 4, 58),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(7, 8, 0), (6, 8, 0)],
    },
    "BATTLE_FRONTIER": {
        "town_map_coords": (860, 530),
        "map_number": (1, 14, 76),
        "112": (3, 52, 1),
        "112_map_number": (1, 53, 76),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(7, 8, 0), (6, 8, 0)],
    },
    "VERDANTURF_TOWN": {
        "town_map_coords": (424, 383),
        "map_number": (1, 14, 50),
        "112": (16, 4, 1),
        "112_map_number": (1, 4, 56),
        "112_nurse": (7, 4, 1),  # x,y,dir
        "112_out": [(7, 8, 0), (6, 8, 0)],
    },
    "Undella_Town": {
        "town_map_coords": (938, 377),
        "map_number": (2, 2, 156),
        "112": (760, 300, 1),
        "112_map_number": (2, 1, 157),
        "112_nurse": (7, 12, 1),  # x,y,dir
        "112_out": [(7, 19, 0), (6, 19, 0), (8, 19, 0)],
    },
    "Icirrus_City": {
        "town_map_coords": (489, 303),
        "map_number": (2, 0, 113),
        "112": (184, 196, 1),
        "112_map_number": (2, 0, 115),
        "112_out": [(7, 19, 0), (6, 19, 0), (8, 19, 0)],
        "112_nurse": (7, 12, 1),  # x,y,dir
    },
    "Mistralton_City": {  # 合众飞行到医院前面下面一格不在大门口
        "town_map_coords": (420, 371),
        "map_number": (2, 0, 107),  # 医院门口
        "112": (108, 306, 1),
        "112_map_number": (2, 0, 109),
        "112_out": [(7, 19, 0), (6, 19, 0), (8, 19, 0)],
        "112_nurse": (7, 12, 1),  # x,y,dir
        # (105,262,1) 要下自行车zzz
        # (107,233,1) 烛光零门口（2，1，81）
        # (16,28,1)(2,1,82) 螺旋塔门口 要变xy了 往上走一步变成（16，28）
        # (16,23,3)(16,24,3)2楼出口方向出口（2，1，83）
        # (2,1,86) 楼顶
        # (2,0,107)  route 7 x,y 不用改
        # （2，1，83） 2 楼（2，1，84）3楼（2，1，85）4楼（2，1，86）楼顶
    },
}
