# enemy_status.py
from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO

import threading

enemy_hp_coords = [
    [(329, 97), (346, 110)],
    [(589, 97), (606, 110)],
    [(849, 97), (866, 110)],
    [(329, 137), (345, 150)],
    [(849, 137), (865, 150)],
]
special_cases = [
    {"coords": [(254, 147), (268, 160)], "enemy_count": 1},
    {"coords": [(329, 137), (345, 150)], "enemy_count": 5},
    {"coords": [(849, 137), (865, 150)], "enemy_count": 5},
]
# enemy_hp_bar_coords = {
#     1: [(274, 151), (471, 155)],  # Enemy 1 HP coordinates
#     2: [(349, 101), (502, 105)],  # Enemy 2 HP coordinates
#     3: [(609, 101), (757, 105)],  # Enemy 3 HP coordinates
#     4: [(870, 101), (1020, 105)],  # Enemy 4 HP coordinates
#     5: [(349, 141), (503, 145)],  # Enemy 5 HP coordinates
#     6: [(869, 141), (1020, 145)],  # Enemy 6 HP coordinates
# }
enemy_hp_bar_coords = {
    1: [(273, 152), (472, 153)],  # Enemy 1 HP coordinates
    2: [(349, 102), (498, 103)],  # Enemy 2 HP coordinates
    3: [(609, 102), (758, 103)],  # Enemy 3 HP coordinates
    4: [(869, 102), (1018, 103)],  # Enemy 4 HP coordinates
    5: [(349, 142), (498, 143)],  # Enemy 5 HP coordinates
    6: [(869, 142), (1018, 143)],  # Enemy 6 HP coordinates
}
enemy_name_coords = {
    1: [(251, 129), (492, 147)],
    2: [(316, 79), (516, 98)],
    3: [(576, 79), (780, 96)],
    4: [(836, 79), (1037, 96)],
    5: [(316, 117), (517, 136)],
    6: [(835, 117), (1037, 136)],
}


