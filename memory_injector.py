import random
import re
import struct

import pymem
from capstone import *
from pymem.pattern import pattern_scan_all


class MemoryInjector:
    def __init__(self, target_process):
        self.target_process = target_process
        self.pm = pymem.Pymem(target_process)
        self.real_aob_offset = None
        self.aob_hex_list = []
        self.aob_address = self.aob_scan()  # 这个要放在aob_hex_list后面
        self.TR = pymem.memory.allocate_memory(self.pm.process_handle, 4)
        self.newmem = None

    def aob_scan(self):
        for i in range(10):
            aob_address_list = pattern_scan_all(
                handle=self.pm.process_handle,
                pattern=b"\\x0F\\xBE.\\x10.\\x0F\\xB6.\\x12",  # .\\x8B.\\x24\\x45\\x0F\\xB6.\\x11',#pattern=bytes.fromhex(self.aob_dict[i]['aob']),
                return_multiple=True,
            )
            print("aob_address_list:", aob_address_list)
            if len(aob_address_list) >= 1:
                print(
                    f"{i} try, aob_address_list offset -1: {aob_address_list} Not unique"
                )
                aob_address = random.choice(aob_address_list) - 1
                self.aob_hex_list = [
                    hex(b)[2:].zfill(2).upper()
                    for b in self.pm.read_bytes(aob_address, 5)
                ]  # ['45', '8B', '55', '18', '45']
                print("aob_hex_list:", self.aob_hex_list, aob_address)
                if self.aob_hex_list[0] not in ["45", "41"]:
                    continue
                return aob_address
            else:
                print(f"{i} try, retrying...")
        raise Exception("No aob found")

    @staticmethod
    def format_address(address, length=8):
        reversed_bytes = address.to_bytes(length, byteorder="little")
        reversed_formatted = " ".join(f"{b:02X}" for b in reversed_bytes)
        return reversed_formatted

    @staticmethod
    def to_signed_32_bit_le(i):
        return struct.pack("<i", i)

    # Other methods omitted for brevity
    @staticmethod
    def calculate_jmp_offset(jmp_addr, target_addr):
        offset = target_addr - (jmp_addr + 5)
        return offset

    def get_lea_magic_number(self) -> str:
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

        hex_str = "".join(self.aob_hex_list)
        print(hex_str)
        # Convert the hex string to bytes
        shellcode = bytes.fromhex(hex_str)
        # The first argument is the architecture type, CS_ARCH_X86 for x86.
        # The second argument is the mode, CS_MODE_64 for 64-bit mode.
        md = Cs(CS_ARCH_X86, CS_MODE_64)

        # Disassemble the code
        for i in md.disasm(shellcode, 0x1000):
            print("0x%x:\t%s\t%s" % (i.address, i.mnemonic, i.op_str))
            op_str = i.op_str

            # Find all occurrences of "r" followed by a number
            matches = re.findall(r"r\d+", op_str)
            if matches:
                # Return the hex value corresponding to the register
                register = matches[-1]  # assuming you want the first match
                if register in register_to_hex:
                    return register_to_hex[register]
            else:
                raise Exception("No register found in operation")

        raise Exception("No lea magic number found")

    def inject_memory(self):
        # Existing code before this...
        self.TR_address_reversed_formatted = self.format_address(self.TR)
        # Add your specific offsets here
        print("self.aob_hex_list:", self.aob_hex_list)
        lea_magic_number = self.get_lea_magic_number()
        lea_eax_rx_x = ["41", "8D", lea_magic_number, "10"]
        # movsx_esi_byte_ptr_rx_x = self.movsx_dict[self.real_aob_offset]
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
        offset_1 = self.calculate_jmp_offset(jmp_addr_1, target_addr_1)
        print("offset_1", offset_1)
        offset_1_le = self.to_signed_32_bit_le(offset_1)
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
        offset_2 = self.calculate_jmp_offset(jmp_addr_2, target_addr_2)
        offset_2_le = self.to_signed_32_bit_le(offset_2)

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

    def print_and_convert_bytes(self, data, start, end):
        converted = int.from_bytes(data[start:end], byteorder="little")
        # print(converted)
        return converted

    def read_data(self):
        data = self.pm.read_bytes(self.TR, 4)
        print(data)
        value = int.from_bytes(data, byteorder="little")
        print("value", value)
        x_address = value - 4 - 80
        print("x_address", x_address, hex(x_address))
        data = self.pm.read_bytes(x_address, 10 + 80)
        print("x_y_map_direction", data)
        self.x_coords = self.print_and_convert_bytes(data, 0 + 80, 2 + 80)
        self.y_coords = self.print_and_convert_bytes(data, 2 + 80, 4 + 80)
        self.map_number = self.print_and_convert_bytes(data, 4 + 80, 5 + 80)
        self.face_dir = hex(data[9 + 80])[-1]
        self.transport = self.print_and_convert_bytes(data, 0, 2)
        data_dict = {
            "x_coords": self.x_coords,
            "y_coords": self.y_coords,
            "map_number": (int(data[4 + 80]), data[4 + 80 + 2], data[4 + 80 + 1]),
            "face_dir": self.face_dir,
            "transport": self.transport,
        }
        print(data_dict)


if __name__ == "__main__":
    injector = MemoryInjector("javaw.exe")
    print(injector.aob_address)
    print(hex(injector.aob_address))
    print(injector.TR)
    print(hex(injector.TR))

    injector.inject_memory()
    print(injector.newmem, hex(injector.newmem))
    import time

    time.sleep(5)
    injector.read_data()
# self.aob_dict = {
#     "r8+10": {"aob": "41 0F BE 48 10 45 0F", "offset": 0},
#     "r9+10": {"aob": "18 41 0F BE 71 10 45", "offset": 1},
#     "r10+10": {"aob": "41 0F BE 72 10 45 0F B6", "offset": 0},
#     "r11+10": {"aob": "45 0F BE 4B 10 41 0F B6", "offset": 0},
#     "r8+10_2": {"aob": "41 0F BE 78 10 45", "offset": 0},
#     "r10+10_2": {"aob": "41 0F BE 5A 10", "offset": 0},
#     "r10+10_3": {"aob": "45 0F BE 4A 10 45", "offset": 0},
#     # Add more keys here as needed
# }
# # Define byte sequences for lea and movsx instructions
# self.lea_dict = {
#     "r9+10": ["41", "8D", "41", "10"],
#     "r10+10": ["41", "8D", "42", "10"],
#     "r10+10_2": ["41", "8D", "42", "10"],  # 都是一样的 _2
#     "r10+10_3": ["41", "8D", "42", "10"],  #
#     "r11+10": ["41", "8D", "43", "10"],
#     "r8+10": ["41", "8D", "40", "10"],
#     "r8+10_2": ["41", "8D", "40", "10"]
#     # Add more keys here as needed
# }
# self.movsx_dict = {
#     "r9+10": ["41", "0F", "BE", "71", "10"],
#     "r10+10": ["41", "0F", "BE", "72", "10"],
#     "r10+10_2": ["41", "0F", "BE", "5A", "10"],  # 这个和特征码一样
#     "r10+10_3": ["45", "0F", "BE", "4A", "10"],  # 这个和特征码一样
#     "r11+10": ["45", "0F", "BE", "4B", "10"],
#     "r8+10": ["41", "0F", "BE", "48", "10"],
#     "r8+10_2": ["41", "0F", "BE", "78", "10"]
#     # Add more keys here as needed
# }
