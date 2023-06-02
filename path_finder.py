# enemy_status.py
from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from auto_strategy.PETALBURG_CITY_FARMING import add_x_y_coords_offset_PETALBURG_CITY

if TYPE_CHECKING:
    from main import PokeMMO

import heapq

import numpy as np
import pandas as pd

from constant import city_info


class PathFinder:
    def __init__(self, pokeMMO: PokeMMO):
        """Initialize the LogPrintSave class."""
        self.pokeMMO = pokeMMO
        self.path = []
        self.keys_and_delays = []

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

    # def path_to_keys_and_delays(self, path, speed=0.1, end_face_dir=None):
    #     game_state = self.pokeMMO.get_game_status()
    #     current_face_dir = game_state["face_dir"]
    #     if path is None:
    #         return None
    #     keys_and_delays = []
    #     for i in range(1, len(path)):
    #         dy = path[i][0] - path[i - 1][0]
    #         dx = path[i][1] - path[i - 1][1]
    #         if dy == 1:
    #             key = "s"
    #         elif dy == -1:
    #             key = "w"
    #         elif dx == 1:
    #             key = "d"
    #         elif dx == -1:
    #             key = "a"
    #         else:
    #             continue

    #         if keys_and_delays and keys_and_delays[-1][0] == key:
    #             # 如果与上一个方向相同，则增加对应的按键时间
    #             keys_and_delays[-1] = (key, keys_and_delays[-1][1] + 0.1)
    #         else:
    #             # 如果与上一个方向不同，则添加新的按键和延时
    #             keys_and_delays.append((key, speed))

    #     return keys_and_delays
    def path_to_keys_and_delays(self, path, transport="bike", end_face_dir=None):
        transport_speed = {"bike": 0.1, "walk": 0.25, "run": 0.2, "surf": 0.1}
        start_delay = {"bike": 0.0, "walk": 0.3, "run": 0.0, "surf": 0.0}  # 启动延迟
        game_state = self.pokeMMO.get_game_status()
        current_face_dir = game_state["face_dir"]
        if path is None:
            return None
        keys_and_delays = []
        for i in range(1, len(path)):
            dy = path[i][0] - path[i - 1][0]
            dx = path[i][1] - path[i - 1][1]
            if dy == 1:
                key = "s"
                new_face_dir = 0
            elif dy == -1:
                key = "w"
                new_face_dir = 1
            elif dx == 1:
                key = "d"
                new_face_dir = 3
            elif dx == -1:
                key = "a"
                new_face_dir = 2
            else:
                continue

            if current_face_dir != new_face_dir:
                # 如果当前面向的方向与下一个方向不同，插入一个转向的动作并更新方向
                keys_and_delays.append((key, 0.03))
                current_face_dir = new_face_dir

            # 在确定方向相同之后再添加移动动作
            if keys_and_delays and keys_and_delays[-1][0] == key:
                keys_and_delays[-1] = (
                    key,
                    round(keys_and_delays[-1][1], 3) + transport_speed[transport],
                )
            else:
                keys_and_delays.append(
                    (key, round(transport_speed[transport] + start_delay[transport], 3))
                )

        # 如果指定了最后的面向方向，添加相应的转向动作
        if end_face_dir is not None and current_face_dir != end_face_dir:
            if end_face_dir == 0:
                keys_and_delays.append(("s", 0.1))
            elif end_face_dir == 1:
                keys_and_delays.append(("w", 0.1))
            elif end_face_dir == 2:
                keys_and_delays.append(("a", 0.1))
            elif end_face_dir == 3:
                keys_and_delays.append(("d", 0.1))

        return keys_and_delays

    def a_star_no_obstacle(self, start, end):
        self.max_x = max(start[1], end[1]) + 1
        self.max_y = max(start[0], end[0]) + 1
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

            for next_node in self.neighbors_no_obstacle(curr):
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

    # 获取邻居节点
    def neighbors_no_obstacle(self, node):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        result = []
        for direction in directions:
            next_node = (node[0] + direction[0], node[1] + direction[1])
            if 0 <= next_node[0] < self.max_y and 0 <= next_node[1] < self.max_x:
                result.append(next_node)
        return result

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

    def go_somewhere(
        self,
        end_point=None,
        city="SOOTOPOLIS_CITY",
        style=None,
        end_face_dir=None,
    ):  # style random_end_point,solid_end_point
        # Reset the index if it's not a continuous integer sequence starting from 0

        df = self.pokeMMO.df_dict[f"{city}_coords_tracking_csv"]

        df = df.reset_index(drop=True)
        df["x_coords"] = df["x_coords"].astype(int)
        df["y_coords"] = df["y_coords"].astype(int)

        # 确定网格的大小
        self.max_x = df["x_coords"].max() + 1
        self.max_y = df["y_coords"].max() + 1

        # 创建网格，所有元素默认为障碍物（0表示障碍物）
        self.grid = np.zeros((self.max_y, self.max_x), dtype=int)
        if style == "farming":
            self.grid[
                df[(df["mark"] == 1) | (df["mark"] == 2)]["y_coords"],
                df[(df["mark"] == 1) | (df["mark"] == 2)]["x_coords"],
            ] = 1  #!地图上1表示可以farming区域

            if city == "SOOTOPOLIS_CITY":
                # 定义区域范围
                min_x, max_x, min_y, max_y = 22, 41, 46, 55
                # 随机选择一个满足条件的mark为1的记录

            elif city == "PETALBURG_CITY":
                min_x, max_x, min_y, max_y = 32, 40, 12, 17

            else:
                random_row = df[df["mark"] == 1].sample(n=1)
                # 获取y_coords和x_coords的值

            filtered_df = df[
                (df["mark"] == 1)
                & (df["x_coords"].between(min_x, max_x))
                & (df["y_coords"].between(min_y, max_y))
            ]
            random_row = filtered_df.sample(n=1)
            y = random_row["y_coords"].values[0]
            x = random_row["x_coords"].values[0]
            end_point = (y, x)
        else:
            # 设置可走的区域
            self.grid[
                df[(df["mark"] == 3) | (df["mark"] == 4) | (df["mark"] == 112)][
                    "y_coords"
                ],
                df[(df["mark"] == 3) | (df["mark"] == 4) | (df["mark"] == 112)][
                    "x_coords"
                ],
            ] = 1

        while end_point:
            game_status=self.pokeMMO.get_game_status()
            if city == "PETALBURG_CITY":
                game_status = add_x_y_coords_offset_PETALBURG_CITY(
                    game_status
                )


            if (
                game_status["x_coords"] == end_point[1]
                and game_status["y_coords"] == end_point[0]
            ):
                break
            if style == "farming" and game_status["return_status"] >= 20:  # 进入战斗了
                break
            start_point = (game_status["y_coords"], game_status["x_coords"])
            if 0 <= start_point[0] < self.max_y and 0 <= start_point[1] < self.max_x:
                self.path = self.a_star(start=start_point, end=end_point)  #! y在前面
                self.pf_move(end_face_dir=end_face_dir)
            time.sleep(0.1)

        # return self.try_to_find_known_grid(start_point, end_point)

    def go_to_nurse(self, city="SOOTOPOLIS_CITY"):
        while True:
            game_status = self.pokeMMO.get_game_status()
            if (
                game_status["x_coords"] == city_info[city]["112_nurse"][0]
                and game_status["y_coords"] == city_info[city]["112_nurse"][1]
                and game_status["face_dir"] == city_info[city]["112_nurse"][2]
            ):
                break
            self.path = self.a_star_no_obstacle(
                (game_status["y_coords"], game_status["x_coords"]),
                (city_info[city]["112_nurse"][1], city_info[city]["112_nurse"][0]),
            )
            print(self.path)

            self.pf_move(end_face_dir=city_info[city]["112_nurse"][2])

            time.sleep(0.5)  # 等一会儿才能知道到底到了没到
        print("到达了护士那里")
        return True

    def leave_pc_center(self, city="SOOTOPOLIS_CITY"):
        while True:
            game_status = self.pokeMMO.get_game_status()
            if (
                game_status["x_coords"] == city_info[city]["112_out"][0][0]
                and game_status["y_coords"] == city_info[city]["112_out"][0][1]
                and game_status["face_dir"] == city_info[city]["112_out"][0][2]
            ):
                break
            self.path = self.a_star_no_obstacle(
                start=(game_status["y_coords"], game_status["x_coords"]),
                end=(
                    city_info[city]["112_out"][0][1],
                    city_info[city]["112_out"][0][0],
                ),
            )
            print(self.path)

            self.pf_move(end_face_dir=city_info[city]["112_out"][0][2])
            time.sleep(0.5)
            self.pokeMMO.controller.key_press("s", 0.2)
            time.sleep(2)
            game_status = self.pokeMMO.get_game_status()
            if game_status["map_number_tuple"] == city_info[city]["map_number"]:
                return True
            else:
                raise Exception("Failed to leave pc center")

    def pf_move(self, end_face_dir=None):  # 面朝方向移动 w 方向是 s : 0，a: 2, d: 3
        game_status = self.pokeMMO.get_game_status()

        transport = None
        if game_status["map_number_tuple"][2] == 50 and game_status[
            "transport"
        ] not in [1, 11]:
            transport = "bike"
            if game_status["transport"] != 10:
                self.pokeMMO.controller.key_press("3", 0.1)

        elif game_status["transport"] in [1, 11]:
            transport = "surf"

        elif game_status["map_number_tuple"][2] != 50:
            transport = "walk"

        self.keys_and_delays = self.path_to_keys_and_delays(
            self.path, transport=transport, end_face_dir=end_face_dir
        )
        # start move
        print(self.keys_and_delays)
        if self.keys_and_delays is not None:
            for key, delay in self.keys_and_delays:
                self.pokeMMO.controller.key_press(key, delay)
                time.sleep(0.1)


if __name__ == "__main__":
    from time import sleep

    from main import PokeMMO

    pokeMMO = PokeMMO()
    sleep(1)
    pokeMMO.pf.go_somewhere(
        end_point=None,
        end_face_dir=None,
        city="SOOTOPOLIS_CITY",
        style="farming",
    )
