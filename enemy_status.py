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
                {"coords": [(254, 78), (268, 89)], "enemy_count": 1},
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

            if enemy_count in [1, 3, 5]:
                self.enemy_status_dict["enemy_count"] = enemy_count
            else:
                self.enemy_status_dict["enemy_count"] = 0
        # print("enemy_count:", self.enemy_status_dict["enemy_count"])

    def check_enemy_hp(self):
        if (
            self.enemy_status_dict["enemy_count"] == 1
            and self.pokeMMO.get_game_status() == 21  # battle_option
        ):
            # print("check_enemy_hp")
            enemy_hp_bar_1_x_y = (274, 151), (471, 155)
            hp_pct = self.pokeMMO.get_hp_pct(
                enemy_hp_bar_1_x_y[0], enemy_hp_bar_1_x_y[1], self.img_BRG
            )
            # print("enemy_1_hp_pct", hp_pct)
            self.enemy_status_dict["enemy_1_hp_pct"] = hp_pct
            return

    def check_enemy_status(self):
        self.img_BRG = self.pokeMMO.get_latest_img_BRG()
        self.check_enemy_number()
        self.check_enemy_hp()
        print("enemy_status_dict:", self.enemy_status_dict)
