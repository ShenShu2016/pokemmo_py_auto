from ctypes import windll

from py_auto import PokeMMO

if __name__ == "__main__":
    import cv2

    pokeMMO = PokeMMO()
    # Make the process DPI-aware
    windll.user32.SetProcessDPIAware()
    image = pokeMMO.get_current_image()

    pokeMMO.get_text_from_area(image, (30, 0), (250, 25))  # city& channel
    pokeMMO.get_text_from_area(
        image,
        (37, 30),
        (130, 45),
        config="--psm 6 -c tessedit_char_whitelist=0123456789",
    )  # current money
