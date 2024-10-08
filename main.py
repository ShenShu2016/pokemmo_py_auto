import json
import random
import threading
import time
from datetime import datetime
from time import sleep

import cv2
import numpy as np
import pandas as pd
import pytesseract

import update_congifure
from action_controller import Action_Controller
from auto_strategy.auto_importer import *
from battle_status import BattleStatus
from game_status import GameStatus
from log_print_save import LogPrintSave
from path_finder import PathFinder
from pokemmoUI import PokemmoUI
from utils.controller import Controller
from utils.memory_injection.memory_injector_coords import MemoryInjector_Coords
from utils.SQLiteDB import SQLiteDB
from utils.window_manager import Window_Manager
from utils.word_recognizer import Word_Recognizer


class PokeMMO:
    """A class to interact with the PokeMMO game."""

    def __init__(self, dev_mode=False):
        """Initialize the PokeMMO class."""
        self.window_manager = Window_Manager()
        self.handle = self.window_manager.handle
        update_congifure.init_config_file()
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
        self.battle_status = {}
        self.state_dict = {"address": ""}
        self.coords_status = {
            "x_coords": 0,
            "y_coords": 0,
            "map_number_tuple": (0, 0, 0),
            "face_dir": 0,
            "transport": "unknown",
        }
        self.encounter_start_time = None

        self.df_dict = {}
        self.load_assets()

        self.game_status_checker = GameStatus(self)
        self.battle_status_checker = BattleStatus(self)

        self.controller = Controller(handle=self.handle, pokeMMO=self)

        self.ac = Action_Controller(self)
        self.word_recognizer = Word_Recognizer()
        self.pf = PathFinder(self)
        self.log_print_save = LogPrintSave(self)
        self.db = SQLiteDB(
            self,
            "pokemmo.sqlite",
        )
        if not dev_mode:
            self.mj_coords = MemoryInjector_Coords()

        self.auto_strategy_flag = False  # 用来控制所有的自动策略 开始与结束

        self.SOOTOPOLIS_CITY_FARMING = Farming_SOOTOPOLIS_CITY(self)
        self.FALLARBOR_TOWN_FARMING = Farming_FALLARBOR_TOWN(self)
        self.PETALBURG_CITY_FARMING = Farming_PETALBURG_CITY(self)
        self.VERDANTURF_TOWN_FARMING = Farming_VERDANTURF_TOWN(self)

        self.stop_threads_flag = False
        self.ui = PokemmoUI(self)
        if not dev_mode:
            self.start_threads()

    def start_threads(self):
        threading.Thread(target=self.update_img_BRG).start()
        threading.Thread(target=self.update_game_status).start()
        threading.Thread(target=self.update_state_dict).start()
        threading.Thread(target=self.update_battle_status).start()
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

                # print(f"Loaded {var_name} from {path}")
                asset_count += 1
        print(f"Loaded {asset_count} assets.")

    def start_ui(self):
        """Start the user interface."""
        self.ui.run()

    def update_img_BRG(self):  # only image will be captured
        """every 0.05s"""
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
        """every 0.02s"""
        while not self.stop_threads_flag:
            new_game_state = self.game_status_checker.check_game_status()
            with self.gs_lock:
                self.game_status = new_game_state
            sleep(0.02)  # wait for 3 seconds

    def update_battle_status(self):
        """every 0.02s"""
        while not self.stop_threads_flag:
            new_battle_status = self.battle_status_checker.check_battle_status()
            with self.bs_lock:
                self.battle_status = new_battle_status
            sleep(0.02)

    def update_state_dict(self):
        """every 3s"""
        while not self.stop_threads_flag:
            # Update every 30 seconds
            sleep(3)
            img_BRG = self.get_img_BRG()
            my_address = self.get_text_from_box_coords(
                (30, 0), (250, 25), img_BRG=img_BRG
            )

            with self.state_dict_lock:
                self.state_dict = {
                    "address": my_address,
                }

    def update_memory_coords(self):
        """every 0.005s"""
        while not self.stop_threads_flag:
            new_memory_coords = self.mj_coords.read_data()
            with self.coords_lock:
                self.coords_status.update(new_memory_coords)
            sleep(0.005)

    # Use this method to safely access the state_dict variable from other threads
    def get_state_dict(self):
        with self.state_dict_lock:
            return self.state_dict

    def get_gs(self):
        with self.gs_lock:
            return self.game_status

    def get_bs(self):
        with self.bs_lock:
            return self.battle_status

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
        original_img_BRG = img_BRG.copy()
        if top_l and bottom_r:
            img_BRG = img_BRG[
                int(top_l[1]) : int(bottom_r[1]), int(top_l[0]) : int(bottom_r[0])
            ]
        else:
            top_l, bottom_r = (0, 0), (img_BRG.shape[1], img_BRG.shape[0])

        # Perform template matching
        result = cv2.matchTemplate(img_BRG, temp_BRG, cv2.TM_CCORR_NORMED)

        # Apply the threshold to the result
        _, thresholded_result = cv2.threshold(result, threshold, 1.0, cv2.THRESH_BINARY)
        match_locations = np.where(thresholded_result >= threshold)

        # Check the number of matches
        num_matches = len(match_locations[0])  # Get the number of matches
        if num_matches > max_matches:
            print(f"Too many matches for template: {num_matches}")
            if not display:
                return None
        if num_matches != 0:
            # print(f"Number of matches: {num_matches}")
            pass

        h, w = temp_BRG.shape[:2]
        match_coords = []
        match_percentages = []

        for index, pt in enumerate(zip(*match_locations[::-1])):
            match_coords.append(
                (
                    pt[0] + top_l[0],
                    pt[1] + top_l[1],
                    pt[0] + w + top_l[0],
                    pt[1] + h + top_l[1],
                )
            )
            match_percentages.append(result[pt[1], pt[0]])

        if display:
            for pt in match_coords:
                print(pt)
                # Draw a rectangle on the original image
                cv2.rectangle(original_img_BRG, pt[:2], pt[2:], (0, 0, 255), 2)

            print(f"Number of matches: {num_matches}")
            print("Match coords with percentage:")
            for coords, percentage in zip(match_coords, match_percentages):
                print(f"Coords: {coords}, Similarity: {percentage * 100:.2f}%")

            cv2.imshow("Match Template", original_img_BRG)
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

    def Speed_EV_Unova_farming(self):
        print("Unova_farming started")
        while self.auto_strategy_flag:
            Farming_Lacunosa_Town_Speed(self).run(repeat_times=999)

    def Unova_field_farming(self):
        print("Unova_field_farming started")
        while self.auto_strategy_flag:
            Farming_Accumula_Town_Field(self).run(repeat_times=999)

    def Hoenn_Ditto_farming(self):
        print("Hoenn_Ditto_farming started")
        while self.auto_strategy_flag:
            Farming_Fallarbor_Town_Ditto(self).run(repeat_times=5)

    def Mail_Ditto_farming(self):
        print("Mail_ditto_farming started")
        # while self.auto_strategy_flag:
        Mail_Ditto(self, to_send="AAcxkAA", total_to_send=60).run()

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
                # 获取除上次地点外的所有地点及其权重
                location_weights = locations.copy()
                del location_weights[previous_location]  # 移除上一次地点
                total_weight = sum(location_weights.values())
                # 计算每个地点被选中的概率
                probabilities = [
                    weight / total_weight for weight in location_weights.values()
                ]
                # 随机选择下一个地点
                next_location = random.choices(
                    list(location_weights.keys()), probabilities
                )[0]
            else:
                # 第一次运行，随机选择一个地点
                next_location = random.choices(
                    list(locations.keys()), list(locations.values())
                )[0]

            # 运行下一个地点的任务
            getattr(self, f"{next_location}_FARMING").run(repeat_times=1)
            sleep(1)
            # 更新上次地点为当前地点
            previous_location = next_location

        print("主循环已停止。")  # 打印消息表示主循环已停止


if __name__ == "__main__":
    pokeMMO = PokeMMO()
    pokeMMO.start_ui()
    # pokeMMO = PokeMMO(dev_mode=True)
    # sleep(1)
    # pokeMMO.find_items(
    #     temp_BRG=pokeMMO.iv_31_BRG,
    #     # top_l=(419, 223),
    #     threshold=0.70,
    #     # bottom_r=(685, 264),
    #     display=True,
    #     max_matches=100,
    # )
