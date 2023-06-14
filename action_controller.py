from __future__ import annotations

import os
import random
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import TYPE_CHECKING

import cv2

if TYPE_CHECKING:
    from main import PokeMMO

import queue
import threading
from functools import wraps

from constant import city_info


def calculate_catch_rate(
    max_hp=65, current_hp=1, catch_rate=1, ball_rate=1, pokemon_condition=1
):
    numerator = (
        (3 * max_hp - 2 * current_hp) * catch_rate * ball_rate * pokemon_condition
    )
    denominator = 3 * max_hp * 255
    final_catch_rate = numerator / denominator
    return final_catch_rate


class Action_Controller:
    def __init__(self, pokeMMO: PokeMMO):
        self.pokeMMO = pokeMMO
        self.my_recent_actions_list = deque(maxlen=1000)
        self.press_down_count = 5
        self.action_lock = threading.Lock()
        self.skill_pp_dict = {
            "点到为止": 0,
            "甜甜香气": 0,
            "蘑菇孢子": 0,
            "黑夜魔影": 0,
            "skill_4": 0,
        }

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
        self.pokeMMO.controller.click(314, 508, tolerance=5)
        sleep(0.08)
        self.pokeMMO.controller.click(312, 507, tolerance=5)
        self.my_recent_actions_list.append(("fight_skill_1_from_s21", time.time()))
        self.skill_pp_dict["点到为止"] = self.skill_pp_dict["点到为止"] - 1
        sleep(5)
        print("Using False Swipe")

    @synchronized
    def multi_fight_skill_1_from_s21(self):  # 地震
        self.pokeMMO.controller.click(314, 508, tolerance=0)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.pokeMMO.controller.key_press("z", 0.2)
        self.my_recent_actions_list.append(
            ("multi_fight_skill_1_from_s21", time.time())
        )
        sleep(5)
        print("Using Earthquake")

    @synchronized
    def fight_skill_2_from_s21(self):  # Spore
        self.pokeMMO.controller.click(314, 508, tolerance=10)
        sleep(0.08)
        self.pokeMMO.controller.click(526, 508, tolerance=10)
        self.my_recent_actions_list.append(("fight_skill_2_from_s21", time.time()))
        self.skill_pp_dict["蘑菇孢子"] = self.skill_pp_dict["蘑菇孢子"] - 1
        sleep(5)
        print("Using Spore")

    @synchronized
    def fight_skill_3_from_s21(self):
        self.pokeMMO.controller.click(314, 508, tolerance=10)
        sleep(0.08)
        self.pokeMMO.controller.click(312, 561, tolerance=10)
        self.my_recent_actions_list.append(("fight_skill_3_from_s21", time.time()))
        self.skill_pp_dict["黑夜魔影"] = self.skill_pp_dict["黑夜魔影"] - 1
        sleep(5)

    @synchronized
    def fight_skill_4_from_s21(self):
        self.pokeMMO.controller.click(314, 508, tolerance=10)
        sleep(0.08)
        self.pokeMMO.controller.click(528, 558, tolerance=10)
        self.my_recent_actions_list.append(("fight_skill_4_from_s21", time.time()))
        self.skill_pp_dict["skill_4"] = self.skill_pp_dict["skill_4"] - 1
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
            self.pokeMMO.controller.key_press("z", 1)
            print("Throwing Pokeball")
            sleep(3)

    @synchronized
    def close_pokemon_summary(self, game_status):
        coords_list = game_status["check_pokemon_summary"][1]
        for i in coords_list:  # [(814, 262, 936, 277)]
            exit_button_x = (i[0] + i[2]) / 2 + 17
            exit_button_y = (i[1] + i[3]) / 2 - 2
            print(exit_button_x, exit_button_y)
            self.pokeMMO.controller.click(exit_button_x, exit_button_y, tolerance=0)
            sleep(0.1)
            self.my_recent_actions_list.append(("close_pokemon_summary", time.time()))
            print("Closing Pokemon Summary at %s, %s" % (exit_button_x, exit_button_y))

    @synchronized
    def click_pokemon_summary_IV(self, game_status):
        coords = game_status["check_pokemon_summary"][1][0]
        iv_icon_x = (coords[0] + coords[2]) / 2 - 386
        iv_icon_y = (coords[1] + coords[3]) / 2 + 3
        print(iv_icon_x, iv_icon_y)
        self.pokeMMO.controller.click(iv_icon_x, iv_icon_y, tolerance=0)
        print("Clicking Pokemon Summary IV at %s, %s" % (iv_icon_x, iv_icon_y))

    def iv_shiny_check_release(self, game_status):
        def check_shiny():
            # ... 这里是检查Shiny的代码
            shiny_x_y_list = self.pokeMMO.find_items(
                temp_BRG=self.pokeMMO.shiny_BRG,
                threshold=0.98,
                max_matches=10,
                top_l=shiny_area_top_l,
                bottom_r=shiny_area_bottom_r,
                img_BRG=img_BRG,
                display=False,
            )
            print("shiny_x_y_list", shiny_x_y_list)
            if len(shiny_x_y_list) >= 1:
                print("Shiny!")
                self.pokeMMO.action_controller.close_pokemon_summary(game_status)
            return len(shiny_x_y_list) >= 1

        def check_secret_shiny():
            # ... 这里是检查Secret Shiny的代码
            secret_shiny_x_y_list = self.pokeMMO.find_items(
                temp_BRG=self.pokeMMO.secret_shiny_BRG,
                threshold=0.99,
                max_matches=10,
                top_l=shiny_area_top_l,
                bottom_r=shiny_area_bottom_r,
                img_BRG=img_BRG,
                display=False,
            )
            print("secret_shiny_x_y_list", secret_shiny_x_y_list)
            if len(secret_shiny_x_y_list) >= 1:
                print("Secret Shiny!")
                self.pokeMMO.action_controller.close_pokemon_summary(game_status)

            return len(secret_shiny_x_y_list) >= 1

        def check_iv_31():
            # ... 这里是检查IV 31的代码
            # Compute IV area coordinates.
            iv_area_top_l = (
                close_summary_button_mid_x - 356,
                close_summary_button_mid_y + 20,
            )
            iv_area_bottom_r = (
                close_summary_button_mid_x - 313,
                close_summary_button_mid_y + 216,
            )  # Round down

            iv_31_x_y_list = self.pokeMMO.find_items(
                temp_BRG=self.pokeMMO.iv_31_BRG,
                threshold=0.95,
                max_matches=10,
                top_l=iv_area_top_l,
                bottom_r=iv_area_bottom_r,
                img_BRG=img_BRG,
                display=False,
            )
            print("IV 31 List:", iv_31_x_y_list)
            return len(iv_31_x_y_list) >= 1

        if game_status["check_pokemon_summary"][0]:
            self.click_pokemon_summary_IV(game_status)
            coords = game_status["check_pokemon_summary"][1][0]

            # Compute common coordinates.
            close_summary_button_mid_x = int((coords[0] + coords[2]) / 2)
            close_summary_button_mid_y = int((coords[1] + coords[3]) / 2)
            shiny_area_top_l = (
                close_summary_button_mid_x,
                close_summary_button_mid_y + 40,
            )
            shiny_area_bottom_r = (
                close_summary_button_mid_x + 33,
                close_summary_button_mid_y + 152,
            )  # Round down
            sleep(0.1)
            img_BRG = self.pokeMMO.get_latest_img_BRG()
            with ThreadPoolExecutor(max_workers=3) as executor:
                shiny_future = executor.submit(check_shiny)
                secret_shiny_future = executor.submit(check_secret_shiny)
                iv_31_future = executor.submit(check_iv_31)

            is_shiny = shiny_future.result()
            is_secret_shiny = secret_shiny_future.result()
            is_iv31 = iv_31_future.result()

            if not (is_shiny or is_secret_shiny or is_iv31):
                timestamp_str = time.strftime(
                    "%Y%m%d%H%M%S", time.localtime(time.time())
                )
                folder_path = "pic_sprite_released"
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                filename = os.path.join(folder_path, f"image_{timestamp_str}.png")
                cv2.imwrite(filename, img_BRG)
                print("start releasing pokemon")
                pc_release_icon_coords = (
                    close_summary_button_mid_x - 260,
                    close_summary_button_mid_y + 3,
                )  # Round up
                self.pokeMMO.controller.click(*pc_release_icon_coords)
                sleep(0.1)

                confirm_release_area_top_l = (
                    close_summary_button_mid_x - 418,
                    close_summary_button_mid_y + 143,
                )  # Round up
                confirm_release_area_bottom_r = (
                    close_summary_button_mid_x - 301,
                    close_summary_button_mid_y + 168,
                )  # Round up

                confirm_release_x_y_list = self.pokeMMO.find_items(
                    temp_BRG=self.pokeMMO.confirm_release_BRG,
                    threshold=0.99,
                    top_l=confirm_release_area_top_l,
                    bottom_r=confirm_release_area_bottom_r,
                    max_matches=1,
                    display=False,
                )

                if len(confirm_release_x_y_list) == 1:
                    # Click the first two elements of the tuple (x and y coords).
                    self.pokeMMO.controller.click(
                        confirm_release_x_y_list[0][0], confirm_release_x_y_list[0][1]
                    )
                    sleep(0.1)
                    self.pokeMMO.controller.click(679, 378)
                else:
                    self.pokeMMO.action_controller.close_pokemon_summary(game_status)

            else:
                self.pokeMMO.action_controller.close_pokemon_summary(game_status)

    @synchronized
    def restart_from_hospital(self):
        self.pokeMMO.controller.key_press("8")
        sleep(4.5)
        self.pokeMMO.controller.key_press("z", 1.5)  # 护士姐姐对话
        self.pokeMMO.controller.key_press("s", 5)
        self.pokeMMO.controller.key_press("z", 1.5)  # 下水
        print("Restarting from hospital")

    @synchronized
    def use_sweet_sent(self):
        if self.skill_pp_dict["甜甜香气"] >= 5:
            self.pokeMMO.controller.key_press("2")
            self.skill_pp_dict["甜甜香气"] = self.skill_pp_dict["甜甜香气"] - 5
            sleep(3)

    def fly_to_city(self, city="SOOTOPOLIS_CITY", locate_teleport=False):
        self.pokeMMO.controller.key_press("7")
        sleep(0.2)
        for i in range(2):
            self.pokeMMO.controller.click(
                city_info[city]["town_map_coords"][0],
                city_info[city]["town_map_coords"][1],
                tolerance=0,
            )
            sleep(0.05)

        sleep(5)
        # check if in right city
        print("Checking if in %s" % city)
        coords_status = self.pokeMMO.get_coords_status()
        if coords_status["map_number_tuple"] == city_info[city]["map_number"]:
            print(
                "Flied to %s" % city,
                f'当前坐标：{coords_status["map_number_tuple"]},应该是{city_info[city]["map_number"]}',
            )
        else:
            raise Exception("Not in %s" % city)

        if locate_teleport:
            if (coords_status["x_coords"], coords_status["y_coords"]) == (
                city_info[city]["112"][0],
                city_info[city]["112"][1],
            ):
                self.pokeMMO.controller.key_press("w", 1)
                sleep(2)
                print("going to find nurse")
                self.pokeMMO.pf.go_to_nurse(city=city)
                self.talk_to_nurse()
                return True
            else:
                raise Exception("Not in front of hospital")

    @synchronized
    def talk_to_nurse(self):
        print("Talking to nurse")
        self.pokeMMO.controller.key_press("z", 5)  # 合众 比较久
        sleep(1)

        self.skill_pp_dict = {
            "点到为止": 30,
            "甜甜香气": 32,
            "蘑菇孢子": 15,
            "黑夜魔影": 18,
            "skill_4": 12,
        }
        return True  #!现在没办法鉴别有没有成功

    @synchronized
    def use_surf(self):
        self.pokeMMO.controller.key_press("z", 1.5)

        for i in range(10):
            if self.pokeMMO.get_coords_status()["transport"] in [1, 11, 75, 65, 7]:
                return True
            sleep(0.1)

        raise Exception("Not in water")

    # @synchronized
    # def use_bike(self):
    #     game_status = self.pokeMMO.get_game_status()
    #     if game_status["map_number_tuple"][2] in [50, 76] and game_status[
    #         "transport"
    #     ] not in [
    #         1,
    #         11,
    #     ]:  # 室外
    #         self.pokeMMO.controller.key_press("3")
    #         sleep(1)
    #     if game_status["transport"] == 10:
    #         return True
    #     else:
    #         raise Exception("Not in bike,还没做完")

    @synchronized
    def use_teleport(self):
        coords_status = self.pokeMMO.get_coords_status()

        if coords_status["map_number_tuple"][2] == 50 or coords_status[
            "map_number_tuple"
        ] in [(1, 14, 76), (2, 1, 81)]:
            self.pokeMMO.controller.key_press("8")
            sleep(3)
        coords_status = self.pokeMMO.get_coords_status()
        if coords_status["map_number_tuple"][2] != 50:
            return True
        else:
            raise Exception("Not in building,还没做完")

    @synchronized
    def use_dig(self):
        coords_status = self.pokeMMO.get_coords_status()
        if coords_status["map_number_tuple"][2] == 74:
            self.pokeMMO.controller.key_press("9")
            sleep(5)
        if self.pokeMMO.get_coords_status()["map_number_tuple"][2] != 74:
            return True
        else:
            raise Exception("Not in building,还没做完")


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    pokeMMO.action_controller.talk_to_nurse()
