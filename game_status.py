from __future__ import annotations

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
        self.game_status_dict = {}

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
        return black_ratio

    def determine_game_status(self):
        timestamp = time.time()

        # Check if the current status is "Unknown Game Status"
        if (
            "important" in self.game_status_dict
            and self.game_status_dict["important"] == "not active"
        ):
            return "Not Active Game Status"
        if (
            "check_normal" in self.game_status_dict
            and self.game_status_dict["check_normal"] > 60
        ):
            return "Normal Game Status"

        # Check if the current status is "Unknown Game Status" and if there is a recent status change
        if (
            "return_status" in self.game_status_dict
            and self.game_status_dict["return_status"] == "Unknown Game Status"
        ):
            recent_statuses = [
                status_dict["return_status"]
                for _, status_dict in reversed(self.recent_status_game_status_dict_list)
            ]
            recent_timestamps = [
                timestamp
                for timestamp, _ in reversed(self.recent_status_game_status_dict_list)
            ]

            for recent_status, recent_timestamp in zip(
                recent_statuses, recent_timestamps
            ):
                if (
                    recent_status != "Unknown Game Status"
                    and timestamp - recent_timestamp <= 10
                ):
                    return recent_status

        # If no recent status change found, return the current status
        return self.game_status_dict["return_status"]

    def check_game_status(self):
        timestamp = time.time()

        def save_screenshot_check_status(timestamp):
            if time.time() - self.last_image_save_time >= 15:
                self.last_image_save_time = time.time()
                image = self.pokeMMO.get_most_recent_image_BRG()
                timestamp_str = time.strftime("%Y%m%d%H%M%S", time.localtime(timestamp))
                filename = f"screenshot\image_{timestamp_str}.png"
                cv2.imwrite(filename, image)

                # Compare with last image if available
                if len(self.recent_images) > 0:
                    _, last_filename, _ = self.recent_images[-1]
                    last_image = cv2.imread(last_filename, cv2.IMREAD_GRAYSCALE)
                    current_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    result = cv2.matchTemplate(
                        last_image, current_image, cv2.TM_CCOEFF_NORMED
                    )
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                    # Save the image, timestamp and match ratio to recent_images
                    self.recent_images.append((timestamp, filename, max_val))

                    # Check if all max_vals in recent_images are not below 0
                    if all(
                        image_data[2] is not None and image_data[2] >= 0
                        for image_data in self.recent_images
                    ):
                        self.game_status_dict["important"] = "not active"
                else:
                    # For the first image, no comparison can be made, so match ratio is None
                    self.recent_images.append((timestamp, filename, None))

        def check_normal():  # use name to check status
            my_name_ORC = self.pokeMMO.get_text_from_center(
                box_width=125, box_height=25, offset_x=0, offset_y=104, config="--psm 7"
            )  # Player Name and guild name
            is_match, match_ratio = self.pokeMMO.word_recognizer.compare_with_target(
                my_name_ORC, target_words=target_words_dict["my_name_ORC"], threshold=60
            )
            # print(
            #     f"my_name_ORC: {my_name_ORC}, is_match: {is_match}, match_ratio: {match_ratio}"
            # )
            self.game_status_dict["check_normal"] = match_ratio  # 这里会导致我之前给的threshold失效
            return is_match, match_ratio

        def check_battle():
            battle_status = None
            battle_black_ratio = 0.35  # 有时候天气原因导致黑色比例下降
            black_ratio = self.calculate_black_ratio()
            self.game_status_dict["black_ratio"] = black_ratio
            if black_ratio > battle_black_ratio:
                battle_option_x_y = (214, 482), (627, 583)
                battle_status = "battle_loading"
                battle_option_ORC = self.pokeMMO.get_text_from_box_coordinate(
                    battle_option_x_y[0], battle_option_x_y[1]
                )
                # print("battle_option_ORC", battle_option_ORC)
                (
                    is_match,
                    match_ratio,
                ) = self.pokeMMO.word_recognizer.compare_with_target(
                    battle_option_ORC, target_words_dict["battle_option_ORC"]
                )
                # print("battle_option_ORC", is_match, match_ratio)
                self.game_status_dict["battle_option_ORC"] = is_match

                battle_option_go_back_x_y = (1080, 558), (1142, 575)
                battle_option_go_back_ORC = self.pokeMMO.get_text_from_box_coordinate(
                    battle_option_go_back_x_y[0], battle_option_go_back_x_y[1]
                )
                # print("get_text_from_box_coordinate", battle_option_go_back_ORC)
                (
                    is_match,
                    match_ratio,
                ) = self.pokeMMO.word_recognizer.compare_with_target(
                    battle_option_go_back_ORC,
                    target_words_dict["battle_option_go_back_ORC"],
                )
                self.game_status_dict["battle_option_go_back_ORC"] = is_match
                if is_match:
                    battle_status = (
                        "battle_action_choice"  # 因为 go back 会出现在 fight bag pokemon 选项里面
                    )

            return battle_status

        check_normal()
        check_battle()
        save_screenshot_check_status(timestamp)

        print(self.game_status_dict)
        return_status = self.determine_game_status()
        self.game_status_dict["return_status"] = return_status
        self.recent_status_game_status_dict_list.append(
            (timestamp, self.game_status_dict)
        )
        return return_status


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    game_status = GameStatus(pokeMMO_instance=pokeMMO)
    black_ratio = game_status.calculate_black_ratio()
    print("calculate_black_ratio", black_ratio)
