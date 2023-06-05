import os
import sys

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)
import json
import struct
import time

import pymem
from capstone import *
from pymem.pattern import pattern_scan_all

from utils.main.window_manager import Window_Manager


def format_address(address, length=8):
    reversed_bytes = address.to_bytes(length, byteorder="little")
    reversed_formatted = " ".join(f"{b:02X}" for b in reversed_bytes)
    return reversed_formatted


def to_signed_32_bit_le(i):
    return struct.pack("<i", i)


def calculate_jmp_offset(jmp_addr, target_addr):
    offset = target_addr - (jmp_addr + 5)
    return offset


def split_bytes_to_int(data, start, end):
    converted = int.from_bytes(data[start:end], byteorder="little")
    return converted


def analyze_shellcode(battle_instance_data, chunk_size):
    if chunk_size != 4:
        raise ValueError("This function only accepts chunks of size 4")

    chunks = [
        battle_instance_data[i : i + chunk_size]
        for i in range(0, len(battle_instance_data), chunk_size)
    ]  # split into each chunk

    print("==========================")
    for i, chunk in enumerate(chunks):
        hex_values = [hex(byte)[2:].zfill(2).upper() for byte in chunk]

        # Convert each byte to decimal
        dec1_values = [str(byte).rjust(3, " ") for byte in chunk]

        # Convert each 2 bytes to decimal and hexadecimal
        dec2_values = [
            str(int.from_bytes(chunk[j : j + 2], "little")).rjust(5, " ")
            for j in range(0, len(chunk), 2)
        ]
        hex2_values = [
            hex(int.from_bytes(chunk[j : j + 2], "little"))[2:]
            .zfill(4)
            .upper()
            .rjust(5, " ")
            for j in range(0, len(chunk), 2)
        ]

        # Convert 4 bytes to hexadecimal
        hex4_value = hex(int.from_bytes(chunk, "little"))[2:].zfill(8).upper()

        print(
            f"Position {str(i*chunk_size).zfill(2)}: 1-byte DEC: {' '.join(dec1_values)} 2-byte DEC: {' '.join(dec2_values)} 2-byte HEX: {' '.join(hex2_values)} 4-byte HEX: {hex4_value} RAW: {' '.join(hex_values)}"
        )


