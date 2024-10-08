import json
import os

# Define the directory to scan and the configuration file
template = "asserts/template"
config_file = "configure.json"
coords_tracking = "asserts/coords_tracking"

# Get a list of all files in the directory
files = os.listdir(template)

# Initialize the dictionary for the new configuration
new_config = {
    "tesseract": "C:/Program Files/Tesseract-OCR/tesseract.exe",
    "pokedex_path": "asserts/clean_pokedex.csv",
}


def init_config_file():
    # Add each file to the new configuration
    for file in files:
        # Only consider .png files
        if file.endswith(".png"):
            # Use the name of the file (without the extension) as the key
            key = os.path.splitext(file)[0]
            # Use the full path to the file as the value
            value = os.path.join(template, file)
            new_config[key + "_path"] = value

    coords_tracking_files = os.listdir(coords_tracking)

    for file in coords_tracking_files:
        # Only consider .png files
        if file.endswith(".csv"):
            # Use the name of the file (without the extension) as the key
            key = os.path.splitext(file)[0]
            # Use the full path to the file as the value
            value = os.path.join(coords_tracking, file)
            new_config[key + "_path"] = value

    # Update the configuration file
    with open(config_file, "w") as f:
        json.dump(new_config, f, indent=4)


if __name__ == "__main__":
    init_config_file()
