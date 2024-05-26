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
        self.p = pokeMMO
        self.my_recent_actions_list = deque(maxlen=1000)
        self.press_down_count = 5
        self.action_lock = threading.Lock()
        self.first_sprit_hp = 100
        self.skill_pp_dict = {
            "点到为止": 0,
            "甜甜香气": 0,
            "蘑菇孢子": 0,
            "黑夜魔影": 0,
            "skill_4": 0,
            "替身": 0,
            "借助": 0,
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

        self.p.controller.key_press(keys[0], delay + random.uniform(0, delay))
        self.p.controller.key_press(keys[1], delay + random.uniform(0, delay))
        total_delay = random.uniform(0, 0.5)
        sleep(total_delay)
        self.my_recent_actions_list.append(("move_left_right", time.time()))

    @synchronized
    def fight_skill_1_from_s21(self):  # False Swipe
        sleep(0.15)
        self.p.controller.click(314, 508, tolerance=5)
        sleep(0.17)
        self.p.controller.click(312, 507, tolerance=5)
        self.my_recent_actions_list.append(("fight_skill_1_from_s21", time.time()))
        self.skill_pp_dict["点到为止"] = self.skill_pp_dict["点到为止"] - 1
        sleep(5)
        print("Using False Swipe")

    @synchronized
    def multi_fight_skill_1_from_s21(self):  # 地震
        self.p.controller.click(314, 508, tolerance=0)
        self.p.controller.key_press("z", 0.2)
        self.p.controller.key_press("z", 0.2)
        self.my_recent_actions_list.append(
            ("multi_fight_skill_1_from_s21", time.time())
        )
        sleep(5)
        print("Using Earthquake")

    @synchronized
    def fight_skill_2_from_s21(self, skill="蘑菇孢子"):  # Spore
        sleep(0.15)
        self.p.controller.click(314, 508, tolerance=10)
        sleep(0.17)
        self.p.controller.click(526, 508, tolerance=10)
        self.my_recent_actions_list.append(("fight_skill_2_from_s21", time.time()))
        if skill == "蘑菇孢子":
            self.skill_pp_dict["蘑菇孢子"] = self.skill_pp_dict["蘑菇孢子"] - 1
        elif skill == "借助":
            self.skill_pp_dict["借助"] = self.skill_pp_dict["借助"] - 1
        sleep(5)
        print("Using Spore")

    @synchronized
    def fight_skill_3_from_s21(self):
        sleep(0.15)
        self.p.controller.click(314, 508, tolerance=10)
        sleep(0.17)
        self.p.controller.click(312, 561, tolerance=10)
        self.my_recent_actions_list.append(("fight_skill_3_from_s21", time.time()))
        self.skill_pp_dict["黑夜魔影"] = self.skill_pp_dict["黑夜魔影"] - 1
        sleep(5)

    @synchronized
    def fight_skill_4_from_s21(self):
        sleep(0.15)
        self.p.controller.click(314, 508, tolerance=10)
        sleep(0.17)
        self.p.controller.click(528, 558, tolerance=10)
        self.my_recent_actions_list.append(("fight_skill_4_from_s21", time.time()))
        self.skill_pp_dict["skill_4"] = self.skill_pp_dict["skill_4"] - 1
        sleep(5)

    @synchronized
    def fight_skill_替身_from_s21(self):
        sleep(0.15)
        self.p.controller.click(314, 508, tolerance=10)
        sleep(0.17)
        self.p.controller.click(528, 558, tolerance=10)
        self.my_recent_actions_list.append(("fight_skill_替身_from_s21", time.time()))
        self.skill_pp_dict["替身"] = self.skill_pp_dict["替身"] - 1
        sleep(5)

    @synchronized
    def run_from_s21(self):
        sleep(0.15)
        self.p.controller.click(522, 557, tolerance=15)
        sleep(4)
        print("Running from battle")

    @synchronized
    def throw_pokeball(self, pokeball_type="poke_ball"):
        sleep(0.2)
        self.p.controller.click(527, 506, tolerance=15)  # 点击背包
        sleep(0.3)
        attr_name = f"{pokeball_type}_BRG"
        temp_BRG = getattr(self.p, attr_name, None)
        if (
            len(
                self.p.find_items(
                    temp_BRG=temp_BRG,
                    top_l=(516, 372),
                    bottom_r=(574, 480),
                    max_matches=1,
                    threshold=0.99,
                )
            )
            > 0
        ):
            print("扔球")
            self.p.controller.key_press("z", 1)
            self.p.db.insert_ball_throw_data(pokeball_type)
            print(f"Throwing {pokeball_type}")
            sleep(3)
        else:
            bag_arrow_page = self.p.find_items(
                temp_BRG=self.p.bag_arrow_page_BRG,
                top_l=(426, 336),
                threshold=0.99,
                bottom_r=(527, 510),
                display=False,
                max_matches=1,
            )
            if len(bag_arrow_page) > 0:
                for i in range(3):
                    self.p.controller.key_press("d", wait=0.2)
                self.p.controller.key_press("a")

                # 寻找指定的球
                for i in range(15):
                    ball_type_pic = self.p.find_items(
                        temp_BRG=temp_BRG,
                        top_l=(516, 372),
                        bottom_r=(574, 480),
                        max_matches=1,
                        threshold=0.99,
                    )
                    if len(ball_type_pic) == 0:
                        print("按s")
                        self.p.controller.key_press("s", wait=0.2)
                        continue
                    elif len(ball_type_pic) == 1:
                        print("扔球")
                        self.p.controller.key_press("z", wait=5)  # 扔球
                        self.p.db.insert_ball_throw_data(pokeball_type)
                        sleep(3)
                        break
                    raise Exception("找不到球")
            else:
                raise Exception("找不翻页按钮")

    @synchronized
    def close_pokemon_summary(self, game_status):
        coords_list = game_status["check_pokemon_summary"][1]
        for i in coords_list:  # [(814, 262, 936, 277)]
            exit_button_x = (i[0] + i[2]) / 2 + 17
            exit_button_y = (i[1] + i[3]) / 2 - 2
            print(exit_button_x, exit_button_y)
            self.p.controller.click(exit_button_x, exit_button_y, tolerance=0)
            sleep(0.1)
            self.my_recent_actions_list.append(("close_pokemon_summary", time.time()))
            print("Closing Pokemon Summary at %s, %s" % (exit_button_x, exit_button_y))

    @synchronized
    def click_pokemon_summary_IV(self, game_status):
        sleep(0.3)  # 看到这个东西之后要等一会儿，不然像是空按
        coords = game_status["check_pokemon_summary"][1][0]
        iv_icon_x = (coords[0] + coords[2]) / 2 - 386
        iv_icon_y = (coords[1] + coords[3]) / 2 + 3
        print(iv_icon_x, iv_icon_y)
        self.p.controller.click(iv_icon_x, iv_icon_y, tolerance=0)
        print("Clicking Pokemon Summary IV at %s, %s" % (iv_icon_x, iv_icon_y))

    def iv_shiny_check_release(self, game_status, release=True):
        def check_shiny():
            # ... 这里是检查Shiny的代码
            shiny_x_y_list = self.p.find_items(
                temp_BRG=self.p.shiny_BRG,
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
                self.p.ac.close_pokemon_summary(game_status)
            return len(shiny_x_y_list) >= 1

        def check_secret_shiny():
            # ... 这里是检查Secret Shiny的代码
            secret_shiny_x_y_list = self.p.find_items(
                temp_BRG=self.p.secret_shiny_BRG,
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
                self.p.ac.close_pokemon_summary(game_status)

            return len(secret_shiny_x_y_list) >= 1

        def check_iv_31():
            # ... 这里是检查IV 31的代码
            # Compute IV area coordinates.
            iv_area_top_l = (
                pokemon_summary_sign_mid_x - 356,
                pokemon_summary_sign_mid_y + 20,
            )
            iv_area_bottom_r = (
                pokemon_summary_sign_mid_x - 313,
                pokemon_summary_sign_mid_y + 216,
            )  # Round down

            iv_31_x_y_list = self.p.find_items(
                temp_BRG=self.p.iv_31_BRG,
                threshold=0.95,
                max_matches=10,
                top_l=iv_area_top_l,
                bottom_r=iv_area_bottom_r,
                img_BRG=img_BRG,
                display=False,
            )
            print("IV 31 List:", iv_31_x_y_list)
            if len(iv_31_x_y_list) >= 1:
                self.p.db.insert_31_iv_data()
                return True
            else:
                return False

        def check_in_iv_page():
            iv_icon_top_l = (
                pokemon_summary_sign_mid_x - 400,
                pokemon_summary_sign_mid_y - 15,
            )
            iv_icon_bottom_r = (
                pokemon_summary_sign_mid_x - 263,
                pokemon_summary_sign_mid_y + 15,
            )  # Round down
            iv_page_list = self.p.find_items(
                temp_BRG=self.p.sprite_iv_page_BRG,
                top_l=iv_icon_top_l,
                threshold=0.97,
                bottom_r=iv_icon_bottom_r,
                display=False,
                max_matches=1,
            )
            result = len(iv_page_list) >= 1
            if not result:
                print("Not in IV page!")
            return len(iv_page_list) >= 1

        if game_status["check_pokemon_summary"][0]:
            self.click_pokemon_summary_IV(game_status)
            coords = game_status["check_pokemon_summary"][1][0]

            # Compute common coordinates.
            pokemon_summary_sign_mid_x = int((coords[0] + coords[2]) / 2)
            pokemon_summary_sign_mid_y = int((coords[1] + coords[3]) / 2)
            shiny_area_top_l = (
                pokemon_summary_sign_mid_x,
                pokemon_summary_sign_mid_y + 40,
            )
            shiny_area_bottom_r = (
                pokemon_summary_sign_mid_x + 33,
                pokemon_summary_sign_mid_y + 152,
            )  # Round down
            sleep(0.5)  # should be 0.5
            img_BRG = self.p.get_img_BRG()
            with ThreadPoolExecutor(max_workers=4) as executor:
                shiny_future = executor.submit(check_shiny)
                secret_shiny_future = executor.submit(check_secret_shiny)
                iv_31_future = executor.submit(check_iv_31)
                in_iv_page_future = executor.submit(
                    check_in_iv_page
                )  # 用于判断是否在IV页面

            is_shiny = shiny_future.result()
            is_secret_shiny = secret_shiny_future.result()
            is_iv31 = iv_31_future.result()
            is_in_iv_page = in_iv_page_future.result()

            print("is_in_iv_page", is_in_iv_page == True)
            if (
                not (is_shiny or is_secret_shiny or is_iv31)
                and is_in_iv_page == True
                and release == True
            ):
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
                    pokemon_summary_sign_mid_x - 260,
                    pokemon_summary_sign_mid_y + 3,
                )  # Round up
                self.p.controller.click(*pc_release_icon_coords)
                sleep(0.1)

                confirm_release_area_top_l = (364, 266)  # Round up
                confirm_release_area_bottom_r = (1025, 557)  # Round up

                confirm_release_x_y_list = self.p.find_items(
                    temp_BRG=self.p.confirm_release_BRG,
                    threshold=0.99,
                    top_l=confirm_release_area_top_l,
                    bottom_r=confirm_release_area_bottom_r,
                    max_matches=1,
                    display=False,
                )

                if len(confirm_release_x_y_list) == 1:
                    # Click the first two elements of the tuple (x and y coords).
                    self.p.controller.click_center(confirm_release_x_y_list[0])
                    sleep(0.4)  # 太快破电脑受不了
                    self.p.controller.click(683, 367)
                    self.p.db.insert_release_data(release=True)

                else:
                    self.p.ac.close_pokemon_summary(game_status)
                    self.p.db.insert_release_data(release=False)

            else:
                self.p.ac.close_pokemon_summary(game_status)
                self.p.db.insert_release_data(release=False)

    @synchronized
    def restart_from_hospital(self):
        self.p.controller.key_press("8")
        sleep(4.5)
        self.p.controller.key_press("z", 1.5)  # 护士姐姐对话
        self.p.controller.key_press("s", 5)
        self.p.controller.key_press("z", 1.5)  # 下水
        print("Restarting from hospital")

    @synchronized
    def use_sweet_sent(self):
        print("使用 甜甜香气")
        if self.skill_pp_dict["甜甜香气"] >= 5:
            self.p.controller.key_press("2")
            self.skill_pp_dict["甜甜香气"] = self.skill_pp_dict["甜甜香气"] - 5
            sleep(5)  # 其实应该加个判断，看有没有成功

    def fly_to_city(self, city="SOOTOPOLIS_CITY", locate_teleport=False):
        self.p.controller.key_press("7")
        sleep(0.2)
        with self.p.coords_lock:
            self.p.coords_status["transport"] = (
                "walk"  # 飞了之后会变成走路,骑自行车之后也会走路
            )
        for i in range(2):
            self.p.controller.click(
                city_info[city]["town_map_coords"][0],
                city_info[city]["town_map_coords"][1],
                tolerance=0,
            )
            sleep(0.05)

        sleep(5)
        # check if in right city
        print("Checking if in %s" % city)
        coords_status = self.p.get_coords()
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
                self.p.controller.key_press("w", 1)  # 进pc
                sleep(2)
                print("going to find nurse")
                self.p.pf.go_to_nurse(city=city)
                self.talk_to_nurse(city=city)
                return True
            else:
                print(
                    coords_status["x_coords"],
                    coords_status["y_coords"],
                    city_info[city]["112"][0],
                    city_info[city]["112"][1],
                )
                raise Exception("Not in front of hospital")

    @synchronized
    def talk_to_nurse(self, city):
        print("Talking to nurse")
        if city_info[city]["area"] in ["Hoenn", "Kanto"]:
            press_delay = 5
        else:
            press_delay = 10
        self.p.controller.key_press("z", press_delay)  # 合众 比较久
        self.rest_pp_health()
        return True  #!现在没办法鉴别有没有成功

    @synchronized
    def use_bike(self):
        print("使用自行车")
        self.p.controller.key_press("3", 1)
        with self.p.coords_lock:
            self.p.coords_status["transport"] = "bike"

        return True

    @synchronized
    def use_surf(self):
        """
        如何判断是否在水里？
        冲浪前后的坐标不一样!
        """
        print("使用冲浪")
        start_coords = self.p.get_coords().copy()
        print("start_coords", start_coords)
        self.p.controller.key_press("z", 5)

        end_coords = self.p.get_coords().copy()
        print("end_coords", end_coords)
        if start_coords == end_coords:
            print(
                (start_coords["x_coords"], start_coords["y_coords"]),
                (end_coords["x_coords"], end_coords["y_coords"]),
            )
            raise Exception("Not in water")
        else:
            with self.p.coords_lock:
                self.p.coords_status["transport"] = "surf"
            return True

    @synchronized
    def use_cut(self):
        print("使用cut")
        self.p.controller.key_press("z", 5)

    @synchronized
    def use_teleport(self):
        print("使用传送")
        coords_status = self.p.get_coords()

        if coords_status["map_number_tuple"][2] == 50 or coords_status[
            "map_number_tuple"
        ] in [
            (1, 14, 76),
            (2, 1, 81),
            (0, 3, 3),
            (0, 23, 3),
            (0, 33, 3),
            (2, 1, 99),
            (2, 1, 109),
            (2, 1, 112),
            (2, 1, 113),
            (2, 1, 61),
            (2, 1, 141),
        ]:
            self.p.controller.key_press("8")
            with self.p.coords_lock:
                self.p.coords_status["transport"] = "walk"
            sleep(5)
        else:
            raise Exception("不在open air")
        coords_status = self.p.get_coords()
        if coords_status["map_number_tuple"][2] != 50:
            return True
        else:
            raise Exception("Not in building,还没做完")

    @synchronized
    def use_dig(self):
        print("使用挖洞")
        coords_status = self.p.get_coords()
        if coords_status["map_number_tuple"][2] == 74:
            self.p.controller.key_press("9")
            with self.p.coords_lock:
                self.p.coords_status["transport"] = "unkown"
            sleep(5)
        if self.p.get_coords()["map_number_tuple"][2] != 74:
            return True
        else:
            raise Exception("Not in building,还没做完")

    def rest_pp_health(self):
        self.skill_pp_dict = {
            "点到为止": 48,
            "甜甜香气": 32,
            "蘑菇孢子": 24,
            "黑夜魔影": 18,
            "skill_4": 12,
            "替身": 16,
            "借助": 32,
        }
        self.first_sprit_hp = 100

    def is_go_pc(self, ignore_hp=False):
        """判断是否需要回城补给"""
        if self.skill_pp_dict["点到为止"] < 5:
            print("点到为止 用完，回家")
            return True
        elif self.skill_pp_dict["蘑菇孢子"] < 1:
            print("蘑菇孢子 用完，回家")
            return True
        elif self.skill_pp_dict["skill_4"] < 1:
            print("skill_4 用完，回家")
            return True
        elif self.skill_pp_dict["黑夜魔影"] < 1:
            print("黑夜魔影 用完，回家")
            return True
        elif self.first_sprit_hp <= 30 and not ignore_hp:
            print("精灵血量过低，回家")
            return True
        elif self.skill_pp_dict["替身"] < 1:
            print("替身 用完，回家")
            return True
        elif self.skill_pp_dict["借助"] < 1:
            print("借助 用完，回家")
            return True


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    sleep(2)
    while True:
        game_status = pokeMMO.get_gs()
        pokeMMO.ac.iv_shiny_check_release(game_status)
        sleep(5)