class MemoryInjector_BattleInfo:
    """This is a class for injecting memory into the target process.
    return: {'enemy_count': 1, 'enemy_1_sleeping': False, 'enemy_1_hp_pct': 2.0, 'enemy_1_name_Lv': '129Lv33\n', 'enemy_1_info':
    {'No': 129, 'Pokemon': 'Magikarp', 'Hp': 20, 'Gender': 1, 'CatchRate': 255, 'Types': 'Water/', 'CatchMethod': 1, 'Chinese': '鲤鱼王'}}
    """

    def __init__(self):
        self.target_process = "javaw.exe"
        self.pattern = b"\\x45\\x8B\\x9A\\x98\\x00\\x00\\x00"
        self.process_name = "Battle_Memory_Injector"
        self.offset = 0
        self.pm = pymem.Pymem(self.target_process)
        self.window_id = Window_Manager().get_window_id()
        self.memory_info_dict = {}

        # Adding a path to your json file
        self.json_file_path = "battle_memory_injector.json"
        self.aob_hex_list_len = 7  # 注入那条指令的长度
        self.aob_address_list = []
        self.aob_hex_list = []
        self.aob_address = 0
        self.bad_newmen_18 = []
        self.TR = None
        self.newmem = None
        # Try to read the stored values from the json file
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, "r") as json_file:
                data = json.load(json_file)
                if data.get("window_id") != self.window_id:
                    print("window_id not match")
                    self.aob_scan()

                else:
                    self.aob_address = data.get("aob_address", 0)
                    self.TR = data.get("TR", None)
                    self.newmem = data.get("newmem", None)
                    print(
                        f"Read data from json file. aob_address: {self.aob_address}, TR: {self.TR}, newmem: {self.newmem}"
                    )
                    # Try to read data

                    result = self.check_data_right()
                    if result:
                        print(
                            f"{self.process_name} Reading data succeeded with stored addresses. aob_address: {self.aob_address}, TR: {self.TR}, newmem: {self.newmem}"
                        )
                    else:
                        print("data not right")
                        self.aob_scan()

        else:
            self.aob_scan()

    def aob_scan(self):
        is_found = False
        while not is_found:
            try:
                self.aob_address_list = pattern_scan_all(
                    handle=self.pm.process_handle,
                    pattern=self.pattern,
                    return_multiple=True,
                )
            except:
                print("scan error")
                continue
            for i in self.aob_address_list:
                self.aob_address = i + self.offset  # 必定要偏移
                self.aob_hex_list = [
                    hex(b)[2:].zfill(2).upper()
                    for b in self.pm.read_bytes(self.aob_address, self.aob_hex_list_len)
                ]
                # print("aob_hex_list:", self.aob_hex_list, self.aob_address)
                if i in self.bad_newmen_18:
                    # print("bad_newmen_18")
                    continue
                try:
                    self.inject_memory()
                    result = self.check_data_right()  #! 找到了基本就是对的
                    if result:
                        with open(self.json_file_path, "w") as json_file:
                            json.dump(
                                {
                                    "aob_address": self.aob_address,
                                    "TR": self.TR,
                                    "newmem": self.newmem,
                                    "window_id": self.window_id,
                                    "timestamp": time.time(),  # current timestamp
                                },
                                json_file,
                            )

                        print(
                            f"Injected {self.process_name}, aob_address: {self.aob_address}, TR: {self.TR}, newmem: {self.newmem}, aob_hex_list: {self.aob_hex_list}"
                        )
                        is_found = True
                except Exception as e:
                    print(e)
                    continue

            # print("aob_address_list:", self.aob_address_list)
            # if len(self.aob_address_list) >= 1:
            #     print(f"{self.process_name}aob_address_list:", self.aob_address_list)
            #     return
            # if len(self.aob_address_list) < 1:
            #     print(f"waiting for AOB {self.process_name} appear, retrying...")
            #     time.sleep(1)

    def try_the_aob(self):
        print("Trying the aob")
        print("aob_address_list:", self.aob_address_list)
        for i in self.aob_address_list:
            self.aob_address = i + self.offset  # 必定要偏移
            self.aob_hex_list = [
                hex(b)[2:].zfill(2).upper()
                for b in self.pm.read_bytes(self.aob_address, self.aob_hex_list_len)
            ]
            print("aob_hex_list:", self.aob_hex_list, self.aob_address)
            if i in self.bad_newmen_18:
                print("bad_newmen_18")
                continue
            try:
                self.inject_memory()
                result = self.check_data_right()  #! 找到了基本就是对的
                with open(self.json_file_path, "w") as json_file:
                    json.dump(
                        {
                            "aob_address": self.aob_address,
                            "TR": self.TR,
                            "newmem": self.newmem,
                            "window_id": self.window_id,
                            "timestamp": time.time(),  # current timestamp
                        },
                        json_file,
                    )

                print(
                    f"Injected {self.process_name}, aob_address: {self.aob_address}, TR: {self.TR}, newmem: {self.newmem}, aob_hex_list: {self.aob_hex_list}"
                )
                break
            except Exception as e:
                print(e)
                continue

    def inject_memory(self):
        # Existing code before this...
        self.TR = pymem.memory.allocate_memory(self.pm.process_handle, 4)
        self.TR_address_reversed_formatted = format_address(self.TR)
        push_rax_lea_eax_rx_x = ["50", "41", "8D", "82", "98", "00", "00", "00"]
        move_TR_eax = ["A3"] + list(self.TR_address_reversed_formatted.split(" "))
        pop_rax = ["58"]
        jmp_place = ["E9"]
        part_head_combine = (
            push_rax_lea_eax_rx_x + move_TR_eax + pop_rax + self.aob_hex_list
        )
        shell_code_len = len(part_head_combine) + 5  # 5:jmp_place + offset_1_le

        # Allocate new memory
        self.newmem = pymem.memory.allocate_memory(
            self.pm.process_handle, shell_code_len
        )

        # Calculate jmp (newmem to aob_address)
        jmp_addr_1 = len(part_head_combine) + self.newmem
        target_addr_1 = self.aob_address + self.aob_hex_list_len
        offset_1 = calculate_jmp_offset(jmp_addr_1, target_addr_1)
        print("offset_1", offset_1)
        offset_1_le = to_signed_32_bit_le(offset_1)
        print("offset_1_le", offset_1_le)

        # Create shell code
        hex_values = (
            part_head_combine
            + jmp_place
            + [offset_1_le[0:1], offset_1_le[1:2], offset_1_le[2:3], offset_1_le[3:4]]
        )
        print("newmem hex_values", hex_values)
        inject_hex_shellcode = self.convert_hex_values_to_bytes(hex_values)

        # Write shell code to new memory
        result1 = self.pm.write_bytes(
            self.newmem, inject_hex_shellcode, len(inject_hex_shellcode)
        )

        # Calculate jmp offset 2 (aob_address to newmem)
        jmp_addr_2 = self.aob_address
        target_addr_2 = self.newmem
        offset_2 = calculate_jmp_offset(jmp_addr_2, target_addr_2)
        offset_2_le = to_signed_32_bit_le(offset_2)

        # Create JMP shell code to inject into aob_address
        extra_nop = None
        if self.aob_hex_list_len - 5 == 2:
            extra_nop = ["66", "90"]
        elif self.aob_hex_list_len - 5 == 1:
            extra_nop = ["90"]
        elif self.aob_hex_list_len == 5:
            pass
        else:
            raise Exception("aob_hex_list_len must be 6 or 7")

        inject_hex = (
            jmp_place
            + [
                offset_2_le[0:1],
                offset_2_le[1:2],
                offset_2_le[2:3],
                offset_2_le[3:4],
            ]
            + extra_nop
        )
        inject_hex_shellcode = self.convert_hex_values_to_bytes(inject_hex)

        # Write JMP to aob_address
        result2 = self.pm.write_bytes(
            self.aob_address, inject_hex_shellcode, len(inject_hex_shellcode)
        )

        return result1, result2

    def convert_hex_values_to_bytes(self, hex_values):
        byte_values = []
        for hv in hex_values:
            if isinstance(hv, str):  # if hv is a hex string
                byte_values.append(int(hv, 16))
            elif isinstance(hv, bytes):  # if hv is a byte object
                byte_values.append(int.from_bytes(hv, "little"))
        return bytes(byte_values)

    def check_data_right(self):
        print(
            "check_data_right---------------------------------------------------------------------------"
        )
        self.bad_newmen_18.append(self.newmem + 18)
        time.sleep(1)
        print(
            f"Checking data for {self.process_name}... aob_address: {self.aob_address} TR: {self.TR} newmem: {self.newmem}"
        )
        data = self.pm.read_bytes(self.TR, 4)
        value = int.from_bytes(data, byteorder="little")
        start_address = value - 4
        print("start_address", start_address, hex(start_address))

        data = self.pm.read_bytes(start_address, 4)
        # analyze_shellcode(data, 4)
        print("data", data)
        player_info_not_sure_address = split_bytes_to_int(data, 0, 4)

        print(
            "player_info_not_sure_address",
            player_info_not_sure_address,
            hex(player_info_not_sure_address),
        )

        if self.pm.read_bytes(player_info_not_sure_address, 4) in [
            b"\x11\x00\x00\x00",
            b"\t\x00\x00\x00",
            b"\x01\x00\x00\x00",
        ]:  # 90000
            print(self.pm.read_bytes(player_info_not_sure_address, 4))
            return True
        else:
            print(
                "self.pm.read_bytes(player_info_not_sure_address, 4)",
                self.pm.read_bytes(player_info_not_sure_address, 4),
            )
            analyze_shellcode(self.pm.read_bytes(player_info_not_sure_address, 4), 4)

            return False

    def read_data(self):
        # pass
        # while True:
        battle_time_passed = None
        player_info_not_sure_address = None
        battle_instance_address = None
        battle_option_ready = None
        data = self.pm.read_bytes(self.TR, 4)
        value = int.from_bytes(data, byteorder="little")
        start_address = value - 4
        data = self.pm.read_bytes(start_address, 36)
        player_info_not_sure_address = split_bytes_to_int(data, 0, 4)
        battle_instance_address = split_bytes_to_int(data, 4, 8)
        if str(battle_instance_address) != "0":
            battle_instance_data = self.pm.read_bytes(battle_instance_address, 128)
            battle_time_passed = round(
                struct.unpack("<f", battle_instance_data[60:64])[0], 2
            )
            battle_option_ready = split_bytes_to_int(battle_instance_data, 98, 99)

        self.memory_info_dict = {
            "player_info_not_sure_address": player_info_not_sure_address,
            "battle_instance_address": battle_instance_address,
            "battle_time_passed": battle_time_passed,
            "battle_option_ready": battle_option_ready,
        }
        return self.memory_info_dict

        # print(self.memory_info_dict)


if __name__ == "__main__":
    injector = MemoryInjector_BattleInfo()
    injector.read_data()
    print(injector.memory_info_dict)
