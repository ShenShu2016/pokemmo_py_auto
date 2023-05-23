import struct
import time

import pymem
from pymem.pattern import pattern_scan_all


class MemoryInjector:
    def __init__(self, target_process):
        self.target_process = target_process
        self.pm = pymem.Pymem(target_process)
        self.aob_dict = {
            "r9+10": "41 0F BE 71 10 45",
            "r10+10": "41 0F BE 72 10 45 0F B6",
            "r11+10": "45 0F BE 4B 10 41 0F B6",
            # Add more keys here as needed
        }
        # Define byte sequences for lea and movsx instructions
        self.lea_dict = {
            "r9+10": ["41", "8D", "41", "10"],
            "r10+10": ["41", "8D", "42", "10"],
            "r11+10": ["41", "8D", "43", "10"]
            # Add more keys here as needed
        }
        self.movsx_dict = {
            "r9+10": ["41", "0F", "BE", "71", "10"],
            "r10+10": ["41", "0F", "BE", "72", "10"],
            "r11+10": ["45", "0F", "BE", "4B", "10"]
            # Add more keys here as needed
        }
        self.real_aob_offset = None
        self.aob_address = self.aob_scan()
        self.TR = pymem.memory.allocate_memory(self.pm.process_handle, 4)
        self.newmem = None
        self.jmp_place = b"\xE9"

    def aob_scan(self):
        for i in self.aob_dict:
            print(f"key is {i}, value is {self.aob_dict[i]}")

            aob_address_list = pattern_scan_all(
                handle=self.pm.process_handle,
                pattern=bytes.fromhex(self.aob_dict[i]),
                return_multiple=True,
            )
            print(aob_address_list)
            if len(aob_address_list) == 1:
                self.real_aob_offset = i
                return aob_address_list[0]
            elif len(aob_address_list) > 1:
                print("aob_address", i, aob_address_list, "not unique")
                continue
            else:
                print("aob_address", i, "not found")
                continue
        raise Exception("AOB not found")

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

    def create_shellcode(self, offset_1_le):
        part_head_combine = (
            self.push_rax
            + self.lea_eax_rx_x
            + self.move_TR_eax
            + self.pop_rax
            + self.movsx_esi_byte_ptr_rx_x
        )
        hex_values = (
            part_head_combine
            + self.jmp_place
            + [offset_1_le[0:1], offset_1_le[1:2], offset_1_le[2:3], offset_1_le[3:4]]
        )
        byte_values = []
        for hv in hex_values:
            if isinstance(hv, str):  # if hv is a hex string
                byte_values.append(int(hv, 16))
            elif isinstance(hv, bytes):  # if hv is a byte object
                byte_values.append(int.from_bytes(hv, "little"))
        return bytes(byte_values)

    def inject_memory(self):
        TR_address_reversed_formatted = self.format_address(self.TR)
        self.push_rax = ["50"]
        self.move_TR_eax = ["A3"] + TR_address_reversed_formatted.split(" ")  # [TR],EAX
        self.pop_rax = ["58"]

        # Use the offset to look up the instruction bytes in the dictionaries
        self.lea_eax_rx_x = self.lea_dict.get(self.real_aob_offset, [])
        self.movsx_esi_byte_ptr_rx_x = self.movsx_dict.get(self.real_aob_offset, [])

        part_head_combine = (
            self.push_rax
            + self.lea_eax_rx_x
            + self.move_TR_eax
            + self.pop_rax
            + self.movsx_esi_byte_ptr_rx_x
        )

        shell_code_len = len(part_head_combine) + 1 + 4

        # Allocate new memory
        self.newmem = pymem.memory.allocate_memory(
            self.pm.process_handle, shell_code_len + 50  # extra
        )

        # Copy old shell code
        old_shell_code = self.pm.read_bytes(self.aob_address, shell_code_len)

        # Write old shell code to new memory
        self.pm.write_bytes(
            self.newmem + shell_code_len + 5, old_shell_code, shell_code_len
        )

        # Write JMP to original shell code location
        offset_2_le = self.to_signed_32_bit_le(
            self.calculate_jmp_offset(
                self.newmem + shell_code_len + 5, self.aob_address + shell_code_len
            )
        )

        self.pm.write_bytes(
            self.newmem + shell_code_len + 5 + shell_code_len,
            self.jmp_place + offset_2_le,
            5,
        )
        print("inject to new memory done")

        # Write JMP to new memory
        offset_1_le = self.to_signed_32_bit_le(
            self.calculate_jmp_offset(self.aob_address, self.newmem)
        )
        inject_hex_shellcode = self.create_shellcode(offset_1_le)

        result2 = self.pm.write_bytes(
            self.aob_address, inject_hex_shellcode, len(inject_hex_shellcode)
        )
        print("inject to aob address done")

    def read_data(self):
        while True:
            data = self.pm.read_bytes(self.TR, 4)
            print(data)
            value = int.from_bytes(data, byteorder="little")
            print(value)
            time.sleep(0.5)


if __name__ == "__main__":
    injector = MemoryInjector("javaw.exe")
    print(injector.aob_address)
    print(hex(injector.aob_address))

    print(injector.TR)
    print(hex(injector.TR))

    injector.inject_memory()

    injector.read_data()
