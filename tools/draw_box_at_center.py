import os
import sys
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

    try:
        # Get a screenshot
        image = pokeMMO.get_current_image()
    except Exception as e:
        print(f"Failed to get image: {e}")
        exit(1)

    # Convert the color from BGRA to BGR
    image_color = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    # Draw a custom box at the center of the image, moved 50 pixels to the right and 100 pixels up
    # start_point, end_point = pokeMMO.draw_custom_box(
    #     image_color, box_width=125, box_height=25, offset_x=0, offset_y=100
    # )
    # Draw a custom box and get the coordinates of the corners
    # print(f"Top-left corner: {start_point}")
    # print(f"Bottom-right corner: {end_point}")
    pokeMMO.draw_box_and_get_text(
        image_color,
        box_width=125,
        box_height=25,
        color=(0, 0, 255),
        thickness=2,
        offset_x=0,
        offset_y=104,
    )

    # Display the image
    cv2.imshow("Match Template", image_color)
    cv2.waitKey()

    # Close the image window
    cv2.destroyAllWindows()
