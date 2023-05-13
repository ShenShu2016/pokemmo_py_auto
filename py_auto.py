import logging
from ctypes import WINFUNCTYPE, byref, c_ubyte, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM, RECT

import cv2
import numpy as np
import pytesseract
from unidecode import unidecode

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
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

    def capture(self):
        """Capture a screenshot of the PokeMMO game."""
        r = RECT()
        self.GetClientRect(self.handle, byref(r))
        width, height = r.right, r.bottom
        print(f"width {width}, height {height}")
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

    def get_current_image(self):
        """Get the current screenshot of the PokeMMO game."""
        return self.capture()

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

    def draw_custom_box(
        self,
        image,
        box_width=200,
        box_height=200,
        color=(0, 0, 255),
        thickness=2,
        offset_x=0,
        offset_y=0,
    ):
        """Draw a box on the image and get the text from the area inside the box."""
        height, width, _ = image.shape
        center_x, center_y = (width // 2) + offset_x, (height // 2) - offset_y

        # Calculate the top-left and bottom-right points of the rectangle
        start_point = (center_x - box_width // 2, center_y - box_height // 2)
        end_point = (center_x + box_width // 2, center_y + box_height // 2)

        # Draw the rectangle on the image
        cv2.rectangle(image, start_point, end_point, color, thickness)

        # Return the coordinates of the top-left and bottom-right corners
        return start_point, end_point

    def get_text_from_area(
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

    def draw_box_and_get_text(
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
        start_point, end_point = self.draw_custom_box(
            image, box_width, box_height, color, thickness, offset_x, offset_y
        )

        # Get the text from the area inside the box
        text = self.get_text_from_area(image, start_point, end_point, config, lang)

        # Return the text
        return text

    def get_text_from_area_start_from_center(
        self,
        image,
        box_width=200,
        box_height=200,
        offset_x=0,
        offset_y=0,
        config="--psm 6",
        lang="eng",
    ):
        """Recognize the text in the given area from the center of the image."""
        height, width, _ = image.shape
        center_x, center_y = (width // 2) + offset_x, (height // 2) - offset_y

        # Calculate the top-left and bottom-right points of the rectangle
        top_left = (center_x - box_width // 2, center_y - box_height // 2)
        bottom_right = (center_x + box_width // 2, center_y + box_height // 2)

        # Extract the area from the image
        area = image[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]

        # Convert the area to grayscale
        gray = cv2.cvtColor(area, cv2.COLOR_BGRA2GRAY)

        # Recognize the text in the area
        text = pytesseract.image_to_string(gray, config=config, lang=lang)
        print(f"Text: {text}")

        return text

    def find_items(self, template_path, threshold=0.95):
        """Find items in the PokeMMO game by matching a template image with the game screenshot."""

        # Capture the current image from the game window
        image = self.get_current_image()
        image_color = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        # Load the template image
        template_color = cv2.imread(template_path, cv2.IMREAD_COLOR)

        # Perform template matching
        result = cv2.matchTemplate(image_color, template_color, cv2.TM_CCORR_NORMED)

        # Apply the threshold to the result
        _, result = cv2.threshold(result, threshold, 1.0, cv2.THRESH_BINARY)
        result = np.where(result >= threshold)

        h, w = template_color.shape[:2]
        for index, pt in enumerate(zip(*result[::-1])):
            # Draw a rectangle on the original image
            cv2.rectangle(image_color, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            # print all the coordinates and values
            print(index, pt[0], pt[1])

        cv2.imshow("Match Template", image_color)
        cv2.waitKey()


if __name__ == "__main__":
    # Make the process DPI-aware
    windll.user32.SetProcessDPIAware()

    # Initialize the PokeMMO class and get a screenshot
    pokeMMO = PokeMMO()

    try:
        image = pokeMMO.get_current_image()
    except Exception as e:
        print(f"Failed to get image: {e}")
        exit(1)

    # Convert the color from BGRA to BGR and display the image
    image_color = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    cv2.imshow("Match Template", image_color)
    cv2.waitKey()

    # Close the image window
    cv2.destroyAllWindows()
