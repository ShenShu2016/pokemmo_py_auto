from __future__ import annotations

import sqlite3
import threading
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class SQLiteDB:
    def __init__(
        self,
        pokeMMO: PokeMMO,
        db_file,
    ):
        self.db_file = db_file
        self.pokeMMO = pokeMMO
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
        column_names = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in range(len(values))])
        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        self.execute_query(query, values)

    def select_data(self, query, parameters=None):
        thread_id = threading.get_ident()
        cursor = self.cursors[thread_id]
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def count_today_released(self):
        today = datetime.now().strftime("%Y-%m-%d")
        query = "SELECT COUNT(*) FROM action WHERE release=1 AND timestamp >= ?"
        parameters = (today,)
        result = self.select_data(query, parameters)
        return result[0][0]

    def count_today_pokeball(self):
        today = datetime.now().strftime("%Y-%m-%d")
        query = "SELECT COUNT(*) FROM action WHERE throw_pokeball=1 AND timestamp >= ?"
        parameters = (today,)
        result = self.select_data(query, parameters)
        return result[0][0]

    def count_today_caught_with31_iv(self):
        today = datetime.now().strftime("%Y-%m-%d")
        query = (
            "SELECT COUNT(*) FROM action WHERE caught_with_31_iv=1 AND timestamp >= ?"
        )
        parameters = (today,)
        result = self.select_data(query, parameters)
        return result[0][0]

    def insert_ball_throw_data(self, ball_type):
        columns = ["throw_pokeball", "ball_type", "timestamp"]
        value = (True, ball_type, self.pokeMMO.encounter_start_time)
        self.insert_data("action", columns, value)

    def insert_release_data(self):
        """
        Inserts a boolean value and timestamp into the 'action' table of the database.
        """
        columns = ["release", "timestamp"]
        value = (True, self.pokeMMO.encounter_start_time)
        self.insert_data("action", columns, value)

    def insert_31_iv_data(self):
        """
        Inserts a boolean value and timestamp into the 'action' table of the database.
        """
        columns = ["caught_with_31_iv", "timestamp"]
        value = (True, self.pokeMMO.encounter_start_time)
        self.insert_data("action", columns, value)


if __name__ == "__main__":
    # 创建SQLiteDB对象
    db = SQLiteDB("pokemmo.sqlite")

    # test count_today_released
    release_count = db.count_today_released()
    print(f"release_count: {release_count}")
    pokeball_used = db.count_today_pokeball()
    print(f"pokeball_used: {pokeball_used}")
    caught_with_31_iv = db.count_today_caught_with31_iv()
    print(f"caught_with_31_iv: {caught_with_31_iv}")
