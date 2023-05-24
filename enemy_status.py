# enemy_status.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO

import subprocess

# Constants
MP3_FILE_PATH = "unravel.mp3"
DEBUG = True
BATTLE_OPTION_STATUS = 21
ENEMY_FOUND_STATUSES = [20, 21, 22, 23]


def _play_mp3(file_path=MP3_FILE_PATH):
    subprocess.run(["wmplayer", file_path])


class EnemyStatus:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.enemy_status_dict = {"enemy_count": 0}

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
        if self.pokeMMO.get_game_status()["return_status"] == 1:
            self.enemy_status_dict = {"enemy_count": 0}
            return
        if (self.pokeMMO.get_game_status()["return_status"] in [20, 21, 22, 23]) and (
            self.enemy_status_dict["enemy_count"] == 0
        ):
            hp_BRG_x_y_list = self.pokeMMO.find_items(
                temp_BRG=self.pokeMMO.hp_BRG,
                threshold=0.99,
                max_matches=5,
                top_l=(0, 70),
                bottom_r=(1080, 170),
                img_BRG=self.img_BRG,
            )
            # print(f"hp_BRG_x_y_list: {hp_BRG_x_y_list}")
            if not hp_BRG_x_y_list:
                self.enemy_status_dict["enemy_count"] = 0
                # print("No HP bars found.")
                return

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
            tolerance = 10
            enemy_count = 0

            for special_case in special_cases:
                for found_hp in hp_BRG_x_y_list:
                    if self._match_coords(special_case["coords"], tolerance, found_hp):
                        self.enemy_status_dict["enemy_count"] = special_case[
                            "enemy_count"
                        ]
                        return

            for enemy_hp in enemy_hp_coords:
                for found_hp in hp_BRG_x_y_list:
                    if self._match_coords(enemy_hp, tolerance, found_hp):
                        enemy_count += 1
                self.enemy_status_dict["enemy_count"] = enemy_count
        # print("enemy_count:", self.enemy_status_dict["enemy_count"])

    def _check_enemy_hp(self):
        if self.pokeMMO.get_game_status()["return_status"] == 21:  # battle_option
            # Define the enemy hp bar coordinates
            enemy_hp_bar_coords = {
                1: [(274, 151), (471, 155)],  # Enemy 1 HP coordinates
                2: [(349, 101), (502, 105)],  # Enemy 2 HP coordinates
                3: [(609, 101), (757, 105)],  # Enemy 3 HP coordinates
                4: [(870, 101), (1020, 105)],  # Enemy 4 HP coordinates
                5: [(349, 141), (503, 145)],  # Enemy 5 HP coordinates
                6: [(869, 141), (1020, 145)],  # Enemy 6 HP coordinates
            }

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
        enemy_count = self.enemy_status_dict["enemy_count"]
        if enemy_count > 0:
            enemy_name_coords = {
                1: [(251, 129), (492, 147)],
                2: [(316, 79), (516, 98)],
                3: [(576, 79), (780, 96)],
                4: [(836, 79), (1037, 96)],
                5: [(316, 117), (517, 136)],
                6: [(835, 117), (1037, 136)],
            }

            for i in range(1, enemy_count + 1):
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
                        config="--psm 7 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",  #
                    )
                    if self.pokeMMO.word_recognizer.compare_with_target(
                        recognized_ORC=name_Lv_ORC.lower(), target_words=["shiny"]
                    )[0]:
                        _play_mp3()
                    elif (
                        self.pokeMMO.word_recognizer.compare_with_target(
                            recognized_ORC=name_Lv_ORC.lower(), target_words=["shiny"]
                        )[0]
                        and self.enemy_status_dict["enemy_count"] > 1
                    ):
                        _play_mp3()
                        # close all python
                        import os

                        os.system("taskkill /f /im python.exe")

                    if "Lv" in name_Lv_ORC:
                        self.enemy_status_dict[f"enemy_{i}_name_Lv"] = name_Lv_ORC
                        # go self.pokedex to get the pokemon info
                        name_ORC = name_Lv_ORC.split("Lv")[0].strip()
                        lv_orc = name_Lv_ORC.split("Lv")[1].strip()
                        # print("name_ORC:", name_ORC)
                        # print("lv_orc:", lv_orc)
                        info = self.pokeMMO.pokedex.loc[
                            self.pokeMMO.pokedex["Pokemon"] == name_ORC
                        ]
                        if info.empty == False and enemy_count == 1:
                            info_dict = info.to_dict(orient="records")
                            # Print the dictionary
                            self.enemy_status_dict[f"enemy_{i}_info"] = info_dict[0]
                            print(info_dict[0])
                            pass
                        else:
                            print(f"{name_ORC} info not found")

    def check_enemy_status(self):
        self.img_BRG = self.pokeMMO.get_latest_img_BRG()
        self._check_enemy_number()
        self._check_enemy_hp()
        self._check_enemy_name_lv()
        # print("enemy_status_dict", self.enemy_status_dict)
        return self.enemy_status_dict