class EnemyStatus:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.enemy_status_dict = {"enemy_count": 0}
        self.game_status_dict = {}

    def _match_coords(self, hp_coords, tolerance, found_hp):
        return (
            hp_coords[0][0] - tolerance <= found_hp[0] <= hp_coords[0][0] + tolerance
            and hp_coords[0][1] - tolerance
            <= found_hp[1]
            <= hp_coords[0][1] + tolerance
            and hp_coords[1][0] - tolerance
            <= found_hp[2]
            <= hp_coords[1][0] + tolerance
            and hp_coords[1][1] - tolerance
            <= found_hp[3]
            <= hp_coords[1][1] + tolerance
        )

    def _check_enemy_number(self):
        if self.game_status_dict.get("return_status") == 1:
            self.enemy_status_dict = {"enemy_count": None}
            return

        if self.game_status_dict.get("return_status") in [
            20,
            21,
            22,
            23,
        ] and self.enemy_status_dict.get("enemy_count") in [0, None]:
            hp_BRG_x_y_list = self.pokeMMO.find_items(
                temp_BRG=self.pokeMMO.hp_BRG,
                threshold=0.995,
                max_matches=5,
                top_l=(0, 70),
                bottom_r=(1080, 170),
                img_BRG=self.img_BRG,
            )
            # print(f"hp_BRG_x_y_list: {hp_BRG_x_y_list}")
            if not hp_BRG_x_y_list:
                return
            self.enemy_status_dict["enemy_count"] = len(hp_BRG_x_y_list)

    def _check_enemy_hp(self):
        if self.game_status_dict.get("return_status") in [
            20,
            21,
            22,
            23,
        ]:
            enemy_count = self.enemy_status_dict["enemy_count"]
            if enemy_count in [3, 5]:
                for i in range(2, enemy_count + 2):
                    hp_pct = self.pokeMMO.get_hp_pct(
                        enemy_hp_bar_coords[i][0],
                        enemy_hp_bar_coords[i][1],
                        self.img_BRG,
                    )
                    self.enemy_status_dict[f"enemy_{i}_hp_pct"] = hp_pct
            elif enemy_count == 1:
                hp_pct = self.pokeMMO.get_hp_pct(
                    enemy_hp_bar_coords[1][0], enemy_hp_bar_coords[1][1], self.img_BRG
                )
                self.enemy_status_dict["enemy_1_hp_pct"] = hp_pct

    def _check_enemy_name_lv(self):
        # start_time = time.time()
        enemy_count = self.enemy_status_dict["enemy_count"]

        def _process_i(self, i):
            if (
                f"enemy_{i}_hp_pct" in self.enemy_status_dict
                and f"enemy_{i}_name_Lv" not in self.enemy_status_dict
                and self.enemy_status_dict[f"enemy_{i}_hp_pct"] is not None
            ):
                sex_coords = self.pokeMMO.find_items(
                    temp_BRG=self.pokeMMO.enemy_male_BRG,
                    top_l=enemy_name_coords[i][0],
                    bottom_r=enemy_name_coords[i][1],
                    img_BRG=self.img_BRG,
                    threshold=0.99,
                    max_matches=1,
                )
                if not sex_coords:
                    sex_coords = self.pokeMMO.find_items(
                        temp_BRG=self.pokeMMO.enemy_female_BRG,
                        top_l=enemy_name_coords[i][0],
                        bottom_r=enemy_name_coords[i][1],
                        img_BRG=self.img_BRG,
                        threshold=0.99,
                        max_matches=1,
                    )
                if sex_coords:
                    enemy_name_coords[i] = (
                        enemy_name_coords[i][0],
                        (sex_coords[0][0], enemy_name_coords[i][1][1]),
                    )
                name_Lv_ORC = self.pokeMMO.get_text_from_box_coords(
                    top_l=enemy_name_coords[i][0],
                    bottom_r=enemy_name_coords[i][1],
                    img_BRG=self.img_BRG,
                    config="--psm 7 --oem 3 -c tessedit_char_whitelist=Lv1234567890",
                )

                numeric_string = "".join(filter(str.isdigit, name_Lv_ORC))
                total_int = int(numeric_string)

                if total_int >= 99999 and enemy_count == 1:  # 闪光
                    pass
                elif total_int >= 99999 and enemy_count > 1:
                    print("闪光宠出现", name_Lv_ORC, total_int)
                    import os

                    os.system("taskkill /f /im python.exe")

                if "Lv" in name_Lv_ORC:
                    self.enemy_status_dict[f"enemy_{i}_name_Lv"] = name_Lv_ORC
                    name_ORC = name_Lv_ORC.split("Lv")[0].strip()
                    lv_orc = name_Lv_ORC.split("Lv")[1].strip()
                    info = self.pokeMMO.pokedex_csv.loc[
                        self.pokeMMO.pokedex_csv["No"] == int(name_ORC)
                    ]

                    if info.empty == False:
                        info_dict = info.to_dict(orient="records")
                        self.enemy_status_dict[f"enemy_{i}_info"] = info_dict[0]

                    else:
                        info = self.pokeMMO.pokedex_csv.loc[
                            self.pokeMMO.pokedex_csv["No"] == int(999)
                        ]
                        info_dict = info.to_dict(orient="records")
                        self.enemy_status_dict[f"enemy_{i}_info"] = info_dict[0]

                        print(f"{name_ORC} 有可能是闪光")

        threads = []
        enemy_count = self.enemy_status_dict["enemy_count"]
        if enemy_count not in [0, None]:
            if enemy_count == 1:
                i = 1
                t = threading.Thread(
                    target=_process_i,
                    args=(
                        self,
                        i,
                    ),
                )
                t.start()
                threads.append(t)
            else:
                for i in range(2, enemy_count + 2):
                    t = threading.Thread(
                        target=_process_i,
                        args=(
                            self,
                            i,
                        ),
                    )
                    t.start()
                    threads.append(t)

        for t in threads:
            t.join()  # 等待所有线程完成
        # enemy_count = self.enemy_status_dict["enemy_count"]
        # if enemy_count not in [0, None]:
        #     for i in range(1, enemy_count + 2):
        #         # print("i-----------------------------------------------------", i)
        #         if (
        #             f"enemy_{i}_hp_pct" in self.enemy_status_dict
        #             and f"enemy_{i}_name_Lv" not in self.enemy_status_dict
        #             and self.enemy_status_dict[f"enemy_{i}_hp_pct"] is not None
        #         ):
        #             sex_coords = self.pokeMMO.find_items(
        #                 temp_BRG=self.pokeMMO.enemy_male_BRG,
        #                 top_l=enemy_name_coords[i][0],
        #                 bottom_r=enemy_name_coords[i][1],
        #                 img_BRG=self.img_BRG,
        #                 threshold=0.99,
        #                 max_matches=1,
        #             )
        #             if not sex_coords:
        #                 sex_coords = self.pokeMMO.find_items(
        #                     temp_BRG=self.pokeMMO.enemy_female_BRG,
        #                     top_l=enemy_name_coords[i][0],
        #                     bottom_r=enemy_name_coords[i][1],
        #                     img_BRG=self.img_BRG,
        #                     threshold=0.99,
        #                     max_matches=1,
        #                 )
        #             if sex_coords:
        #                 enemy_name_coords[i] = (
        #                     enemy_name_coords[i][0],
        #                     (sex_coords[0][0], enemy_name_coords[i][1][1]),
        #                 )
        #             name_Lv_ORC = self.pokeMMO.get_text_from_box_coords(
        #                 top_l=enemy_name_coords[i][0],
        #                 bottom_r=enemy_name_coords[i][1],
        #                 img_BRG=self.img_BRG,
        #                 config="--psm 7 --oem 3 -c tessedit_char_whitelist=Lv1234567890",  #
        #             )
        #             # print(
        #             #     "i-----------------------------------------------------",
        #             #     i,
        #             #     name_Lv_ORC,
        #             # )

        #             # print("name_Lv_ORC 使用时间:", time.time() - start_time)

        #             numeric_string = "".join(filter(str.isdigit, name_Lv_ORC))
        #             total_int = int(numeric_string)

        #             if total_int >= 9999:  # 闪光
        #                 pass
        #             elif total_int >= 9999 and enemy_count > 1:
        #                 # close all python
        #                 import os

        #                 os.system("taskkill /f /im python.exe")
        #             # print("Shiny 检测时间:", time.time() - start_time)

        #             if "Lv" in name_Lv_ORC:
        #                 self.enemy_status_dict[f"enemy_{i}_name_Lv"] = name_Lv_ORC
        #                 # go self.pokedex to get the pokemon info
        #                 name_ORC = name_Lv_ORC.split("Lv")[0].strip()
        #                 lv_orc = name_Lv_ORC.split("Lv")[1].strip()
        #                 # print("name_ORC:", name_ORC)
        #                 # print("lv_orc:", lv_orc)
        #                 info = self.pokeMMO.pokedex_csv.loc[
        #                     self.pokeMMO.pokedex_csv["No"] == int(name_ORC)
        #                 ]

        #                 if info.empty == False:
        #                     info_dict = info.to_dict(orient="records")
        #                     # Print the dictionary
        #                     self.enemy_status_dict[f"enemy_{i}_info"] = info_dict[0]
        #                     print(info_dict[0])

        #                 else:  # 闪光宠直接变成999 当普通宠来抓
        #                     info = self.pokeMMO.pokedex_csv.loc[
        #                         self.pokeMMO.pokedex_csv["No"] == int(999)
        #                     ]
        #                     info_dict = info.to_dict(orient="records")
        #                     # Print the dictionary
        #                     self.enemy_status_dict[f"enemy_{i}_info"] = info_dict[0]

        #                     print(f"{name_ORC} 有可能是闪光")
        #             # print("检查名字与等级使用时间:", time.time() - start_time)

    def check_enemy_sleep(self):
        if self.game_status_dict.get("return_status") in [
            20,
            21,
            22,
            23,
        ]:
            # print("检查敌人睡眠状态")
            sleeping_sign_coords_list = self.pokeMMO.find_items(
                temp_BRG=self.pokeMMO.battle_bar_sleep_sign_BRG,
                top_l=(220, 120),
                bottom_r=(492, 150),
                img_BRG=self.img_BRG,
                threshold=0.99,
                max_matches=1,
            )
            # print("sleeping_sign_coords_list", sleeping_sign_coords_list)
            if len(sleeping_sign_coords_list) > 0:
                self.enemy_status_dict["enemy_1_sleeping"] = True
            else:
                self.enemy_status_dict["enemy_1_sleeping"] = False

    def check_enemy_status(self):
        self.img_BRG = self.pokeMMO.get_latest_img_BRG()
        self.game_status_dict = self.pokeMMO.get_game_status()
        self._check_enemy_number()
        self._check_enemy_hp()
        # start_time = time.time()
        self._check_enemy_name_lv()
        # print("检查敌人名字与等级使用时间:", time.time() - start_time)
        self.check_enemy_sleep()
        # print("enemy_status_dict", self.enemy_status_dict)
        return self.enemy_status_dict
