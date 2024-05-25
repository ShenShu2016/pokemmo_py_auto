from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class GameStatus:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.p = pokeMMO_instance
        self.recent_status_game_status_dict_list = deque(maxlen=200)
        self.recent_images = deque(maxlen=5)
        self.last_image_save_time = 0
        self.img_BRG = None
        self.game_status_dict = {}
        self.skill_pp_dict = {}

    def is_battle_in_progress(self):
        battle_in_progress_coords_list = self.p.find_items(
            img_BRG=self.img_BRG,
            top_l=(726, 581),
            bottom_r=(797, 591),
            temp_BRG=self.p.battle_in_progress_BRG,
            threshold=0.99,
            max_matches=5,
        )
        return len(battle_in_progress_coords_list) > 0

    def is_battle_option_ready(self):
        battle_option_ready_coords_list = self.p.find_items(
            img_BRG=self.img_BRG,
            top_l=(504, 488),
            bottom_r=(547, 508),
            temp_BRG=self.p.battle_option_BRG,
            threshold=0.99,
            max_matches=5,
        )
        return len(battle_option_ready_coords_list) > 0

    def check_pokemon_summary(self):
        # print("check_battle_end_pokemon_caught")
        pokemon_summary_coords_list = self.p.find_items(
            img_BRG=self.img_BRG,
            bottom_r=(1360, 487),  # ,(479, 12)
            top_l=(316, 7),
            temp_BRG=self.p.pokemon_summary_BRG,  # self.p.Pokemon_Summary_Exit_Button_BRG,
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
        }
        return_status = 0

        self.img_BRG = self.p.get_img_BRG()
        self.skill_pp_dict = self.p.ac.skill_pp_dict.copy()

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
            "skill_pp": self.skill_pp_dict,
        }

        return self.game_status_dict


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
