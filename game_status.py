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
        self.recent_status_game_status_dict_list = deque(maxlen=100)
        self.recent_images = deque(maxlen=5)
        self.last_image_save_time = 0
        self.img_BRG = None
        self.game_status_dict = {
            "real_status": 0,  # Unknown Game Status
        }

    def determine_game_status(self):
        def check_not_active_status():
            if self.game_status_dict.get("important") == 404:
                return set_and_return_status(404)  # Not Active Game Status

        def check_normal_status():
            if self.game_status_dict.get("check_normal")[0]:
                return set_and_return_status(1)  # Normal Game Status

        def check_battle_option_status():
            if self.game_status_dict.get("battle_option_ORC") == True:
                return set_and_return_status(21)  # Battle Option Status

        def check_battle_go_back_status():
            if self.game_status_dict.get("battle_option_go_back_ORC") == True:
                return set_and_return_status(22)  # Battle Go Back Status

        def check_battle_end_pokemon_caught_status():
            if (
                self.game_status_dict.get("battle_end_pokemon_caught") is not None
                and self.game_status_dict.get("battle_end_pokemon_caught")[0] == True
            ):
                return set_and_return_status(23)

        def check_battle_loading_status():
            if (
                self.game_status_dict.get("black_ratio") is not None
                and self.game_status_dict.get("black_ratio") > 0.65
            ):
                return set_and_return_status(20)  # Battle Loading Status

        def set_and_return_status(status):
            self.game_status_dict["real_status"] = status
            return status

        def check_recent_status_or_return_unknown():
            timestamp = time.time()
            self.game_status_dict["real_status"] = 0  # Unknown Game Status

            if self.recent_status_game_status_dict_list:
                for recent_timestamp, recent_status_dict in reversed(
                    self.recent_status_game_status_dict_list
                ):
                    recent_status = recent_status_dict.get("real_status")
                    if recent_status != 0 and timestamp - recent_timestamp <= 10:
                        return recent_status

            return 0  # Unknown Game Status

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

    def check_normal(self):
        my_name_x_y = (624, 270), (738, 291)
        my_name_ORC = self.pokeMMO.get_text_from_box_coords(
            top_l=my_name_x_y[0],
            bottom_r=my_name_x_y[1],
            config="--psm 7",
            img_BRG=self.img_BRG,
        )
        is_match, match_ratio = self.pokeMMO.word_recognizer.compare_with_target(
            my_name_ORC,
            target_words=target_words_dict["my_name_ORC"],
            threshold=30,
        )
        self.game_status_dict["check_normal"] = (is_match, match_ratio)
        return is_match

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

        def check_battle_end_pokemon_caught():
            pokemon_summary_coords_list = self.pokeMMO.find_items(
                img_BRG=self.img_BRG,
                bottom_r=(1360, 487),  # ,(479, 12)
                top_l=(316, 7),
                temp_BRG=self.pokeMMO.pokemon_summary_BRG,  # self.pokeMMO.Pokemon_Summary_Exit_Button_BRG,
                threshold=0.99,
                max_matches=2,
            )

            self.game_status_dict["battle_end_pokemon_caught"] = (
                len(pokemon_summary_coords_list) > 0,
                pokemon_summary_coords_list,
            )

        black_ratio = self.pokeMMO.calculate_black_ratio(img_BRG=self.img_BRG)
        self.game_status_dict["black_ratio"] = black_ratio
        if black_ratio > 0.35:
            if not check_battle_option():
                check_battle_go_back()
        if black_ratio <= 0.35:
            check_battle_end_pokemon_caught()

    def check_game_status(self) -> int:
        self.img_BRG = self.pokeMMO.get_latest_img_BRG()
        current_time = time.time()
        self.game_status_dict = {
            "real_status": 0,  # Unknown Game Status
        }

        if not self.check_normal():
            self.check_battle()

        self.save_screenshot_check_status()

        return_status = self.determine_game_status()
        self.game_status_dict["return_status"] = return_status
        self.recent_status_game_status_dict_list.append(
            (current_time, copy.deepcopy(self.game_status_dict))
        )
        print("game_status_dict", self.game_status_dict)
        return self.game_status_dict


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
