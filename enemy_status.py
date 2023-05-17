# enemy_status.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class EnemyStatus:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.enemy_status_dict = {
            "enemy_count": 0,
        }

    def match_coords(self, hp_coords, tolerance, found_hp):
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

    def check_enemy_number(self):
        if self.pokeMMO.get_game_status() == 1:
            self.enemy_status_dict = {"enemy_count": 0}
            return
        if (self.pokeMMO.get_game_status() in [20, 21, 22, 23]) and (
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
            print(f"hp_BRG_x_y_list: {hp_BRG_x_y_list}")
            if not hp_BRG_x_y_list:
                self.enemy_status_dict["enemy_count"] = 0
                print("No HP bars found.")
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
                    if self.match_coords(special_case["coords"], tolerance, found_hp):
                        self.enemy_status_dict["enemy_count"] = special_case[
                            "enemy_count"
                        ]
                        return

            for enemy_hp in enemy_hp_coords:
                for found_hp in hp_BRG_x_y_list:
                    if self.match_coords(enemy_hp, tolerance, found_hp):
                        enemy_count += 1
                self.enemy_status_dict["enemy_count"] = enemy_count
        # print("enemy_count:", self.enemy_status_dict["enemy_count"])

    def check_enemy_hp(self):
        # Define the enemy hp bar coordinates
        enemy_hp_bar_coords = {
            1: [(274, 151), (471, 155)],  # Enemy 1 HP coordinates
            2: [(349, 101), (502, 105)],  # Enemy 2 HP coordinates
            3: [(609, 101), (757, 105)],  # Enemy 3 HP coordinates
            4: [(870, 101), (1020, 105)],  # Enemy 4 HP coordinates
            5: [(349, 141), (502, 145)],  # Enemy 5 HP coordinates
            6: [(869, 141), (1020, 145)],  # Enemy 6 HP coordinates
        }

        if self.pokeMMO.get_game_status() == 21:  # battle_option
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

    def check_enemy_name_lv(self):
        # Define the enemy name coordinates
        enemy_name_coords = {
            1: [(251, 129), (492, 147)],  # Enemy 1 Name coordinates
            2: [(316, 79), (518, 98)],  # Enemy 2 Name coordinates
            3: [(576, 79), (780, 96)],  # Enemy 3 Name coordinates
            4: [(836, 79), (1038, 96)],  # Enemy 4 Name coordinates
            5: [(316, 117), (519, 136)],  # Enemy 5 Name coordinates
            6: [(835, 117), (1038, 136)],  # Enemy 6 Name coordinates
        }

        enemy_count = self.enemy_status_dict["enemy_count"]

        if enemy_count > 0:
            for i in range(1, enemy_count + 1):
                if (
                    f"enemy_{i}_hp_pct" in self.enemy_status_dict
                    and self.enemy_status_dict[f"enemy_{i}_hp_pct"] is not None
                ):
                    sex_coords = self.pokeMMO.find_items(
                        temp_BRG=self.pokeMMO.enemy_male_BRG,
                        top_l=enemy_name_coords[i][0],
                        bottom_r=enemy_name_coords[i][1],
                        img_BRG=self.img_BRG,
                        threshold=0.99,
                        max_matches=2,  #! should be 1
                    )
                    name_text = self.pokeMMO.get_text_from_box_coords(
                        top_l=enemy_name_coords[i][0],
                        bottom_r=enemy_name_coords[i][1],
                        img_BRG=self.img_BRG,
                    )
                    self.enemy_status_dict[f"enemy_{i}_name"] = name_text
        return

    def check_enemy_status(self):
        self.img_BRG = self.pokeMMO.get_latest_img_BRG()
        self.check_enemy_number()
        self.check_enemy_hp()
        self.check_enemy_name_lv()
        print("enemy_status_dict:", self.enemy_status_dict)
