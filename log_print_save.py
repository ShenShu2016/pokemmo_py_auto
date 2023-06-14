# enemy_status.py
from __future__ import annotations

import threading
import time
from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO

from collections import deque
from datetime import datetime

import pandas as pd


class LogPrintSave:
    """A class to manage logs, print them to the terminal, and save them to a JSON file."""

    def __init__(self, pokemmo: PokeMMO):
        """Initialize the LogPrintSave class."""
        self.pokemmo = pokemmo
        self.logs = deque(maxlen=200)  # A queue that holds the last 200 logs
        self.data_lock = threading.Lock()  # Added lock for data
        self.last_log = None

    def update_logs(self):
        """Update the logs every 0.3 seconds."""
        print("Starting update_logs")

        # 主线程循环
        while not self.pokemmo.stop_threads_flag:
            try:
                # 获取状态和信息
                game_status = self.pokemmo.get_game_status()
                enemy_status = self.pokemmo.get_enemy_status()
                state_dict = self.pokemmo.get_state_dict()
                coords_status = self.pokemmo.get_coords_status()

                # 获取当前时间戳
                timestamp = time.time()
                formatted_timestamp = datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # 创建新的日志
                new_log = {
                    "game_status": game_status,
                    "enemy_status": enemy_status,
                    "state_dict": state_dict,
                    "coords_status": coords_status,
                    "timestamp": timestamp,
                }

                # 创建不包含'timestamp'的日志，用于比较
                new_log_without_timestamp = {
                    key: value for key, value in new_log.items() if key != "timestamp"
                }

                # 比较新旧日志，如果有变化，将新日志插入数据库，并更新last_log
                if self.last_log is None or new_log_without_timestamp != self.last_log:
                    columns = "game_status, enemy_status, address,money, x_coords,y_coords,map_number_tuple,timestamp"
                    values = (
                        str(new_log["game_status"]),
                        str(new_log["enemy_status"]),
                        str(new_log["state_dict"]["address"]),
                        int(new_log["state_dict"]["money"]),
                        int(new_log["coords_status"]["x_coords"]),
                        int(new_log["coords_status"]["y_coords"]),
                        str(new_log["coords_status"]["map_number_tuple"]),
                        str(formatted_timestamp),
                    )
                    self.pokemmo.db.insert_data("general_status", columns, values)
                    self.last_log = new_log_without_timestamp

                    # 将新日志添加到日志列表中
                    self.logs.append(new_log)

                    # 如果日志数量超过200，删除最旧的日志
                    if len(self.logs) > 200:
                        self.logs.pop(0)

                # 等待0.1秒再次执行
                sleep(0.1)
            except Exception as e:
                print(f"An error occurred in update_logs: {e}")

    def print_logs(self):
        print("Starting print_logs")
        while not self.pokemmo.stop_threads_flag:
            try:
                print(f"\033[31mgame_status: {self.logs[-1]['game_status']}\033[31m")
                print(f"\033[32menemy_status: {self.logs[-1]['enemy_status']}\033[32m")
                print(
                    f"\033[33mcoords_status: {self.logs[-1]['coords_status']}\033[33m"
                )
                print(f"\033[34mstate_dict: {self.logs[-1]['state_dict']}\033[34m")
                sleep(5)
            except Exception as e:
                pass
