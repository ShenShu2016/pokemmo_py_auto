import struct

import pymem
from pymem.pattern import pattern_scan_all


class AobInjection:
    pass


target_process = "javaw.exe"  # Define the name of the process
pm = pymem.Pymem(target_process)


def aob_scan():
    global real_aob_offset
    # Open a handle to the process

    for i in aob_dict:
        print(f"key is {i}, value is {aob_dict[i]}")

        aob_address_list = pattern_scan_all(
            handle=pm.process_handle,
            pattern=bytes.fromhex(aob_dict[i]),
            return_multiple=True,
        )  # Scan the entire memory of the process for the AOB
        print(aob_address_list)
        if len(aob_address_list) == 1:
            real_aob_offset = i
            return aob_address_list[0]
        elif len(aob_address_list) > 1:
            print("aob_address", i, aob_address_list, "not unique")
            continue
        else:
            print("aob_address", i, "not found")
            continue


real_aob_offset = None
aob_dict = {
    "r9+10": "41 0F BE 71 10 45",
    "r10+10": "41 0F BE 72 10 45 0F B6",
}
aob_address = aob_scan()
print(aob_address)  # Print the address where the AOB was found
print(hex(aob_address))


TR = pymem.memory.allocate_memory(pm.process_handle, 4)
print(TR)
print(hex(TR))


def format_address(address, length=8):
    reversed_bytes = address.to_bytes(length, byteorder="little")
    reversed_formatted = " ".join(f"{b:02X}" for b in reversed_bytes)
    return reversed_formatted


# print(format_address(0x1CA99861000))
TR_address_reversed_formatted = format_address(TR)
print(TR_address_reversed_formatted)

lea_eax_rx_x = None
movsx_esi_byte_ptr_rx_x = None
push_rax = ["50"]
if real_aob_offset == "r9+10":
    lea_eax_rx_x = ["41", "8D", "41", "10"]  # r9+10
    movsx_esi_byte_ptr_rx_x = ["41", "0F", "BE", "71", "10"]
elif real_aob_offset == "r10+10":
    lea_eax_rx_x = ["41", "8D", "42", "10"]  # r10+10
    movsx_esi_byte_ptr_rx_x = ["41", "0F", "BE", "72", "10"]
elif True == False:
    pass

move_TR_eax = ["A3"] + TR_address_reversed_formatted.split(" ")  # [TR],EAX
pop_rax = ["58"]

part_head_combine = (
    push_rax + lea_eax_rx_x + move_TR_eax + pop_rax + movsx_esi_byte_ptr_rx_x
)

part_head_combine
print("len part_head_combine", len(part_head_combine))

print(part_head_combine)

jmp_place = ["E9"]

shell_code_len = len(part_head_combine) + 1 + 4

print("shell_code_len", shell_code_len)

# Allocate new memory
newmem = pymem.memory.allocate_memory(pm.process_handle, shell_code_len)
print(newmem)

print(hex(newmem))
newmen_end_row_address_jmp = hex(len(part_head_combine) + newmem)
newmen_end_row_address_jmp


def calculate_jmp_offset(jmp_addr, target_addr):
    offset = target_addr - (jmp_addr + 5)
    return offset


def to_signed_32_bit_le(i):
    return struct.pack("<i", i)


# 先算 newmen中jmp 的偏移量
jmp_addr_1 = int(newmen_end_row_address_jmp, 16)  # 多数以14结尾
print("jmp_addr_1", jmp_addr_1)
target_addr_1 = aob_address + 5
print("target_addr_1", target_addr_1)
print(hex(target_addr_1))
print("offset_1", jmp_addr_1, target_addr_1)
offset_1 = calculate_jmp_offset(jmp_addr_1, target_addr_1)
print("offset_1", offset_1)
offset_1_le = to_signed_32_bit_le(offset_1)
print("offset_1_le", offset_1_le)

# offset_2_le 是从 aob_address 跳到 newmen 的偏移量 A开头
jmp_addr_2 = aob_address  # aob address
print("jmp_addr_2", jmp_addr_2, hex(jmp_addr_2))
target_addr_2 = newmem
print("target_addr_2", target_addr_2, hex(target_addr_2))
offset_2 = calculate_jmp_offset(jmp_addr_2, target_addr_2)
# Convert to signed 32-bit little endian format
offset_2_le = to_signed_32_bit_le(offset_2)
# Print the offset in hexadecimal
print(offset_2_le.hex())

hex_values = (
    part_head_combine
    + jmp_place
    + [offset_1_le[0:1], offset_1_le[1:2], offset_1_le[2:3], offset_1_le[3:4]]
)
print(hex_values)

hex_values = (
    part_head_combine
    + jmp_place
    + [offset_1_le[0:1], offset_1_le[1:2], offset_1_le[2:3], offset_1_le[3:4]]
)
byte_values = []
for hv in hex_values:
    if isinstance(hv, str):  # if hv is a hex string
        byte_values.append(int(hv, 16))
    elif isinstance(hv, bytes):  # if hv is a byte object
        byte_values.append(
            int.from_bytes(hv, "little")
        )  # or 'big' if your data is big-endian
newmen_shellcode = bytes(byte_values)
print(newmen_shellcode)
result1 = pm.write_bytes(newmem, newmen_shellcode, len(newmen_shellcode))
print(result1)

# 现在要去aob address jmp 到newmen
inject_hex = ["E9"] + [
    offset_2_le[0:1],
    offset_2_le[1:2],
    offset_2_le[2:3],
    offset_2_le[3:4],
]
print(inject_hex)
byte_values = []
for hv in inject_hex:
    if isinstance(hv, str):  # if hv is a hex string
        byte_values.append(int(hv, 16))
    elif isinstance(hv, bytes):  # if hv is a byte object
        byte_values.append(
            int.from_bytes(hv, "little")
        )  # or 'big' if your data is big-endian
inject_hex_shellcode = bytes(byte_values)
print(inject_hex_shellcode)

print("aob_address", aob_address, hex(aob_address))

print(inject_hex_shellcode)
print(aob_address, inject_hex_shellcode, len(inject_hex_shellcode))

result2 = pm.write_bytes(aob_address, inject_hex_shellcode, len(inject_hex_shellcode))
print(result2)

# durning the game I will always nee to do this...
# Define the memory address
address = TR
# address = 0x240B47B0000

while True:
    from time import sleep

    # Read bytes from the memory
    # Assuming you want to read 4 bytes (an integer) at that address
    data = pm.read_bytes(address, 4)
    print(data)
    # Convert the bytes to an integer
    value = int.from_bytes(
        data, byteorder="little"
    )  # Use 'big' if the byteorder is big endian
    print(value)

    x_address = value - 4

    x_y_map_direction = pm.read_bytes(x_address, 10)

    # Convert the first 2 bytes to an integer
    x_coords = int.from_bytes(
        data[:2], byteorder="little"
    )  # Use 'big' if the byteorder is big endian

    print(value)

    # Convert the first 2 bytes to an integer
    y_coords = int.from_bytes(
        data[2:4], byteorder="little"
    )  # Use 'big' if the byteorder is big endian

    print(value)

    map_number = int.from_bytes(
        data[4:6], byteorder="little"
    )  # Use 'big' if the byteorder is big endian
    print(value)  # Output: 12081

    # hex_value = hex(data[9])
    # avatar_direction = hex_value[-3]  # 3 right,0 down
    # print(avatar_direction)

    sleep(0.5)
