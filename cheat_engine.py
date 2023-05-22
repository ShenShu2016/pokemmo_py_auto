import pymem
from pymem.pattern import pattern_scan_all


def aob_injection(process, aob):
    pm = pymem.Pymem(process)  # Open a handle to the process
    aob_address = pattern_scan_all(
        pm.process_handle, aob
    )  # Scan the entire memory of the process for the AOB
    print(aob_address)  # Print the address where the AOB was found
    print(hex(aob_address))


aob = bytes.fromhex("41 0F BE 71 10 45")  # Define the AOB

aob_injection(
    "javaw.exe", aob
)  # Call the function with the name of the process and the AOB


def read_memory(process, address, length):
    pm = pymem.Pymem(process)
    data = pm.read_bytes(address, length)
    return data


# Convert the address from a hexadecimal string to an integer
address = int("0x1811ecc7854", 16)

# Read 2 bytes from the memory address
data = read_memory("javaw.exe", address, 2)

# Print the data
print(data)


# from pymem import Pymem
# from pymem.memory import allocate_memory
# from pymem.pattern import pattern_scan_all


# def aob_injection(process, aob, shellcode):
#     pm = Pymem(process)
#     aob_address = pattern_scan_all(pm.process_handle, aob)
#     print(aob_address)


# aob = b"\x88\x96\xA5\x01\x00\x00"
# new_code = b"\xC7\x86\xA5\x01\x00\x00\x56\x02\x00\x00"

# aob_injection("CastleMinerZ.exe", aob, new_code)


# newmem = allocate_memory(pm.process_handle, len(shellcode))
# pm.write_bytes(newmem, shellcode, len(shellcode))
# jump_inst = b"\xE9" + (newmem - (aob_address + 5)).to_bytes(4, byteorder='little', signed=True)
# pm.write_bytes(aob_address, jump_inst, len(jump_inst))

# #Add nop
# nop = b'\x90'
# pm.write_bytes(aob_address + len(jump_inst), nop, len(nop))

# # Add return jump
# return_jump_offset = (aob_address + len(jump_inst) - (newmem + len(shellcode)))
# return_jump = b"\xE9" + return_jump_offset.to_bytes(4, byteorder='little', signed=True)
# pm.write_bytes(newmem + len(shellcode), return_jump, len(return_jump))
