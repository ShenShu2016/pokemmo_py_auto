from __future__ import annotations

import copy
import os
import time
from collections import deque
from typing import TYPE_CHECKING

import cv2

from constant import target_words_dict

if TYPE_CHECKING:
    from main import PokeMMO


class GameStatus:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.recent_status_game_status_dict_list = deque(maxlen=200)
        self.recent_images = deque(maxlen=5)
        self.last_image_save_time = 0
        self.img_BRG = None
        self.memory_battle_status = {}
        self.memory_coords_status = {}
        self.memory_my_sprits_status = {}
        self.game_status_dict = {}

    def determine_game_status(self):
        def check_not_active_status():
            if self.game_status_dict.get("important") == 404:
                return set_and_return_status(404)  # Not Active Game Status

        def check_battle_option_status():
            if self.game_status_dict.get("battle_option_ORC") == True:
                return set_and_return_status(21)  # Battle Option Status

        def check_battle_go_back_status():
            if self.game_status_dict.get("battle_option_go_back_ORC") == True:
                return set_and_return_status(22)  # Battle Go Back Status

        def set_and_return_status(status):
            self.game_status_dict["real_status"] = status
            return status

        status_check_funcs = [
            check_not_active_status,
            check_normal_status,
            check_battle_option_status,
            check_battle_go_back_status,
            check_battle_loading_status,
            check_battle_end_pokemon_caught_status,
        ]

        for check_func in status_check_funcs:
            status = check_func()
            if status:
                return status

        return check_recent_status_or_return_unknown()

    def save_screenshot_check_status(self):  #! later need to be multi-thread
        if time.time() - self.last_image_save_time >= 15:
            print("Saving screenshot")
            self.last_image_save_time = time.time()
            gray_image = cv2.cvtColor(self.img_BRG, cv2.COLOR_BGR2GRAY)

            timestamp_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            folder_path = "screenshot"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            filename = os.path.join(folder_path, f"image_{timestamp_str}.png")
            cv2.imwrite(filename, gray_image)

            if self.recent_images:
                _, last_filename, _ = self.recent_images[-1]
                last_image = cv2.imread(last_filename, cv2.IMREAD_GRAYSCALE)

                result = cv2.matchTemplate(last_image, gray_image, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                self.game_status_dict["image_match_ratio"] = round(max_val, 2)
                self.recent_images.append((time.time(), filename, max_val))

                if all(
                    image_data[2] is not None and image_data[2] >= 0.2
                    for image_data in self.recent_images
                ):
                    self.game_status_dict["important"] = "404"
            else:
                self.recent_images.append((time.time(), filename, None))

    def check_battle(self):
        def check_battle_option():
            battle_option_x_y = (229, 507), (399, 522)  # select your attack move
            battle_option_ORC = self.pokeMMO.get_text_from_box_coords(
                battle_option_x_y[0], battle_option_x_y[1], img_BRG=self.img_BRG
            )
            is_match, match_ratio = self.pokeMMO.word_recognizer.compare_with_target(
                battle_option_ORC, target_words_dict["battle_option_ORC"]
            )
            self.game_status_dict["battle_option_ORC"] = is_match
            return is_match

        def check_battle_go_back():
            battle_option_go_back_x_y = (1080, 558), (1142, 575)
            battle_option_go_back_ORC = self.pokeMMO.get_text_from_box_coords(
                battle_option_go_back_x_y[0],
                battle_option_go_back_x_y[1],
                config="--psm 7",
                img_BRG=self.img_BRG,
            )
            is_match, match_ratio = self.pokeMMO.word_recognizer.compare_with_target(
                battle_option_go_back_ORC,
                target_words_dict["battle_option_go_back_ORC"],
            )
            self.game_status_dict["battle_option_go_back_ORC"] = is_match
            return is_match

    def check_battle_end_pokemon_caught(self):
        # print("check_battle_end_pokemon_caught")
        pokemon_summary_coords_list = self.pokeMMO.find_items(
            img_BRG=self.img_BRG,
            bottom_r=(1360, 487),  # ,(479, 12)
            top_l=(316, 7),
            temp_BRG=self.pokeMMO.pokemon_summary_BRG,  # self.pokeMMO.Pokemon_Summary_Exit_Button_BRG,
            threshold=0.99,
            max_matches=2,
        )
        return (len(pokemon_summary_coords_list) > 0, pokemon_summary_coords_list)

    def check_game_status(self):
        self.game_status_dict = {
            "return_status": 0,
            "check_battle_end_pokemon_caught": (
                False,
                [],
            ),  # 可以这样，多线程，每个操作都是不同线程然后用个lock就行了
            "x_coords": None,
            "y_coords": None,
            "map_number_tuple": None,
            "face_dir": None,
            "transport": None,
            "battle_time_passed": 0,
        }
        return_status = 0

        self.img_BRG = self.pokeMMO.get_latest_img_BRG()
        self.memory_coords_status = self.pokeMMO.get_memory_coords_status()
        self.memory_battle_status = self.pokeMMO.get_memory_battle_status()
        self.memory_my_sprits_status = self.pokeMMO.get_memory_my_sprits_status()
        # print("memory_battle_status", self.memory_battle_status)
        # print("memory_coords_status", self.memory_coords_status)
        current_time = time.time()

        if self.memory_battle_status.get("battle_instance_address") in [None, 0]:
            return_status = 1
        elif self.memory_battle_status.get("battle_option_ready") == 1:
            return_status = 20
        elif self.memory_battle_status.get("battle_option_ready") == 0:
            return_status = 21
        else:
            print(
                self.memory_battle_status.get("battle_instance_address"),
                self.memory_battle_status.get("battle_option_ready"),
                self.memory_battle_status.get("battle_option_ready"),
            )
        new_sprite_dict = {
            "Sweet Scent": {"pp": 0, "sprite": None},
            "False Swipe": {"pp": 0, "sprite": None},
        }

        try:
            for key in self.memory_my_sprits_status:
                for skill_key in ["skill_0", "skill_1", "skill_2", "skill_3"]:
                    if self.memory_my_sprits_status[key][skill_key]["id"] == 206:
                        new_sprite_dict["False Swipe"] = {
                            "pp": self.memory_my_sprits_status[key][skill_key]["pp"],
                            "sprite": key,
                        }
                    elif self.memory_my_sprits_status[key][skill_key]["id"] == 230:
                        new_sprite_dict["Sweet Scent"] = {
                            "pp": self.memory_my_sprits_status[key][skill_key]["pp"],
                            "sprite": key,
                        }

        except:
            pass

        self.game_status_dict = {
            "return_status": return_status,
            "check_battle_end_pokemon_caught": self.check_battle_end_pokemon_caught(),  # 可以这样，多线程，每个操作都是不同线程然后用个lock就行了
            "x_coords": self.memory_coords_status.get("x_coords"),
            "y_coords": self.memory_coords_status.get("y_coords"),
            "map_number_tuple": self.memory_coords_status.get("map_number"),
            "face_dir": self.memory_coords_status.get("face_dir"),
            "transport": self.memory_coords_status.get("transport"),
            "battle_time_passed": self.memory_battle_status.get("battle_time_passed"),
            "sprite_dict": new_sprite_dict,
        }

        self.recent_status_game_status_dict_list.append(
            (current_time, copy.deepcopy(self.game_status_dict))
        )

        return self.game_status_dict


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
