from ctypes import windll

import cv2

from py_auto import PokeMMO

if __name__ == "__main__":
    # Make the process DPI-aware
    windll.user32.SetProcessDPIAware()

    # Initialize the PokeMMO class
    pokeMMO = PokeMMO()

    try:
        pokeMMO.find_items(
            r"C:\Users\Shen\Documents\GitHub\pokemmo_py_auto\data\Pokemon_Summary_Exit_Button.png"
        )
    except Exception as e:
        print(f"Failed to find items: {e}")
        exit(1)

    # Close the image window
    cv2.destroyAllWindows()
