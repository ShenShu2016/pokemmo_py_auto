from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from constant import game_status_dict

if TYPE_CHECKING:
    from main import PokeMMO


class PokemmoUI:
    def __init__(self, pokeMMO: PokeMMO):
        self.pokeMMO = pokeMMO
        self.Hoenn_farming_thread = None

        self.root = tk.Tk()
        self.root.geometry("300x700")  # Set window width and height
        self.root.title("PokeMMO Status")

        # Make the window semi-transparent
        self.root.attributes("-alpha", 0.8)

        # Keep the window always on top
        self.root.attributes("-topmost", 1)

        self.status_label = ttk.Label(
            self.root,
            text="Game Status:",
            font=("Helvetica", 16),
            padding="10 10 10 10",
        )
        self.status_label.grid(column=0, row=0, columnspan=2, sticky=(tk.W, tk.E))
        self.skill_labels = {}
        for skill in {"点到为止": 0, "甜甜香气": 0, "蘑菇孢子": 0, "黑夜魔影": 0, "skill_4": 0}.keys():
            self.skill_labels[skill] = ttk.Label(
                self.root, text="", font=("Helvetica", 14), padding="10 10 10 10"
            )
            self.skill_labels[skill].grid(
                column=0,
                row=len(self.skill_labels) + 4,
                columnspan=2,
                sticky=(tk.W, tk.E),
            )
        # Add labels for x and y coordinates
        self.x_label = ttk.Label(
            self.root, text="", font=("Helvetica", 14), padding="10 10 10 10"
        )
        self.x_label.grid(column=0, row=1, sticky=(tk.W, tk.E))
        self.y_label = ttk.Label(
            self.root, text="", font=("Helvetica", 14), padding="10 10 10 10"
        )
        self.y_label.grid(column=1, row=1, sticky=(tk.W, tk.E))

        self.map_label = ttk.Label(
            self.root, text="", font=("Helvetica", 14), padding="10 10 10 10"
        )
        self.map_label.grid(column=0, row=2, columnspan=2, sticky=(tk.W, tk.E))

        # Add labels for face dir and transport
        self.face_dir_label = ttk.Label(
            self.root, text="", font=("Helvetica", 14), padding="10 10 10 10"
        )
        self.face_dir_label.grid(column=0, row=3, sticky=(tk.W, tk.E))
        self.transport_label = ttk.Label(
            self.root, text="", font=("Helvetica", 14), padding="10 10 10 10"
        )
        self.transport_label.grid(column=1, row=3, sticky=(tk.W, tk.E))

        self.Hoenn_farming_button = tk.Button(
            self.root,
            text="Start Hoenn Farming",
            command=self.toggle_Hoenn_farming,
            fg="white",
            bg="green",
        )
        self.Hoenn_farming_button.grid(
            column=0, row=5, columnspan=2, sticky=(tk.W, tk.E, tk.S), padx=10, pady=10
        )
        self.stop_button = tk.Button(
            self.root,
            text="Stop",
            command=self.stop_threads_and_exit,
            fg="white",
            bg="red",
        )  # Use tk.Button instead of ttk.Button
        self.stop_button.grid(
            column=0, row=4, columnspan=2, sticky=(tk.W, tk.E, tk.S), padx=10, pady=10
        )  # Put the button at the bottom

        self.root.grid_columnconfigure(
            0, weight=1
        )  # Make the column fill the entire window width
        self.root.grid_columnconfigure(
            1, weight=1
        )  # Make the column fill the entire window width
        self.root.grid_rowconfigure(4, weight=1)  # Make the button row expandable

        self.update_ui()

    def update_ui(self):
        game_status = self.pokeMMO.get_game_status()

        # Update the labels with the new values
        coords_status = self.pokeMMO.get_coords_status()
        self.x_label.configure(text=f"X: {coords_status['x_coords']}")
        self.y_label.configure(text=f"Y: {coords_status['y_coords']}")
        self.map_label.configure(text=f"Map: {coords_status['map_number_tuple']}")
        self.face_dir_label.configure(
            text=f"Face direction: {coords_status['face_dir']}"
        )
        self.transport_label.configure(text=f"Transport: {coords_status['transport']}")

        self.status_label.configure(
            text=f"Game Status: {game_status_dict[game_status['return_status']]}"
        )
        for skill, pp in game_status["skill_pp"].items():
            self.skill_labels[skill].configure(text=f"{skill}: {pp}")

        self.root.after(500, self.update_ui)

    def toggle_Hoenn_farming(self):
        if self.Hoenn_farming_thread and self.Hoenn_farming_thread.is_alive():
            self.pokeMMO.auto_strategy_flag = False
            self.Hoenn_farming_button.configure(
                text="Stopping Main Loop...", state=tk.DISABLED
            )
            stop_thread = threading.Thread(target=self.wait_and_reset_button)
            stop_thread.start()
        else:
            self.pokeMMO.auto_strategy_flag = True
            self.Hoenn_farming_thread = threading.Thread(
                target=self.pokeMMO.Hoenn_farming
            )
            self.Hoenn_farming_thread.start()
            self.Hoenn_farming_button.configure(text="Stop Main Loop", bg="red")

    def wait_and_reset_button(self):
        if self.Hoenn_farming_thread and self.Hoenn_farming_thread.is_alive():
            self.Hoenn_farming_thread.join()  # Wait for the thread to finish
        self.Hoenn_farming_thread = None
        self.Hoenn_farming_button.configure(
            text="Start Main Loop", bg="green", state=tk.NORMAL
        )

    def stop_threads_and_exit(self):
        if self.Hoenn_farming_thread and self.Hoenn_farming_thread.is_alive():
            self.pokeMMO.auto_strategy_flag = False
            self.Hoenn_farming_thread.join()
        self.pokeMMO.stop_threads()
        self.root.quit()
        os._exit(0)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Create an instance of the PokeMMO class
    from main import PokeMMO

    pokeMMO = PokeMMO()

    # Create an instance of the PokeMMOUI class
    ui = PokemmoUI(pokeMMO)

    # Run the UI
    ui.run()
