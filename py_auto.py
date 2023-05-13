from ctypes import WINFUNCTYPE, byref, c_ubyte, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM, RECT

import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from unidecode import unidecode


class PokeMMO:
    # Define necessary Windows API functions
    GetWindowText = windll.user32.GetWindowTextW
    GetWindowTextLength = windll.user32.GetWindowTextLengthW
    IsWindowVisible = windll.user32.IsWindowVisible

    # Define the callback function prototype
    EnumWindowsProc = WINFUNCTYPE(BOOL, HWND, LPARAM)

    window_name = None

    # init
    def __init__(self):
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
        # 获取窗口客户区的大小
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
        return self.capture()

    def get_window_name(self):
        # Create a C-compatible callback function
        callback = self.EnumWindowsProc(self.foreach_window)

        windll.user32.EnumWindows(callback, 0)

        if self.window_name is None:
            # close this program
            exit(0)
        else:
            print(f"window name: {self.window_name}")
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
        # Calculate the center of the image
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
