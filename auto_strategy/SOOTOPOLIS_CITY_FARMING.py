from __future__ import annotations

import random
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class Faming_SOOTOPOLIS_CITY:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.my_df = self.pokeMMO.df_dict["SOOTOPOLIS_CITY_coords_tracking_csv"]
        self.lake_edge_df = self.my_df[
            self.my_df["mark"] == 3
        ].copy()  # Create a copy of the filtered DataFrame
        self.lake_edge_df.loc[:, "face_dir"] = self.lake_edge_df.apply(
            lambda row: self.determine_face_dir(self.my_df, row), axis=1
        )
        self.lake_edge_face_dir_list = list(
            self.lake_edge_df[["y_coords", "x_coords", "face_dir"]].itertuples(
                index=False, name=None
            )
        )

    @staticmethod
    def determine_face_dir(df, row):
        # Look around the point in four directions
        directions = [
            (0, -1, 1),
            (0, 1, 0),
            (-1, 0, 2),
            (1, 0, 3),
        ]  # (dx, dy, face_dir)
        for dx, dy, face_dir in directions:
            # If there is a lake in the direction, return the direction
            if (
                df[
                    (df["x_coords"] == row["x_coords"] + dx)
                    & (df["y_coords"] == row["y_coords"] + dy)
                    & (df["mark"].isin([1, 2]))
                ].size
                > 0
            ):
                return face_dir
        return None  # Return None if no lake is around

    def leave_pc_center_and_go_farm(self, city: str):
        self.pokeMMO.pf.leave_pc_center(city="SOOTOPOLIS_CITY")
        # 去湖边
        my_edge_choice = random.choice(self.lake_edge_face_dir_list)
        self.pokeMMO.pf.go_somewhere(
            end_point=(my_edge_choice[0], my_edge_choice[1]),
            face_dir=my_edge_choice[2],
            city="SOOTOPOLIS_CITY",
        )

        # 冲浪
        self.pokeMMO.roleController.use_surf()

    def run(self):
        # 首先要确认是否能飞走

        if self.pokeMMO.get_game_status["map_number_tuple"][2] == 50:
            result = self.pokeMMO.roleController.fly_to_city(
                "SOOTOPOLIS_CITY", locate_teleport=True
            )
            if result:
                print("飞走成功")
            else:
                raise Exception("飞不走")

        # 检测是否回城补给
        # 开始刷怪
          while self.pokeMMO.get_game_status()["return_status"] < 20:
            if (
                self.pokeMMO.roleController.false_swipe <= 0
                and self.pokeMMO.roleController.sweet_scent == 0
            ):
                self.pokeMMO.roleController.restart_from_hospital()

            self.pokeMMO.roleController.use_sweet_sent()
            round = 0
            if self.pokeMMO.get_game_status().get("check_battle_end_pokemon_caught")[0]:
                self.pokeMMO.roleController.close_pokemon_summary(game_status)
                round = 0
                print(
                    "剩余:",
                    "sweet_scent",
                    self.pokeMMO.roleController.sweet_scent,
                    "false_swipe",
                    self.pokeMMO.roleController.false_swipe,
                )
                break
            self.pokeMMO.roleController.move_left_right(0.8)

        while True:
            # print("进入战斗")
            game_status = self.pokeMMO.get_game_status()
            enemy_status = self.pokeMMO.get_enemy_status()
            if (
                game_status["return_status"] == 21
                and enemy_status.get("enemy_1_info") is not None
            ):  # 当血量不够低的时候，就用技能1
                # print("当血量不够低的时候，就用技能1")
                if (
                    enemy_status.get("enemy_1_hp_pct") >= 8
                    and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1]) <= 10
                ) or (
                    enemy_status.get("enemy_1_hp_pct") >= 2.5
                    and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1]) >= 10
                ):
                    round += 1
                    self.pokeMMO.roleController.fight_skill_1_from_s21()
                    round += 1
                elif (
                    (
                        enemy_status.get("enemy_1_hp_pct") < 8
                        and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1])
                        <= 10
                    )
                    or (
                        enemy_status.get("enemy_1_hp_pct") < 2.5
                        and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1])
                        >= 10
                    )
                ) and enemy_status.get("enemy_1_info")["CatchRate"] == 255:
                    self.pokeMMO.roleController.throw_pokeball()
                    round += 1
            elif (
                game_status["return_status"] == 21
                and enemy_status.get("enemy_count") > 1
            ):
                self.pokeMMO.roleController.run_from_s21()
            if game_status["return_status"] == 1:
                break
