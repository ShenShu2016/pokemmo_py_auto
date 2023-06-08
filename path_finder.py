# enemy_status.py
from __future__ import annotations

import time
from typing import TYPE_CHECKING

from auto_strategy.FALLARBOR_TOWN_FARMING import add_x_y_coords_offset_FALLARBOR_TOWN
from auto_strategy.PETALBURG_CITY_FARMING import add_x_y_coords_offset_PETALBURG_CITY
from auto_strategy.SOOTOPOLIS_CITY_FARMING import add_x_y_coords_offset_SOOTOPOLIS_CITY
from auto_strategy.VERDANTURF_TOWN_FARMING import add_x_y_coords_offset_VERDANTURF_TOWN

if TYPE_CHECKING:
    from main import PokeMMO

import heapq

import numpy as np

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
            else:
                # print(f"节点 {next_node} 是障碍物或者超出网格边界")
                pass
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

            # print(f"当前节点: {curr}")  # 打印当前节点

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

                # print(f"检查相邻节点: {next_node}")  # 打印正在检查的相邻节点

        print("完成，没有找到路径")  # 如果没有找到路径，打印消息
        return None

    def path_to_keys_and_delays(self, path, transport="bike", end_face_dir=None):
        transport_speed = {"bike": 0.08, "walk": 0.25, "run": 0.2, "surf": 0.1}
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
                    round(keys_and_delays[-1][1] + transport_speed[transport], 3),
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

        return keys_and_delays[:8]

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

    def go_somewhere(
        self, end_point=None, city="SOOTOPOLIS_CITY", style=None, end_face_dir=None
    ):  # style random_end_point,solid_end_point
        df = self.pokeMMO.df_dict[f"{city}_coords_tracking_csv"]
        df = df.reset_index(drop=True)

        # Convert coords to integer and shift to non-negative range
        df["x_coords"] = df["x_coords"].astype(int)
        df["y_coords"] = df["y_coords"].astype(int)
        min_x = df["x_coords"].min()
        min_y = df["y_coords"].min()
        df["x_coords"] -= min_x
        df["y_coords"] -= min_y
        if end_point is not None:
            end_point = (end_point[0] - min_y, end_point[1] - min_x)
        # Define grid size
        self.max_x = df["x_coords"].max() + 1
        self.max_y = df["y_coords"].max() + 1
        self.grid = np.zeros((self.max_y, self.max_x), dtype=int)

        # Set walkable area based on style
        walkable_markers = [1, 2, 66] if style == "farming" else [3, 4, 112]
        for marker in walkable_markers:
            mask = df["mark"] == marker
            self.grid[df[mask]["y_coords"], df[mask]["x_coords"]] = 1

        # print("网格数据：\n", self.grid)

        offset_func_mapping = {
            "PETALBURG_CITY": add_x_y_coords_offset_PETALBURG_CITY,
            "FALLARBOR_TOWN": add_x_y_coords_offset_FALLARBOR_TOWN,
            "VERDANTURF_TOWN": add_x_y_coords_offset_VERDANTURF_TOWN,
            "SOOTOPOLIS_CITY": add_x_y_coords_offset_SOOTOPOLIS_CITY,
        }
        offset_func = offset_func_mapping.get(city, lambda x: x)

        while True:
            game_status = self.pokeMMO.get_game_status()
            game_status_with_offset = offset_func(game_status)
            if style == "farming":
                random_row = df[df["mark"] == 66].sample(n=1)
                end_point = (
                    random_row["y_coords"].values[0],
                    random_row["x_coords"].values[0],
                )

            # If end_point is reached or enters battle, break the loop
            if (
                game_status_with_offset["x_coords"] - min_x == end_point[1]
                and game_status_with_offset["y_coords"] - min_y == end_point[0]
            ):
                break
            if (
                style == "farming" and game_status_with_offset["return_status"] >= 20
            ):  # 进入战斗了
                break

            # Update start_point and end_point if farming
            start_point = (
                game_status_with_offset["y_coords"] - min_y,
                game_status_with_offset["x_coords"] - min_x,
            )

            # print(f"当前开始坐标: {start_point}, 网格大小: {(self.max_y, self.max_x)}")
            # print("start_point", start_point, "end_point", end_point)

            # Find path if start_point is within grid
            if 0 <= start_point[0] < self.max_y and 0 <= start_point[1] < self.max_x:
                # print("开始坐标在网格范围内，开始寻找路径...")
                self.path = self.a_star(start=start_point, end=end_point)  #! y在前面
                # print("self.path", self.path, "\033[0m")
                self.pf_move(end_face_dir=end_face_dir)
            else:
                print("开始坐标不在网格范围内，跳过寻找路径")
            time.sleep(0.1)

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
            # print(self.path)

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
        if (
            game_status["map_number_tuple"][2] == 50
            or game_status["map_number_tuple"] in [(1, 14, 76), (1, 4, 74)]
        ) and game_status["transport"] not in [1, 11, 65, 75, 7]:
            transport = "bike"
            if game_status["transport"] not in [10, 74, 6]:
                self.pokeMMO.controller.key_press("3", 0.1)

        elif game_status["transport"] in [1, 11, 75, 65, 7]:
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
        # end_point=(10, 16),
        end_face_dir=None,
        city="VERDANTURF_TOWN",
        style="farming",
    )
