import string
import time
from ctypes import windll
from ctypes.wintypes import HWND

import win32gui

PostMessageW = windll.user32.PostMessageW
MapVirtualKeyW = windll.user32.MapVirtualKeyW
VkKeyScanA = windll.user32.VkKeyScanA

WM_KEYDOWN = 0x100
WM_KEYUP = 0x101
MAPVK_VK_TO_VSC = 0
# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
KEYBOARD_MAPPING = {
    "escape": 0x01,
    "esc": 0x01,
    "f1": 0x3B,
    "f2": 0x3C,
    "f3": 0x3D,
    "f4": 0x3E,
    "f5": 0x3F,
    "f6": 0x40,
    "f7": 0x41,
    "f8": 0x42,
    "f9": 0x43,
    "f10": 0x44,
    "f11": 0x57,
    "f12": 0x58,
    "printscreen": 0xB7,
    "prntscrn": 0xB7,
    "prtsc": 0xB7,
    "prtscr": 0xB7,
    "scrolllock": 0x46,
    "pause": 0xC5,
    "`": 0x29,
    "1": 0x02,
    "2": 0x03,
    "3": 0x04,
    "4": 0x05,
    "5": 0x06,
    "6": 0x07,
    "7": 0x08,
    "8": 0x09,
    "9": 0x0A,
    "0": 0x0B,
    "-": 0x0C,
    "=": 0x0D,
    "backspace": 0x0E,
    "insert": 0xD2 + 1024,
    "home": 0xC7 + 1024,
    "pageup": 0xC9 + 1024,
    "pagedown": 0xD1 + 1024,
    # numpad
    "numlock": 0x45,
    "divide": 0xB5 + 1024,
    "multiply": 0x37,
    "subtract": 0x4A,
    "add": 0x4E,
    "decimal": 0x53,
    "numpadenter": 0x9C + 1024,
    "numpad1": 0x4F,
    "numpad2": 0x50,
    "numpad3": 0x51,
    "numpad4": 0x4B,
    "numpad5": 0x4C,
    "numpad6": 0x4D,
    "numpad7": 0x47,
    "numpad8": 0x48,
    "numpad9": 0x49,
    "numpad0": 0x52,
    # end numpad
    "tab": 0x0F,
    "q": 0x10,
    "w": 0x11,
    "e": 0x12,
    "r": 0x13,
    "t": 0x14,
    "y": 0x15,
    "u": 0x16,
    "i": 0x17,
    "o": 0x18,
    "p": 0x19,
    "[": 0x1A,
    "]": 0x1B,
    "\\": 0x2B,
    "del": 0xD3 + 1024,
    "delete": 0xD3 + 1024,
    "end": 0xCF + 1024,
    "capslock": 0x3A,
    "a": 0x1E,
    "s": 0x1F,
    "d": 0x20,
    "f": 0x21,
    "g": 0x22,
    "h": 0x23,
    "j": 0x24,
    "k": 0x25,
    "l": 0x26,
    ";": 0x27,
    "'": 0x28,
    "enter": 0x1C,
    "return": 0x1C,
    "shift": 0x2A,
    "shiftleft": 0x2A,
    "z": 0x2C,
    "x": 0x2D,
    "c": 0x2E,
    "v": 0x2F,
    "b": 0x30,
    "n": 0x31,
    "m": 0x32,
    ",": 0x33,
    ".": 0x34,
    "/": 0x35,
    "shiftright": 0x36,
    "ctrl": 0x1D,
    "ctrlleft": 0x1D,
    "win": 0xDB + 1024,
    "winleft": 0xDB + 1024,
    "alt": 0x38,
    "altleft": 0x38,
    " ": 0x39,
    "space": 0x39,
    "altright": 0xB8 + 1024,
    "winright": 0xDC + 1024,
    "apps": 0xDD + 1024,
    "ctrlright": 0x9D + 1024,
    # arrow key scancodes can be different depending on the hardware,
    # so I think the best solution is to look it up based on the virtual key
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mapvirtualkeya?redirectedfrom=MSDN
    "up": MapVirtualKeyW(0x26, MAPVK_VK_TO_VSC),
    "left": MapVirtualKeyW(0x25, MAPVK_VK_TO_VSC),
    "down": MapVirtualKeyW(0x28, MAPVK_VK_TO_VSC),
    "right": MapVirtualKeyW(0x27, MAPVK_VK_TO_VSC),
}


def get_virtual_keycode(key: str):
    """根据按键名获取虚拟按键码

    Args:
        key (str): 按键名

    Returns:
        int: 虚拟按键码
    """
    if len(key) == 1 and key in string.printable:
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-vkkeyscana
        return VkKeyScanA(ord(key)) & 0xFF
    else:
        return KEYBOARD_MAPPING[key]


def key_down(handle: HWND, key: str):
    """按下指定按键

    Args:
        handle (HWND): 窗口句柄
        key (str): 按键名
    """
    vk_code = get_virtual_keycode(key)
    scan_code = MapVirtualKeyW(vk_code, 0)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keydown
    wparam = vk_code
    lparam = (scan_code << 16) | 1
    PostMessageW(handle, WM_KEYDOWN, wparam, lparam)
    print(f"key down: {key}")


def key_up(handle: HWND, key: str):
    """放开指定按键

    Args:
        handle (HWND): 窗口句柄
        key (str): 按键名
    """
    vk_code = get_virtual_keycode(key)
    scan_code = MapVirtualKeyW(vk_code, 0)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keyup
    wparam = vk_code
    lparam = (scan_code << 16) | 0xC0000001
    PostMessageW(handle, WM_KEYUP, wparam, lparam)
    print(f"key up: {key}")


if __name__ == "__main__":
    # 需要和目标窗口同一权限，游戏窗口通常是管理员权限
    import sys

    if not windll.shell32.IsUserAnAdmin():
        # 不是管理员就提权
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

    from py_auto import PokeMMO

    pokeMMo = PokeMMO()
    window_handle = pokeMMo.handle

    import win32gui

    window_handle = pokeMMo.handle
    try:
        win32gui.SetForegroundWindow(window_handle)
    except Exception as e:
        print(e)

    # 控制角色向前移动两秒
    key_down(pokeMMo.handle, "left")
    time.sleep(1)
    key_up(pokeMMo.handle, "left")
