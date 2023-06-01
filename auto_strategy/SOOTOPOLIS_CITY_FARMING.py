from __future__ import annotations

import random
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class Faming_SOOTOPOLIS_CITY:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.my_df = self.pokeMMO.df_dict["SOOTOPOLIS_CITY_coords_tracking_csv"]
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

    def leave_pc_center_and_go_farm(self, city="SOOTOPOLIS_CITY"):
        self.pokeMMO.pf.leave_pc_center(city=city)
        # 去湖边
        my_edge_choice = random.choice(self.lake_edge_face_dir_list)
        self.pokeMMO.pf.go_somewhere(
            end_point=(my_edge_choice[0], my_edge_choice[1]),
            end_face_dir=my_edge_choice[2],
            city=city,
        )

        # 冲浪
        self.pokeMMO.roleController.use_surf()

    def teleport_and_heal(self, city: str):
        self.pokeMMO.roleController.use_teleport()
        self.pokeMMO.roleController.talk_to_nurse()

    def run(self):
        # 首先要确认是否能飞走
        time.sleep(1)

        if self.pokeMMO.get_game_status()["map_number_tuple"][2] == 50:
            result = self.pokeMMO.roleController.fly_to_city(
                "SOOTOPOLIS_CITY", locate_teleport=True
            )
            if result:
                print("飞走成功")
                self.leave_pc_center_and_go_farm(city="SOOTOPOLIS_CITY")
            else:
                raise Exception("飞不走")
        else:
            raise Exception("飞不走的情况之后处理")

        # 检测是否回城补给
        # 开始刷怪

        while True:
            print("开始刷怪,或者是回城补给")
            while self.pokeMMO.get_game_status()["return_status"] < 20:
                game_status = self.pokeMMO.get_game_status()
                if (game_status["sprite_dict"]["Sweet Scent"]["pp"] == 0) and (
                    game_status["sprite_dict"]["False Swipe"]["pp"] <= 5
                ):
                    self.teleport_and_heal(city="SOOTOPOLIS_CITY")
                    self.leave_pc_center_and_go_farm(
                        city="SOOTOPOLIS_CITY"
                    )  # 应该已经到了湖里了

                self.pokeMMO.roleController.use_sweet_sent()

                # if self.pokeMMO.get_game_status().get("check_battle_end_pokemon_caught")[0]:
                #     self.pokeMMO.roleController.close_pokemon_summary(game_status)
                #     break

                self.pokeMMO.pf.go_somewhere(
                    end_point=None,
                    end_face_dir=None,
                    city="SOOTOPOLIS_CITY",
                    style="farming",
                )

            while True:
                # print("进入战斗")
                game_status = self.pokeMMO.get_game_status()
                enemy_status = self.pokeMMO.get_enemy_status()
                if (
                    game_status["return_status"] == 21
                    and enemy_status.get("enemy_1_info") is not None
                ):  # 当血量不够低的时候，就用技能1
                    # print("当血量不够低的时候，就用技能1")
                    if (
                        enemy_status.get("enemy_1_hp_pct") >= 8
                        and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1])
                        <= 10
                    ) or (
                        enemy_status.get("enemy_1_hp_pct") >= 2.5
                        and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1])
                        >= 10
                    ):
                        self.pokeMMO.roleController.fight_skill_1_from_s21()

                    elif (
                        (
                            enemy_status.get("enemy_1_hp_pct") < 8
                            and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1])
                            <= 10
                        )
                        or (
                            enemy_status.get("enemy_1_hp_pct") < 2.5
                            and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1])
                            >= 10
                        )
                    ) and enemy_status.get("enemy_1_info")["CatchRate"] == 255:
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
    farming = Faming_SOOTOPOLIS_CITY(pokeMMO)
    farming.run()
