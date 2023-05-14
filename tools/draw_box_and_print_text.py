import os
import sys
import time
from ctypes import windll

# Get the directory of the current script
current_directory = os.path.dirname(os.path.realpath(__file__))

# Get the parent directory
parent_directory = os.path.dirname(current_directory)

# Add the parent directory to sys.path
sys.path.append(parent_directory)
from main import PokeMMO

if __name__ == "__main__":
    import cv2

    # Make the process DPI-aware
    windll.user32.SetProcessDPIAware()

    # Initialize the PokeMMO class
    pokeMMO = PokeMMO()

    for i in range(20):
        time.sleep(0.2)

        try:
            # Get a screenshot
            image = pokeMMO.get_current_image()
        except Exception as e:
            print(f"Failed to get image: {e}")
            exit(1)

        # Convert the color from BGRA to BGR
        image_color = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        pokeMMO.get_text_from_area_start_from_center(
            image_color,
            box_width=125,
            box_height=25,
            offset_x=0,
            offset_y=104,
        )
    # # Display the image
    # cv2.imshow("Match Template", image_color)
    # cv2.waitKey()

    # Close the image window
    # cv2.destroyAllWindows()
