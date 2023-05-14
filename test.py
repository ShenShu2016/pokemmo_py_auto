from time import sleep

from keyboard_message import KeyPresser
from py_auto import PokeMMO

pokeMMO = PokeMMO()

pokeMMO.start_threads()
sleep(1)
# pokeMMO.detect_and_draw_edges()

# while True:
#     sleep(1)
#     pokeMMO.find_items(
#         image_normal=pokeMMO.get_current_image_normal(),
#         template_color=pokeMMO.battle_option_color,
#         # display=True,
#         threshold=0.94,
#     )
# pokeMMO.get_box_coordinate_from_center(
#     # image_normal=pokeMMO.get_current_image_normal(),
#     box_width=65,
#     box_height=65,
#     color=(0, 0, 255),
#     thickness=2,
#     offset_x=0,
#     offset_y=65,
#     display=True,
# )

keyPresser = KeyPresser(pokeMMO.handle)
result = pokeMMO.find_items(
    image_normal=pokeMMO.get_current_image_normal(),
    template_color=pokeMMO.Pokemon_Summary_Exit_Button_color,
    threshold=0.99,
    max_matches=5,
    display=True,
)
print(result)
# for i in result:
#     keyPresser.click_at(i[0], i[1])
#     sleep(1)
