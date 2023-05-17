from __future__ import annotations

import random
from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


def calculate_catch_rate(
    max_hp=65, current_hp=1, catch_rate=1, ball_rate=1, pokemon_condition=1
):
    numerator = (
        (3 * max_hp - 2 * current_hp) * catch_rate * ball_rate * pokemon_condition
    )
    denominator = 3 * max_hp * 255
    final_catch_rate = numerator / denominator
    return final_catch_rate


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
