from __future__ import annotations

import os
import sys

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)
import random
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class Farming_BATTLE_FRONTINER:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.city = "BATTLE_FRONTIER"
        self.my_df = self.pokeMMO.df_dict["BATTLE_FRONTIER_coords_tracking_csv"]
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

    def leave_pc_center_and_go_farm(
        self,
    ):
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
        time.sleep(1)

        if self.pokeMMO.get_game_status()["map_number_tuple"][2] in [50, 76]:
            result = self.pokeMMO.action_controller.fly_to_city(
                self.city, locate_teleport=True
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
                if self.pokeMMO.get_game_status().get(
                    "check_battle_end_pokemon_caught"
                )[0]:
                    self.pokeMMO.action_controller.close_pokemon_summary(game_status)
                if self.pokeMMO.action_controller.skill_pp_dict["甜甜香气"] < 5:
                    farming_times += 1
                    if farming_times >= repeat_times:
                        print("刷怪次数达到上限!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        return
                    self.teleport_and_heal()
                    self.leave_pc_center_and_go_farm()  # 应该已经到了湖里了

                self.pokeMMO.action_controller.use_sweet_sent()

            while True:
                # print("进入战斗")
                game_status = self.pokeMMO.get_game_status()
                enemy_status = self.pokeMMO.get_enemy_status()
                if self.pokeMMO.get_game_status().get(
                    "check_battle_end_pokemon_caught"
                )[0]:
                    self.pokeMMO.action_controller.close_pokemon_summary(game_status)

                if (
                    game_status["return_status"] == 21
                    and enemy_status.get("enemy_count") == 3
                    and enemy_status.get("enemy_2_info") is not None
                    and enemy_status.get("enemy_3_info") is not None
                    and enemy_status.get("enemy_4_info") is not None
                ):
                    self.pokeMMO.action_controller.multi_fight_skill_1_from_s21()

                elif (
                    game_status["return_status"] == 21
                    and enemy_status.get("enemy_count") == 5
                    and enemy_status.get("enemy_2_info") is not None
                    and enemy_status.get("enemy_3_info") is not None
                    and enemy_status.get("enemy_4_info") is not None
                    and enemy_status.get("enemy_5_info") is not None
                    and enemy_status.get("enemy_6_info") is not None
                ):
                    self.pokeMMO.action_controller.multi_fight_skill_1_from_s21()
                elif (
                    game_status["return_status"] == 21
                    and enemy_status.get("enemy_count") == 1
                ):
                    self.pokeMMO.action_controller.multi_fight_skill_1_from_s21()

                if game_status["return_status"] == 1:
                    break


if __name__ == "__main__":
    import sys

    sys.path.append(
        r"C:\Users\shush\文档\Git\pokemmo_py_auto"
    )  # 将 main.py 所在的文件夹路径添加到模块搜索路径中

    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Farming_BATTLE_FRONTINER(pokeMMO)
    farming.run()
