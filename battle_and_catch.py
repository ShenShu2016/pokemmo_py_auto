from time import sleep

from pywinauto import Application

from keyboard_message import KeyPresser
from mouse_control import MouseController
from py_auto import PokeMMO

pokeMMO = PokeMMO()
pokeMMO.start_threads()

window_handle = pokeMMO.handle
keyPresser = KeyPresser(window_handle)
app = Application().connect(handle=window_handle)  # Replace with your window handle
mouse = MouseController(app)
stage = "walking"
while True:
    sleep(1)

    if stage == "walking":
        while stage == "walking":
            if pokeMMO.get_game_status() == "BATTLE":
                stage = "battle"
                break

            keyPresser.key_press("a", 1)
            keyPresser.key_press("d", 1)

    if stage == "battle":
        print("battle")
        while stage == "battle":
            sleep(1)
            result = pokeMMO.find_items(
                image_normal=pokeMMO.get_current_image_normal(),
                template_color=pokeMMO.battle_option_color,
                threshold=0.95,
            )
            print(result)
            if len(result) > 0:
                keyPresser.key_press("w", 0.2)
                keyPresser.key_press("a", 0.2)
                keyPresser.key_press("j", 0.2)
                keyPresser.key_press("j", 0.2)
                stage = "through_ball"
                sleep(10)

                break
    if stage == "through_ball":
        print("through_ball")
        while stage == "through_ball":
            sleep(1)
            result = pokeMMO.find_items(
                image_normal=pokeMMO.get_current_image_normal(),
                template_color=pokeMMO.battle_option_color,
                threshold=0.95,
            )
            if len(result) > 0:
                keyPresser.key_press("w", 0.3)
                keyPresser.key_press("d", 0.3)
                keyPresser.key_press("j", 0.3)
                keyPresser.key_press("d", 0.2)
                keyPresser.key_press("d", 0.2)
                keyPresser.key_press("d", 0.2)
                keyPresser.key_press("a", 0.3)
                keyPresser.key_press("w", 0.2)
                keyPresser.key_press("w", 0.3)
                keyPresser.key_press("j", 0.2)

                sleep(10)
                stage = "close_summary"

                break
    if stage == "close_summary":
        while stage == "close_summary":
            sleep(1)
            print("close_summary")
            result = pokeMMO.find_items(
                image_normal=pokeMMO.get_current_image_normal(),
                template_color=pokeMMO.Pokemon_Summary_Exit_Button_color,
                threshold=0.99,
                max_matches=5,
            )
            for i in result:
                print("move to", i[0] + 3, i[1] + 3)
                mouse.move_to(i[0] + 3, i[1] + 3)
                sleep(0.5)
                mouse.click(i[0] + 3, i[1] + 3)
                sleep(1)

                stage = "walking"
