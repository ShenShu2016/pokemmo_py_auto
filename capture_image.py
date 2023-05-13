from ctypes import POINTER, WINFUNCTYPE, byref, c_ubyte, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM, RECT

import numpy as np
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
        """窗口客户区截图

        Args:
            handle (HWND): 要截图的窗口句柄

        Returns:
            numpy.ndarray: 截图数据
        """
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
        """获取当前窗口的截图

        Returns:
            numpy.ndarray: 截图数据
        """
        return self.capture()

    def get_window_name(self):
        # Create a C-compatible callback function
        callback = self.EnumWindowsProc(self.foreach_window)

        windll.user32.EnumWindows(callback, 0)

        if self.window_name is None:
            # close this program
            exit(0)

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


if __name__ == "__main__":
    import cv2

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
