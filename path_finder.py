# enemy_status.py
from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO

import heapq

import numpy as np
import pandas as pd


class PathFinder:
    def __init__(self, pokeMMO: PokeMMO):
        """Initialize the LogPrintSave class."""
        self.pokeMMO = pokeMMO

    # 启发式函数（这里使用曼哈顿距离）
    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # 获取邻居节点
    def neighbors(self, node):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        result = []
        for direction in directions:
            next_node = (node[0] + direction[0], node[1] + direction[1])
            if (
                0 <= next_node[0] < self.max_y
                and 0 <= next_node[1] < self.max_x
                and self.grid[next_node] == 1
            ):
                result.append(next_node)
        return result

    # A*算法
    def a_star(self, start, end):
        heap = []
        heapq.heappush(heap, (0, start))
        parent = {start: None}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}

        while heap:
            curr = heapq.heappop(heap)[1]

            if curr == end:
                path = []
                while curr is not None:
                    path.append(curr)
                    curr = parent[curr]
                return path[::-1]

            for next_node in self.neighbors(curr):
                tentative_g_score = g_score[curr] + 1
                if next_node not in g_score or tentative_g_score < g_score[next_node]:
                    g_score[next_node] = tentative_g_score
                    f_score[next_node] = tentative_g_score + self.heuristic(
                        next_node, end
                    )
                    parent[next_node] = curr
                    if next_node not in [i[1] for i in heap]:
                        heapq.heappush(heap, (f_score[next_node], next_node))

        return None

    def path_to_keys_and_delays(self, path):
        if path is None:
            return None
        keys_and_delays = []
        for i in range(1, len(path)):
            dy = path[i][0] - path[i - 1][0]
            dx = path[i][1] - path[i - 1][1]
            if dy == 1:
                key = "s"
            elif dy == -1:
                key = "w"
            elif dx == 1:
                key = "d"
            elif dx == -1:
                key = "a"
            else:
                continue

            if keys_and_delays and keys_and_delays[-1][0] == key:
                # 如果与上一个方向相同，则增加对应的按键时间
                keys_and_delays[-1] = (key, keys_and_delays[-1][1] + 0.1)
            else:
                # 如果与上一个方向不同，则添加新的按键和延时
                keys_and_delays.append((key, 0.1))

        return keys_and_delays

    def try_to_find_known_grid(self, start_point, end_point):
        # 以任何方式尝试回到已知的网格，例如，你可以创建一个默认的方向列表
        default_directions = ["w", "d", "s", "a"]  # 上、右、下、左
        keys_and_delays = []

        for direction in default_directions:
            next_point = self.get_next_point(start_point, direction)
            if 0 <= next_point[0] < self.max_y and 0 <= next_point[1] < self.max_x:
                # 发现一个可以回到网格的方向
                keys_and_delays.append((direction, 0.1))  # 假设移动一步需要0.1秒
                break
            else:
                # 如果没有发现可以回到网格的方向，也添加当前方向，希望能找到一个出口
                keys_and_delays.append((direction, 0.1))

        return keys_and_delays

    def get_next_point(self, start_point, direction):
        if direction == "w":
            return (start_point[0] - 1, start_point[1])
        elif direction == "s":
            return (start_point[0] + 1, start_point[1])
        elif direction == "a":
            return (start_point[0], start_point[1] - 1)
        elif direction == "d":
            return (start_point[0], start_point[1] + 1)

    def get_action(self, end_point):
        # Reset the index if it's not a continuous integer sequence starting from 0
        df = self.pokeMMO.SOOTOPOLIS_CITY_coords_tracking_csv

        df = df.reset_index(drop=True)
        df["x_coords"] = df["x_coords"].astype(int)
        df["y_coords"] = df["y_coords"].astype(int)

        # 确定网格的大小
        self.max_x = df["x_coords"].max() + 1
        self.max_y = df["y_coords"].max() + 1

        # 创建网格，所有元素默认为障碍物（0表示障碍物）
        self.grid = np.zeros((self.max_y, self.max_x), dtype=int)

        # 设置可走的区域
        self.grid[
            df[(df["mark"] == 3) | (df["mark"] == 4) | (df["mark"] == 112)]["y_coords"],
            df[(df["mark"] == 3) | (df["mark"] == 4) | (df["mark"] == 112)]["x_coords"],
        ] = 1
        game_status = self.pokeMMO.get_game_status()
        start_point = (game_status["y_coords"], game_status["x_coords"])
        if 0 <= start_point[0] < self.max_y and 0 <= start_point[1] < self.max_x:
            path = self.a_star(start=start_point, end=end_point)  #! y在前面

            result = self.path_to_keys_and_delays(path)
            if result is not None:
                for i in result:
                    print(i)
                return result
        return self.try_to_find_known_grid(start_point, end_point)


if __name__ == "__main__":
    from time import sleep

    from main import PokeMMO

    pokeMMO = PokeMMO()
    sleep(1)
    pathFinder = PathFinder(pokeMMO)
    while True:
        keys_and_delays = pathFinder.get_action((37, 40))
        if keys_and_delays is not None:
            for key, delay in keys_and_delays:
                pokeMMO.controller.key_press(key, delay)

            sleep(5)

    pass
