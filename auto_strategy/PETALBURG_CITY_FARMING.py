from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


def add_x_y_coords_offset_PETALBURG_CITY(game_status):
    if game_status["map_number_tuple"][1] == 17:
        game_status["x_coords"] = game_status["x_coords"] + 30
        game_status["y_coords"] = game_status["y_coords"] + 10

    else:
        pass
    return game_status


class Faming_PETALBURG_CITY:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.my_df = self.pokeMMO.df_dict["PETALBURG_CITY_coords_tracking_csv"]

    def leave_pc_center_and_go_farm(self, city="PETALBURG_CITY"):
        self.pokeMMO.pf.leave_pc_center(city=city)

    def teleport_and_heal(self, city: str):
        self.pokeMMO.roleController.use_teleport()
        self.pokeMMO.roleController.talk_to_nurse()  # teleport 就直接面对护士了

    def run(self):
        # 首先要确认是否能飞走
        time.sleep(1)

        if self.pokeMMO.get_game_status()["map_number_tuple"][2] == 50:
            result = self.pokeMMO.roleController.fly_to_city(
                "PETALBURG_CITY", locate_teleport=True
            )
            if result:
                print("飞走成功")
                self.leave_pc_center_and_go_farm(city="PETALBURG_CITY")
            else:
                raise Exception("飞不走")
        else:
            raise Exception("飞不走的情况之后处理")

        # 检测是否回城补给
        # 开始刷怪

        while True:
            print("开始刷怪,或者是回城补给")
            while self.pokeMMO.get_game_status()["return_status"] < 20:
                game_status = add_x_y_coords_offset_PETALBURG_CITY(
                    self.pokeMMO.get_game_status()
                )
                if self.pokeMMO.get_game_status().get(
                    "check_battle_end_pokemon_caught"
                )[0]:
                    self.pokeMMO.roleController.close_pokemon_summary(game_status)
                if (game_status["sprite_dict"]["Sweet Scent"]["pp"] == 0) and (
                    game_status["sprite_dict"]["False Swipe"]["pp"] <= 5
                    or game_status["sprite_dict"]["Spore"]["pp"] <= 2
                ):
                    self.teleport_and_heal(city="PETALBURG_CITY")
                    self.leave_pc_center_and_go_farm(city="PETALBURG_CITY")  # 应该已经到了湖里了
                min_x, max_x, min_y, max_y = 22, 41, 12, 16

                if (
                    (game_status["x_coords"] >= min_x)
                    and (game_status["x_coords"] <= max_x)
                    and (game_status["y_coords"] >= min_y)
                    and (game_status["y_coords"] <= max_y)
                ):
                    self.pokeMMO.roleController.use_sweet_sent()

                self.pokeMMO.pf.go_somewhere(
                    end_point=None,
                    end_face_dir=None,
                    city="PETALBURG_CITY",
                    style="farming",
                )

            while True:
                # print("进入战斗")
                game_status = self.pokeMMO.get_game_status()
                enemy_status = self.pokeMMO.get_enemy_status()
                if game_status["return_status"] == 21:  # 当血量不够低的时候，就用技能1
                    # print("当血量不够低的时候，就用技能1")
                    if enemy_status.get("enemy_1_hp_pct") >= 20:
                        self.pokeMMO.roleController.fight_skill_1_from_s21()

                    elif enemy_status.get("enemy_1_hp_pct") < 20:
                        self.pokeMMO.roleController.throw_pokeball()

                elif (
                    game_status["return_status"] == 21
                    and enemy_status.get("enemy_count") > 1
                ):
                    self.pokeMMO.roleController.run_from_s21()
                if game_status["return_status"] == 1:
                    break


if __name__ == "__main__":
    import sys

    sys.path.append(
        "C:/Users/SS/Documents/GitHub/pokemmo_py_auto"
    )  # 将 main.py 所在的文件夹路径添加到模块搜索路径中

    from main import PokeMMO

    pokeMMO = PokeMMO()
    farming = Faming_PETALBURG_CITY(pokeMMO)
    farming.run()
