from ctypes import WINFUNCTYPE, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM

from unidecode import unidecode


class Window_Manager:
    def __init__(self, window_names=None):
        self.window_names = window_names or ["PokeMMO", "RokeMMO"]
        self.window_name = None
        self.EnumWindowsProc = WINFUNCTYPE(BOOL, HWND, LPARAM)
        self.GetWindowText = windll.user32.GetWindowTextW
        self.GetWindowTextLength = windll.user32.GetWindowTextLengthW
        self.IsWindowVisible = windll.user32.IsWindowVisible

    def get_window_name(self):
        """Get the window name of the PokeMMO game."""
        callback = self.EnumWindowsProc(self.foreach_window)

        windll.user32.EnumWindows(callback, 0)

        if self.window_name is None:
            raise Exception("Failed to find window name for PokeMMO")

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
