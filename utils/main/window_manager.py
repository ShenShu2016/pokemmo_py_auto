from ctypes import WINFUNCTYPE, byref, c_ubyte, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM, RECT

import cv2
import numpy as np
from unidecode import unidecode


class Window_Manager:
    def __init__(self, window_names=None):
        self.window_names = window_names or ["PokeMMO", "RokeMMO"]
        self.window_name = None
        self.EnumWindowsProc = WINFUNCTYPE(BOOL, HWND, LPARAM)
        self.GetWindowText = windll.user32.GetWindowTextW
        self.GetWindowTextLength = windll.user32.GetWindowTextLengthW
        self.IsWindowVisible = windll.user32.IsWindowVisible
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
        self.handle = None

    def get_window_name(self):
        """Get the window name of the PokeMMO game."""
        callback = self.EnumWindowsProc(self.foreach_window)

        windll.user32.EnumWindows(callback, 0)

        if self.window_name is None:
            raise Exception("Failed to find window name for PokeMMO")

        self.handle = windll.user32.FindWindowW(None, self.window_name)

        print(f"window name: {self.window_name}")
        return self.window_name

    def foreach_window(self, hwnd, lParam):
        if self.IsWindowVisible(hwnd):
            length = self.GetWindowTextLength(hwnd)
            buff = create_unicode_buffer(length + 1)
            self.GetWindowText(hwnd, buff, length + 1)
            ascii_text = unidecode(buff.value)
            if ascii_text in self.window_names:
                self.window_name = buff.value
                return True
        return True

    def get_current_img_BRG(self):
        """Capture a screenshot of the PokeMMO game."""
        self.GetClientRect = windll.user32.GetClientRect
        self.GetDC = windll.user32.GetDC
        self.CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
        self.CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
        self.SelectObject = windll.gdi32.SelectObject
        self.BitBlt = windll.gdi32.BitBlt
        self.GetBitmapBits = windll.gdi32.GetBitmapBits
        self.DeleteObject = windll.gdi32.DeleteObject
        self.ReleaseDC = windll.user32.ReleaseDC
        self.SRCCOPY = 0xCC0020

        r = RECT()
        self.GetClientRect(self.handle, byref(r))
        width, height = r.right, r.bottom
        dc = self.GetDC(self.handle)
        cdc = self.CreateCompatibleDC(dc)
        bitmap = self.CreateCompatibleBitmap(dc, width, height)
        self.SelectObject(cdc, bitmap)
        self.BitBlt(cdc, 0, 0, width, height, dc, 0, 0, self.SRCCOPY)
        total_bytes = width * height * 4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte * total_bytes
        self.GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
        self.DeleteObject(bitmap)
        self.DeleteObject(cdc)
        self.ReleaseDC(self.handle, dc)
        image_normal = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)
        img_BRG = cv2.cvtColor(image_normal, cv2.COLOR_BGRA2BGR)
        return img_BRG  # return img_BRG

    def get_window_id(self):
        """Get the unique ID of the PokeMMO game window."""
        if self.handle is None:
            self.get_window_name()  # 获取窗口名字以确保句柄被正确获取
        return self.handle


if __name__ == "__main__":
    window_manager = Window_Manager()
    window_id = window_manager.get_window_id()
    print(window_id)
