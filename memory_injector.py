import struct

import pymem
from pymem.pattern import pattern_scan_all


class MemoryInjector:
    def __init__(self, target_process):
        self.target_process = target_process
        self.pm = pymem.Pymem(target_process)
        self.aob_dict = {
            "r8+10": {"aob": "41 0F BE 48 10 45 0F", "offset": 0},
            "r9+10": {"aob": "18 41 0F BE 71 10 45", "offset": 1},
            "r10+10": {"aob": "41 0F BE 72 10 45 0F B6", "offset": 0},
            "r11+10": {"aob": "45 0F BE 4B 10 41 0F B6", "offset": 0},
            "r8+10_2": {"aob": "41 0F BE 78 10 45", "offset": 0},
            "r10+10_2": {"aob": "41 0F BE 5A 10", "offset": 0},
            "r10+10_3": {"aob": "45 0F BE 4A 10 45", "offset": 0},
            # Add more keys here as needed
        }
        # Define byte sequences for lea and movsx instructions
        self.lea_dict = {
            "r9+10": ["41", "8D", "41", "10"],
            "r10+10": ["41", "8D", "42", "10"],
            "r10+10_2": ["41", "8D", "42", "10"],  # 都是一样的 _2
            "r10+10_3": ["41", "8D", "42", "10"],  # 这个和特征码一样
            "r11+10": ["41", "8D", "43", "10"],
            "r8+10": ["41", "8D", "40", "10"],
            "r8+10_2": ["41", "8D", "40", "10"]
            # Add more keys here as needed
        }
        self.movsx_dict = {
            "r9+10": ["41", "0F", "BE", "71", "10"],
            "r10+10": ["41", "0F", "BE", "72", "10"],
            "r10+10_2": ["41", "0F", "BE", "5A", "10"],  # 这个和特征码一样
            "r10+10_3": ["45", "0F", "BE", "4A", "10"],  # 这个和特征码一样
            "r11+10": ["45", "0F", "BE", "4B", "10"],
            "r8+10": ["41", "0F", "BE", "48", "10"],
            "r8+10_2": ["41", "0F", "BE", "78", "10"]
            # Add more keys here as needed
        }
        self.real_aob_offset = None
        self.aob_address = self.aob_scan()
        self.TR = pymem.memory.allocate_memory(self.pm.process_handle, 4)
        self.newmem = None

    def aob_scan(self):
        for i in self.aob_dict:
            aob_address_list = pattern_scan_all(
                handle=self.pm.process_handle,
                pattern=bytes.fromhex(self.aob_dict[i]["aob"]),
                return_multiple=True,
            )
            if len(aob_address_list) == 1:
                self.real_aob_offset = i
                real_aob_address = aob_address_list[0] + self.aob_dict[i]["offset"]
                print(
                    f"AOB Found!!! {i}, value is {self.aob_dict[i]['aob']}",
                    "aob_address",
                    i,
                    real_aob_address,
                )
                return real_aob_address
            elif len(aob_address_list) > 1:
                print(
                    f"key is {i}, value is {self.aob_dict[i]['aob']}",
                    "aob_address",
                    i,
                    aob_address_list,
                    "not unique",
                )
                continue
            else:
                print(
                    f"key is {i}, value is {self.aob_dict[i]['aob']}",
                    "aob_address",
                    i,
                    "not found",
                )
                continue
        return None

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

    def inject_memory(self):
        # Existing code before this...
        self.TR_address_reversed_formatted = self.format_address(self.TR)
        # Add your specific offsets here
        lea_eax_rx_x = self.lea_dict[self.real_aob_offset]
        movsx_esi_byte_ptr_rx_x = self.movsx_dict[self.real_aob_offset]
        push_rax = ["50"]
        move_TR_eax = ["A3"] + list(self.TR_address_reversed_formatted.split(" "))
        pop_rax = ["58"]
        jmp_place = ["E9"]
        part_head_combine = (
            push_rax + lea_eax_rx_x + move_TR_eax + pop_rax + movsx_esi_byte_ptr_rx_x
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
        # print("offset_1", offset_1)
        offset_1_le = self.to_signed_32_bit_le(offset_1)
        # print("offset_1_le", offset_1_le)

        # Create shell code
        hex_values = (
            part_head_combine
            + jmp_place
            + [offset_1_le[0:1], offset_1_le[1:2], offset_1_le[2:3], offset_1_le[3:4]]
        )
        # print("newmem hex_values", hex_values)
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
        # print(data)
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
