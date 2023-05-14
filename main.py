import datetime
import json
import logging
import threading
import time
from ctypes import byref, c_ubyte, windll
from ctypes.wintypes import RECT

import cv2
import numpy as np
import pytesseract

from constant import target_words_dict
from game_status import GameStatus
from utils.controller import Controller
from utils.window_manager import Window_Manager
from utils.word_recognizer import Word_Recognizer

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PokeMMO:
    """A class to interact with the PokeMMO game."""

    def __init__(self):
        """Initialize the PokeMMO class."""
        self.window_name = Window_Manager().get_window_name()
        self.handle = windll.user32.FindWindowW(None, self.window_name)

        with open("configure.json", "r") as f:
            self.config = json.load(f)
        pytesseract.pytesseract.tesseract_cmd = self.config["tesseract"]

        # Load the template images
        for key, path in self.config.items():
            if path.endswith(".png"):
                # Create variable name
                var_name = key.replace("_path", "_color")
                # Load image and set it as instance variable
                setattr(self, var_name, cv2.imread(path, cv2.IMREAD_COLOR))

                print(
                    f"Successfully initialized variable: {var_name} with path: {path}"
                )

        self.GetDC = windll.user32.GetDC
        self.CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
        self.GetClientRect = windll.user32.GetClientRect
        self.CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
        self.SelectObject = windll.gdi32.SelectObject
        self.BitBlt = windll.gdi32.BitBlt
        self.SRCCOPY = 0x00CC0020
        self.GetBitmapBits = windll.gdi32.GetBitmapBits
        self.DeleteObject = windll.gdi32.DeleteObject
        self.ReleaseDC = windll.user32.ReleaseDC

        SetForegroundWindow = windll.user32.SetForegroundWindow
        SetForegroundWindow(self.handle)

        self.images_BRG_list_lock = threading.Lock()
        self.images_BRG_list = []

        self.most_recent_image_BRG_lock = threading.Lock()
        self.most_recent_image_BRG = self.get_current_image_BRG()

        self.game_status_lock = threading.Lock()
        self.game_status = None  # "battle", "map", "dialog", "menu", "unknown"

        self.state_dict_lock = threading.Lock()
        self.state_dict = {}
        self.game_status_checker = GameStatus(self)
        self.controller = Controller(handle=self.handle)
        self.word_recognizer = Word_Recognizer()

        # Start the threads
        self.start_threads()

    def start_threads(self):
        threading.Thread(target=self.update_images_BRG_list).start()
        threading.Thread(target=self.update_game_status).start()
        threading.Thread(target=self.update_state_dict).start()

    def update_images_BRG_list(self):  # only image will be captured
        image_count = 0
        while True:
            with self.images_BRG_list_lock:
                # Add the current image, timestamp, and name to the list
                image_name = f"image_{image_count}"
                current_image_BRG = self.get_current_image_BRG()
                self.images_BRG_list.append(
                    (
                        datetime.datetime.now(),
                        current_image_BRG,
                        image_name,
                    )
                )
                with self.most_recent_image_BRG_lock:
                    self.most_recent_image_BRG = current_image_BRG
                image_count += 1  # Increment the counter
                # If the list size has exceeded 10, remove the oldest image
                if len(self.images_BRG_list) > 10:
                    self.images_BRG_list.pop(0)

            time.sleep(0.2)  # wait for 2 seconds

    def update_game_status(self):
        while True:
            self.game_status = self.game_status_checker.check_game_status()
            time.sleep(1)  # wait for 3 seconds

    def update_state_dict(self):
        while True:
            # Update every 30 seconds
            time.sleep(30)
            my_address = self.get_text_from_box_coordinate((30, 0), (250, 25))
            my_money = self.get_text_from_box_coordinate(
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
                print(
                    f"Updated state_dict at {current_time}, address: {my_address}, money: {my_money}"
                )
                # If the dictionary size has exceeded 10, remove the oldest entry
                if len(self.state_dict) > 10:
                    oldest_entry = min(self.state_dict.keys())
                    del self.state_dict[oldest_entry]
                # print the most recent state_dict

    # Use this method to safely access the state_dict variable from other threads
    def get_state_dict(self):
        with self.state_dict_lock:
            return self.state_dict

    # Use these methods to safely access the image_BRG and game_status variables from other threads
    def get_images_BRG_list(self):
        with self.images_BRG_list_lock:
            return self.images_BRG_list

    def get_game_status(self):
        with self.game_status_lock:
            return self.game_status

    def get_most_recent_image_BRG(self):
        with self.most_recent_image_BRG_lock:
            return self.most_recent_image_BRG

    def get_current_image_BRG(self):
        """Capture a screenshot of the PokeMMO game."""
        r = RECT()
        self.GetClientRect(self.handle, byref(r))
        width, height = r.right, r.bottom
        # print(f"width {width}, height {height}")
        # 开始截图
        dc = self.GetDC(self.handle)
        cdc = self.CreateCompatibleDC(dc)
        bitmap = self.CreateCompatibleBitmap(dc, width, height)
        self.SelectObject(cdc, bitmap)
        self.BitBlt(cdc, 0, 0, width, height, dc, 0, 0, self.SRCCOPY)
        # 截图是BGRA排列，因此总元素个数需要乘以4
        total_bytes = width * height * 4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte * total_bytes
        self.GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
        self.DeleteObject(bitmap)
        self.DeleteObject(cdc)
        self.ReleaseDC(self.handle, dc)
        # 返回截图数据为numpy.ndarray
        image_normal = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)
        image_BRG = cv2.cvtColor(image_normal, cv2.COLOR_BGRA2BGR)
        return image_BRG  # return image_BRG

    def get_box_coordinate_from_center(
        self,
        box_width=200,
        box_height=200,
        color=(0, 0, 255),
        thickness=2,
        offset_x=0,
        offset_y=0,
        display=False,
    ):
        """Draw a box on the image and get the text from the area inside the box."""
        image_BRG = self.get_most_recent_image_BRG()
        height, width, _ = image_BRG.shape
        center_x, center_y = (width // 2) + offset_x, (height // 2) - offset_y

        # Calculate the top-left and bottom-right points of the rectangle
        top_left = (center_x - box_width // 2, center_y - box_height // 2)
        bottom_right = (center_x + box_width // 2, center_y + box_height // 2)

        # Draw the rectangle on the image
        if display:
            cv2.rectangle(image_BRG, top_left, bottom_right, color, thickness)
            cv2.imshow("Match Template", image_BRG)
            cv2.waitKey()

        # Return the coordinates of the top-left and bottom-right corners
        return top_left, bottom_right

    def get_text_from_box_coordinate(
        self, top_left, bottom_right, config="--psm 6", lang="eng"
    ):
        image_BRG = self.get_most_recent_image_BRG()
        # Extract the area from the image
        area = image_BRG[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]

        # Convert the area to grayscale
        gray = cv2.cvtColor(area, cv2.COLOR_BGRA2GRAY)

        # Recognize the text in the area
        text = pytesseract.image_to_string(gray, config=config, lang=lang)
        print(f"Text: {text}")

        return text

    def get_text_from_center(
        self,
        box_width=200,
        box_height=200,
        color=(0, 0, 255),
        thickness=2,
        offset_x=0,
        offset_y=0,
        config="--psm 6",
        lang="eng",
    ):
        # Draw the box and get its coordinates
        top_left, bottom_right = self.get_box_coordinate_from_center(
            box_width, box_height, color, thickness, offset_x, offset_y
        )

        # Get the text from the area inside the box
        text = self.get_text_from_box_coordinate(top_left, bottom_right, config, lang)

        # Return the text
        return text

    def find_items(
        self,
        template_color=None,
        top_left=None,
        bottom_right=None,
        threshold=1,
        max_matches=10,
        display=False,
    ):
        """Find items in the PokeMMO game by matching a template image with the game screenshot."""
        # print(top_left, bottom_right)
        image_BRG = self.get_most_recent_image_BRG()
        if top_left and bottom_right:
            image_BRG = image_BRG[
                top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]
            ]

        # Perform template matching
        result = cv2.matchTemplate(image_BRG, template_color, cv2.TM_CCORR_NORMED)

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

        h, w = template_color.shape[:2]
        match_coordinates = []
        for index, pt in enumerate(zip(*result[::-1])):
            match_coordinates.append((pt[0], pt[1], pt[0] + w, pt[1] + h))

        if display:
            for pt in match_coordinates:
                print(pt)
                # Draw a rectangle on the original image
                cv2.rectangle(image_BRG, pt[:2], pt[2:], (0, 0, 255), 2)
            cv2.imshow("Match Template", image_BRG)
            cv2.waitKey()

        return match_coordinates


if __name__ == "__main__":
    # Make the process DPI-aware
    windll.user32.SetProcessDPIAware()

    # Initialize the PokeMMO class and get a screenshot
    pokeMMO = PokeMMO()

    my_address = pokeMMO.get_text_from_box_coordinate(
        (30, 0), (250, 25)
    )  # city& channel
    my_money = pokeMMO.get_text_from_box_coordinate(
        (37, 30),
        (130, 45),
        config="--psm 6 -c tessedit_char_whitelist=0123456789",
    )
    my_name_ORC = pokeMMO.get_text_from_center(
        box_width=125,
        box_height=25,
        offset_x=0,
        offset_y=104,
        config="--psm 7",
    )  # Player Name and guild name
    is_match, match_ratio = pokeMMO.word_recognizer.compare_with_target(
        my_name_ORC,
        target_words=target_words_dict["my_name_ORC"],
        threshold=40,
        mode="partial_ratio",
    )
    print(
        f"my_name_ORC: {my_name_ORC}, is_match: {is_match}, match_ratio: {match_ratio}"
    )

    pokeMMO.find_items(
        template_color=pokeMMO.Pokemon_Summary_Exit_Button_color,
    )
    pokeMMO.game_status_checker.check_game_status()

    # cv2.imshow("Match Template", image_BRG)
    # cv2.waitKey()

    # Close the image window
    cv2.destroyAllWindows()
