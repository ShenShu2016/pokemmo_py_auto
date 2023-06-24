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


def add_x_y_coords_offset_Cerulean_City(coords_status):
    coords_status_copy = coords_status.copy()  # Create a copy of the game_status
    if coords_status_copy["map_number_tuple"] == (0, 23, 3):
        coords_status_copy["y_coords"] = coords_status_copy["y_coords"] + 40
    else:
        pass
    return coords_status_copy  # Return the modified copy


class Farming_Cerulean_City:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.p = pokeMMO_instance
        self.city = "Cerulean_City"
        self.my_df = self.p.df_dict[f"{self.city}_coords_tracking_csv"]
        self.farming_coords = [
            (x, y)
            for x, y, mark in zip(
                self.my_df["x_coords"], self.my_df["y_coords"], self.my_df["mark"]
            )
            if mark == 66
        ]

    def leave_pc_center_and_go_farm(self):
        self.p.pf.leave_pc_center(city=self.city)
        self.step_1_go_tree()
        self.step_2_cut_tree()
        self.step_3_go_farming_are()

    def teleport_and_heal(self):
        self.p.ac.use_teleport()
        self.p.ac.talk_to_nurse(city=self.city)

    def step_1_go_tree(self):
        self.p.pf.go_somewhere(
            end_point=(31, 26), end_face_dir=0, style="ignore_sprite", city=self.city
        )
        self.p.controller.key_press("s", 0.3)

    def step_2_cut_tree(self):
        self.p.ac.use_cut()

    def step_3_go_farming_are(self):
        self.p.pf.go_somewhere(
            end_point=(45, 26), style="ignore_sprite", city=self.city
        )

    def run(self, repeat_times=10):
        # 首先要确认是否能飞走
        sleep(1)

        result = self.p.ac.fly_to_city("Cerulean_City", locate_teleport=True)
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
                coords_status = add_x_y_coords_offset_Cerulean_City(self.p.get_coords())
                if self.p.get_gs().get("check_pokemon_summary")[0]:
                    self.p.ac.iv_shiny_check_release(game_status)
                if self.p.ac.is_go_pc():
                    farming_times += 1
                    if farming_times >= repeat_times:
                        return
                    self.teleport_and_heal()
                    self.leave_pc_center_and_go_farm()  # 应该已经到了湖里了

                if (
                    coords_status["x_coords"],
                    coords_status["y_coords"],
                ) in self.farming_coords:
                    # Trigger the desired operation
                    self.p.ac.use_sweet_sent()
                    pass

                self.p.pf.go_somewhere(
                    end_point=None,
                    end_face_dir=None,
                    city=self.city,
                    style="left_right_farming",  # 编号66
                )
            while self.p.auto_strategy_flag:
                # print("进入战斗")
                game_status = self.p.get_gs()
                battle_status = self.p.get_bs()
                if game_status.get("check_pokemon_summary")[0]:
                    self.p.ac.iv_shiny_check_release(game_status)

                if (
                    game_status["return_status"] == 21
                    and battle_status.get("enemy_1_info") is not None
                ):
                    if battle_status.get("enemy_1_info")["CatchMethod"] == 1:
                        if battle_status.get("enemy_1_hp_pct") >= 20:
                            self.p.ac.fight_skill_1_from_s21()

                        elif battle_status.get("enemy_1_hp_pct") < 20:
                            self.p.ac.throw_pokeball()

                    elif battle_status.get("enemy_1_info")["CatchMethod"] == 2:
                        if battle_status.get("enemy_1_hp_pct") >= 20:
                            self.p.ac.fight_skill_1_from_s21()

                        elif (
                            battle_status.get("enemy_1_hp_pct") < 20
                            and battle_status.get("enemy_1_sleeping") == False
                        ):
                            self.p.ac.fight_skill_2_from_s21()  # Spore

                        elif (
                            battle_status.get("enemy_1_hp_pct") < 20
                            and battle_status.get("enemy_1_sleeping") == True
                        ):
                            self.p.ac.throw_pokeball()
                    elif battle_status.get("enemy_1_info")["CatchMethod"] == 0:
                        self.p.ac.run_from_s21()

                elif (
                    game_status["return_status"] == 21
                    and battle_status.get("enemy_count") >= 2
                    and battle_status.get("allChecked") == True
                ):
                    self.p.ac.run_from_s21()

                if game_status["return_status"] == 1:
                    break
                sleep(0.05)


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Farming_Cerulean_City(pokeMMO)
    farming.run()
