from __future__ import annotations

import copy
import time
from collections import deque
from typing import TYPE_CHECKING

import cv2
import numpy as np

from constant import target_words_dict

if TYPE_CHECKING:
    from main import PokeMMO


class GameStatus:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.recent_status_game_status_dict_list = deque(maxlen=100)
        self.recent_images = deque(maxlen=5)
        self.last_image_save_time = 0
        self.game_status_dict = {
            "real_status": "Unknown Game Status",
        }
        self.enemy_status_dict = {
            "enemy_count": 0,
        }

    def calculate_black_ratio(self):
        """Calculate the ratio of black area in the image."""
        # Get the current image
        image_BRG = self.pokeMMO.get_most_recent_image_BRG()

        # Define the value for black pixels in RGB
        black_value = [0, 0, 0]

        # Count the number of black pixels
        black_pixels = np.sum(np.all(image_BRG == black_value, axis=-1))

        # Get the total number of pixels in the image
        total_pixels = image_BRG.shape[0] * image_BRG.shape[1]

        # Calculate and return the ratio of black pixels
        black_ratio = black_pixels / total_pixels
        self.game_status_dict["black_ratio"] = black_ratio
        return black_ratio

    def determine_game_status(self):
        status_check_funcs = [
            self.check_not_active_status,
            self.check_normal_status,
            self.check_battle_option_status,
            self.check_battle_go_back_status,
            self.check_battle_loading_status,
        ]

        for check_func in status_check_funcs:
            status = check_func()
            if status:
                return status

        return self.check_recent_status_or_return_unknown()

    def check_not_active_status(self):
        if self.game_status_dict.get("important") == "not active":
            return self.set_and_return_status(("not_active," "Not Active Game Status"))

    def check_normal_status(self):
        if self.game_status_dict.get("check_normal")[0]:
            return self.set_and_return_status(("normal", "Normal Game Status"))

    def check_battle_option_status(self):
        if self.game_status_dict.get("battle_option_ORC") == True:
            return self.set_and_return_status(("battle", "Battle Option Status"))

    def check_battle_go_back_status(self):
        if self.game_status_dict.get("battle_option_go_back_ORC") == True:
            return self.set_and_return_status(("battle", "Battle Go Back Status"))

    def check_battle_loading_status(self):
        if (
            self.game_status_dict.get("black_ratio") is not None
            and self.game_status_dict.get("black_ratio") > 0.65
        ):
            return self.set_and_return_status(("battle", "Battle Loading Status"))

    def set_and_return_status(self, status):
        self.game_status_dict["real_status"] = status
        return status

    def check_recent_status_or_return_unknown(self):
        timestamp = time.time()
        self.game_status_dict["real_status"] = ("unknown", "Unknown Game Status")

        if self.recent_status_game_status_dict_list:
            for recent_timestamp, recent_status_dict in reversed(
                self.recent_status_game_status_dict_list
            ):
                recent_status = recent_status_dict.get("real_status")
                if recent_status[0] != "unknown" and timestamp - recent_timestamp <= 10:
                    return recent_status

        return ("unknown", "Unknown Game Status")

    def save_screenshot_check_status(self):
        if time.time() - self.last_image_save_time >= 15:
            print("Saving screenshot")
            self.last_image_save_time = time.time()
            image = self.pokeMMO.get_most_recent_image_BRG()
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            timestamp_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            filename = f"screenshot\image_{timestamp_str}.png"
            cv2.imwrite(filename, gray_image)

            if self.recent_images:
                _, last_filename, _ = self.recent_images[-1]
                last_image = cv2.imread(last_filename, cv2.IMREAD_GRAYSCALE)

                result = cv2.matchTemplate(last_image, gray_image, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                self.game_status_dict["image_match_ratio"] = max_val
                self.recent_images.append((time.time(), filename, max_val))

                if all(
                    image_data[2] is not None and image_data[2] >= 0.2
                    for image_data in self.recent_images
                ):
                    self.game_status_dict["important"] = "not active"
            else:
                self.recent_images.append((time.time(), filename, None))

    def check_normal(self):
        my_name_ORC = self.pokeMMO.get_text_from_center(
            box_width=125, box_height=25, offset_x=0, offset_y=104, config="--psm 7"
        )
        is_match, match_ratio = self.pokeMMO.word_recognizer.compare_with_target(
            my_name_ORC,
            target_words=target_words_dict["my_name_ORC"],
            threshold=30,
        )
        self.game_status_dict["check_normal"] = (is_match, match_ratio)
        return is_match

    def check_battle(self):
        black_ratio = self.calculate_black_ratio()
        self.game_status_dict["black_ratio"] = black_ratio
        if black_ratio > 0.35:
            if not self.check_battle_option():
                self.check_battle_go_back()

    def check_battle_option(self):
        battle_option_x_y = (214, 482), (627, 583)
        battle_option_ORC = self.pokeMMO.get_text_from_box_coordinate(
            battle_option_x_y[0], battle_option_x_y[1]
        )
        is_match, match_ratio = self.pokeMMO.word_recognizer.compare_with_target(
            battle_option_ORC, target_words_dict["battle_option_ORC"]
        )
        self.game_status_dict["battle_option_ORC"] = is_match
        return is_match

    def check_battle_go_back(self):
        battle_option_go_back_x_y = (1080, 558), (1142, 575)
        battle_option_go_back_ORC = self.pokeMMO.get_text_from_box_coordinate(
            battle_option_go_back_x_y[0], battle_option_go_back_x_y[1]
        )
        is_match, match_ratio = self.pokeMMO.word_recognizer.compare_with_target(
            battle_option_go_back_ORC,
            target_words_dict["battle_option_go_back_ORC"],
        )
        self.game_status_dict["battle_option_go_back_ORC"] = is_match
        return is_match

    def check_enemy(self):
        current_time = time.time()
        # 情况1：战斗开始，敌人数量未知 多次，直到得到敌人数量
        if self.game_status_dict["return_status"][0] == "normal":
            self.enemy_status_dict["enemy_count"] = 0
            return
        if (self.game_status_dict["return_status"][0] == "battle") and (
            self.enemy_status_dict["enemy_count"] == 0
        ):
            hp_BRG_x_y_list = self.pokeMMO.find_items(
                temp_BRG=self.pokeMMO.hp_BRG,
                threshold=0.99,
                max_matches=5,
                top_left=(0, 70),
                bottom_right=(1080, 170),
            )
            print(f"hp_BRG_x_y_list: {hp_BRG_x_y_list}")
            if not hp_BRG_x_y_list:
                self.enemy_status_dict["enemy_count"] = 0
                print("No HP bars found.")
                return

            # Coordinates for enemy HP bars
            enemy_hp_coords = [
                [(329, 97), (346, 110)],  # 1st enemy
                [(589, 97), (606, 110)],  # 2nd enemy
                [(849, 97), (866, 110)],  # 3rd enemy
                [(329, 137), (345, 150)],  # 4th enemy
                [(849, 137), (865, 150)],  # 5th enemy
            ]

            # Special cases
            special_cases = [
                {"coords": [(254, 78), (268, 89)], "enemy_count": 1},
                {"coords": [(329, 137), (345, 150)], "enemy_count": 5},
                {"coords": [(849, 137), (865, 150)], "enemy_count": 5},
            ]

            tolerance = 10  # Define a suitable tolerance value
            enemy_count = 0

            for special_case in special_cases:
                for found_hp in hp_BRG_x_y_list:
                    if (
                        special_case["coords"][0][0] - tolerance
                        <= found_hp[0]
                        <= special_case["coords"][0][0] + tolerance
                        and special_case["coords"][0][1] - tolerance
                        <= found_hp[1]
                        <= special_case["coords"][0][1] + tolerance
                        and special_case["coords"][1][0] - tolerance
                        <= found_hp[2]
                        <= special_case["coords"][1][0] + tolerance
                        and special_case["coords"][1][1] - tolerance
                        <= found_hp[3]
                        <= special_case["coords"][1][1] + tolerance
                    ):
                        self.enemy_status_dict["enemy_count"] = special_case[
                            "enemy_count"
                        ]
                        return  # Exit the function if a special case has been found

            for enemy_hp in enemy_hp_coords:
                for found_hp in hp_BRG_x_y_list:
                    # Check if the found HP bar is close enough to the expected coordinates
                    if (
                        enemy_hp[0][0] - tolerance
                        <= found_hp[0]
                        <= enemy_hp[0][0] + tolerance
                        and enemy_hp[0][1] - tolerance
                        <= found_hp[1]
                        <= enemy_hp[0][1] + tolerance
                        and enemy_hp[1][0] - tolerance
                        <= found_hp[2]
                        <= enemy_hp[1][0] + tolerance
                        and enemy_hp[1][1] - tolerance
                        <= found_hp[3]
                        <= enemy_hp[1][1] + tolerance
                    ):
                        enemy_count += 1

            # Update the game_status_dict with the number of enemies
            if enemy_count == 1:
                self.enemy_status_dict["enemy_count"] = 1
            elif enemy_count == 3:
                self.enemy_status_dict["enemy_count"] = 3
            elif enemy_count == 5:
                self.enemy_status_dict["enemy_count"] = 5
            else:
                self.enemy_status_dict["enemy_count"] = 0
        print("enemy_count:", self.enemy_status_dict["enemy_count"])

    def check_game_status(self):
        current_time = time.time()
        self.game_status_dict = {
            "real_status": ("unknown", "Unknown Game Status"),
        }

        if not self.check_normal():
            self.check_battle()

        self.save_screenshot_check_status()

        return_status = self.determine_game_status()
        self.game_status_dict["return_status"] = return_status
        self.check_enemy()
        self.recent_status_game_status_dict_list.append(
            (current_time, copy.deepcopy(self.game_status_dict))
        )
        # print the using time
        print("run time", time.time() - current_time)
        print(self.game_status_dict, end=" ")
        print(self.enemy_status_dict)
        return return_status


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    game_status = GameStatus(pokeMMO_instance=pokeMMO)
    black_ratio = game_status.calculate_black_ratio()
    print("calculate_black_ratio", black_ratio)
