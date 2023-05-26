# enemy_status.py
from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO

import pandas as pd


class LogPrintSave:
    """A class to manage logs, print them to the terminal, and save them to a JSON file."""

    def __init__(self, pokemmo: PokeMMO):
        """Initialize the LogPrintSave class."""
        self.pokemmo = pokemmo
        self.logs = []  # A queue that holds the last 25 logs
        self.data = []
        self.data_lock = threading.Lock()  # Added lock for data

    def update_logs(self):
        """Update the logs every 0.3 seconds."""
        print("Starting update_logs")
        while not self.pokemmo.stop_threads_flag:
            try:
                start_time = time.time()
                # with self.pokemmo.game_status_lock:
                game_status = self.pokemmo.get_game_status()
                # print(f"game_status time: {time.time() - start_time}")
                enemy_status = self.pokemmo.get_enemy_status()
                # print(f"enemy_status time: {time.time() - start_time}")
                state_dict = self.pokemmo.get_state_dict()
                # print(f"state_dict time: {time.time() - start_time}")
                memory_coords = self.pokemmo.get_memory_coords_status()
                # print(f"memory_coords time: {time.time() - start_time}")
                memory_battle_status = self.pokemmo.get_memory_battle_status()

                new_log = {
                    "game_status": game_status,
                    "enemy_status": enemy_status,
                    "state_dict": state_dict,
                    "memory_coords": memory_coords,
                    "memory_battle_status": memory_battle_status,
                    "timestamp": time.time(),
                }

                with self.data_lock:  # Added lock
                    self.logs.append(new_log)
                    self.data.append(new_log)
                # print(f"Data: {self.data}")  # debug print statement
                # print(f"log run time: {time.time() - start_time}")
                time.sleep(0.1)
            except Exception as e:
                print(f"An error occurred in update_logs: {e}")

    def save_logs(self):
        print("Starting save_logs")
        """Save the logs to a JSON file every 5 seconds."""
        while not self.pokemmo.stop_threads_flag:
            try:
                time.sleep(30)

                with self.data_lock:  # Lock to copy the data
                    data_copy = self.data.copy()  # Copy the data
                    self.data = []  # Clear the original data

                if data_copy:  # Save the copied data
                    # Convert list of dictionaries to DataFrame
                    df = pd.DataFrame(data_copy)

                    # Save the logs to a CSV file
                    df.to_csv(f"logs\logs_{int(time.time())}.csv", index=False, sep=";")
            except Exception as e:
                print(f"An error occurred in save_logs: {e}")

    def print_logs(self):
        print("Starting print_logs")
        """Print the logs every 2 seconds."""
        while not self.pokemmo.stop_threads_flag:
            # Print the logs to the terminal
            try:
                # print("\n".join(map(str, self.logs[-1])))
                # os.system("cls" if os.name == "nt" else "clear")  # Clear the terminal
                print(f"game_status: {self.logs[-1]['game_status']}")
                print(f"enemy_status: {self.logs[-1]['enemy_status']}")
                # print(f"state_dict: {self.logs[-1]['state_dict']}")
                # print(f"memory_coords: {self.logs[-1]['memory_coords']}")
                # print(f'memory_battle_status: {self.logs[-1]["memory_battle_status"]}')

                time.sleep(2)
            except Exception as e:
                pass
