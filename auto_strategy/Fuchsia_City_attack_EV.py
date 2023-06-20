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


def add_x_y_coords_offset_Fuchsia_City(coords_status):
    coords_status_copy = coords_status.copy()  # Create a copy of the game_status
    if coords_status_copy["map_number_tuple"] == (0, 33, 3):
        coords_status_copy["x_coords"] = coords_status_copy["x_coords"] + 48
        coords_status_copy["y_coords"] = coords_status_copy["y_coords"] + 10
    elif coords_status_copy["map_number_tuple"] == (0, 0, 24):
        coords_status_copy["x_coords"] = coords_status_copy["x_coords"] + 55
        coords_status_copy["y_coords"] = coords_status_copy["y_coords"] + 15

    else:
        pass
    return coords_status_copy  # Return the modified copy


class Farming_Fuchsia_City:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.p = pokeMMO_instance
        self.city = "Fuchsia_City"
        self.my_df = self.p.df_dict["Fuchsia_City_coords_tracking_csv"]
        self.farming_coords = [
            (x, y)
            for x, y, mark in zip(
                self.my_df["x_coords"], self.my_df["y_coords"], self.my_df["mark"]
            )
            if mark == 66
        ]

    def leave_pc_center_and_go_farm(self):
        self.p.pf.leave_pc_center(city=self.city)
        self.p.pf.go_somewhere(
            city=self.city,
            style="farming",  # 编号66
        )

    def teleport_and_heal(self):
        self.p.ac.use_teleport()
        self.p.ac.talk_to_nurse(city=self.city)  # teleport 就直接面对护士了

    def run(self, repeat_times=10):
        # 首先要确认是否能飞走
        sleep(1)

        result = self.p.ac.fly_to_city(self.city, locate_teleport=True)
        if result:
            print("飞走成功")
            self.leave_pc_center_and_go_farm()
        else:
            raise Exception("飞不走")

        # 检测是否回城补给
        # 开始刷怪
        farming_times = 0
        while self.p.auto_strategy_flag:
            print("开始刷怪,或者是回城补给")
            while self.p.get_gs()["return_status"] < 20:
                game_status = self.p.get_gs()
                coords_status = add_x_y_coords_offset_Fuchsia_City(self.p.get_coords())

                if self.p.ac.skill_pp_dict["甜甜香气"] < 5:
                    farming_times += 1
                    if farming_times >= repeat_times:
                        print("刷怪次数达到上限!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        return
                    self.teleport_and_heal()
                    self.leave_pc_center_and_go_farm()  # 应该已经到了湖里了

                if (
                    coords_status["x_coords"],
                    coords_status["y_coords"],
                ) in self.farming_coords:
                    # Trigger the desired operation
                    self.p.ac.use_sweet_sent()
                    # pass

            while self.p.auto_strategy_flag:
                # print("进入战斗")
                game_status = self.p.get_gs()
                enemy_status = self.p.get_bs()
                if game_status.get("check_pokemon_summary")[0]:
                    self.p.ac.close_pokemon_summary(game_status)

                if (
                    game_status["return_status"] == 21
                    and enemy_status.get("allChecked") == True
                    and enemy_status.get("enemy_count") == 1
                ):
                    self.p.ac.run_from_s21()

                elif (
                    game_status["return_status"] == 21
                    and enemy_status.get("allChecked") == True
                ):
                    self.p.ac.multi_fight_skill_1_from_s21()

                if game_status["return_status"] == 1:
                    break
                sleep(0.05)


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Farming_Fuchsia_City(pokeMMO)
    farming.run()
