from __future__ import annotations

import random
from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class RoleController:
    def __init__(self, pokeMMO: PokeMMO):
        pass

    def move_left_right(self, delay: float):
        keys = ["a", "d"]
        random.shuffle(keys)

        pokeMMO.controller.key_press(keys[0], delay + random.uniform(0, delay))
        pokeMMO.controller.key_press(keys[1], delay + random.uniform(0, delay))

        total_delay = random.uniform(0, 0.5)
        sleep(total_delay)


if __name__ == "__main__":
    from main import PokeMMO

    pokeMMO = PokeMMO()
    # pokeMMO.start_ui()
    roleController = RoleController(pokeMMO)

    while True:
        while not pokeMMO.get_game_status() in range(20, 30):
            roleController.move_left_right(0.5)
            sleep(1)

        sleep(1)
    pass
