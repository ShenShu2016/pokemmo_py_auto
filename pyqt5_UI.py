from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from main import PokeMMO

if TYPE_CHECKING:
    from main import PokeMMO


class MainWindow(QMainWindow):
    def __init__(self, pokeMMO):
        super().__init__()

        self.pokeMMO = pokeMMO

        self.setWindowTitle("PokeMMO Status")

        self.status_label = QLabel()
        self.state_dict_text = QTextEdit()

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_threads)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.state_dict_text)
        layout.addWidget(self.stop_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.update_ui()

    def stop_threads(self):
        self.pokeMMO.stop_threads()
        self.close()  # This will close the PyQt window

    def update_ui(self):
        game_status = self.pokeMMO.get_game_status()
        state_dict = self.pokeMMO.get_state_dict()

        self.status_label.setText(f"Game Status: {game_status}")
        self.state_dict_text.setPlainText(str(state_dict))

        # update the UI every 500 ms
        QTimer.singleShot(500, self.update_ui)


def main():
    pokeMMO = PokeMMO()

    app = QApplication([])

    main_win = MainWindow(pokeMMO)
    main_win.show()

    app.exec_()


if __name__ == "__main__":
    main()
