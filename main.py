import datetime
import json
import logging
import threading
import time
from ctypes import windll

import cv2
import numpy as np
import pandas as pd
import pytesseract

from enemy_status import EnemyStatus
from game_status import GameStatus
from pokemmoUI import PokemmoUI
from role_controller import RoleController
from utils.main.controller import Controller
from utils.main.window_manager import Window_Manager
from utils.main.word_recognizer import Word_Recognizer

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PokeMMO:
    """A class to interact with the PokeMMO game."""

    def __init__(self):
        """Initialize the PokeMMO class."""
        self.window_manager = Window_Manager()
        self.window_name = self.window_manager.get_window_name()
        self.handle = windll.user32.FindWindowW(None, self.window_name)

        with open("configure.json", "r") as f:
            self.config = json.load(f)
        pytesseract.pytesseract.tesseract_cmd = self.config["tesseract"]

        # Load the template images
        for key, path in self.config.items():
            if path.endswith(".png"):
                # Create variable name
                var_name = key.replace("_path", "_BRG")
                # Load image and set it as instance variable
                setattr(self, var_name, cv2.imread(path, cv2.IMREAD_COLOR))

                print(
                    f"Successfully initialized variable: {var_name} with path: {path}"
                )
        self.pokedex = pd.read_csv("data\clean_pokedex.csv")
        print(self.pokedex.head())
        SetForegroundWindow = windll.user32.SetForegroundWindow
        SetForegroundWindow(self.handle)

        self.imgs_BRG_list_lock = threading.Lock()
        self.imgs_BRG_list = []

        self.latest_img_BRG_lock = threading.Lock()
        self.latest_img_BRG = self.window_manager.get_current_img_BRG()

        self.game_status_lock = threading.Lock()
        self.game_status = {"return_status": 0}

        self.enemy_status_lock = threading.Lock()
        self.enemy_status = {}

        self.state_dict_lock = threading.Lock()
        self.state_dict = {}

        self.game_status_checker = GameStatus(self)
        self.enemy_status_checker = EnemyStatus(self)

        self.controller = Controller(handle=self.handle)
        self.roleController = RoleController(self)
        self.word_recognizer = Word_Recognizer()
        self.ui = PokemmoUI(self)

        # Initialize stop flag for threads
        self.stop_threads_flag = False
        # Start the threads
        self.start_threads()

    def start_threads(self):
        threading.Thread(target=self.update_imgs_BRG_list).start()
        threading.Thread(target=self.update_game_status).start()
        threading.Thread(target=self.update_state_dict).start()
        threading.Thread(target=self.update_enemy_status).start()

    def stop_threads(self):
        self.stop_threads_flag = True

    def start_ui(self):
        """Start the user interface."""
        self.ui.run()

    def update_imgs_BRG_list(self):  # only image will be captured
        image_count = 0
        while not self.stop_threads_flag:
            with self.imgs_BRG_list_lock:
                # Add the current image, timestamp, and name to the list
                image_name = f"image_{image_count}"
                current_img_BRG = self.window_manager.get_current_img_BRG()
                self.imgs_BRG_list.append(
                    (
                        datetime.datetime.now(),
                        current_img_BRG,
                        image_name,
                    )
                )
                with self.latest_img_BRG_lock:
                    self.latest_img_BRG = current_img_BRG
                image_count += 1  # Increment the counter
                # If the list size has exceeded 10, remove the oldest image
                if len(self.imgs_BRG_list) > 10:
                    self.imgs_BRG_list.pop(0)

            time.sleep(0.2)  # wait for 2 seconds

    def update_game_status(self):
        while not self.stop_threads_flag:
            new_game_state = self.game_status_checker.check_game_status()
            with self.game_status_lock:
                self.game_status = new_game_state
                time.sleep(1)  # wait for 3 seconds

    def update_enemy_status(self):
        while not self.stop_threads_flag:
            new_enemy_status = self.enemy_status_checker.check_enemy_status()
            with self.enemy_status_lock:
                self.enemy_status = new_enemy_status
                time.sleep(1)

    def update_state_dict(self):
        while not self.stop_threads_flag:
            # Update every 30 seconds
            time.sleep(30)
            my_address = self.get_text_from_box_coords((30, 0), (250, 25))
            my_money = self.get_text_from_box_coords(
                (37, 30),
                (130, 45),
                config="--psm 6 -c tessedit_char_whitelist=0123456789",
            )
            with self.state_dict_lock:
                current_time = datetime.datetime.now()
                self.state_dict[current_time] = {
                    "address": my_address,
                    "money": my_money,
                }
                # print(
                #     f"Updated state_dict at {current_time}, address: {my_address}, money: {my_money}"
                # )
                # If the dictionary size has exceeded 10, remove the oldest entry
                if len(self.state_dict) > 10:
                    oldest_entry = min(self.state_dict.keys())
                    del self.state_dict[oldest_entry]
                # print the most recent state_dict

    # Use this method to safely access the state_dict variable from other threads
    def get_state_dict(self):
        with self.state_dict_lock:
            return self.state_dict

    # Use these methods to safely access the img_BRG and game_status variables from other threads
    def get_imgs_BRG_list(self):
        with self.imgs_BRG_list_lock:
            return self.imgs_BRG_list

    def get_game_status(self):
        with self.game_status_lock:
            return self.game_status

    def get_enemy_status(self):
        with self.enemy_status_lock:
            return self.enemy_status

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

        return text

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

    def calculate_black_ratio(self, img_BRG=None):
        """Calculate the ratio of black area in the image."""
        # Get the current image
        if img_BRG is None:
            img_BRG = self.get_latest_img_BRG()

        # Define the value for black pixels in RGB
        black_value = [0, 0, 0]

        # Count the number of black pixels
        black_pixels = np.sum(np.all(img_BRG == black_value, axis=-1))

        # Get the total number of pixels in the image
        total_pixels = img_BRG.shape[0] * img_BRG.shape[1]

        # Calculate and return the ratio of black pixels
        black_ratio = black_pixels / total_pixels
        return round(black_ratio, 2)

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
    # Make the process DPI-aware
    windll.user32.SetProcessDPIAware()
    # Initialize the PokeMMO class and get a screenshot
    pokeMMO = PokeMMO()
    pokeMMO.start_ui()

    cv2.destroyAllWindows()
