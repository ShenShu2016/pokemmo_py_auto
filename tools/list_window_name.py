from ctypes import POINTER, WINFUNCTYPE, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM

# Define necessary Windows API functions
GetWindowText = windll.user32.GetWindowTextW
GetWindowTextLength = windll.user32.GetWindowTextLengthW
IsWindowVisible = windll.user32.IsWindowVisible

# Define the callback function prototype
EnumWindowsProc = WINFUNCTYPE(BOOL, HWND, LPARAM)


def foreach_window(hwnd, lParam):
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        print(buff.value)
    return True


# Create a C-compatible callback function
callback = EnumWindowsProc(foreach_window)

windll.user32.EnumWindows(callback, 0)
