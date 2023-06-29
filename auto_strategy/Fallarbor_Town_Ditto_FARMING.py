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


def add_x_y_coords_offset_Fallarbor_Town_Ditto(coords_status):
    coords_status_copy = coords_status.copy()  # Create a copy of the game_status
    if coords_status_copy["map_number_tuple"] == (1, 29, 50):
        coords_status_copy["x_coords"] = coords_status_copy["x_coords"] - 40
    elif coords_status_copy["map_number_tuple"] == (1, 0, 70):
        coords_status_copy["x_coords"] = coords_status_copy["x_coords"] - 15
        coords_status_copy["y_coords"] = coords_status_copy["y_coords"] - 3
    elif coords_status_copy["map_number_tuple"] == (1, 1, 70):
        coords_status_copy["x_coords"] = coords_status_copy["x_coords"] - 17
        coords_status_copy["y_coords"] = coords_status_copy["y_coords"] - 28
    elif coords_status_copy["map_number_tuple"] == (1, 98, 74):
        coords_status_copy["x_coords"] = coords_status_copy["x_coords"] - 21
        coords_status_copy["y_coords"] = coords_status_copy["y_coords"] - 39

    else:
        pass
    return coords_status_copy  # Return the modified copy


class Farming_Fallarbor_Town_Ditto:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.p = pokeMMO_instance
        self.city = "Fallarbor_Town_Ditto"
        self.is替身 = False
        self.my_df = self.p.df_dict["Fallarbor_Town_Ditto_coords_tracking_csv"]
        self.farming_coords = [
            (x, y)
            for x, y, mark in zip(
                self.my_df["x_coords"], self.my_df["y_coords"], self.my_df["mark"]
            )
            if mark == 66
        ]

    def leave_pc_center_and_go_farm(self):
        self.p.pf.leave_pc_center(city=self.city)

    def teleport_and_heal(self):
        self.p.ac.use_dig()
        self.go_outside()
        sleep(3)
        self.p.ac.use_teleport()
        self.p.ac.talk_to_nurse(city=self.city)  # teleport 就直接面对护士了

    def go_outside(self):
        self.p.pf.go_somewhere(end_point=(6, -11), city=self.city)

    def run(self, repeat_times=10):
        # 首先要确认是否能飞走
        sleep(1)

        result = self.p.ac.fly_to_city(self.city, locate_teleport=True)
        if result:
            print("飞走成功")
            self.leave_pc_center_and_go_farm()
        else:
            raise Exception("飞不走")

        farming_times = 0
        while self.p.auto_strategy_flag:
            print("开始刷怪,或者是回城补给")
            while self.p.get_gs()["return_status"] < 20:
                coords_status = self.p.get_coords()
                game_status = self.p.get_gs()
                coords_status = add_x_y_coords_offset_Fallarbor_Town_Ditto(
                    coords_status
                )
                if game_status.get("check_pokemon_summary")[0]:
                    self.p.ac.iv_shiny_check_release(game_status)
                if self.p.ac.is_go_pc():
                    farming_times += 1
                    if farming_times >= repeat_times:
                        self.p.ac.use_dig()
                        self.go_outside()
                        self.teleport_and_heal()

                        return
                    self.teleport_and_heal()
                    self.leave_pc_center_and_go_farm()

                # Check if there are any rows where both x_coords and y_coords are equal to 66
                if (
                    coords_status["x_coords"],
                    coords_status["y_coords"],
                ) in self.farming_coords:
                    # Trigger the desired operation
                    self.p.ac.use_sweet_sent()
                    # pass

                self.p.pf.go_somewhere(
                    end_point=None,
                    end_face_dir=None,
                    city=self.city,
                    style="farming",  # 编号66
                )

            while self.p.auto_strategy_flag:
                # print("进入战斗")
                game_status = self.p.get_gs()
                battle_status = self.p.get_bs()
                if self.p.get_gs().get("check_pokemon_summary")[0]:
                    self.p.ac.iv_shiny_check_release(game_status, release=False)

                if (
                    game_status["return_status"] == 21
                    and battle_status.get("enemy_1_info") is not None
                ):
                    if (
                        battle_status.get("enemy_1_info")["No"]
                        in [
                            293,
                            294,
                        ]
                        or self.p.ac.is_go_pc()
                    ):  # 碰到别的东西逃跑
                        self.p.ac.run_from_s21()
                    elif battle_status.get("enemy_1_info")["CatchMethod"] == 132:
                        if self.is替身 == False:
                            self.p.ac.fight_skill_替身_from_s21()
                            self.is替身 = True
                        elif battle_status.get("enemy_1_hp_pct") >= 20:
                            self.p.ac.fight_skill_1_from_s21()
                        elif (
                            battle_status.get("enemy_1_hp_pct") < 20
                            and battle_status.get("enemy_1_sleeping") == False
                        ):
                            self.p.ac.fight_skill_2_from_s21()
                        elif (
                            battle_status.get("enemy_1_hp_pct") < 20
                            and battle_status.get("enemy_1_sleeping") == True
                        ):
                            self.p.ac.throw_pokeball(pokeball_type="dark_ball")
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

                elif (
                    game_status["return_status"] == 21
                    and battle_status.get("enemy_count") >= 2
                    and battle_status.get("allChecked") == True
                ):
                    self.p.ac.run_from_s21()

                if game_status["return_status"] == 1:
                    self.is替身 = False
                    break
                sleep(0.05)


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Farming_Fallarbor_Town_Ditto(pokeMMO)
    farming.run()
