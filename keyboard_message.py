import string
import time
from ctypes import windll
from ctypes.wintypes import HWND

from pywinauto import Application

from py_auto import PokeMMO


class KeyPresser:
    PostMessageW = windll.user32.PostMessageW
    MapVirtualKeyW = windll.user32.MapVirtualKeyW
    VkKeyScanA = windll.user32.VkKeyScanA

    WM_KEYDOWN = 0x100
    WM_KEYUP = 0x101
    MAPVK_VK_TO_VSC = 0
    WM_LBUTTONUP = 0x202
    WM_MOUSEMOVE = 0x0200
    WM_LBUTTONDOWN = 0x0201

    ARROW_KEYS = {"up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27}

    def __init__(self, handle: HWND):
        self.handle = handle

    def get_virtual_keycode(self, key: str):
        if len(key) == 1 and key in string.printable:
            return self.VkKeyScanA(ord(key)) & 0xFF
        elif key in self.ARROW_KEYS:
            return self.MapVirtualKeyW(self.ARROW_KEYS[key], self.MAPVK_VK_TO_VSC)
        else:
            raise ValueError(f"Unknown key: {key}")

    def post_message(self, message, key, lparam_end):
        vk_code = self.get_virtual_keycode(key)
        scan_code = self.MapVirtualKeyW(vk_code, 0)
        wparam = vk_code
        lparam = (scan_code << 16) | lparam_end
        self.PostMessageW(self.handle, message, wparam, lparam)

    def key_down(self, key: str):
        self.post_message(self.WM_KEYDOWN, key, 1)

    def key_up(self, key: str):
        self.post_message(self.WM_KEYUP, key, 0xC0000001)

    def key_press(self, key: str, delay: float):
        time.sleep(0.05)
        self.key_down(key)
        time.sleep(delay)
        self.key_up(key)


if __name__ == "__main__":
    import sys

    # if not windll.shell32.IsUserAnAdmin():
    #     # 不是管理员就提权
    #     windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    pokeMMo = PokeMMO()
    window_handle = pokeMMo.handle

    time.sleep(2)

    # move_to_2(window_handle, 583, 770)

    # left_down(window_handle, 583, 770)
    # time.sleep(0.1)
    # left_up(window_handle, 583, 770)
    # time.sleep(1)
    keyPresser = KeyPresser(window_handle)
    # time.sleep(2)
    # keyPresser.move_to(100, 100)
    keyPresser.key_press("escape", 0.5)
    # keyPresser.key_press("d", 1.0)

    # keyPresser.key_press("w", 1.0)
    # keyPresser.key_press("s", 1.0)
