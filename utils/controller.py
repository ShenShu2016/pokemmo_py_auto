from ctypes.wintypes import HWND
from time import sleep

from pywinauto import Application, keyboard
from pywinauto.application import Application


class Controller:
    def __init__(self, handle: HWND):
        self.app = Application().connect(handle=handle)
        self.window = self.app.windows()[0]

    def move_to(self, x, y, tolerance=0):
        """Move the mouse to a specific position on the window."""
        self.window.set_focus()
        self.window.click_input(
            button="move", coords=(int(x) + tolerance, int(y) + tolerance)
        )
        sleep(0.02)

    def click(self, x=None, y=None, tolerance=0):
        """Click at the current mouse position or at a specific position if provided."""
        self.window.set_focus()
        if x is not None and y is not None:
            self.window.click_input(coords=(int(x) + tolerance, int(y) + tolerance))
            sleep(0.03)
        else:
            self.window.click_input()

    def click_center(self, point):
        try:
            x1, y1, x2, y2 = point
            if x1 > x2 or y1 > y2:
                raise ValueError("Invalid coordinates: x1 > x2 or y1 > y2")

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            self.window.set_focus()
            self.window.click_input(coords=(int(center_x), int(center_y)))
            sleep(0.03)

        except (TypeError, ValueError) as e:
            print(f"Error: {e}")

    def drag(self, x1, y1, x2, y2):
        """Drag the mouse from one position to another."""
        self.window.set_focus()
        self.window.drag_mouse(
            button="left", press_coords=(x1, y1), release_coords=(x2, y2)
        )

    def key_press(self, key: str, delay: float = 0.2):
        self.window.set_focus()
        # print(f"Pressing {key} for {delay} seconds")

        keyboard.send_keys("{" + key + " down}")
        sleep(delay)
        keyboard.send_keys("{" + key + " up}")
        # print(f"Finished pressing {key} for {delay} seconds")

    def key_down(
        self,
        key: str,
    ):
        self.window.set_focus()
        keyboard.send_keys("{" + key + " down}")

    def key_up(self, key: str):
        self.window.set_focus()
        keyboard.send_keys("{" + key + " up}")


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()

    controller = Controller(pokeMMO.handle)
    # controller.move_to(589, 771)
    # sleep(3)
    # controller.click(589, 771)
    controller.key_press("a", 0.5)
    controller.key_press("d", 0.5)

    # controller.drag(100, 100, 200, 200)
