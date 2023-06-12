import json
import logging
import threading
import time
from time import sleep

import cv2
import numpy as np
import pandas as pd
import pytesseract

from action_controller import Action_Controller
from auto_strategy.FALLARBOR_TOWN_FARMING import Farming_FALLARBOR_TOWN
from auto_strategy.PETALBURG_CITY_FARMING import Farming_PETALBURG_CITY
from auto_strategy.SOOTOPOLIS_CITY_FARMING import Farming_SOOTOPOLIS_CITY
from auto_strategy.VERDANTURF_TOWN_FARMING import Farming_VERDANTURF_TOWN
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

        self.latest_img_BRG_lock = threading.Lock()
        self.game_status_lock = threading.Lock()
        self.enemy_status_lock = threading.Lock()
        self.state_dict_lock = threading.Lock()
        self.coords_status_lock = threading.Lock()
        self.latest_img_BRG = self.window_manager.get_current_img_BRG()

        self.game_status = {"return_status": 0}
        self.enemy_status = {}
        self.state_dict = {"address": "", "money": 0}
        self.coords_status = {}
        self.df_dict = {}
        self.load_assets()
        self.game_status_checker = GameStatus(self)
        self.enemy_status_checker = EnemyStatus(self)

        self.controller = Controller(handle=self.handle)

        self.action_controller = Action_Controller(self)
        self.word_recognizer = Word_Recognizer()
        self.pf = PathFinder(self)
        self.log_print_save = LogPrintSave(self)
        self.db = SQLiteDB("pokemmo.sqlite")
        self.mj_coords = MemoryInjector_Coords()

        self.PETALBURG_CITY_FARMING = Farming_PETALBURG_CITY(self)
        self.SOOTOPOLIS_CITY_FARMING = Farming_SOOTOPOLIS_CITY(self)
        self.FALLARBOR_TOWN_FARMING = Farming_FALLARBOR_TOWN(self)
        self.VERDANTURF_TOWN_FARMING = Farming_VERDANTURF_TOWN(self)

        self.stop_threads_flag = False
        self.start_threads()

    def start_threads(self):
        threading.Thread(target=self.update_latest_img_BRG).start()
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

    def update_latest_img_BRG(self):  # only image will be captured
        while not self.stop_threads_flag:
            # Add the current image, timestamp, and name to the list
            start_time = time.time()
            current_img_BRG = self.window_manager.get_current_img_BRG()
            with self.latest_img_BRG_lock:
                self.latest_img_BRG = current_img_BRG

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
            with self.game_status_lock:
                self.game_status = new_game_state
            sleep(0.02)  # wait for 3 seconds

    def update_enemy_status(self):
        while not self.stop_threads_flag:
            new_enemy_status = self.enemy_status_checker.check_enemy_status()
            with self.enemy_status_lock:
                self.enemy_status = new_enemy_status
            sleep(0.02)

    def update_state_dict(self):
        while not self.stop_threads_flag:
            # Update every 30 seconds
            sleep(3)
            img_BRG = self.get_latest_img_BRG()
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
            with self.coords_status_lock:
                self.coords_status = new_memory_coords
            sleep(0.02)

    # Use this method to safely access the state_dict variable from other threads
    def get_state_dict(self):
        with self.state_dict_lock:
            return self.state_dict

    def get_game_status(self):
        with self.game_status_lock:
            return self.game_status

    def get_enemy_status(self):
        with self.enemy_status_lock:
            return self.enemy_status

    def get_coords_status(self):
        with self.coords_status_lock:
            return self.coords_status

    def get_latest_img_BRG(self):
        with self.latest_img_BRG_lock:
            return self.latest_img_BRG

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
            img_BRG = self.get_latest_img_BRG()
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
            img_BRG = self.get_latest_img_BRG()
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
            img_BRG = self.get_latest_img_BRG()
        if top_l and bottom_r:
            img_BRG = img_BRG[top_l[1] : bottom_r[1], top_l[0] : bottom_r[0]]

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
            img_BRG = self.get_latest_img_BRG()
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


