from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class PokemmoUI:
    def __init__(self, pokeMMO: PokeMMO):
        self.pokeMMO = pokeMMO

        self.root = tk.Tk()
        self.root.title("PokeMMO Status")

        self.status_label = ttk.Label(self.root, text="Game Status:")
        self.status_label.pack()

        self.state_dict_label = ttk.Label(self.root, text="State Dict:")
        self.state_dict_label.pack()

        self.state_dict_text = tk.Text(self.root, height=10, width=50)
        self.state_dict_text.pack()

        self.stop_button = ttk.Button(
            self.root, text="Stop", command=self.stop_threads_and_exit
        )
        self.stop_button.pack()

        self.update_ui()

    def stop_threads_and_exit(self):
        self.pokeMMO.stop_threads()
        self.root.quit()  # This will close the Tkinter window
        os._exit(0)  # This will terminate the entire Python program

    def update_ui(self):
        game_status = self.pokeMMO.get_game_status()
        state_dict = self.pokeMMO.get_state_dict()

        self.status_label.configure(text=f"Game Status: {game_status}")
        self.state_dict_text.delete(1.0, tk.END)
        self.state_dict_text.insert(tk.END, self.format_state_dict(state_dict))

        self.root.after(1000, self.update_ui)

    def format_state_dict(self, state_dict):
        formatted_text = ""
        for timestamp, state in state_dict.items():
            formatted_text += f"Timestamp: {timestamp}\n"
            formatted_text += f"Address: {state['address']}\n"
            formatted_text += f"Money: {state['money']}\n"
            formatted_text += "\n"
        return formatted_text

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
