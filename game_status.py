from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO
# muti-thread
import threading


class GameStatus:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.recent_status_game_status_dict_list = deque(maxlen=200)
        self.recent_images = deque(maxlen=5)
        self.last_image_save_time = 0
        self.img_BRG = None
        self.memory_coords_status = {}
        self.game_status_dict = {}
        self.skill_pp_dict = {}

    def is_battle_in_progress(self):
        battle_in_progress_coords_list = self.pokeMMO.find_items(
            img_BRG=self.img_BRG,
            top_l=(726, 581),
            bottom_r=(797, 591),
            temp_BRG=self.pokeMMO.battle_in_progress_BRG,
            threshold=0.99,
            max_matches=5,
        )
        return len(battle_in_progress_coords_list) > 0

    def is_battle_option_ready(self):
        battle_option_ready_coords_list = self.pokeMMO.find_items(
            img_BRG=self.img_BRG,
            top_l=(504, 488),
            bottom_r=(547, 508),
            temp_BRG=self.pokeMMO.battle_option_BRG,
            threshold=0.99,
            max_matches=5,
        )
        return len(battle_option_ready_coords_list) > 0

    def check_pokemon_summary(self):
        # print("check_battle_end_pokemon_caught")
        pokemon_summary_coords_list = self.pokeMMO.find_items(
            img_BRG=self.img_BRG,
            bottom_r=(1360, 487),  # ,(479, 12)
            top_l=(316, 7),
            temp_BRG=self.pokeMMO.pokemon_summary_BRG,  # self.pokeMMO.Pokemon_Summary_Exit_Button_BRG,
            threshold=0.99,
            max_matches=5,
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
            "map_number_tuple": (None, None, None),
            "face_dir": None,
            "transport": None,
        }
        return_status = 0

        self.img_BRG = self.pokeMMO.get_latest_img_BRG()
        self.memory_coords_status = self.pokeMMO.get_memory_coords_status()
        # self.check_pokemon_summary_status = self.check_pokemon_summary()
        self.skill_pp_dict = self.pokeMMO.action_controller.skill_pp_dict.copy()

        with ThreadPoolExecutor(max_workers=3) as executor:
            battle_in_progress_future = executor.submit(self.is_battle_in_progress)
            battle_option_ready_future = executor.submit(self.is_battle_option_ready)
            check_pokemon_summary_future = executor.submit(self.check_pokemon_summary)

            self.is_battle_in_progress_status = battle_in_progress_future.result()
            self.is_battle_option_ready_status = battle_option_ready_future.result()
            self.check_pokemon_summary_status = check_pokemon_summary_future.result()

        if self.is_battle_option_ready_status:
            return_status = 21
        elif self.is_battle_in_progress_status:
            return_status = 20
        else:
            return_status = 1

        self.game_status_dict = {
            "return_status": return_status,
            "check_pokemon_summary": self.check_pokemon_summary_status,  # 可以这样，多线程，每个操作都是不同线程然后用个lock就行了
            "x_coords": self.memory_coords_status.get("x_coords"),
            "y_coords": self.memory_coords_status.get("y_coords"),
            "map_number_tuple": self.memory_coords_status.get("map_number"),
            "face_dir": self.memory_coords_status.get("face_dir"),
            "transport": self.memory_coords_status.get("transport"),
            "skill_pp": self.skill_pp_dict,
        }

        return self.game_status_dict


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
