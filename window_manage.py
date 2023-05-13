# File: window_manager.py

import logging
from ctypes import WINFUNCTYPE, byref, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM, RECT

from unidecode import unidecode

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class WindowManager:
    """A class to interact with the Windows API."""

    # Define necessary Windows API functions

    GetWindowText = windll.user32.GetWindowTextW
    GetWindowTextLength = windll.user32.GetWindowTextLengthW
    IsWindowVisible = windll.user32.IsWindowVisible

    # Define the callback function prototype
    EnumWindowsProc = WINFUNCTYPE(BOOL, HWND, LPARAM)

    def __init__(self):
        """Initialize the WindowManager class."""
        self.window_name = self.get_window_name()
        self.handle = windll.user32.FindWindowW(None, self.window_name)

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
