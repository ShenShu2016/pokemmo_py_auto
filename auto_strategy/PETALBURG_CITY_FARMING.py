from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


def add_x_y_coords_offset_PETALBURG_CITY(game_status):
    game_status_copy = game_status.copy()  # Create a copy of the game_status
    if game_status_copy["map_number_tuple"][1] == 17:
        game_status_copy["x_coords"] = game_status_copy["x_coords"] + 30
        game_status_copy["y_coords"] = game_status_copy["y_coords"] + 10

    else:
        pass
    return game_status_copy  # Return the modified copy


class Farming_PETALBURG_CITY:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.city = "PETALBURG_CITY"
        self.my_df = self.pokeMMO.df_dict["PETALBURG_CITY_coords_tracking_csv"]
        self.farming_coords = [
            (x, y)
            for x, y, mark in zip(
                self.my_df["x_coords"], self.my_df["y_coords"], self.my_df["mark"]
            )
            if mark == 66
        ]

    def leave_pc_center_and_go_farm(self):
        self.pokeMMO.pf.leave_pc_center(city=self.city)

    def teleport_and_heal(self):
        self.pokeMMO.action_controller.use_teleport()
        self.pokeMMO.action_controller.talk_to_nurse()  # teleport 就直接面对护士了

    def run(self, repeat_times=10):
        # 首先要确认是否能飞走
        time.sleep(1)

        if self.pokeMMO.get_game_status()["map_number_tuple"][2] == 50:
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
                game_status = add_x_y_coords_offset_PETALBURG_CITY(
                    self.pokeMMO.get_game_status()
                )
                if self.pokeMMO.get_game_status().get(
                    "check_battle_end_pokemon_caught"
                )[0]:
                    self.pokeMMO.action_controller.iv_shiny_check_release(game_status)
                if (self.pokeMMO.action_controller.skill_pp_dict["甜甜香气"] < 5) and (
                    self.pokeMMO.action_controller.skill_pp_dict["点到为止"] <= 5
                    or self.pokeMMO.action_controller.skill_pp_dict["蘑菇孢子"] <= 3
                ):
                    farming_times += 1
                    if farming_times >= repeat_times:
                        return
                    self.teleport_and_heal()
                    self.leave_pc_center_and_go_farm(city="PETALBURG_CITY")

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
                    city="PETALBURG_CITY",
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


if __name__ == "__main__":
    import sys

    sys.path.append(
        r"C:\Users\SS\Documents\GitHub\pokemmo_py_auto"
    )  # 将 main.py 所在的文件夹路径添加到模块搜索路径中

    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Farming_PETALBURG_CITY(pokeMMO)
    farming.run()
