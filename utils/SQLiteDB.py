import sqlite3
import threading


class SQLiteDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connections = {}
        self.cursors = {}
        self.thread_ids = set()  # 存储线程标识符的集合
        self.connect()
        self.create_general_status_table()
        self.create_encounter_table()
        self.create_action_table()

    def connect(self):
        thread_id = threading.get_ident()
        if thread_id not in self.connections:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            self.connections[thread_id] = conn
            self.cursors[thread_id] = cursor
            self.thread_ids.add(thread_id)

    def disconnect(self):
        thread_id = threading.get_ident()
        if thread_id in self.thread_ids:
            self.cursors[thread_id].close()
            self.connections[thread_id].close()
            del self.cursors[thread_id]
            del self.connections[thread_id]
            self.thread_ids.remove(thread_id)

    def execute_query(self, query, parameters=None):
        thread_id = threading.get_ident()
        # If the thread does not have a connection, create one.
        if thread_id not in self.thread_ids:
            self.connect()
        cursor = self.cursors[thread_id]
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        self.connections[thread_id].commit()

    def create_general_status_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS general_status (
            game_status TEXT,
            enemy_status TEXT,
            address TEXT,
            money INTEGER,
            x_coords INTEGER,
            y_coords INTEGER,
            map_number_tuple TEXT,
            timestamp TEXT
        )
        """
        self.execute_query(query)

    def create_encounter_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS encounter (
            pokedex_number INTEGER,
            level_number INTEGER,
            encounter_number INTEGER,
            timestamp TEXT
        )
        """
        self.execute_query(query)

    def create_action_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS action (
            throw_pokeball BOOLEAN,
            ball_type TEXT,
            caught_with_31_iv BOOLEAN,
            release BOOLEAN,
            message TEXT,
            timestamp TEXT
        )
        """
        self.execute_query(query)

    def insert_data(self, table_name, columns, values):
        placeholders = ", ".join(["?" for _ in range(len(values))])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, values)

    def select_data(self, table_name, columns="*", condition=None):
        query = f"SELECT {columns} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.execute_query(query)
        thread_id = threading.get_ident()
        rows = self.cursors[thread_id].fetchall()
        return rows


if __name__ == "__main__":
    # 创建SQLiteDB对象
    db = SQLiteDB("pokemmo.sqlite")

    # 定义要插入的数据
    game_status = {
        "return_status": 1,
        "check_pokemon_summary": (False, []),
        "x_coords": 108,
        "y_coords": 282,
        "map_number_tuple": (2, 1, 81),
        "face_dir": 3,
        "transport": 0,
        "battle_time_passed": None,
        "skill_pp": {"点到为止": 0, "甜甜香气": 0, "蘑菇孢子": 0},
    }
    enemy_status = {"enemy_count": None}
    state_dict = {"address": "Route 7 Ch. 3\n", "money": "86532\n"}
    memory_coords = {
        "x_coords": 108,
        "y_coords": 282,
        "map_number": (2, 1, 81),
        "face_dir": 1,
        "transport": 0,
    }
    memory_battle_status = {
        "player_info_not_sure_address": 3937488048,
        "battle_instance_address": 0,
        "battle_time_passed": None,
        "battle_option_ready": None,
    }
    timestamp = 1686329023.1261268

    # 将数据插入到general_status表中
    columns = "game_status, enemy_status, state_dict, memory_coords, memory_battle_status, timestamp"
    values = (
        str(game_status),
        str(enemy_status),
        str(state_dict),
        str(memory_coords),
        str(memory_battle_status),
        str(timestamp),
    )
    db.insert_data("general_status", columns, values)
