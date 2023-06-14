# enemy_status.py
from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from main import PokeMMO

import threading

enemy_hp_bar_coords = {
    1: [(273, 152), (472, 153)],  # Enemy 1 HP coordinates
    2: [(349, 102), (498, 103)],  # Enemy 2 HP coordinates
    3: [(609, 102), (758, 103)],  # Enemy 3 HP coordinates
    4: [(869, 102), (1018, 103)],  # Enemy 4 HP coordinates
    5: [(349, 142), (498, 143)],  # Enemy 5 HP coordinates
    6: [(869, 142), (1018, 143)],  # Enemy 6 HP coordinates
}
enemy_name_coords = {
    1: [(251, 129), (492, 147)],
    2: [(316, 79), (516, 98)],
    3: [(576, 79), (780, 96)],
    4: [(836, 79), (1037, 96)],
    5: [(316, 117), (517, 136)],
    6: [(835, 117), (1037, 136)],
}


def play_music(music_file=r"asserts\unravel.mp3"):
    def _play_music():
        pygame.mixer.init()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    thread = threading.Thread(target=_play_music)
    thread.start()


class EnemyStatus:
    def __init__(self, pokeMMO_instance: PokeMMO):
        self.pokeMMO = pokeMMO_instance
        self.enemy_status_dict = {"enemy_count": 0}
        self.game_status_dict = {}

    def _check_enemy_number(self):
        if self.game_status_dict.get("return_status") == 1:
            self.enemy_status_dict = {"enemy_count": None}
            return

        if self.game_status_dict.get("return_status") in [
            20,
            21,
            22,
            23,
        ] and self.enemy_status_dict.get("enemy_count") in [0, None]:
            self.pokeMMO.set_encounter_start_time()
            hp_BRG_x_y_list = self.pokeMMO.find_items(
                temp_BRG=self.pokeMMO.hp_BRG,
                threshold=0.995,
                max_matches=5,
                top_l=(0, 70),
                bottom_r=(1080, 170),
                img_BRG=self.img_BRG,
            )
            # print(f"hp_BRG_x_y_list: {hp_BRG_x_y_list}")
            if not hp_BRG_x_y_list:
                return
            self.enemy_status_dict["enemy_count"] = len(hp_BRG_x_y_list)

    def _check_enemy_hp_individual(self, enemy_index):
        hp_pct = self.pokeMMO.get_hp_pct(
            enemy_hp_bar_coords[enemy_index][0],
            enemy_hp_bar_coords[enemy_index][1],
            self.img_BRG,
        )
        self.enemy_status_dict[f"enemy_{enemy_index}_hp_pct"] = hp_pct

    def _check_enemy_hp(self):
        if self.game_status_dict.get("return_status") in [
            20,
            21,
            22,
            23,
        ]:
            enemy_count = self.enemy_status_dict["enemy_count"]
            threads = []
            if enemy_count in [3, 5]:
                for i in range(2, enemy_count + 2):
                    thread = threading.Thread(
                        target=self._check_enemy_hp_individual, args=(i,)
                    )
                    thread.start()
                    threads.append(thread)
            elif enemy_count == 1:
                thread = threading.Thread(
                    target=self._check_enemy_hp_individual, args=(1,)
                )
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

    def _check_enemy_name_lv(self):
        # start_time = time.time()
        enemy_count = self.enemy_status_dict["enemy_count"]

        def _process_i(i):
            if (
                f"enemy_{i}_hp_pct" in self.enemy_status_dict
                and f"enemy_{i}_name_Lv" not in self.enemy_status_dict
                and self.enemy_status_dict[f"enemy_{i}_hp_pct"] is not None
            ):
                sex_coords = self.pokeMMO.find_items(
                    temp_BRG=self.pokeMMO.enemy_male_BRG,
                    top_l=enemy_name_coords[i][0],
                    bottom_r=enemy_name_coords[i][1],
                    img_BRG=self.img_BRG,
                    threshold=0.99,
                    max_matches=1,
                )
                if not sex_coords:
                    sex_coords = self.pokeMMO.find_items(
                        temp_BRG=self.pokeMMO.enemy_female_BRG,
                        top_l=enemy_name_coords[i][0],
                        bottom_r=enemy_name_coords[i][1],
                        img_BRG=self.img_BRG,
                        threshold=0.99,
                        max_matches=1,
                    )
                if sex_coords:
                    enemy_name_coords[i] = (
                        enemy_name_coords[i][0],
                        (sex_coords[0][0], enemy_name_coords[i][1][1]),
                    )
                name_Lv_OCR = self.pokeMMO.get_text_from_box_coords(
                    top_l=enemy_name_coords[i][0],
                    bottom_r=enemy_name_coords[i][1],
                    img_BRG=self.img_BRG,
                    config="--psm 7 --oem 3 -c tessedit_char_whitelist=Lv1234567890",
                )

                numeric_string = "".join(filter(str.isdigit, name_Lv_OCR))
                total_int = int(numeric_string)

                if total_int >= 99999 and enemy_count == 1:  # 闪光
                    play_music()
                    pass
                elif total_int >= 99999 and enemy_count > 1:
                    play_music()
                    print("闪光宠出现", name_Lv_OCR, total_int)
                    time.sleep(600)
                    import os

                    os.system("taskkill /f /im python.exe")

                if "Lv" in name_Lv_OCR:
                    self.enemy_status_dict[f"enemy_{i}_name_Lv"] = name_Lv_OCR
                    name_OCR = name_Lv_OCR.split("Lv")[0].strip()
                    lv_orc = name_Lv_OCR.split("Lv")[1].strip()
                    info = self.pokeMMO.pokedex_csv.loc[
                        self.pokeMMO.pokedex_csv["No"] == int(name_OCR)
                    ]
                    if info.empty == False:
                        info_dict = info.to_dict(orient="records")
                        self.enemy_status_dict[f"enemy_{i}_info"] = info_dict[0]
                        # 开始插入数据
                        columns = [
                            "pokedex_number",
                            "level_number",
                            "encounter_number",
                            "timestamp",
                        ]
                        columns_str = ", ".join(columns)
                        values = (
                            int(name_OCR),
                            int(lv_orc),
                            enemy_count,
                            self.pokeMMO.encounter_start_time,
                        )

                        self.pokeMMO.db.insert_data("encounter", columns_str, values)
                    else:
                        info = self.pokeMMO.pokedex_csv.loc[
                            self.pokeMMO.pokedex_csv["No"] == int(999)
                        ]
                        info_dict = info.to_dict(orient="records")
                        self.enemy_status_dict[f"enemy_{i}_info"] = info_dict[0]

                        print(f"{name_OCR} 有可能是闪光")

        threads = []
        enemy_count = self.enemy_status_dict["enemy_count"]
        if enemy_count not in [0, None]:
            if enemy_count == 1:
                i = 1
                t = threading.Thread(
                    target=_process_i,
                    args=(i,),
                )
                t.start()
                threads.append(t)
            else:
                for i in range(2, enemy_count + 2):
                    t = threading.Thread(
                        target=_process_i,
                        args=(i,),
                    )
                    t.start()
                    threads.append(t)

        for t in threads:
            t.join()  # 等待所有线程完成
        self.enemy_status_dict["allChecked"] = True

    def check_enemy_sleep(self):
        # print("检查敌人睡眠状态")
        sleeping_sign_coords_list = self.pokeMMO.find_items(
            temp_BRG=self.pokeMMO.battle_bar_sleep_sign_BRG,
            top_l=(220, 120),
            bottom_r=(492, 150),
            img_BRG=self.img_BRG,
            threshold=0.99,
            max_matches=1,
        )
        # print("sleeping_sign_coords_list", sleeping_sign_coords_list)
        if len(sleeping_sign_coords_list) > 0:
            self.enemy_status_dict["enemy_1_sleeping"] = True
        else:
            self.enemy_status_dict["enemy_1_sleeping"] = False

    def check_my_hp(self):
        my_hp_coords = (939, 360), (1134, 362)

        my_hp_pct = self.pokeMMO.get_hp_pct(
            top_l=my_hp_coords[0], bottom_r=my_hp_coords[1], img_BRG=self.img_BRG
        )
        if my_hp_pct == 100:
            pass
        else:
            self.enemy_status_dict["my_hp_pct"] = my_hp_pct
            self.pokeMMO.action_controller.first_sprit_hp = my_hp_pct

    def check_enemy_status(self):
        self.img_BRG = self.pokeMMO.get_latest_img_BRG()
        self.game_status_dict = self.pokeMMO.get_game_status()
        start_time = time.time()
        self._check_enemy_number()
        check_enemy_number_time = time.time() - start_time
        # print("检查敌人数量使用时间:", time.time() - start_time)
        start_time = time.time()
        self._check_enemy_hp()
        check_enemy_hp_time = time.time() - start_time
        # print("检查敌人血量使用时间:", time.time() - start_time)
        start_time = time.time()
        self._check_enemy_name_lv()
        check_enemy_name_lv_time = time.time() - start_time
        # print("检查敌人名字与等级使用时间:", time.time() - start_time)
        start_time = time.time()
        if self.game_status_dict.get("return_status") in [
            20,
            21,
            22,
            23,
        ]:
            self.check_my_hp()
            self.check_enemy_sleep()

        check_enemy_sleep_time = time.time() - start_time
        # print("enemy_status_dict", self.enemy_status_dict)
        if (
            check_enemy_number_time > 0.1
            or check_enemy_hp_time > 0.1
            or check_enemy_name_lv_time > 0.1
            or check_enemy_sleep_time > 0.1
        ):
            print(
                "检查敌人状态使用时间:",
                "check_enemy_number_time",
                check_enemy_number_time,
                "check_enemy_hp_time",
                check_enemy_hp_time,
                "check_enemy_name_lv_time",
                check_enemy_name_lv_time,
                "check_enemy_sleep_time",
                check_enemy_sleep_time,
            )
        return self.enemy_status_dict


if __name__ == "__main__":
    play_music()
    print("开始")