if __name__ == "__main__":
    pokeMMO = PokeMMO()
    # pokeMMO.start_ui()
    # sleep(2)

    # while True:
    #     game_status = pokeMMO.get_game_status()
    #     pokeMMO.action_controller.iv_shiny_check_release(game_status)

    #     sleep(5)

    # while True:
    #     game_status = pokeMMO.get_game_status()

    #     if game_status["check_pokemon_summary"][0]:
    #         pokeMMO.action_controller.click_pokemon_summary_IV(game_status)
    #         coords = game_status["check_pokemon_summary"][1][0]

    #         # Compute common coordinates.
    #         close_summary_button_mid_x = int((coords[0] + coords[2]) / 2)
    #         close_summary_button_mid_y = int((coords[1] + coords[3]) / 2)

    #         # 检查闪光
    #         shiny_area_top_l = (
    #             close_summary_button_mid_x,
    #             close_summary_button_mid_y + 40,
    #         )
    #         shiny_area_bottom_r = (
    #             close_summary_button_mid_x + 33,
    #             close_summary_button_mid_y + 152,
    #         )  # Round down
    #         shiny_x_y_list = pokeMMO.find_items(
    #             temp_BRG=pokeMMO.shiny_BRG,
    #             threshold=0.98,
    #             max_matches=10,
    #             top_l=shiny_area_top_l,
    #             bottom_r=shiny_area_bottom_r,
    #             display=False,
    #         )
    #         print("shiny_x_y_list", shiny_x_y_list)
    #         if len(shiny_x_y_list) >= 1:
    #             print("Shiny!")
    #             pokeMMO.action_controller.close_pokemon_summary(game_status)

    #         secret_shiny_x_y_list = pokeMMO.find_items(
    #             temp_BRG=pokeMMO.secret_shiny_BRG,
    #             threshold=0.995,
    #             max_matches=10,
    #             top_l=shiny_area_top_l,
    #             bottom_r=shiny_area_bottom_r,
    #             display=False,
    #         )
    #         print("secret_shiny_x_y_list", secret_shiny_x_y_list)
    #         if len(secret_shiny_x_y_list) >= 1:
    #             print("Secret Shiny!")
    #             pokeMMO.action_controller.close_pokemon_summary(game_status)

    #         # Compute IV area coordinates.
    #         iv_area_top_l = (
    #             close_summary_button_mid_x - 346,
    #             close_summary_button_mid_y + 27,
    #         )
    #         iv_area_bottom_r = (
    #             close_summary_button_mid_x - 312,
    #             close_summary_button_mid_y + 211,
    #         )  # Round down
    #         print("IV area top left:", iv_area_top_l)
    #         print("IV area bottom right:", iv_area_bottom_r)

    #         iv_31_x_y_list = pokeMMO.find_items(
    #             temp_BRG=pokeMMO.iv_31_BRG,
    #             threshold=0.995,
    #             max_matches=10,
    #             top_l=iv_area_top_l,
    #             bottom_r=iv_area_bottom_r,
    #             display=False,
    #         )
    #         print("IV 31 List:", iv_31_x_y_list)

    #         if len(iv_31_x_y_list) == 0:
    #             print("start releasing pokemon")
    #             pc_release_icon_coords = (
    #                 close_summary_button_mid_x - 260,
    #                 close_summary_button_mid_y + 3,
    #             )  # Round up
    #             pokeMMO.controller.click(*pc_release_icon_coords)
    #             sleep(0.3)

    #             confirm_release_area_top_l = (
    #                 close_summary_button_mid_x - 418,
    #                 close_summary_button_mid_y + 143,
    #             )  # Round up
    #             confirm_release_area_bottom_r = (
    #                 close_summary_button_mid_x - 301,
    #                 close_summary_button_mid_y + 168,
    #             )  # Round up
    #             print("Confirm release area top left:", confirm_release_area_top_l)
    #             print(
    #                 "Confirm release area bottom right:", confirm_release_area_bottom_r
    #             )

    #             confirm_release_x_y_list = pokeMMO.find_items(
    #                 temp_BRG=pokeMMO.confirm_release_BRG,
    #                 threshold=0.995,
    #                 top_l=confirm_release_area_top_l,
    #                 bottom_r=confirm_release_area_bottom_r,
    #                 max_matches=1,
    #                 display=False,
    #             )
    #             print("Confirm release list:", confirm_release_x_y_list)

    #             if len(confirm_release_x_y_list) == 1:
    #                 # Click the first two elements of the tuple (x and y coords).
    #                 pokeMMO.controller.click(
    #                     confirm_release_x_y_list[0][0], confirm_release_x_y_list[0][1]
    #                 )
    #                 sleep(0.3)
    #                 pokeMMO.controller.click(679, 378)
    #         else:
    #             pokeMMO.action_controller.close_pokemon_summary(game_status)

    #     sleep(5)

    # hp_BRG_x_y_list = pokeMMO.find_items(
    #     temp_BRG=pokeMMO.hp_BRG,
    #     threshold=0.995,
    #     max_matches=10,
    #     top_l=(0, 70),
    #     bottom_r=(1080, 170),
    #     display=True,
    # )

    # sleep(6)
    # while True:
    #     pokeMMO.action_controller.close_pokemon_summary(pokeMMO.get_game_status())
    #     sleep(1)

    import random
    import time

    locations = {
        "SOOTOPOLIS_CITY": 10,
        "FALLARBOR_TOWN": 30,
        "PETALBURG_CITY": 10,
        "VERDANTURF_TOWN": 40,
    }
    previous_location = None

    while False:
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

        getattr(pokeMMO, f"{next_location}_FARMING").run(repeat_times=1)
        sleep(1)
        previous_location = next_location

    while True:
        sleep(1)
