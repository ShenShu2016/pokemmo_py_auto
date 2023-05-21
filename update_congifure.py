import json
import os

# Define the directory to scan and the configuration file
directory = r"C:\Users\SS\Documents\GitHub\pokemmo_py_auto\data"
config_file = r"C:\Users\SS\Documents\GitHub\pokemmo_py_auto\configure.json"

# Get a list of all files in the directory
files = os.listdir(directory)

# Initialize the dictionary for the new configuration
new_config = {"tesseract": "C:/Program Files/Tesseract-OCR/tesseract.exe"}

# Add each file to the new configuration
for file in files:
    # Only consider .png files
    if file.endswith(".png"):
        # Use the name of the file (without the extension) as the key
        key = os.path.splitext(file)[0]
        # Use the full path to the file as the value
        value = os.path.join(directory, file)
        new_config[key + "_path"] = value

# Update the configuration file
with open(config_file, "w") as f:
    json.dump(new_config, f, indent=4)
