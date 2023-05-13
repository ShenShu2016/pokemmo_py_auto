from ctypes import POINTER, WINFUNCTYPE, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM

from unidecode import unidecode

# Define necessary Windows API functions
GetWindowText = windll.user32.GetWindowTextW
GetWindowTextLength = windll.user32.GetWindowTextLengthW
IsWindowVisible = windll.user32.IsWindowVisible

# Define the callback function prototype
EnumWindowsProc = WINFUNCTYPE(BOOL, HWND, LPARAM)

window_name = None


def foreach_window(hwnd, lParam):
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        ascii_text = unidecode(buff.value)
        if ascii_text == "PokeMMO" or ascii_text == "RokeMMO":
            global window_name
            window_name = buff.value
            return True
    return True


# Create a C-compatible callback function
callback = EnumWindowsProc(foreach_window)

windll.user32.EnumWindows(callback, 0)


def get_window_name():
    if window_name is None:
        # close this program
        exit(0)
    return window_name
