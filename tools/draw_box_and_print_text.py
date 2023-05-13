import os
import sys
from ctypes import windll

import cv2

# Get the directory of the current script
current_directory = os.path.dirname(os.path.realpath(__file__))

# Get the parent directory
parent_directory = os.path.dirname(current_directory)

# Add the parent directory to sys.path
sys.path.append(parent_directory)
from py_auto import PokeMMO

pokeMMO = PokeMMO()
# Make the process DPI-aware
windll.user32.SetProcessDPIAware()
image = pokeMMO.get_current_image()
image_color = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
text = pokeMMO.draw_box_and_get_text(
    image_color,
    box_width=200,
    box_height=200,
    color=(0, 0, 255),
    thickness=2,
    offset_x=0,
    offset_y=0,
)
print(f"Text: {text}")
