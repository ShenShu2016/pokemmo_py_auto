# File: image_processor.py

import cv2
import pytesseract


class ImageProcessor:
    """A class to handle image processing and OCR."""

    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

    def draw_custom_box(
        self,
        image,
        box_width=200,
        box_height=200,
        color=(0, 0, 255),
        thickness=2,
        offset_x=0,
        offset_y=0,
    ):
        """Draw a box on the image and get the text from the area inside the box."""
        height, width, _ = image.shape
        center_x, center_y = (width // 2) + offset_x, (height // 2) - offset_y

        # Calculate the top-left and bottom-right points of the rectangle
        start_point = (center_x - box_width // 2, center_y - box_height // 2)
        end_point = (center_x + box_width // 2, center_y + box_height // 2)

        # Draw the rectangle on the image
        cv2.rectangle(image, start_point, end_point, color, thickness)

        # Return the coordinates of the top-left and bottom-right corners
        return start_point, end_point

    def get_text_from_area(
        self, image, top_left, bottom_right, config="--psm 6", lang="eng"
    ):
        # Extract the area from the image
        area = image[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]

        # Convert the area to grayscale
        gray = cv2.cvtColor(area, cv2.COLOR_BGRA2GRAY)

        # Recognize the text in the area
        text = pytesseract.image_to_string(gray, config=config, lang=lang)
        print(f"Text: {text}")

        return text
