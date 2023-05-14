import time
from ctypes.wintypes import HWND

from pywinauto import Application


class MouseController:
    def __init__(self, app):
        self.app = app

    def move_to(self, x, y):
        """Move the mouse to a specific position on the window."""
        self.app.windows()[0].set_focus()
        self.app.windows()[0].click_input(button="move", coords=(x, y))

    def click(self, x=None, y=None):
        """Click at the current mouse position or at a specific position if provided."""
        self.app.windows()[0].set_focus()
        if x is not None and y is not None:
            self.app.windows()[0].click_input(coords=(x, y))
        else:
            self.app.windows()[0].click_input()

    def drag(self, x1, y1, x2, y2):
        """Drag the mouse from one position to another."""
        self.app.windows()[0].set_focus()
        self.app.windows()[0].drag_mouse(
            button="left", press_coords=(x1, y1), release_coords=(x2, y2)
        )


if __name__ == "__main__":
    from py_auto import PokeMMO

    pokeMMO = PokeMMO()

    app = Application().connect(
        handle=pokeMMO.handle
    )  # Replace with your window handle
    mouse = MouseController(app)
    mouse.move_to(589, 771)
    time.sleep(3)
    mouse.click(589, 771)
    # mouse.drag(100, 100, 200, 200)
