from __future__ import annotations

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录的绝对路径
package_path = os.path.join(current_dir, "..")  # 获取上级目录的路径
sys.path.append(package_path)  # 将上级目录添加到模块搜索路径中
from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


def add_x_y_coords_offset_VERDANTURF_TOWN(coords_status):
    coords_status_copy = coords_status.copy()  # Create a copy of the game_status
    if coords_status_copy["map_number_tuple"] == (1, 4, 74):
        coords_status_copy["x_coords"] = coords_status_copy["x_coords"] - 21
        coords_status_copy["y_coords"] = coords_status_copy["y_coords"] - 16

    else:
        pass
    return coords_status_copy  # Return the modified copy


class Farming_VERDANTURF_TOWN:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.city = "VERDANTURF_TOWN"
        self.my_df = self.pokeMMO.df_dict[f"{self.city}_coords_tracking_csv"]
        self.farming_coords = [
            (x, y)
            for x, y, mark in zip(
                self.my_df["x_coords"], self.my_df["y_coords"], self.my_df["mark"]
            )
            if mark == 66
        ]

    def leave_pc_center_and_go_farm(self):
        self.pokeMMO.pf.leave_pc_center(city=self.city)

    def dig_teleport_and_heal(self):
        self.pokeMMO.action_controller.use_dig()
        self.pokeMMO.action_controller.use_teleport()
        self.pokeMMO.action_controller.talk_to_nurse()  # teleport 就直接面对护士了

    def run(self, repeat_times=10):
        # 首先要确认是否能飞走
        sleep(1)
        print(self.pokeMMO.get_coords_status())

        if self.pokeMMO.get_coords_status()["map_number_tuple"][2] == 50:
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
        while self.pokeMMO.auto_strategy_flag:
            print("开始刷怪,或者是回城补给")
            while True:
                game_status = self.pokeMMO.get_game_status()
                if game_status["return_status"] >= 20:
                    break

                coords_status = add_x_y_coords_offset_VERDANTURF_TOWN(
                    self.pokeMMO.get_coords_status()
                )

                if game_status.get("check_pokemon_summary")[0]:
                    self.pokeMMO.action_controller.iv_shiny_check_release(game_status)

                if self.pokeMMO.action_controller.is_go_pc():
                    farming_times += 1
                    if farming_times >= repeat_times:
                        self.pokeMMO.action_controller.use_dig()
                        sleep(1)
                        return
                    self.dig_teleport_and_heal()
                    self.leave_pc_center_and_go_farm()

                coords = (coords_status["x_coords"], coords_status["y_coords"])
                if coords in self.farming_coords:
                    self.pokeMMO.action_controller.use_sweet_sent()

                self.pokeMMO.pf.go_somewhere(
                    end_point=None,
                    end_face_dir=None,
                    city=self.city,
                    style="farming",
                )

            while self.pokeMMO.auto_strategy_flag:
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
    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Farming_VERDANTURF_TOWN(pokeMMO)
    farming.run()
