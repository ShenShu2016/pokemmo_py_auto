# enemy_status.py
from __future__ import annotations

import json
import os
import time
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class LogPrintSave:
    """A class to manage logs, print them to the terminal, and save them to a JSON file."""

    def __init__(self, pokemmo: PokeMMO):
        """Initialize the LogPrintSave class."""
        self.pokemmo = pokemmo
        self.logs = deque(maxlen=50)  # A queue that holds the last 25 logs
        self.data = []

    def update_logs(self):
        """Update the logs every 0.2 seconds."""
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
                memory_status = self.pokemmo.get_memory_status()
                # print(f"memory_status time: {time.time() - start_time}")
                new_record = {
                    "game_status": game_status,
                    "enemy_status": enemy_status,
                    "state_dict": state_dict,
                    "memory_status": memory_status,
                    "timestamp": time.time(),
                }
                self.logs.append(new_record)
                self.data.append(new_record)
                # print(f"Data: {self.data}")  # debug print statement
                print(f"log run time: {time.time() - start_time}")
                time.sleep(0.3)
            except Exception as e:
                print(f"An error occurred in update_logs: {e}")

    def save_logs(self):
        print("Starting save_logs")
        """Save the logs to a JSON file every 5 seconds."""
        while not self.pokemmo.stop_threads_flag:
            try:
                time.sleep(10)
                # Save the logs to a JSON file
                with open(f"logs\logs_{int(time.time())}.json", "w") as file:
                    # json.dump(list(map(lambda deque: list(deque), self.data)), file)
                    for item in self.data:
                        json.dump(item, file)
                        file.write("\n")
                    file.flush()
                    os.fsync(file.fileno())
                # Reset the logs
                self.data = []
            except Exception as e:
                print(f"An error occurred in save_logs: {e}")

    def print_logs(self):
        print("Starting print_logs")
        """Print the logs every 2 seconds."""
        while not self.pokemmo.stop_threads_flag:
            # Print the logs to the terminal
            try:
                # print("\n".join(map(str, self.logs[-1])))
                time.sleep(2)
            except IndexError:
                pass
