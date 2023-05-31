from __future__ import annotations

import random
import time
from collections import deque
from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO

import queue
import threading
from functools import wraps


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
        self.sweet_scent = 0
        self.false_swipe = 0
        self.press_down_count = 5
        self.action_lock = threading.Lock()

    @staticmethod
    def synchronized(method):
        @wraps(method)
        def _synchronized(self, *args, **kwargs):
            with self.action_lock:
                return method(self, *args, **kwargs)

        return _synchronized

    @synchronized
    def move_left_right(self, delay: float):
        keys = ["a", "d"]
        random.shuffle(keys)
        if self.press_down_count > 0:
            keys = ["s", "s"]
            self.press_down_count -= 1

        self.pokeMMO.controller.key_press(keys[0], delay + random.uniform(0, delay))

        self.pokeMMO.controller.key_press(keys[1], delay + random.uniform(0, delay))

        total_delay = random.uniform(0, 0.5)
        sleep(total_delay)
        self.my_recent_actions_list.append(("move_left_right", time.time()))

    @synchronized
    def fight_skill_1_from_s21(self):  # False Swipe
        self.pokeMMO.controller.click(314, 508, tolerance=15)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.false_swipe -= 1
        self.my_recent_actions_list.append(("fight_skill_1_from_s21", time.time()))
        sleep(5)
        print("Using False Swipe")

    @synchronized
    def fight_skill_2_from_s21(self):  # Spore
        self.pokeMMO.controller.click(314, 508, tolerance=15)
        self.pokeMMO.controller.key_press("d", 0.2)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.my_recent_actions_list.append(("fight_skill_2_from_s21", time.time()))
        sleep(5)
        print("Using Spore")

    @synchronized
    def fight_skill_3_from_s21(self):
        self.pokeMMO.controller.click(314, 508, tolerance=15)
        self.pokeMMO.controller.key_press("s", 0.2)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.my_recent_actions_list.append(("fight_skill_3_from_s21", time.time()))
        sleep(5)

    @synchronized
    def fight_skill_4_from_s21(self):
        self.pokeMMO.controller.click(314, 508, tolerance=15)
        self.pokeMMO.controller.key_press("s", 0.2)
        self.pokeMMO.controller.key_press("d", 0.2)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.my_recent_actions_list.append(("fight_skill_4_from_s21", time.time()))
        sleep(5)

    @synchronized
    def run_from_s21(self):
        self.pokeMMO.controller.click(522, 557, tolerance=15)
        sleep(2)
        print("Running from battle")

    @synchronized
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
            print("Throwing Pokeball")
            sleep(5)

    @synchronized
    def close_pokemon_summary(self, game_status):
        for i in game_status["check_battle_end_pokemon_caught"][
            1
        ]:  # [(814, 262, 936, 277)]
            exit_button_x = (i[0] + i[2]) / 2 + 103
            exit_button_y = (i[1] + i[3]) / 2 + 0
            print(exit_button_x, exit_button_y)

            self.pokeMMO.controller.click(exit_button_x, exit_button_y, tolerance=0)
            self.my_recent_actions_list.append(("close_pokemon_summary", time.time()))
            print("Closing Pokemon Summary at %s, %s" % (exit_button_x, exit_button_y))

    @synchronized
    def restart_from_hospital(self):
        self.pokeMMO.controller.key_press("8")
        sleep(4.5)

        self.pokeMMO.controller.key_press("z", 1.5)  # 护士姐姐对话

        self.pokeMMO.controller.key_press("s", 5)
        self.pokeMMO.controller.key_press("z", 1.5)  # 下水

        self.sweet_scent = 4
        self.false_swipe = 30

        print("Restarting from hospital")

    @synchronized
    def use_sweet_sent(self):
        if self.false_swipe > 0 and self.sweet_scent > 0:
            self.pokeMMO.controller.key_press("2")
            self.sweet_scent -= 1
            sleep(3)


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    # pokeMMO.start_ui()

    while True:
        round = 0
        sleep(0.5)

        while pokeMMO.get_game_status()["return_status"] < 20:
            if (
                pokeMMO.roleController.false_swipe <= 0
                and pokeMMO.roleController.sweet_scent == 0
            ):
                pokeMMO.roleController.restart_from_hospital()

            pokeMMO.roleController.use_sweet_sent()
            round = 0
            if pokeMMO.get_game_status().get("check_battle_end_pokemon_caught")[0]:
                pokeMMO.roleController.close_pokemon_summary(game_status)
                round = 0
                print(
                    "剩余:",
                    "sweet_scent",
                    pokeMMO.roleController.sweet_scent,
                    "false_swipe",
                    pokeMMO.roleController.false_swipe,
                )
                break
            pokeMMO.roleController.move_left_right(0.8)

        # start battle 有可能进医院黑屏了，有可能就是进入战斗了

        # 1 解决进入医院黑屏问题dwd

        # 进入战斗
        while True:
            # print("进入战斗")
            game_status = pokeMMO.get_game_status()
            enemy_status = pokeMMO.get_enemy_status()
            if (
                game_status["return_status"] == 21
                and enemy_status.get("enemy_1_info") is not None
            ):  # 当血量不够低的时候，就用技能1
                # print("当血量不够低的时候，就用技能1")
                if (
                    enemy_status.get("enemy_1_hp_pct") >= 8
                    and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1]) <= 10
                ) or (
                    enemy_status.get("enemy_1_hp_pct") >= 2.5
                    and int(enemy_status.get("enemy_1_name_Lv").split("Lv")[-1]) >= 10
                ):
                    round += 1
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
            elif (
                game_status["return_status"] == 21
                and enemy_status.get("enemy_count") > 1
            ):
                pokeMMO.roleController.run_from_s21()
            if game_status["return_status"] == 1:
                # print(game_status["black_ratio"])
                print(
                    "剩余:",
                    "sweet_scent",
                    pokeMMO.roleController.sweet_scent,
                    "false_swipe",
                    pokeMMO.roleController.false_swipe,
                )
                break

            sleep(0.1)
