from time import sleep

if __name__ == "__main__":
    from constant import target_words_dict
    from main import PokeMMO

    pokeMMO = PokeMMO()

    while True:
        # battle_option_go_back_x_y = (1080, 558), (1142, 575)
        # battle_option_go_back_ORC = pokeMMO.get_text_from_box_coordinate(
        #     battle_option_go_back_x_y[0], battle_option_go_back_x_y[1]
        # )
        # print("get_text_from_box_coordinate", battle_option_go_back_ORC)
        # # remove '\n'
        # is_match, match_ratio = pokeMMO.word_recognizer.compare_with_target(
        #     battle_option_go_back_ORC, target_words_dict["battle_option_go_back_ORC"]
        # )
        # print(f"Match: {is_match}, Match Ratio: {match_ratio}")

        # my_name_ORC = pokeMMO.get_text_from_center(
        #     box_width=125, box_height=25, offset_x=0, offset_y=104, config="--psm 7"
        # )  # Player Name and guild name
        # is_match, match_ratio = pokeMMO.word_recognizer.compare_with_target(
        #     my_name_ORC, target_words=target_words_dict["name_area"], threshold=60
        # )
        # # print(
        # #     f"my_name_ORC: {my_name_ORC}, is_match: {is_match}, match_ratio: {match_ratio}"
        # # )
        # results = pokeMMO.word_recognizer.compare_with_target(
        #     my_name_ORC,
        #     target_words=target_words_dict["name_area"],
        #     threshold=40,
        #     mode="partial_ratio",
        # )
        # for mode, (is_match, match_ratio) in results.items():
        #     print(f"Mode: {mode}, Match: {is_match}, Match Ratio: {match_ratio}")
        #

        black_ratio = pokeMMO.game_status_checker.calculate_black_ratio()
        print(black_ratio)

        sleep(3)
