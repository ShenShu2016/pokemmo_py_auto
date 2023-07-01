import os
import sys

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
import json
import re
import struct
import time
from time import sleep

import pymem
from capstone import *
from pymem.pattern import pattern_scan_all


def format_address(address, length=8):
    reversed_bytes = address.to_bytes(length, byteorder="little")
    reversed_formatted = " ".join(f"{b:02X}" for b in reversed_bytes)
    return reversed_formatted


def to_signed_32_bit_le(i):
    return struct.pack("<i", i)


def calculate_jmp_offset(jmp_addr, target_addr):
    offset = target_addr - (jmp_addr + 5)
    return offset


def get_lea_magic_number(aob_hex_list) -> str:
    # Dictionary to map registers to hex numbers
    register_to_hex = {
        "r8": "40",
        "r9": "41",
        "r10": "42",
        "r11": "43",
        "r12": "44",
        "r13": "45",
        "r14": "46",
        "r15": "47",
    }

    hex_str = "".join(aob_hex_list)
    print(hex_str)
    shellcode = bytes.fromhex(hex_str)
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    for i in md.disasm(shellcode, 0x1000):
        print("0x%x:\t%s\t%s" % (i.address, i.mnemonic, i.op_str))
        op_str = i.op_str
        matches = re.findall(r"r\d+", op_str)
        if matches:
            # Return the hex value corresponding to the register
            register = matches[-1]  # assuming you want the first match
            if register in register_to_hex:
                return register_to_hex[register]
        else:
            raise Exception("No register found in operation")

    raise Exception("No lea magic number found")


def split_bytes_to_int(data, start, end):
    converted = int.from_bytes(data[start:end], byteorder="little")
    return converted


class MemoryInjector_Coords:
    def __init__(self):
        self.target_process = "javaw.exe"
        self.pm = pymem.Pymem(self.target_process)
        self.memory_info_dict = {
            "x_coords": 0,
            "y_coords": 0,
            "map_number_tuple": (
                0,
                0,
                0,
            ),
            "face_dir": 0,
            "transport": 0,
        }

        # Adding a path to your json file
        self.json_file_path = r"utils\memory_injection\memory_injector_coords.json"

        self.aob_address_list = []
        self.aob_hex_list = []
        self.aob_address = 0
        self.TR = None
        self.newmem = None
        # Try to read the stored values from the json file
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, "r") as json_file:
                data = json.load(json_file)
                self.aob_address = data.get("aob_address", 0)
                self.TR = data.get("TR", None)
                self.newmem = data.get("newmem", None)
                print(
                    f"Read data from json file. aob_address: {self.aob_address}, TR: {self.TR}, newmem: {self.newmem}"
                )

            # Try to read data
            try:
                self.test_data()
                print(
                    f"Reading data succeeded with stored addresses. aob_address: {self.aob_address}, TR: {self.TR}, newmem: {self.newmem}"
                )
            except Exception as e:
                print(
                    "Reading data failed with stored addresses, starting normal scanning and injection process:",
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
                pattern=b"\\x0F\\xBE.\\x10.\\x0F\\xB6.\\x12",  # 44 0FBE ?? 10 0FBE ?? 11
                return_multiple=True,
            )
            # print("aob_address_list:", self.aob_address_list)
            if len(self.aob_address_list) >= 1:
                self.aob_address_list = [
                    j
                    for j in self.aob_address_list
                    if [
                        hex(b)[2:].zfill(2).upper()
                        for b in self.pm.read_bytes(j - 1, 5)
                    ][0]
                    in ["45", "41"]
                ]
                print("aob_address_list after 45 41:", self.aob_address_list)
                return
            if len(self.aob_address_list) < 1:
                print(f"retrying...")
                sleep(0.5)

    def try_the_aob(self):
        for i in self.aob_address_list:
            self.aob_address = i - 1  # 必定要偏移
            self.aob_hex_list = [
                hex(b)[2:].zfill(2).upper()
                for b in self.pm.read_bytes(self.aob_address, 5)
            ]
            print("aob_hex_list:", self.aob_hex_list, self.aob_address)

            try:
                self.inject_memory()
                sleep(1)
                result = self.test_data()
                if result:
                    with open(self.json_file_path, "w") as json_file:
                        json.dump(
                            {
                                "aob_address": self.aob_address,
                                "TR": self.TR,
                                "newmem": self.newmem,
                                "timestamp": time.time(),  # current timestamp
                            },
                            json_file,
                        )

                    print(
                        f"Injected, aob_address: {self.aob_address}, TR: {self.TR}, newmem: {self.newmem}, aob_hex_list: {self.aob_hex_list}"
                    )
                    return
            except Exception as e:
                print(e)
                continue

    def inject_memory(self):
        # Existing code before this...
        self.TR = pymem.memory.allocate_memory(self.pm.process_handle, 4)
        self.TR_address_reversed_formatted = format_address(self.TR)
        lea_magic_number = get_lea_magic_number(self.aob_hex_list)
        lea_eax_rx_x = ["41", "8D", lea_magic_number, "10"]
        push_rax = ["50"]
        move_TR_eax = ["A3"] + list(self.TR_address_reversed_formatted.split(" "))
        pop_rax = ["58"]
        jmp_place = ["E9"]
        part_head_combine = (
            push_rax + lea_eax_rx_x + move_TR_eax + pop_rax + self.aob_hex_list
        )
        shell_code_len = len(part_head_combine) + 1 + 4

        # Allocate new memory
        self.newmem = pymem.memory.allocate_memory(
            self.pm.process_handle, shell_code_len
        )

        # Calculate jmp offset 1 (newmem to aob_address)
        jmp_addr_1 = len(part_head_combine) + self.newmem
        target_addr_1 = self.aob_address + 5
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

    def test_data(self):
        data = self.pm.read_bytes(self.TR, 4)
        value = int.from_bytes(data, byteorder="little")
        x_address = value - 4 - 80
        # print("x_address", x_address, hex(x_address))
        data = self.pm.read_bytes(x_address, 10 + 80)
        self.transport = split_bytes_to_int(data, 0, 2)
        if self.transport != 0 and self.transport <= 100:
            print("交通状态正常")
            return True
        else:
            print("交通状态异常")
            return False

    def read_data(self):
        data = self.pm.read_bytes(self.TR, 4)
        value = int.from_bytes(data, byteorder="little")
        x_address = value - 4 - 80
        # print("x_address", x_address, hex(x_address))
        data = self.pm.read_bytes(x_address, 10 + 80)
        # print("x_y_map_direction", data)
        self.x_coords = split_bytes_to_int(data, 0 + 80, 2 + 80)
        self.y_coords = split_bytes_to_int(data, 2 + 80, 4 + 80)
        self.map_number = split_bytes_to_int(data, 4 + 80, 5 + 80)
        self.face_dir = hex(data[9 + 80])[-1]
        self.transport = split_bytes_to_int(data, 0, 2)
        self.memory_info_dict = {
            "x_coords": self.x_coords,
            "y_coords": self.y_coords,
            "map_number_tuple": (
                int(data[4 + 80]),
                int(data[4 + 80 + 2]),
                int(data[4 + 80 + 1]),
            ),
            "face_dir": int(self.face_dir),
            "transport": self.transport,
        }
        return self.memory_info_dict


if __name__ == "__main__":
    injector = MemoryInjector_Coords()
    injector.read_data()
    print(injector.memory_info_dict)
