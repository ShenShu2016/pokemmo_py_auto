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
        self.p = pokeMMO

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
        skills = ["点到为止", "甜甜香气", "蘑菇孢子", "黑夜魔影", "skill_4"]
        self.skill_labels = {}

        for index, skill in enumerate(skills):
            self.skill_labels[skill] = ttk.Label(
                self.root, text="", font=("Helvetica", 12), padding="5 5 5 5"
            )
            self.skill_labels[skill].grid(
                column=index % 2,
                row=7 + index // 2,
                sticky=(tk.W, tk.E),
            )
        self.xy_label = ttk.Label(
            self.root, text="坐标: (x , y)", font=("Helvetica", 12), padding="5 5 5 5"
        )

        self.face_dir_label = ttk.Label(
            self.root, text="", font=("Helvetica", 12), padding="5 5 5 5"
        )
        self.xy_label.grid(column=0, row=1, sticky=(tk.W, tk.E))
        self.face_dir_label.grid(column=1, row=1, sticky=(tk.W, tk.E))
        # For map and transport:
        self.map_label = ttk.Label(
            self.root, text="", font=("Helvetica", 12), padding="5 5 5 5"
        )

        self.transport_label = ttk.Label(
            self.root, text="", font=("Helvetica", 12), padding="5 5 5 5"
        )
        self.map_label.grid(column=0, row=2, sticky=(tk.W, tk.E))
        self.transport_label.grid(column=1, row=2, sticky=(tk.W, tk.E))

        self.farming_buttons = {}
        button_names = ["Unova", "Hoenn_LV_up", "Hoenn", "Kanto", "Attack_EV_Kanto"]
        for index, farming in enumerate(button_names):
            self.farming_buttons[farming] = tk.Button(
                self.root,
                text=f"开始 {farming}",
                command=lambda farming=farming: self.toggle_farming(farming),
                fg="white",
                bg="green",
            )
            self.farming_buttons[farming].grid(
                column=index % 2,
                row=10 + index // 2,
                sticky=(tk.W, tk.E, tk.S),
                padx=2,
                pady=2,
            )

        self.stop_button = tk.Button(
            self.root,
            text="Stop",
            command=self.stop_threads_and_exit,
            fg="white",
            bg="red",
        )  # Use tk.Button instead of ttk.Button
        self.stop_button.grid(
            column=0, row=3, columnspan=2, sticky=(tk.W, tk.E, tk.S), padx=10, pady=10
        )

        self.root.grid_columnconfigure(
            0, weight=1
        )  # Make the column fill the entire window width
        self.root.grid_columnconfigure(
            1, weight=1
        )  # Make the column fill the entire window width
        # self.root.grid_rowconfigure(4, weight=1)  # Make the button row expandable
        self.released_label = ttk.Label(
            self.root, text="", font=("Helvetica", 12), padding="5 5 5 5"
        )

        self.pokeball_label = ttk.Label(
            self.root, text="", font=("Helvetica", 12), padding="5 5 5 5"
        )

        self.caught_iv_label = ttk.Label(
            self.root, text="", font=("Helvetica", 12), padding="5 5 5 5"
        )
        self.released_label.grid(row=5, columnspan=2, sticky=(tk.W, tk.E))

        self.pokeball_label.grid(row=4, columnspan=2, sticky=(tk.W, tk.E))
        self.caught_iv_label.grid(row=6, columnspan=2, sticky=(tk.W, tk.E))
        self.update_ui()
        self.update_db()

    def update_db(self):
        # Update the new labels with data from the database
        pokeballs_today = self.p.db.count_today_pokeball()
        self.pokeball_label.configure(text=f"今天用掉的精灵球: {pokeballs_today}")
        released_today = self.p.db.count_today_released()
        self.released_label.configure(text=f"今天放掉的精灵: {released_today}")

        caught_iv_today = self.p.db.count_today_caught_with31_iv()
        self.caught_iv_label.configure(text=f"今天抓到的lv31素材: {caught_iv_today}")

        self.root.after(5000, self.update_db)  # Refresh every 5 seconds

    def update_ui(self):
        game_status = self.p.get_gs()

        # Update the labels with the new values
        coords_status = self.p.get_coords()
        self.xy_label[
            "text"
        ] = f"坐标: ({coords_status['x_coords']} , {coords_status['y_coords']})"
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

        self.root.after(500, self.update_ui)  # Refresh every 500 ms

    def toggle_farming(self, farming):
        # If another farming thread is running, stop it
        for other_farming in [
            "Unova",
            "Hoenn_LV_up",
            "Hoenn",
            "Kanto",
            "Attack_EV_Kanto",
        ]:
            if (
                other_farming != farming
                and hasattr(self, f"{other_farming}_thread")
                and getattr(self, f"{other_farming}_thread")
                and getattr(self, f"{other_farming}_thread").is_alive()
            ):
                setattr(self.p, "auto_strategy_flag", False)
                self.farming_buttons[other_farming].configure(
                    text=f"Stopping {other_farming} Farming...", state=tk.DISABLED
                )
                stop_thread = threading.Thread(
                    target=self.wait_and_reset_button, args=(other_farming,)
                )
                stop_thread.start()

        if (
            hasattr(self, f"{farming}_thread")
            and getattr(self, f"{farming}_thread")
            and getattr(self, f"{farming}_thread").is_alive()
        ):
            setattr(self.p, "auto_strategy_flag", False)
            self.farming_buttons[farming].configure(
                text=f"Stopping {farming} Farming...", state=tk.DISABLED
            )
            stop_thread = threading.Thread(
                target=self.wait_and_reset_button, args=(farming,)
            )
            stop_thread.start()
        else:
            setattr(self.p, "auto_strategy_flag", True)
            setattr(
                self,
                f"{farming}_thread",
                threading.Thread(target=getattr(self.p, f"{farming}_farming")),
            )
            getattr(self, f"{farming}_thread").start()
            self.farming_buttons[farming].configure(
                text=f"Stop {farming} Farming", bg="red"
            )

    def wait_and_reset_button(self, farming):
        if (
            getattr(self, f"{farming}_thread")
            and getattr(self, f"{farming}_thread").is_alive()
        ):
            getattr(self, f"{farming}_thread").join()  # Wait for the thread to finish
        setattr(self, f"{farming}_thread", None)
        self.farming_buttons[farming].configure(
            text=f"Start {farming} Farming", bg="green", state=tk.NORMAL
        )

    def stop_threads_and_exit(self):
        for farming in ["Unova", "Hoenn_LV_up", "Hoenn", "Kanto", "Attack_EV_Kanto"]:
            if (
                hasattr(self, f"{farming}_thread")
                and getattr(self, f"{farming}_thread")
                and getattr(self, f"{farming}_thread").is_alive()
            ):
                setattr(self.p, f"{farming}_farming_flag", False)
                getattr(self, f"{farming}_thread").join()
        self.p.stop_threads()
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
