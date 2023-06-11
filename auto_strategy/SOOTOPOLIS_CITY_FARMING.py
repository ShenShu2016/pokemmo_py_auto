from __future__ import annotations

import random
from time import sleep
from typing import TYPE_CHECKING

from auto_strategy.common_funciton import is_go_pc

if TYPE_CHECKING:
    from main import PokeMMO


def add_x_y_coords_offset_SOOTOPOLIS_CITY(game_status):
    game_status_copy = game_status.copy()  # Create a copy of the game_status
    return game_status_copy  # Return the modified copy


class Farming_SOOTOPOLIS_CITY:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.city = "SOOTOPOLIS_CITY"
        self.my_df = self.pokeMMO.df_dict[f"{self.city}_coords_tracking_csv"]
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

    def leave_pc_center_and_go_farm(self):
        self.pokeMMO.pf.leave_pc_center(city=self.city)
        # 去湖边
        my_edge_choice = random.choice(self.lake_edge_face_dir_list)
        self.pokeMMO.pf.go_somewhere(
            end_point=(my_edge_choice[0], my_edge_choice[1]),
            end_face_dir=my_edge_choice[2],
            city=self.city,
        )

        # 冲浪
        self.pokeMMO.action_controller.use_surf()

    def teleport_and_heal(self):
        self.pokeMMO.action_controller.use_teleport()
        self.pokeMMO.action_controller.talk_to_nurse()

    def run(self, repeat_times=10):
        # 首先要确认是否能飞走
        sleep(1)

        if self.pokeMMO.get_game_status()["map_number_tuple"][2] in [50, 76]:
            result = self.pokeMMO.action_controller.fly_to_city(
                "SOOTOPOLIS_CITY", locate_teleport=True
            )
            if result:
                print("飞走成功")
                self.leave_pc_center_and_go_farm()
            else:
                raise Exception("飞不走")
        else:
            raise Exception("飞不走的情况之后处理")

        # 检测是否回城补给
        # 开始刷怪
        farming_times = 0
        while True:
            print("开始刷怪,或者是回城补给")
            while self.pokeMMO.get_game_status()["return_status"] < 20:
                game_status = self.pokeMMO.get_game_status()
                if self.pokeMMO.get_game_status().get("check_pokemon_summary")[0]:
                    self.pokeMMO.action_controller.iv_shiny_check_release(game_status)
                if is_go_pc(self.pokeMMO.action_controller.skill_pp_dict):
                    farming_times += 1
                    if farming_times >= repeat_times:
                        return
                    self.teleport_and_heal(city="SOOTOPOLIS_CITY")
                    self.leave_pc_center_and_go_farm(
                        city="SOOTOPOLIS_CITY"
                    )  # 应该已经到了湖里了

                self.pokeMMO.action_controller.use_sweet_sent()

                self.pokeMMO.pf.go_somewhere(
                    end_point=None,
                    end_face_dir=None,
                    city="SOOTOPOLIS_CITY",
                    style="farming",
                )

            while True:
                # print("进入战斗")
                game_status = self.pokeMMO.get_game_status()
                enemy_status = self.pokeMMO.get_enemy_status()
                if game_status.get("check_pokemon_summary")[0]:
                    self.pokeMMO.action_controller.iv_shiny_check_release(game_status)

                if (
                    game_status["return_status"] == 21
                    and enemy_status.get("enemy_1_info") is not None
                ):
                    if enemy_status.get("enemy_1_info")["CatchMethod"] == 1:
                        if enemy_status.get("enemy_1_hp_pct") >= 20:
                            self.pokeMMO.action_controller.fight_skill_1_from_s21()

                        elif enemy_status.get("enemy_1_hp_pct") < 20:
                            self.pokeMMO.action_controller.throw_pokeball()

                    elif enemy_status.get("enemy_1_info")["CatchMethod"] == 2:
                        if enemy_status.get("enemy_1_hp_pct") >= 20:
                            self.pokeMMO.action_controller.fight_skill_1_from_s21()

                        elif (
                            enemy_status.get("enemy_1_hp_pct") < 20
                            and enemy_status.get("enemy_1_sleeping") == False
                        ):
                            self.pokeMMO.action_controller.fight_skill_2_from_s21()  # Spore

                        elif (
                            enemy_status.get("enemy_1_hp_pct") < 20
                            and enemy_status.get("enemy_1_sleeping") == True
                        ):
                            self.pokeMMO.action_controller.throw_pokeball()
                    elif enemy_status.get("enemy_1_info")["CatchMethod"] == 0:
                        self.pokeMMO.action_controller.run_from_s21()

                elif (
                    game_status["return_status"] == 21
                    and enemy_status.get("enemy_count") == 3
                    and enemy_status.get("enemy_2_info") is not None
                    and enemy_status.get("enemy_3_info") is not None
                    and enemy_status.get("enemy_4_info") is not None
                ):
                    self.pokeMMO.action_controller.run_from_s21()

                elif (
                    game_status["return_status"] == 21
                    and enemy_status.get("enemy_count") == 5
                    and enemy_status.get("enemy_2_info") is not None
                    and enemy_status.get("enemy_3_info") is not None
                    and enemy_status.get("enemy_4_info") is not None
                    and enemy_status.get("enemy_5_info") is not None
                    and enemy_status.get("enemy_6_info") is not None
                ):
                    self.pokeMMO.action_controller.run_from_s21()

                if game_status["return_status"] == 1:
                    break
                sleep(0.05)


if __name__ == "__main__":
    import os
    import sys

    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录的绝对路径
    package_path = os.path.join(current_dir, "..")  # 获取上级目录的路径
    sys.path.append(package_path)  # 将上级目录添加到模块搜索路径中
    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Farming_SOOTOPOLIS_CITY(pokeMMO)
    farming.run()
