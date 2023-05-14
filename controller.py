import time
from ctypes.wintypes import HWND

from pywinauto import Application, keyboard
from pywinauto.application import Application


class Controller:
    ARROW_KEYS = {"up": "{UP}", "down": "{DOWN}", "left": "{LEFT}", "right": "{RIGHT}"}

    def __init__(self, handle: HWND):
        self.app = Application().connect(handle=handle)
        self.window = self.app.windows()[0]

    def move_to(self, x, y):
        """Move the mouse to a specific position on the window."""
        self.window.set_focus()
        self.window.click_input(button="move", coords=(x, y))

    def click(self, x=None, y=None):
        """Click at the current mouse position or at a specific position if provided."""
        self.window.set_focus()
        if x is not None and y is not None:
            self.window.click_input(coords=(x, y))
        else:
            self.window.click_input()

    def drag(self, x1, y1, x2, y2):
        """Drag the mouse from one position to another."""
        self.window.set_focus()
        self.window.drag_mouse(
            button="left", press_coords=(x1, y1), release_coords=(x2, y2)
        )

    def key_press(self, key: str, delay: float = 0.05):
        self.window.set_focus()
        if key in self.ARROW_KEYS:
            key = self.ARROW_KEYS[key]
        keyboard.send_keys("{" + key + " down}")
        time.sleep(delay)
        keyboard.send_keys("{" + key + " up}")


if __name__ == "__main__":
    from py_auto import PokeMMO

    pokeMMO = PokeMMO()

    controller = Controller(pokeMMO.handle)
    # controller.move_to(589, 771)
    # time.sleep(3)
    # controller.click(589, 771)
    controller.key_press("a", 0.5)
    controller.key_press("d", 0.5)

    # controller.drag(100, 100, 200, 200)
