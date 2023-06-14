import logging
from ctypes.wintypes import HWND
from time import sleep

from pywinauto import Application, keyboard

logging.basicConfig(level=logging.INFO)


class Controller:
    DEFAULT_SLEEP_TIME = 0.02

    def __init__(self, handle: HWND):
        self.app = Application().connect(handle=handle)
        self.window = self.app.windows()[0]

    def move_to(self, x, y, tolerance=0):
        """Move the mouse to a specific position on the window."""
        self.window.set_focus()
        self.window.click_input(
            button="move", coords=(int(x) + tolerance, int(y) + tolerance)
        )
        sleep(self.DEFAULT_SLEEP_TIME)

    def click(self, x=None, y=None, tolerance=0):
        """Click at the current mouse position or at a specific position if provided."""
        self.window.set_focus()
        if x is not None and y is not None:
            x = int(x) + tolerance
            y = int(y) + tolerance
            # 移动鼠标
            self.move_to(x, y)
            # 等待一段时间
            sleep(0.1)
            # 点击
            self.window.click_input(coords=(x, y))
            sleep(self.DEFAULT_SLEEP_TIME)
        else:
            self.window.click_input()

    def click_center(self, point):
        """Click at the center of the given coordinates."""
        try:
            x1, y1, x2, y2 = point
            if x1 > x2 or y1 > y2:
                raise ValueError("Invalid coordinates: x1 > x2 or y1 > y2")

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            self.window.set_focus()
            # 移动鼠标
            self.move_to(center_x, center_y)
            # 等待一段时间
            sleep(0.1)
            # 点击
            self.window.click_input(coords=(int(center_x), int(center_y)))
            sleep(self.DEFAULT_SLEEP_TIME)

        except (TypeError, ValueError) as e:
            logging.error(f"Error: {e}")
            raise e

    def drag(self, x1, y1, x2, y2):
        """Drag the mouse from one position to another."""
        self.window.set_focus()
        self.window.drag_mouse(
            button="left", press_coords=(x1, y1), release_coords=(x2, y2)
        )

    def key_press(self, key: str, delay: float = 0.2):
        """Press a key for a certain amount of time."""
        self.window.set_focus()

        keyboard.send_keys("{" + key + " down}")
        sleep(delay)
        keyboard.send_keys("{" + key + " up}")

    def key_down(self, key: str):
        """Press a key down."""
        self.window.set_focus()
        keyboard.send_keys("{" + key + " down}")

    def key_up(self, key: str):
        """Lift a key up."""
        self.window.set_focus()
        keyboard.send_keys("{" + key + " up}")


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()

    controller = Controller(pokeMMO.handle)
    controller.key_press("a", 0.5)
    controller.key_press("d", 0.5)
