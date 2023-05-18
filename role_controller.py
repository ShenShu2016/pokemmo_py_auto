from __future__ import annotations

import datetime
import logging
import random
import time
from collections import deque
from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


def calculate_catch_rate(
    max_hp=65, current_hp=1, catch_rate=1, ball_rate=1, pokemon_condition=1
):
    numerator = (
        (3 * max_hp - 2 * current_hp) * catch_rate * ball_rate * pokemon_condition
    )
    denominator = 3 * max_hp * 255
    final_catch_rate = numerator / denominator
    return final_catch_rate


class RoleController:
    def __init__(self, pokeMMO: PokeMMO):
        self.pokeMMO = pokeMMO
        self.my_recent_actions_list = deque(maxlen=1000)
        self.logger = logging.getLogger("movement_log")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(message)s")

        # Include start time in the log filename
        start_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_filename = f"movement_{start_time}.log"

        # Specify directory for the log file
        log_directory = "logs/"  # Modify this as per your desired directory

        file_handler = logging.FileHandler(f"{log_directory}{log_filename}")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def move_left_right(self, delay: float):
        keys = ["a", "d"]
        random.shuffle(keys)

        self.logger.info("Moving: %s" % keys[0])
        self.pokeMMO.controller.key_press(keys[0], delay + random.uniform(0, delay))
        self.logger.info("Moving: %s" % keys[1])
        self.pokeMMO.controller.key_press(keys[1], delay + random.uniform(0, delay))

        total_delay = random.uniform(0, 0.5)
        sleep(total_delay)
        self.my_recent_actions_list.append(("move_left_right", time.time()))
        self.logger.info("Total Delay: %.2f" % total_delay)

    def fight_skill_1_from_s21(self):  # False Swipe
        self.pokeMMO.controller.click(314, 508, tolerance=15)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.my_recent_actions_list.append(("fight_skill_1_from_s21", time.time()))
        self.logger.info("Using False Swipe")

    def fight_skill_2_from_s21(self):  # Spore
        self.pokeMMO.controller.click(314, 508, tolerance=15)
        self.pokeMMO.controller.key_press("d", 0.2)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.my_recent_actions_list.append(("fight_skill_2_from_s21", time.time()))
        self.logger.info("Using Spore")

    def fight_skill_3_from_s21(self):
        self.pokeMMO.controller.click(314, 508, tolerance=15)
        self.pokeMMO.controller.key_press("s", 0.2)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.my_recent_actions_list.append(("fight_skill_3_from_s21", time.time()))

    def fight_skill_4_from_s21(self):
        self.pokeMMO.controller.click(314, 508, tolerance=15)
        self.pokeMMO.controller.key_press("s", 0.2)
        self.pokeMMO.controller.key_press("d", 0.2)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.my_recent_actions_list.append(("fight_skill_4_from_s21", time.time()))

    def run_from_s21(self):
        self.pokeMMO.controller.click(522, 557, tolerance=15)
        self.logger.info("Running from battle")

    def throw_pokeball(self, pokeball_type="pokeball"):
        print("Throwing Pokeball")
        self.pokeMMO.controller.click(527, 506, tolerance=15)  # 点击背包
        sleep(0.3)
        if (
            len(
                self.pokeMMO.find_items(
                    temp_BRG=self.pokeMMO.poke_ball_BRG,
                    top_l=(521, 395),
                    bottom_r=(563, 438),
                    max_matches=1,
                    threshold=0.99,
                )
            )
            > 0
        ):
            print("扔球")
            self.pokeMMO.controller.key_press("z", 5)
            self.logger.info("Throwing Pokeball")
            sleep(5)

    def close_pokemon_summary(self, game_status):
        for i in game_status["battle_end_pokemon_caught"][1]:  # [(814, 262, 936, 277)]
            exit_button_x = (i[0] + i[2]) / 2 + 103
            exit_button_y = (i[1] + i[3]) / 2 + 0
            print(exit_button_x, exit_button_y)

            self.pokeMMO.controller.click(exit_button_x, exit_button_y, tolerance=0)
            self.my_recent_actions_list.append(("close_pokemon_summary", time.time()))
            self.logger.info(
                "Closing Pokemon Summary at %s, %s" % (exit_button_x, exit_button_y)
            )


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    # pokeMMO.start_ui()
    round = 0

    while True:
        while pokeMMO.get_game_status()["return_status"] < 20:
            round = 0
            pokeMMO.roleController.move_left_right(0.8)

        # start battle 有可能进医院黑屏了，有可能就是进入战斗了

        # 1 解决进入医院黑屏问题dwd

        # 进入战斗
        while True:
            print("进入战斗")
            game_status = pokeMMO.get_game_status()
            enemy_status = pokeMMO.get_enemy_status()
            # print("game_status", game_status)
            # print("enemy_status", enemy_status)
            print("enemy_status.get(enemy_1_info)", enemy_status.get("enemy_1_info"))
            if (
                game_status["return_status"] == 21
                and enemy_status.get("enemy_1_info") is not None
            ):  # 当血量不够低的时候，就用技能1
                print("当血量不够低的时候，就用技能1")
                if (
                    enemy_status.get("enemy_1_hp_pct") >= 8
                    and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1]) <= 10
                ) or (
                    enemy_status.get("enemy_1_hp_pct") >= 2.5
                    and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1]) >= 10
                ):
                    pokeMMO.roleController.fight_skill_1_from_s21()
                    round += 1
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
                    pokeMMO.roleController.throw_pokeball()
                    round += 1

            if game_status["return_status"] == 23:
                pokeMMO.roleController.close_pokemon_summary(game_status)
                round = 0
                break
            if game_status["black_ratio"] <= 0.35:
                break
            sleep(0.1)
