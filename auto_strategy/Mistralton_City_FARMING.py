from __future__ import annotations

import time
from typing import TYPE_CHECKING

# from auto_strategy.common_funciton import is_go_pc
from auto_strategy.common_funciton import is_go_pc

if TYPE_CHECKING:
    from main import PokeMMO


def add_x_y_coords_offset_Mistralton_City(game_status):
    game_status_copy = game_status.copy()  # Create a copy of the game_status

    if game_status_copy["map_number_tuple"] == (2, 1, 82):
        if game_status_copy["y_coords"] <= 10:
            game_status_copy["x_coords"] = 13 - game_status_copy["x_coords"]
            game_status_copy["y_coords"] = 25 - game_status_copy["y_coords"]

    elif game_status_copy["map_number_tuple"] == (2, 1, 83):
        game_status_copy["x_coords"] = game_status_copy["x_coords"] - 26
        game_status_copy["y_coords"] = game_status_copy["y_coords"] + 2
    else:
        pass

    return game_status_copy  # Return the modified copy


class Farming_Mistralton_City:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.city = "Mistralton_City"
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

    def step_1_go_bridge(self):
        self.pokeMMO.pf.go_somewhere(end_point=(262, 105), city=self.city)

    def step_2_pass_bridge(self):
        self.pokeMMO.pf.go_somewhere(
            end_point=(259, 115), city=self.city, transport="run"
        )

    def step_3_go_tower(self):
        self.pokeMMO.pf.go_somewhere(end_point=(233, 107), city=self.city)
        self.pokeMMO.controller.key_press("w", 0.7)
        time.sleep(2)

    def teleport_and_heal(self):
        self.pokeMMO.action_controller.use_teleport()
        self.pokeMMO.action_controller.talk_to_nurse()  # teleport 就直接面对护士了

    def back_to_open_air(self):
        pass

    def run(self, repeat_times=10):
        # 首先要确认是否能飞走
        time.sleep(1)

        result = self.pokeMMO.action_controller.fly_to_city(
            self.city, locate_teleport=True
        )
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
        while True:
            print("开始刷怪,或者是回城补给")
            while self.pokeMMO.get_game_status()["return_status"] < 20:
                game_status = add_x_y_coords_offset_Mistralton_City(
                    self.pokeMMO.get_game_status()
                )
                if self.pokeMMO.get_game_status().get(
                    "check_battle_end_pokemon_caught"
                )[0]:
                    self.pokeMMO.action_controller.iv_shiny_check_release(game_status)
                if is_go_pc(self.pokeMMO.action_controller.skill_pp_dict):
                    farming_times += 1
                    if farming_times >= repeat_times:  # 如果重复次数到了，会停到一个可以飞的地方，没到的话就会pc
                        self.pokeMMO.pf.go_somewhere(
                            end_point=(25, 16),
                            end_face_dir=None,
                            city=self.city,
                            style="ignore_sprite",  # 编号66
                        )
                        if self.pokeMMO.get_game_status()["return_status"] >= 20:
                            break
                        game_status = self.pokeMMO.get_game_status()
                        if (
                            game_status["x_coords"] == 16
                            and game_status["y_coords"] == 25
                        ):
                            print("到达塔里,出门前")
                            self.pokeMMO.controller.key_press("s", 3)
                            if self.pokeMMO.get_game_status()["map_number_tuple"] == (
                                2,
                                1,
                                81,
                            ):
                                return  # 出function

                    self.pokeMMO.pf.go_somewhere(
                        end_point=(25, 16),
                        end_face_dir=None,
                        city=self.city,
                        style="ignore_sprite",  # 编号66
                    )
                    if self.pokeMMO.get_game_status()["return_status"] >= 20:
                        break  # break 出，因为要战斗了
                    game_status = self.pokeMMO.get_game_status()
                    if game_status["x_coords"] == 16 and game_status["y_coords"] == 25:
                        print("到达塔里,出门前")
                        self.pokeMMO.controller.key_press("s", 3)
                        if self.pokeMMO.get_game_status()["map_number_tuple"] == (
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
                if (
                    game_status["x_coords"],
                    game_status["y_coords"],
                ) in self.farming_coords:
                    # Trigger the desired operation
                    self.pokeMMO.action_controller.use_sweet_sent()
                    # pass

                self.pokeMMO.pf.go_somewhere(
                    end_point=None,
                    end_face_dir=None,
                    city=self.city,
                    style="farming",  # 编号66
                )

            while True:
                # print("进入战斗")
                game_status = self.pokeMMO.get_game_status()
                enemy_status = self.pokeMMO.get_enemy_status()
                if self.pokeMMO.get_game_status().get(
                    "check_battle_end_pokemon_caught"
                )[0]:
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
                    elif (
                        enemy_status.get("enemy_1_info")["CatchMethod"] == 0
                        and int(enemy_status.get("enemy_1_info")["No"]) != 999
                    ):
                        self.pokeMMO.action_controller.run_from_s21()

                    elif enemy_status.get("enemy_1_info")["CatchMethod"] == 11:
                        if is_go_pc(self.pokeMMO.action_controller.skill_pp_dict):
                            self.pokeMMO.action_controller.run_from_s21()
                        elif enemy_status.get("enemy_1_hp_pct") >= 80:
                            self.pokeMMO.action_controller.fight_skill_3_from_s21()
                        else:
                            self.pokeMMO.action_controller.throw_pokeball()
                    # elif (
                    #     enemy_status.get("enemy_1_info")["CatchMethod"] == 11
                    # ):  # 直接睡了扔球
                    #     if is_go_pc(self.pokeMMO.action_controller.skill_pp_dict):
                    #         self.pokeMMO.action_controller.run_from_s21()
                    #     elif enemy_status.get("enemy_1_hp_pct") >= 80:
                    #         self.pokeMMO.action_controller.fight_skill_4_from_s21()  # 龙之怒
                    #     elif enemy_status.get("enemy_1_sleeping") == False:
                    #         self.pokeMMO.action_controller.fight_skill_2_from_s21()
                    #     elif enemy_status.get("enemy_1_sleeping") == True:
                    #         self.pokeMMO.action_controller.throw_pokeball()
                    # elif (
                    #     enemy_status.get("enemy_1_info")["CatchMethod"] == 11
                    # ):  # 直接睡了扔球
                    #     if is_go_pc(self.pokeMMO.action_controller.skill_pp_dict):
                    #         self.pokeMMO.action_controller.run_from_s21()
                    #     elif enemy_status.get("enemy_1_sleeping") == False:
                    #         self.pokeMMO.action_controller.fight_skill_2_from_s21()
                    #     elif enemy_status.get("enemy_1_sleeping") == True:
                    #         self.pokeMMO.action_controller.throw_pokeball()
                    else:
                        raise Exception("闪光，有问题！！！")

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


if __name__ == "__main__":
    import os
    import sys

    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录的绝对路径
    package_path = os.path.join(current_dir, "..")  # 获取上级目录的路径
    sys.path.append(package_path)  # 将上级目录添加到模块搜索路径中
    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Farming_Mistralton_City(pokeMMO)
    farming.run()
