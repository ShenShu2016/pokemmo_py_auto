import json
import os
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


def process_shellcode(shellcode):
    # print(shellcode)
    string_end = shellcode.index(b"\x00\x00")
    try:
        name = shellcode[:string_end].decode()
    except:
        name = "Unknown"
    shellcode_start = shellcode.index(b"\x81\x00")
    shellcode_start = shellcode_start - 1 if shellcode_start > 0 else shellcode_start
    new_shellcode = shellcode[shellcode_start:]
    return name, new_shellcode


class MemoryInjector_MySprites:
    def __init__(self):
        self.target_process = "javaw.exe"
        self.pattern = b"\\x8B\\x5B\\x0C\\x3B\\xD8"
        self.process_name = "mj_my_sprites"
        self.offset = 0
        self.window_id = Window_Manager().get_window_id()
        self.pm = pymem.Pymem(self.target_process)
        self.team_dict = {}

        # Adding a path to your json file
        self.json_file_path = r"mj_my_sprites.json"
        self.aob_hex_list_len = 5  # 注入那条指令的长度
        self.aob_address_list = []
        self.aob_hex_list = []
        self.aob_address = 0
        self.TR = None
        self.newmem = None
        # Try to read the stored values from the json file
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, "r") as json_file:
                data = json.load(json_file)
                if data.get("window_id") != self.window_id:
                    print("window_id not match")
                    self.aob_address = self.aob_scan()
                    self.try_the_aob()

                else:
                    print("window_id match")

                    self.aob_address = data.get("aob_address", 0)
                    self.TR = data.get("TR", None)
                    self.newmem = data.get("newmem", None)
                    print(
                        f"Read data from json file. aob_address: {self.aob_address}, TR: {self.TR}, newmem: {self.newmem}"
                    )

                    # Try to read data
                    try:
                        self.read_data()
                        print(
                            f"{self.process_name} Reading data succeeded with stored addresses. aob_address: {self.aob_address}, TR: {self.TR}, newmem: {self.newmem}"
                        )
                    except Exception as e:
                        print(
                            f"{self.process_name} Reading data failed with stored addresses, starting normal scanning and injection process:",
                            e,
                        )
                        self.aob_address = self.aob_scan()
                        self.try_the_aob()
        else:
            self.aob_address = self.aob_scan()
            self.try_the_aob()

    def aob_scan(self):
        while True:
            self.aob_address_list = pattern_scan_all(
                handle=self.pm.process_handle,
                pattern=self.pattern,
                return_multiple=True,
            )
            print("aob_address_list:", self.aob_address_list)
            if len(self.aob_address_list) >= 1:
                print(f"{self.process_name}aob_address_list:", self.aob_address_list)
                return
            if len(self.aob_address_list) < 1:
                print(f"waiting for AOB {self.process_name} appear, retrying...")
                time.sleep(1)

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

            try:
                self.inject_memory()
                # time.sleep(5)
                # self.read_data()  #!不需要了因为找到肯定是对的
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
            except Exception as e:
                print(e)
                continue

    def inject_memory(self):
        # Existing code before this...
        self.TR = pymem.memory.allocate_memory(self.pm.process_handle, 4)
        self.TR_address_reversed_formatted = format_address(self.TR)
        push_rax_lea_eax_rx_x = ["50", "8D", "43", "0C"]  #!这个也得改！43是eax，0C是偏移
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

        inject_hex = jmp_place + [
            offset_2_le[0:1],
            offset_2_le[1:2],
            offset_2_le[2:3],
            offset_2_le[3:4],
        ]
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

    def read_data(self):
        try:
            data = self.pm.read_bytes(self.TR, 4)
            value = int.from_bytes(data, byteorder="little")
            # print("value", value)
            target_value = self.pm.read_bytes(value, 28)
            self.team_dict = {}
            for i in range(6):
                start_index = 4 + i * 4
                end_index = start_index + 4
                pokemon_address = split_bytes_to_int(
                    target_value, start_index, end_index
                )
                # print("pokemon_address", pokemon_address, hex(pokemon_address))
                pokemon_data = self.pm.read_bytes(pokemon_address, 264)
                pokemon_data_200_plus = pokemon_data[200:]
                try:
                    name, new_shellcode = process_shellcode(pokemon_data_200_plus)
                except Exception as e:
                    print(e)
                    name = "unknown"
                # print("name", name, "new_shellcode", new_shellcode)

                self.team_dict[i] = {
                    "pokedex": split_bytes_to_int(pokemon_data, 86, 88),
                    "hp": split_bytes_to_int(pokemon_data, 88, 90),
                    "happiness": round(
                        split_bytes_to_int(pokemon_data, 94, 96) / 255 * 100, 0
                    ),
                    "name": name,
                    "skill_0": {
                        "id": split_bytes_to_int(new_shellcode, 8, 10),
                        "pp": split_bytes_to_int(new_shellcode, 32, 33),
                    },
                    "skill_1": {
                        "id": split_bytes_to_int(new_shellcode, 10, 12),
                        "pp": split_bytes_to_int(new_shellcode, 33, 34),
                    },
                    "skill_2": {
                        "id": split_bytes_to_int(new_shellcode, 12, 14),
                        "pp": split_bytes_to_int(new_shellcode, 34, 35),
                    },
                    "skill_3": {
                        "id": split_bytes_to_int(new_shellcode, 14, 16),
                        "pp": split_bytes_to_int(new_shellcode, 35, 36),
                    },
                }
        except Exception as e:
            print(e)
        # print(self.team_dict)
        return self.team_dict


if __name__ == "__main__":
    injector = MemoryInjector_MySprites()
    time.sleep(1)
    injector.read_data()
    print(injector.team_dict)
