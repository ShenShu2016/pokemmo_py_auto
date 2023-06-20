import logging
from ctypes.wintypes import HWND
from time import sleep
from typing import TYPE_CHECKING

from pywinauto import Application, keyboard

logging.basicConfig(level=logging.INFO)
import win32api

if TYPE_CHECKING:
    from main import PokeMMO


class Controller:
    DEFAULT_SLEEP_TIME = 0.02

    def __init__(self, handle: HWND, pokeMMO):
        self.app = Application().connect(handle=handle)
        self.window = self.app.windows()[0]
        self.p = pokeMMO

    def move_to(self, x, y, tolerance=0):
        """Move the mouse to a specific position on the window."""
        self.window.set_focus()
        self.window.click_input(
            button="move", coords=(int(x) + tolerance, int(y) + tolerance)
        )
        sleep(self.DEFAULT_SLEEP_TIME)

    def click(self, x=None, y=None, tolerance=0, back_to_original=False):
        """Click at the current mouse position or at a specific position if provided."""
        # Store the original mouse position
        original_position = win32api.GetCursorPos() if back_to_original else None

        self.window.set_focus()
        if x is not None and y is not None:
            x = int(x) + tolerance
            y = int(y) + tolerance
            # Move the mouse
            self.move_to(x, y)
            # Wait for a moment
            sleep(0.05)
            # Click
            self.window.click_input(coords=(x, y))
            sleep(self.DEFAULT_SLEEP_TIME)
        else:
            self.window.click_input()

        # Move the mouse back to the original position
        if back_to_original and original_position is not None:
            win32api.SetCursorPos(original_position)

    def click_center(self, point, back_to_original=False):
        """Click at the center of the given coordinates."""
        # Store the original mouse position
        original_position = win32api.GetCursorPos() if back_to_original else None

        try:
            x1, y1, x2, y2 = point
            if x1 > x2 or y1 > y2:
                raise ValueError("Invalid coordinates: x1 > x2 or y1 > y2")

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            self.window.set_focus()
            # Move the mouse
            self.move_to(center_x, center_y)
            # Wait for a moment
            sleep(0.05)
            # Click
            self.window.click_input(coords=(int(center_x), int(center_y)))
            sleep(self.DEFAULT_SLEEP_TIME)

            # Move the mouse back to the original position
            if back_to_original and original_position is not None:
                win32api.SetCursorPos(original_position)

        except Exception as e:
            print(f"Error in click_center: {e}")

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

    def key_press_2(self, key: str, delay: float = 0.2):
        """Press a key for a certain amount of time."""
        self.window.set_focus()

        keyboard.send_keys("{" + key + " down}")
        for _ in range(int(delay / 0.03)):
            sleep(0.03)
            if self.p.pf.stop_move_threads:
                keyboard.send_keys("{" + key + " up}")
                break
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
