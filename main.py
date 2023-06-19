import json
import logging
import random
import threading
import time
from datetime import datetime
from time import sleep

import cv2
import numpy as np
import pandas as pd
import pytesseract

from action_controller import Action_Controller
from auto_strategy.auto_importer import *
from enemy_status import EnemyStatus
from game_status import GameStatus
from log_print_save import LogPrintSave
from path_finder import PathFinder
from pokemmoUI import PokemmoUI
from utils.controller import Controller
from utils.memory_injection.memory_injector_coords import MemoryInjector_Coords
from utils.SQLiteDB import SQLiteDB
from utils.window_manager import Window_Manager
from utils.word_recognizer import Word_Recognizer

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PokeMMO:
    """A class to interact with the PokeMMO game."""

    def __init__(self):
        """Initialize the PokeMMO class."""
        self.window_manager = Window_Manager()
        self.handle = self.window_manager.handle
        with open("configure.json", "r") as f:
            self.config = json.load(f)

        pytesseract.pytesseract.tesseract_cmd = self.config["tesseract"]

        self.img_BRG_lock = threading.Lock()
        self.gs_lock = threading.Lock()
        self.bs_lock = threading.Lock()
        self.state_dict_lock = threading.Lock()
        self.coords_lock = threading.Lock()
        self.img_BRG = self.window_manager.get_current_img_BRG()

        self.game_status = {"return_status": 0, "skill_pp": {}}
        self.enemy_status = {}
        self.state_dict = {"address": "", "money": 0}
        self.coords_status = {
            "x_coords": 0,
            "y_coords": 0,
            "map_number_tuple": (0, 0, 0),
            "face_dir": 0,
            "transport": 0,
        }
        self.encounter_start_time = None

        self.df_dict = {}
        self.load_assets()

        self.game_status_checker = GameStatus(self)
        self.enemy_status_checker = EnemyStatus(self)

        self.controller = Controller(handle=self.handle)

        self.ac = Action_Controller(self)
        self.word_recognizer = Word_Recognizer()
        self.pf = PathFinder(self)
        self.log_print_save = LogPrintSave(self)
        self.db = SQLiteDB(
            self,
            "pokemmo.sqlite",
        )
        self.mj_coords = MemoryInjector_Coords()

        self.PETALBURG_CITY_FARMING = Farming_PETALBURG_CITY(self)
        self.SOOTOPOLIS_CITY_FARMING = Farming_SOOTOPOLIS_CITY(self)
        self.FALLARBOR_TOWN_FARMING = Farming_FALLARBOR_TOWN(self)
        self.VERDANTURF_TOWN_FARMING = Farming_VERDANTURF_TOWN(self)

        self.auto_strategy_flag = False  # 用来控制所有的自动策略 开始与结束

        self.stop_threads_flag = False
        self.ui = PokemmoUI(self)
        self.start_threads()

    def start_threads(self):
        threading.Thread(target=self.update_img_BRG).start()
        threading.Thread(target=self.update_game_status).start()
        threading.Thread(target=self.update_state_dict).start()
        threading.Thread(target=self.update_enemy_status).start()
        threading.Thread(target=self.update_memory_coords).start()
        threading.Thread(target=self.log_print_save.update_logs).start()
        threading.Thread(target=self.log_print_save.print_logs).start()

    def stop_threads(self):
        self.stop_threads_flag = True

    def load_assets(self):
        """Load images and CSV files from the configuration file."""
        asset_count = 0
        for key, path in self.config.items():
            if key.endswith("_path"):
                var_name = key.replace(
                    "_path", "_BRG" if path.endswith(".png") else "_csv"
                )
                if path.endswith(".png"):
                    setattr(self, var_name, cv2.imread(path, cv2.IMREAD_COLOR))
                elif path.endswith(".csv"):
                    setattr(self, var_name, pd.read_csv(path))
                    self.df_dict[var_name] = getattr(self, var_name)

                print(f"Loaded {var_name} from {path}")
                asset_count += 1
        logger.info(f"Loaded {asset_count} assets.")

    def start_ui(self):
        """Start the user interface."""
        self.ui.run()

    def update_img_BRG(self):  # only image will be captured
        while not self.stop_threads_flag:
            # Add the current image, timestamp, and name to the list
            start_time = time.time()
            current_img_BRG = self.window_manager.get_current_img_BRG()
            with self.img_BRG_lock:
                self.img_BRG = current_img_BRG

            time_passed = time.time() - start_time
            if time_passed >= 0.05:
                print(
                    "time to get image--------------------------------------------",
                    time_passed,
                )
            sleep(0.05)  # wait for 2 seconds

    def update_game_status(self):
        while not self.stop_threads_flag:
            new_game_state = self.game_status_checker.check_game_status()
            with self.gs_lock:
                self.game_status = new_game_state
            sleep(0.02)  # wait for 3 seconds

    def update_enemy_status(self):
        while not self.stop_threads_flag:
            new_enemy_status = self.enemy_status_checker.check_enemy_status()
            with self.bs_lock:
                self.enemy_status = new_enemy_status
            sleep(0.02)

    def update_state_dict(self):
        while not self.stop_threads_flag:
            # Update every 30 seconds
            sleep(3)
            img_BRG = self.get_img_BRG()
            my_address = self.get_text_from_box_coords(
                (30, 0), (250, 25), img_BRG=img_BRG
            )
            my_money = self.get_text_from_box_coords(
                (37, 30),
                (130, 45),
                config="--psm 6 -c tessedit_char_whitelist=0123456789",
                img_BRG=img_BRG,
            )

            with self.state_dict_lock:
                self.state_dict = {
                    "address": my_address,
                    "money": int(my_money),
                }

    def update_memory_coords(self):
        while not self.stop_threads_flag:
            new_memory_coords = self.mj_coords.read_data()
            with self.coords_lock:
                self.coords_status = new_memory_coords
            sleep(0.02)

    # Use this method to safely access the state_dict variable from other threads
    def get_state_dict(self):
        with self.state_dict_lock:
            return self.state_dict

    def get_gs(self):
        with self.gs_lock:
            return self.game_status

    def get_bs(self):
        with self.bs_lock:
            return self.enemy_status

    def get_coords(self):
        with self.coords_lock:
            return self.coords_status

    def get_img_BRG(self):
        with self.img_BRG_lock:
            return self.img_BRG

    def get_box_coordinate_from_center(
        self,
        box_width=200,
        box_height=200,
        offset_x=0,
        offset_y=0,
        display=False,
        img_BRG=None,
    ):
        """Draw a box on the image and get the text from the area inside the box."""
        if img_BRG is None:
            img_BRG = self.get_img_BRG()
        height, width, _ = img_BRG.shape
        center_x, center_y = (width // 2) + offset_x, (height // 2) - offset_y

        # Calculate the top-left and bottom-right points of the rectangle
        top_l = (center_x - box_width // 2, center_y - box_height // 2)
        bottom_r = (center_x + box_width // 2, center_y + box_height // 2)

        # Draw the rectangle on the image
        if display:
            cv2.rectangle(img_BRG, top_l, bottom_r, color=((0, 0, 255),), thickness=2)
            cv2.imshow("Match Template", img_BRG)
            cv2.waitKey()

        # Return the coordinates of the top-left and bottom-right corners
        return top_l, bottom_r

    def get_text_from_box_coords(
        self, top_l, bottom_r, config="--psm 6", lang="eng", img_BRG=None
    ):
        if img_BRG is None:
            img_BRG = self.get_img_BRG()
        # Extract the area from the image
        area = img_BRG[top_l[1] : bottom_r[1], top_l[0] : bottom_r[0]]

        # Convert the area to grayscale
        gray = cv2.cvtColor(area, cv2.COLOR_BGRA2GRAY)
        # Recognize the text in the area
        text = pytesseract.image_to_string(gray, config=config, lang=lang)
        # print(f"Text: {text}")

        return text.rstrip("\n")

    def get_text_from_center(
        self,
        box_width=200,
        box_height=200,
        offset_x=0,
        offset_y=0,
        config="--psm 6",
        lang="eng",
        img_BRG=None,
    ):
        # Draw the box and get its coordinates
        top_l, bottom_r = self.get_box_coordinate_from_center(
            box_width, box_height, offset_x, offset_y
        )

        # Get the text from the area inside the box
        text = self.get_text_from_box_coords(
            top_l, bottom_r, config, lang, img_BRG=img_BRG
        )

        # Return the text
        return text

    def find_items(
        self,
        temp_BRG=None,
        top_l=None,
        bottom_r=None,
        threshold=1,
        max_matches=10,
        display=False,
        img_BRG=None,
    ):
        """Find items in the PokeMMO game by matching a template image with the game screenshot."""
        # print(top_l, bottom_r)
        if img_BRG is None:
            img_BRG = self.get_img_BRG()
        if top_l and bottom_r:
            img_BRG = img_BRG[
                int(top_l[1]) : int(bottom_r[1]), int(top_l[0]) : int(bottom_r[0])
            ]

        # Perform template matching
        result = cv2.matchTemplate(img_BRG, temp_BRG, cv2.TM_CCORR_NORMED)

        # Apply the threshold to the result
        _, result = cv2.threshold(result, threshold, 1.0, cv2.THRESH_BINARY)
        # print(f"Result: {result}")
        result = np.where(result >= threshold)  #! i don't know what this does
        # print(f"Result: {result}")

        # Check the number of matches
        num_matches = len(result[0])  # Get the number of matches
        if num_matches > max_matches:
            print(f"Too many matches for template: {num_matches}")
            return None
        if num_matches != 0:
            # print(f"Number of matches: {num_matches}")
            pass

        h, w = temp_BRG.shape[:2]
        match_coords = []
        for index, pt in enumerate(zip(*result[::-1])):
            match_coords.append(
                (
                    pt[0] + top_l[0],
                    pt[1] + top_l[1],
                    pt[0] + w + top_l[0],
                    pt[1] + h + top_l[1],
                )
            )

        if display:
            for pt in match_coords:
                print(pt)
                # Draw a rectangle on the original image
                cv2.rectangle(img_BRG, pt[:2], pt[2:], (0, 0, 255), 2)
            cv2.imshow("Match Template", img_BRG)
            cv2.waitKey()

        return match_coords

    def get_hp_pct(self, top_l, bottom_r, img_BRG=None):
        if img_BRG is None:
            img_BRG = self.get_img_BRG()
        hp_image = img_BRG[top_l[1] : bottom_r[1], top_l[0] : bottom_r[0]]
        total_hp_length = bottom_r[0] - top_l[0]

        for x in range(hp_image.shape[1]):
            for y in range(hp_image.shape[0]):
                # Check if the pixel is close to white
                if np.all(hp_image[y, x] >= [251, 251, 251]):
                    current_hp_length = x
                    hp_pct = (current_hp_length / total_hp_length) * 100
                    return round(hp_pct, 1)
        return 100  # Return 0 if no white pixel is found

    def set_encounter_start_time(self, set_None=False):
        if set_None:
            self.encounter_start_time = None
            return
        timestamp = time.time()
        formatted_timestamp = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.encounter_start_time = formatted_timestamp
        return

    def Unova_farming(self):
        print("Unova_farming started")

        while self.auto_strategy_flag:
            Farming_Mistralton_City(self).run(repeat_times=999)

    def Hoenn_LV_up_farming(self):
        print("Hoenn_LV_up started")
        while self.auto_strategy_flag:
            Farming_BATTLE_FRONTINER(self).run(repeat_times=999)

    def Kanto_farming(self):
        print("Kanto_farming started")
        while self.auto_strategy_flag:
            Farming_Cerulean_City(self).run(repeat_times=999)

    def Attack_EV_Kanto_farming(self):
        print("Kanto_farming started")
        while self.auto_strategy_flag:
            Farming_Fuchsia_City(self).run(repeat_times=999)

    def Sp_Defend_EV_Unova_farming(self):
        print("Unova_farming started")
        while self.auto_strategy_flag:
            Farming_Opelucid_City(self).run(repeat_times=999)

    def Sp_Attack_EV_Unova_farming(self):
        print("Unova_farming started")
        while self.auto_strategy_flag:
            Farming_Opelucid_City_Sp_Attack(self).run(repeat_times=999)

    def Hoenn_farming(self):
        print("Hoenn_farming started")
        locations = {
            "SOOTOPOLIS_CITY": 10,
            "FALLARBOR_TOWN": 10,
            "PETALBURG_CITY": 10,
            "VERDANTURF_TOWN": 10,
        }
        previous_location = None

        while self.auto_strategy_flag:  # 主循环现在会检查 run_main_loop 标志
            if previous_location is not None:
                available_locations = locations.copy()
                del available_locations[previous_location]  # 移除上一次地点
                total_weight = sum(available_locations.values())
                probabilities = [
                    weight / total_weight for weight in available_locations.values()
                ]
                next_location = random.choices(
                    list(available_locations.keys()), probabilities
                )[0]
            else:
                next_location = random.choices(
                    list(locations.keys()), list(locations.values())
                )[0]

            getattr(self, f"{next_location}_FARMING").run(repeat_times=1)
            sleep(1)
            previous_location = next_location
        print("Main loop has stopped.")  # 打印消息表示主循环已停止


if __name__ == "__main__":
    pokeMMO = PokeMMO()
    sleep(1)
    pokeMMO.start_ui()

    while True:
        game_states = pokeMMO.get_gs()
        if game_states["check_pokemon_summary"][0]:
            coords = game_states["check_pokemon_summary"][1][0]
            pokemon_summary_sign_mid_x = (coords[0] + coords[2]) / 2
            pokemon_summary_sign_mid_y = (coords[1] + coords[3]) / 2
            iv_icon_top_l = (
                pokemon_summary_sign_mid_x - 393,
                pokemon_summary_sign_mid_y - 13,
            )
            iv_icon_bottom_r = (
                pokemon_summary_sign_mid_x - 373,
                pokemon_summary_sign_mid_y + 15,
            )  # Round down
            iv_page_list = pokeMMO.find_items(
                temp_BRG=pokeMMO.sprite_iv_page_BRG,
                top_l=iv_icon_top_l,
                threshold=0.97,
                bottom_r=iv_icon_bottom_r,
                display=False,
                max_matches=1,
            )
            print(iv_page_list)
        sleep(3)
