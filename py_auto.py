import datetime
import json
import logging
import threading
import time
from ctypes import WINFUNCTYPE, byref, c_ubyte, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM, RECT

import cv2
import numpy as np
import pytesseract
from unidecode import unidecode

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


SRCCOPY = 0x00CC0020  # Raster operation code


class PokeMMO:
    """A class to interact with the PokeMMO game."""

    # Define necessary Windows API functions

    GetWindowText = windll.user32.GetWindowTextW
    GetWindowTextLength = windll.user32.GetWindowTextLengthW
    IsWindowVisible = windll.user32.IsWindowVisible

    # Define the callback function prototype
    EnumWindowsProc = WINFUNCTYPE(BOOL, HWND, LPARAM)

    def __init__(self):
        """Initialize the PokeMMO class."""
        self.window_name = self.get_window_name()
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

        self.images_normal_list_lock = threading.Lock()
        self.images_normal_list = []

        self.most_recent_image_normal_lock = threading.Lock()
        self.most_recent_image_normal = None

        self.game_status_lock = threading.Lock()
        self.game_status = None  # "battle", "map", "dialog", "menu", "unknown"

        self.state_dict_lock = threading.Lock()
        self.state_dict = {}

        # Start the threads
        # self.start_threads()

    def start_threads(self):
        threading.Thread(target=self.update_images_normal_list).start()
        threading.Thread(target=self.update_game_status).start()
        threading.Thread(target=self.update_state_dict).start()

    def update_images_normal_list(self):  # only image will be captured
        image_count = 0
        while True:
            with self.images_normal_list_lock:
                # Add the current image, timestamp, and name to the list
                image_name = f"image_{image_count}"
                current_image_normal = self.get_current_image_normal()
                self.images_normal_list.append(
                    (
                        datetime.datetime.now(),
                        current_image_normal,
                        image_name,
                    )
                )
                with self.most_recent_image_normal_lock:
                    self.most_recent_image_normal = current_image_normal
                image_count += 1  # Increment the counter
                # If the list size has exceeded 10, remove the oldest image
                if len(self.images_normal_list) > 10:
                    self.images_normal_list.pop(0)

            time.sleep(0.2)  # wait for 2 seconds

    def update_game_status(self):
        while True:
            if self.most_recent_image_normal is None:
                logger.error("Failed to capture image.")
                time.sleep(3)
                continue
            with self.most_recent_image_normal_lock:
                image_normal_copy = self.most_recent_image_normal.copy()
            if image_normal_copy is not None:
                with self.game_status_lock:
                    self.game_status = self.check_game_status(image_normal_copy)
            time.sleep(1)  # wait for 3 seconds

    def update_state_dict(self):
        while True:
            # Update every 30 seconds
            time.sleep(30)
            with self.most_recent_image_normal_lock:
                current_image_normal = self.most_recent_image_normal.copy()
            my_address = self.get_text_from_box_coordinate(
                current_image_normal, (30, 0), (250, 25)
            )
            my_money = self.get_text_from_box_coordinate(
                current_image_normal,
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

    # Use these methods to safely access the image_normal and game_status variables from other threads
    def get_images_normal_list(self):
        with self.images_normal_list_lock:
            return self.images_normal_list

    def get_game_status(self):
        with self.game_status_lock:
            return self.game_status

    def get_most_recent_image_normal(self):
        with self.most_recent_image_normal_lock:
            return self.most_recent_image_normal

    def capture(self):
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
        return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)

    def get_current_image_normal(self):
        """Get the current screenshot of the PokeMMO game."""
        return self.capture()  # return image_normal

    def get_window_name(self):
        """Get the window name of the PokeMMO game."""
        callback = self.EnumWindowsProc(self.foreach_window)

        windll.user32.EnumWindows(callback, 0)

        if self.window_name is None:
            raise Exception("Failed to find window name for PokeMMO")

        logger.debug(f"window name: {self.window_name}")
        return self.window_name

    def foreach_window(self, hwnd, lParam):
        if self.IsWindowVisible(hwnd):
            length = self.GetWindowTextLength(hwnd)
            buff = create_unicode_buffer(length + 1)
            self.GetWindowText(hwnd, buff, length + 1)
            ascii_text = unidecode(buff.value)
            if ascii_text == "PokeMMO" or ascii_text == "RokeMMO":
                self.window_name = buff.value
                return True
        return True

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
        image_normal = self.get_most_recent_image_normal()
        height, width, _ = image_normal.shape
        center_x, center_y = (width // 2) + offset_x, (height // 2) - offset_y

        # Calculate the top-left and bottom-right points of the rectangle
        top_left = (center_x - box_width // 2, center_y - box_height // 2)
        bottom_right = (center_x + box_width // 2, center_y + box_height // 2)

        # Draw the rectangle on the image
        if display:
            cv2.rectangle(image_normal, top_left, bottom_right, color, thickness)
            cv2.imshow("Match Template", image_normal)
            cv2.waitKey()

        # Return the coordinates of the top-left and bottom-right corners
        return top_left, bottom_right

    def get_text_from_box_coordinate(
        self, image, top_left, bottom_right, config="--psm 6", lang="eng"
    ):
        # Extract the area from the image
        area = image[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]

        # Convert the area to grayscale
        gray = cv2.cvtColor(area, cv2.COLOR_BGRA2GRAY)

        # Recognize the text in the area
        text = pytesseract.image_to_string(gray, config=config, lang=lang)
        print(f"Text: {text}")

        return text

    def get_text_from_center(
        self,
        image,
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
            image, box_width, box_height, color, thickness, offset_x, offset_y
        )

        # Get the text from the area inside the box
        text = self.get_text_from_box_coordinate(
            image, top_left, bottom_right, config, lang
        )

        # Return the text
        return text

    def find_items(
        self,
        image_color,
        template_color,
        top_left=None,
        bottom_right=None,
        threshold=1,
        max_matches=10,
        display=False,
    ):
        """Find items in the PokeMMO game by matching a template image with the game screenshot."""
        print(top_left, bottom_right)
        if top_left and bottom_right:
            image_color = image_color[
                top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]
            ]

        # Perform template matching
        result = cv2.matchTemplate(image_color, template_color, cv2.TM_CCORR_NORMED)

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
            print(f"Number of matches: {num_matches}")

        h, w = template_color.shape[:2]
        match_coordinates = []
        for index, pt in enumerate(zip(*result[::-1])):
            match_coordinates.append((pt[0], pt[1], pt[0] + w, pt[1] + h))

        if display:
            for pt in match_coordinates:
                # Draw a rectangle on the original image
                cv2.rectangle(image_color, pt[:2], pt[2:], (0, 0, 255), 2)
            cv2.imshow("Match Template", image_color)
            cv2.waitKey()

        return match_coordinates

    def check_game_status(self, image_normal, threshold=0.985):
        """Check the game state based on the existence of certain images."""
        # Capture the current image from the game window
        image_color = cv2.cvtColor(image_normal, cv2.COLOR_BGRA2BGR)
        face_area = self.get_box_coordinate_from_center(
            box_width=150,
            box_height=150,
            offset_x=0,
            offset_y=50,
        )
        face_area_l = face_area[0]
        face_area_r = face_area[1]
        # Try to find each template in the image
        if (
            self.find_items(
                image_color,
                self.face_down_color,
                threshold=threshold,
                max_matches=5,
                top_left=face_area_l,
                bottom_right=face_area_r,
            )
            or self.find_items(
                image_color,
                template_color=self.face_up_color,
                threshold=threshold,
                max_matches=5,
                top_left=face_area_l,
                bottom_right=face_area_r,
            )
            or self.find_items(
                image_color,
                self.face_left_color,
                threshold=threshold,
                max_matches=5,
                top_left=face_area_l,
                bottom_right=face_area_r,
            )
            or self.find_items(
                image_color,
                self.face_right_color,
                threshold=threshold,
                max_matches=5,
                top_left=face_area_l,
                bottom_right=face_area_r,
            )
        ):
            print("Player character detected.")
            return "NORMAL"
        elif self.find_items(
            image_color, self.enemy_hp_bar_color, threshold=0.99, max_matches=10
        ):
            print("Enemy HP bar detected.")
            return "BATTLE"
        else:
            print("Unknown game state.")
            return "OTHER"


if __name__ == "__main__":
    # Make the process DPI-aware
    windll.user32.SetProcessDPIAware()

    # Initialize the PokeMMO class and get a screenshot
    pokeMMO = PokeMMO()

    try:
        image_normal = pokeMMO.get_current_image_normal()
    except Exception as e:
        print(f"Failed to get image: {e}")
        exit(1)

    # Convert the color from BGRA to BGR and display the image
    image_color = cv2.cvtColor(image_normal, cv2.COLOR_BGRA2BGR)

    # get text
    my_address = pokeMMO.get_text_from_box_coordinate(
        image_normal, (30, 0), (250, 25)
    )  # city& channel
    my_money = pokeMMO.get_text_from_box_coordinate(
        image_normal,
        (37, 30),
        (130, 45),
        config="--psm 6 -c tessedit_char_whitelist=0123456789",
    )
    pokeMMO.get_text_from_center(
        image_color,
        box_width=125,
        box_height=25,
        offset_x=0,
        offset_y=104,
    )  # Player Name and guild name
    pokeMMO.find_items(
        image_color,
        pokeMMO.Pokemon_Summary_Exit_Button_color,
    )
    pokeMMO.check_game_status(image_normal)

    # cv2.imshow("Match Template", image_color)
    # cv2.waitKey()

    # Close the image window
    cv2.destroyAllWindows()
