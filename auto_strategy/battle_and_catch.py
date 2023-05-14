from time import sleep


def battle_and_catch(pokeMMO):
    stage = "walking"
    while True:
        sleep(1)

        if stage == "walking":
            while stage == "walking":
                if pokeMMO.get_game_status() == "BATTLE":
                    stage = "battle"
                    break

                pokeMMO.controller.key_press("a", 1)
                pokeMMO.controller.key_press("d", 1)

        if stage == "battle":
            print("battle")
            while stage == "battle":
                sleep(1)
                result = pokeMMO.find_items(
                    template_color=pokeMMO.battle_option_color,
                    threshold=0.95,
                )
                print(result)
                if len(result) > 0:
                    pokeMMO.controller.key_press("w", 0.2)
                    pokeMMO.controller.key_press("a", 0.2)
                    pokeMMO.controller.key_press("j", 0.2)
                    pokeMMO.controller.key_press("j", 0.2)
                    stage = "through_ball"
                    sleep(10)

                    break
        if stage == "through_ball":
            print("through_ball")
            while stage == "through_ball":
                sleep(1)
                result = pokeMMO.find_items(
                    template_color=pokeMMO.battle_option_color,
                    threshold=0.95,
                )
                if len(result) > 0:
                    pokeMMO.controller.key_press("w", 0.3)
                    pokeMMO.controller.key_press("d", 0.3)
                    pokeMMO.controller.key_press("j", 0.3)
                    pokeMMO.controller.key_press("d", 0.2)
                    pokeMMO.controller.key_press("d", 0.2)
                    pokeMMO.controller.key_press("d", 0.2)
                    pokeMMO.controller.key_press("a", 0.3)
                    pokeMMO.controller.key_press("w", 0.2)
                    pokeMMO.controller.key_press("w", 0.3)
                    pokeMMO.controller.key_press("j", 0.2)

                    sleep(10)
                    stage = "close_summary"

                    break
        if stage == "close_summary":
            while stage == "close_summary":
                sleep(1)
                print("close_summary")
                result = pokeMMO.find_items(
                    template_color=pokeMMO.Pokemon_Summary_Exit_Button_color,
                    threshold=0.99,
                    max_matches=5,
                )
                for i in result:
                    print("move to", i[0] + 3, i[1] + 3)
                    pokeMMO.controller.move_to(i[0] + 3, i[1] + 3)
                    sleep(0.5)
                    pokeMMO.controller.click(i[0] + 3, i[1] + 3)
                    sleep(1)

                    stage = "walking"


if __name__ == "__main__":
    # Create an instance of the PokeMMO class
    import sys
    from os.path import abspath, dirname

    # Get the absolute path of the current script
    current_dir = dirname(abspath(__file__))

    # Add the parent directory to the sys.path
    parent_dir = dirname(current_dir)
    sys.path.append(parent_dir)
    from main import PokeMMO

    pokeMMO = PokeMMO()

    # Run the auto strategy
    battle_and_catch(pokeMMO)
