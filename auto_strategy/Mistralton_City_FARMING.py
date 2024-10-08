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


def add_x_y_coords_offset_Mistralton_City(coords_status):
    coords_status_copy = coords_status.copy()  # Create a copy of the game_status

    if coords_status_copy["map_number_tuple"] == (2, 1, 82):
        if coords_status_copy["y_coords"] <= 10:
            coords_status_copy["x_coords"] = 13 - coords_status_copy["x_coords"]
            coords_status_copy["y_coords"] = 25 - coords_status_copy["y_coords"]

    elif coords_status_copy["map_number_tuple"] == (2, 1, 83):
        coords_status_copy["x_coords"] = coords_status_copy["x_coords"] - 26
        coords_status_copy["y_coords"] = coords_status_copy["y_coords"] + 2
    else:
        pass

    return coords_status_copy  # Return the modified copy


class Farming_Mistralton_City:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.p = pokeMMO_instance
        self.city = "Mistralton_City"
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

    def step_1_go_bridge(self):
        self.p.pf.go_somewhere(end_point=(262, 105), city=self.city)

    def step_2_pass_bridge(self):
        self.p.pf.go_somewhere(end_point=(259, 116), city=self.city, transport="run")

    def step_3_go_tower(self):
        self.p.pf.go_somewhere(end_point=(233, 107), city=self.city)
        self.p.controller.key_press("w", 0.7)
        sleep(2)

    def teleport_and_heal(self):
        self.p.ac.use_teleport()
        self.p.ac.talk_to_nurse(city=self.city)  # teleport 就直接面对护士了

    def back_to_open_air(self):
        pass

    def run(self, repeat_times=10):
        # 首先要确认是否能飞走
        sleep(1)

        result = self.p.ac.fly_to_city(self.city, locate_teleport=True)
        if result:
            print("飞走成功")
            self.leave_pc_center_and_go_farm()
            self.step_1_go_bridge()
            self.step_2_pass_bridge()
            self.step_3_go_tower()

        else:
            raise Exception("飞不走")

        # 检测是否回城补给
        # 开始刷怪

        farming_times = 0
        while self.p.auto_strategy_flag:
            print("开始刷怪,或者是回城补给")
            while self.p.get_gs()["return_status"] < 20:
                coords_status = add_x_y_coords_offset_Mistralton_City(
                    self.p.get_coords()
                )
                game_status = self.p.get_gs()
                if game_status.get("check_pokemon_summary")[0]:
                    self.p.ac.iv_shiny_check_release(game_status)
                if self.p.ac.is_go_pc():
                    farming_times += 1
                    if farming_times >= repeat_times:  # 如果重复次数到了，会停到一个可以飞的地方，没到的话就会pc
                        self.p.pf.go_somewhere(
                            end_point=(25, 16),
                            end_face_dir=None,
                            city=self.city,
                            style="ignore_sprite",  # 编号66
                        )
                        if self.p.get_gs()["return_status"] >= 20:
                            break
                        coords_status = self.p.get_coords()
                        if (
                            coords_status["x_coords"] == 16
                            and coords_status["y_coords"] == 25
                        ):
                            print("到达塔里,出门前")
                            self.p.controller.key_press("s", 2.5)
                            if self.p.get_coords()["map_number_tuple"] == (
                                2,
                                1,
                                81,
                            ):
                                return  # 出function

                    self.p.pf.go_somewhere(
                        end_point=(25, 16),
                        end_face_dir=None,
                        city=self.city,
                        style="ignore_sprite",  # 编号66
                    )
                    if self.p.get_gs()["return_status"] >= 20:
                        break  # break 出，因为要战斗了
                    coords_status = self.p.get_coords()
                    if (
                        coords_status["x_coords"] == 16
                        and coords_status["y_coords"] == 25
                    ):
                        print("到达塔里,出门前")
                        self.p.controller.key_press("s", 3)
                        if self.p.get_coords()["map_number_tuple"] == (
                            2,
                            1,
                            81,
                        ):
                            print("可以飞咯")
                        else:
                            raise Exception("出毛病咯噢噢噢噢")
                    self.teleport_and_heal()
                    self.leave_pc_center_and_go_farm()
                    self.step_1_go_bridge()
                    self.step_2_pass_bridge()
                    self.step_3_go_tower()

                # Check if there are any rows where both x_coords and y_coords are equal to 66
                # coords_status = self.p.get_coords()
                if (
                    coords_status["x_coords"],
                    coords_status["y_coords"],
                ) in self.farming_coords:
                    # Trigger the desired operation
                    self.p.ac.use_sweet_sent()
                    # pass

                else:
                    print("不在刷怪点", coords_status["x_coords"], coords_status["y_coords"])

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
                    elif (
                        battle_status.get("enemy_1_info")["CatchMethod"] == 0
                        and int(battle_status.get("enemy_1_info")["No"]) != 999
                    ):
                        self.p.ac.run_from_s21()

                    elif battle_status.get("enemy_1_info")["CatchMethod"] == 11:
                        if (
                            self.p.ac.is_go_pc()
                            and battle_status.get("enemy_1_hp_pct") >= 80
                        ):
                            self.p.ac.run_from_s21()
                        elif battle_status.get("enemy_1_hp_pct") >= 80:
                            self.p.ac.fight_skill_3_from_s21()
                        else:
                            self.p.ac.throw_pokeball()
                    # elif (
                    #     battle_status.get("enemy_1_info")["CatchMethod"] == 11
                    # ):  # 直接睡了扔球
                    #     if is_go_pc(self.p.ac.skill_pp_dict):
                    #         self.p.ac.run_from_s21()
                    #     elif battle_status.get("enemy_1_hp_pct") >= 80:
                    #         self.p.ac.fight_skill_4_from_s21()  # 龙之怒
                    #     elif battle_status.get("enemy_1_sleeping") == False:
                    #         self.p.ac.fight_skill_2_from_s21()
                    #     elif battle_status.get("enemy_1_sleeping") == True:
                    #         self.p.ac.throw_pokeball()
                    # elif (
                    #     battle_status.get("enemy_1_info")["CatchMethod"] == 11
                    # ):  # 直接睡了扔球
                    #     if is_go_pc(self.p.ac.skill_pp_dict):
                    #         self.p.ac.run_from_s21()
                    #     elif battle_status.get("enemy_1_sleeping") == False:
                    #         self.p.ac.fight_skill_2_from_s21()
                    #     elif battle_status.get("enemy_1_sleeping") == True:
                    #         self.p.ac.throw_pokeball()
                    else:
                        raise Exception("闪光，有问题！！！")

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
    import os
    import sys

    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录的绝对路径
    package_path = os.path.join(current_dir, "..")  # 获取上级目录的路径
    sys.path.append(package_path)  # 将上级目录添加到模块搜索路径中
    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Farming_Mistralton_City(pokeMMO)
    farming.run(30)
