# enemy_status.py
from __future__ import annotations

import random
from time import sleep
from typing import TYPE_CHECKING

from auto_strategy.Cerulean_City_FARMING import add_x_y_coords_offset_Cerulean_City
from auto_strategy.FALLARBOR_TOWN_FARMING import add_x_y_coords_offset_FALLARBOR_TOWN
from auto_strategy.Mistralton_City_FARMING import add_x_y_coords_offset_Mistralton_City
from auto_strategy.PETALBURG_CITY_FARMING import add_x_y_coords_offset_PETALBURG_CITY
from auto_strategy.SOOTOPOLIS_CITY_FARMING import add_x_y_coords_offset_SOOTOPOLIS_CITY
from auto_strategy.VERDANTURF_TOWN_FARMING import add_x_y_coords_offset_VERDANTURF_TOWN

if TYPE_CHECKING:
    from main import PokeMMO

import heapq

import numpy as np

from constant import city_info


def default_offset_func(coords):
    # 默认处理函数的逻辑
    return coords


class PathFinder:
    def __init__(self, pokeMMO: PokeMMO):
        """Initialize the LogPrintSave class."""
        self.p = pokeMMO
        self.path = []
        self.keys_and_delays = []

    # 启发式函数（这里使用曼哈顿距离）
    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # 获取邻居节点
    def neighbors(self, node):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
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
                pass
        return result

    # A*算法
    def a_star(self, start, end):
        heap = []
        in_heap = set()
        heapq.heappush(heap, (self.heuristic(start, end), start))
        in_heap.add(start)
        parent = {start: None}
        g_score = {start: 0}
        coords_status = self.p.get_coords()  # 新增：获取初始状态
        current_face_dir = coords_status["face_dir"]  # 新增：获取初始方向
        # 新增：根据初始方向设置 prev_node
        if current_face_dir == 0:  # 往y变大方向
            prev_node = (start[0], start[1] - 1)
        elif current_face_dir == 1:  # 往y变小方向
            prev_node = (start[0], start[1] + 1)
        elif current_face_dir == 2:  # 往x变小方向
            prev_node = (start[0] + 1, start[1])
        elif current_face_dir == 3:  # 往x变大方向
            prev_node = (start[0] - 1, start[1])
        else:
            prev_node = None

        while heap:
            curr = heapq.heappop(heap)[1]
            in_heap.remove(curr)

            if curr == end:
                path = []
                while curr is not None:
                    path.append(curr)
                    curr = parent[curr]
                return path[::-1]

            for next_node in self.neighbors(curr):
                tentative_g_score = g_score[curr] + self.get_base_cost(
                    next_node
                )  # 修改：只计算基本移动成本

                if next_node not in g_score or tentative_g_score < g_score[next_node]:
                    g_score[next_node] = tentative_g_score
                    parent[next_node] = curr
                    if next_node not in in_heap:
                        f_score = tentative_g_score + self.heuristic(next_node, end)
                        if parent[curr] is not None and self.turned(
                            parent[curr], curr, next_node
                        ):
                            f_score += 3  # 修改：在这里添加转弯惩罚
                        heapq.heappush(heap, (f_score, next_node))
                        in_heap.add(next_node)

            prev_node = curr  # 更新前一个节点

        raise ValueError("No path found")
        return None

    # 计算从curr到next_node的基本移动成本
    def get_base_cost(self, next_node):  # 修改：只计算基本移动成本并且删除了curr参数
        base_cost = 1

        # 若下一个点周围一格有障碍物，则增加相应的惩罚值
        x, y = next_node
        if any(
            0 <= a < self.max_y and 0 <= b < self.max_x and self.grid[a][b] == 0
            for a in range(max(0, x), min(self.max_y, x + 1))
            for b in range(max(0, y), min(self.max_x, y + 1))
        ):
            base_cost += 3

        return base_cost

    # 判断是否转弯
    def turned(self, A, B, C):
        return not (A[0] == B[0] == C[0] or A[1] == B[1] == C[1])

    def path_to_keys_and_delays(self, path, transport="bike", end_face_dir=None):
        transport_speed = {"bike": 0.075, "walk": 0.25, "run": 0.16, "surf": 0.1}
        start_delay = {"bike": 0.0, "walk": 0.2, "run": 0, "surf": 0.0}  # 启动延迟
        coords_status = self.p.get_coords()
        current_face_dir = coords_status["face_dir"]
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
                    keys_and_delays[-1][1] + transport_speed[transport],
                )
            else:
                keys_and_delays.append(
                    (key, transport_speed[transport] + start_delay[transport])
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

        total_delay = 0
        default_delay = 2
        keys_and_delays_two_seconds = []
        for key_and_delay in keys_and_delays:
            new_delay = default_delay - total_delay
            if new_delay < 0.1:
                # 如果新的延迟时间小于0.1，设置延迟时间为0.1
                new_delay = 0.1
            if total_delay + key_and_delay[1] > default_delay:
                # 如果加上当前的延迟会超过2秒，那么就只加上足够的延迟以达到2秒
                keys_and_delays_two_seconds.append((key_and_delay[0], new_delay))
                break
            else:
                total_delay += key_and_delay[1]
                keys_and_delays_two_seconds.append(key_and_delay)

        return keys_and_delays_two_seconds

    def get_farthest_point(self, rows, coords_status_with_offset, min_x, min_y):
        origin = np.array(
            [
                coords_status_with_offset["y_coords"] - min_y,
                coords_status_with_offset["x_coords"] - min_x,
            ]
        )
        distances = rows.apply(
            lambda row: self.heuristic((row["y_coords"], row["x_coords"]), origin),
            axis=1,
        )
        farthest_row = rows.loc[distances.idxmax()]
        return farthest_row["y_coords"], farthest_row["x_coords"]

    def go_somewhere(
        self,
        end_point=None,
        city=None,
        style=None,
        end_face_dir=None,
        transport=None,
        pc=False,
    ):  # style random_end_point,solid_end_point
        """end_point: (y, x)"""
        if pc:
            df = self.p.df_dict[f"{city_info[city]['pc_type']}_coords_tracking_csv"]
        else:
            df = self.p.df_dict[f"{city}_coords_tracking_csv"]
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
        # for i in self.grid:
        #     print(i)

        # Set walkable area based on style
        walkable_markers = (
            [1, 2, 66]
            if style in ["farming", "ignore_sprite", "left_right_farming"]
            else [3, 4, 112]
        )
        for marker in walkable_markers:
            mask = df["mark"] == marker
            self.grid[df[mask]["y_coords"], df[mask]["x_coords"]] = 1

        offset_func_mapping = {
            "PETALBURG_CITY": add_x_y_coords_offset_PETALBURG_CITY,
            "FALLARBOR_TOWN": add_x_y_coords_offset_FALLARBOR_TOWN,
            "VERDANTURF_TOWN": add_x_y_coords_offset_VERDANTURF_TOWN,
            "SOOTOPOLIS_CITY": add_x_y_coords_offset_SOOTOPOLIS_CITY,
            "Mistralton_City": add_x_y_coords_offset_Mistralton_City,
            "Cerulean_City": add_x_y_coords_offset_Cerulean_City,
        }

        offset_func = offset_func_mapping.get(city, default_offset_func)

        while True:
            game_status = self.p.get_gs()
            coords_status = self.p.get_coords()
            coords_status_with_offset = offset_func(coords_status)
            if style == "farming":
                selected_rows = df[df["mark"] == 66]
                end_point = self.get_farthest_point(
                    selected_rows, coords_status_with_offset, min_x=min_x, min_y=min_y
                )
            elif style == "left_right_farming":
                y_coords = coords_status_with_offset["y_coords"]
                selected_rows = df[
                    (df["mark"] == 66) & (df["y_coords"] == y_coords - min_y)
                ]
                end_point = self.get_farthest_point(
                    selected_rows, coords_status_with_offset, min_x, min_y
                )
                # print("end_point", end_point)

            # If end_point is reached or enters battle, break the loop
            if (
                coords_status_with_offset["x_coords"] - min_x == end_point[1]
                and coords_status_with_offset["y_coords"] - min_y == end_point[0]
            ):
                break
            if (
                style == "farming"
                or style == "ignore_sprite"
                or style == "left_right_farming"
            ) and game_status[
                "return_status"
            ] >= 20:  # 进入战斗了
                break

            # Update start_point and end_point if farming
            start_point = (
                coords_status_with_offset["y_coords"] - min_y,
                coords_status_with_offset["x_coords"] - min_x,
            )
            # print("start_point", start_point, "end_point", end_point, min_x, min_y)

            # Find path if start_point is within grid
            if 0 <= start_point[0] < self.max_y and 0 <= start_point[1] < self.max_x:
                # print("开始坐标在网格范围内，开始寻找路径...")
                self.path = self.a_star(start=start_point, end=end_point)  #! y在前面
                # print("self.path", self.path, "\033[0m")
                self.pf_move(end_face_dir=end_face_dir, transport=transport)
            else:
                print("开始坐标不在网格范围内，跳过寻找路径")

            sleep(0.001)

    def go_to_nurse(self, city):
        self.go_somewhere(
            city=city,
            end_point=(
                city_info[city]["112_nurse"][1],
                city_info[city]["112_nurse"][0],
            ),
            end_face_dir=1,
            pc=True,
        )
        print("到达了护士那里")
        return True

    def leave_pc_center(self, city):
        self.go_somewhere(
            city=city,
            end_point=(
                city_info[city]["112_out"][0][1],
                city_info[city]["112_out"][0][0],
            ),
            end_face_dir=0,
            pc=True,
        )
        sleep(0.2)
        self.p.controller.key_press("s", 0.5)
        sleep(2)
        coords_status = self.p.get_coords()
        if coords_status["map_number_tuple"] == city_info[city]["map_number"]:
            return True
        else:
            raise Exception("Failed to leave pc center")

    def pf_move(
        self, end_face_dir=None, transport=None
    ):  # 面朝方向移动 w 方向是 s : 0，a: 2, d: 3
        coords_status = self.p.get_coords()

        if transport == None:
            if (
                coords_status["map_number_tuple"][2] == 50
                or coords_status["map_number_tuple"]
                in [(1, 14, 76), (1, 4, 74), (2, 0, 107), (2, 1, 81), (0, 3, 3)]
            ) and coords_status["transport"] not in [1, 11, 65, 75, 7]:
                transport = "bike"
                if coords_status["transport"] not in [10, 74, 6, 2]:
                    self.p.controller.key_press("3", 0.1)

            elif coords_status["transport"] in [1, 11, 75, 65, 7]:
                transport = "surf"
            else:
                transport = "run"
        elif transport == "walk" or transport == "run":
            if coords_status["transport"] in [10, 74, 6, 2]:
                self.p.controller.key_press("3", 0.1)

        self.keys_and_delays = self.path_to_keys_and_delays(
            self.path, transport=transport, end_face_dir=end_face_dir
        )
        # start move
        print(self.keys_and_delays)
        if self.keys_and_delays is not None:
            if transport == "run":
                self.p.controller.key_down("x")
            for key, delay in self.keys_and_delays:
                self.p.controller.key_press(key, delay)
                sleep(0.1)
            if transport == "run":
                self.p.controller.key_up("x")


if __name__ == "__main__":
    from time import sleep

    from main import PokeMMO

    p = PokeMMO()
    sleep(1)
    p.pf.go_somewhere(end_point=(31, 26), end_face_dir=0, city="Cerulean_City")
