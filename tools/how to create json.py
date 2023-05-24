import json
import time
from datetime import datetime

# Get current time and format it as a string
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create a new filename for each run
filename = f"data_{current_time}.json"

data_list = []  # Initialize an empty list to store data dictionaries

while True:
    # Update your dictionary
    self.memory_info_dict = {
        "x_coords": self.x_coords,
        "y_coords": self.y_coords,
        "map_number": (int(data[4 + 80]), data[4 + 80 + 2], data[4 + 80 + 1]),
        "face_dir": self.face_dir,
        "transport": self.transport,
        "timestamp": datetime.now().isoformat(),
        # You can add other keys here as needed
    }

    # Append new data to data list
    data_list.append(self.memory_info_dict)

    # Write data list to JSON file
    with open(filename, "w") as outfile:
        json.dump(data_list, outfile)

    time.sleep(5)  # wait for 5 seconds
