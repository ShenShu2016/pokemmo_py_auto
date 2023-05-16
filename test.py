from time import sleep

if __name__ == "__main__":
    from main import PokeMMO

    print("wo lai la ")
    pokeMMO = PokeMMO()
    print("wo lai la ")
    while True:
        enemy_hp_bar_x_y = (274, 151), (471, 155)
        hp_percentage = pokeMMO.get_hp_percentage(
            enemy_hp_bar_x_y[0], enemy_hp_bar_x_y[1]
        )
        print(f"The current HP percentage is {hp_percentage}%")
        sleep(1)
    pokeMMO.start_ui()


# enemy_hp_bar_x_y = (274, 151), (471, 155)  # [253,253,253]


# enemy_name_1in3_x_y = (316, 79), (518, 98)
# enemy_name_2in3_x_y = (576, 79), (780, 96)
# enemy_name_3in3_x_y = (836, 79), (1038, 96)
# enenmy_name_4in5_x_y = (316, 117), (519, 136)
# enenmy_name_5in5_x_y = (835, 117), (1038, 136)


# enemy_hp_1in3_x_y = (329, 97), (346, 110)
# enemy_hp_2in3_x_y = (589, 97), (606, 110)
# enemy_hp_3in3_x_y = (849, 97), (866, 110)
# enemy_hp_4in5_x_y = (329, 137), (345, 150)
# enemy_hp_5in5_x_y = (849, 137), (865, 150)


# bag_page_name = (308, 347), (403, 373)
# bag_poke_ball_icon_x_y = (521, 395), (563, 438)

# battle_option_confirm_x_y = (604, 558), (672, 573)
