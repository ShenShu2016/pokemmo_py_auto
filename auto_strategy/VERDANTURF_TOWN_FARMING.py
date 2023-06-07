from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


def add_x_y_coords_offset_VERDANTURF_TOWN(game_status):
    game_status_copy = game_status.copy()  # Create a copy of the game_status
    if game_status_copy["map_number_tuple"] == (1, 4, 74):
        game_status_copy["x_coords"] = game_status_copy["x_coords"] - 21
        game_status_copy["y_coords"] = game_status_copy["y_coords"] - 16

    else:
        pass
    return game_status_copy  # Return the modified copy


class Farming_VERDANTURF_TOWN:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.my_df = self.pokeMMO.df_dict["VERDANTURF_TOWN_coords_tracking_csv"]

    def leave_pc_center_and_go_farm(self, city="VERDANTURF_TOWN"):
        self.pokeMMO.pf.leave_pc_center(city=city)

    def teleport_and_heal(self, city: str):
        self.pokeMMO.action_controller.use_teleport()
        self.pokeMMO.action_controller.talk_to_nurse()  # teleport 就直接面对护士了

    def run(self, repeat_times=10):
        # 首先要确认是否能飞走
        time.sleep(1)

        if self.pokeMMO.get_game_status()["map_number_tuple"][2] == 50:
            result = self.pokeMMO.action_controller.fly_to_city(
                "VERDANTURF_TOWN", locate_teleport=True
            )
            if result:
                print("飞走成功")
                self.leave_pc_center_and_go_farm(city="VERDANTURF_TOWN")
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
                game_status = add_x_y_coords_offset_VERDANTURF_TOWN(
                    self.pokeMMO.get_game_status()
                )
                if self.pokeMMO.get_game_status().get(
                    "check_battle_end_pokemon_caught"
                )[0]:
                    self.pokeMMO.action_controller.close_pokemon_summary(game_status)
                if (game_status["sprite_dict"]["Sweet Scent"]["pp"] < 5) and (
                    game_status["sprite_dict"]["False Swipe"]["pp"] <= 5
                    or game_status["sprite_dict"]["Spore"]["pp"] <= 2
                ):
                    farming_times += 1
                    if farming_times >= repeat_times:
                        return
                    self.teleport_and_heal(city="VERDANTURF_TOWN")
                    self.leave_pc_center_and_go_farm(city="VERDANTURF_TOWN")

                min_x, max_x, min_y, max_y = 22, 41, 12, 16

                if (
                    (game_status["x_coords"] >= min_x)
                    and (game_status["x_coords"] <= max_x)
                    and (game_status["y_coords"] >= min_y)
                    and (game_status["y_coords"] <= max_y)
                ):
                    self.pokeMMO.action_controller.use_sweet_sent()

                self.pokeMMO.pf.go_somewhere(
                    end_point=None,
                    end_face_dir=None,
                    city="VERDANTURF_TOWN",
                    style="farming",  # 编号66
                )

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
    farming = Farming_VERDANTURF_TOWN(pokeMMO)
    farming.run()
