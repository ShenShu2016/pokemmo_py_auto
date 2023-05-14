from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from constant import target_words_dict

if TYPE_CHECKING:
    from main import PokeMMO


class GameStatus:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance

    def calculate_black_ratio(self):
        """Calculate the ratio of black pixels in the image."""
        image_normal = self.pokeMMO.get_most_recent_image_normal()
        height, width, _ = image_normal.shape

        total_pixels = width * height
        black_pixels = np.sum(np.all(image_normal[:, :, :3] == [0, 0, 0], axis=2))

        black_ratio = black_pixels / total_pixels
        print(f"Black ratio: {black_ratio}")

        return black_ratio

    # def check_game_status(self, threshold=0.986):
    #     # Access the PokeMMO instance and call its methods
    #     # window_name = self.pokeMMO_instance.window_name
    #     # handle = self.pokeMMO_instance.handle
    #     face_area = self.pokeMMO_instance.get_box_coordinate_from_center(
    #         box_width=65,
    #         box_height=65,
    #         offset_x=0,
    #         offset_y=65,
    #     )
    #     face_area_l = face_area[0]
    #     face_area_r = face_area[1]

    #     templates = [
    #         self.pokeMMO_instance.face_down_color,
    #         self.pokeMMO_instance.face_up_color,
    #         self.pokeMMO_instance.face_left_color,
    #         self.pokeMMO_instance.face_right_color,
    #     ]
    #     template_names = [
    #         "face_down_color",
    #         "face_up_color",
    #         "face_left_color",
    #         "face_right_color",
    #     ]

    #     for template, template_name in zip(templates, template_names):
    #         if self.pokeMMO_instance.find_items(
    #             template_color=template,
    #             threshold=threshold,
    #             max_matches=5,
    #             top_left=face_area_l,
    #             bottom_right=face_area_r,
    #         ):
    #             # print(f"{template_name} detected.")
    #             return "NORMAL"

    #     if self.pokeMMO_instance.find_items(
    #         self.pokeMMO_instance.enemy_hp_bar_color, threshold=0.99, max_matches=10
    #     ):
    #         # print("Enemy HP bar detected.")
    #         return "BATTLE"
    #     else:
    #         # print("Unknown game state.")
    #         return "OTHER"
    def check_game_status(self, threshold=0.986):
        def check_normal():
            my_name_ORC = self.pokeMMO.get_text_from_center(
                box_width=125, box_height=25, offset_x=0, offset_y=104, config="--psm 7"
            )  # Player Name and guild name
            is_match, match_ratio = self.pokeMMO.word_recognizer.compare_with_target(
                my_name_ORC, target_words=target_words_dict["my_name_ORC"], threshold=60
            )
            print(
                f"my_name_ORC: {my_name_ORC}, is_match: {is_match}, match_ratio: {match_ratio}"
            )
            return is_match, match_ratio

        def check_battle():
            pass


if __name__ == "__main__":
    pokeMMO = PokeMMO()
    game_status = GameStatus(pokeMMO_instance=pokeMMO)
    black_ratio = game_status.calculate_black_ratio()
    print("calculate_black_ratio", black_ratio)
