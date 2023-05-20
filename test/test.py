import psutil


def get_pid(name):
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == name:
            return proc.info["pid"]
    return None


# Usage:
pid = get_pid("javaw.exe")
print(pid)


import ctypes

# The array of bytes to search for
aob = bytes([0x45, 0x0F, 0xBE, 0x4A, 0x10, 0x45])

# Open the process
PROCESS_ALL_ACCESS = 0x000F0000 | 0x00100000 | 0xFFF
process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

# The range of addresses to search
start_address = 0x00000000
end_address = 0x7FFFFFFF

# The size of the memory to read at once
chunk_size = 4096

# The buffer to read the memory into
buffer = (ctypes.c_ubyte * chunk_size)()

# The number of bytes read
bytes_read = ctypes.c_ulong(0)

# Loop over the memory
for address in range(start_address, end_address, chunk_size):
    # Read the memory
    ctypes.windll.kernel32.ReadProcessMemory(
        process_handle, address, buffer, chunk_size, ctypes.byref(bytes_read)
    )

    # Search for the array of bytes
    for i in range(chunk_size - len(aob)):
        if bytes(buffer[i : i + len(aob)]) == aob:
            print("Found array of bytes at address: 0x%X" % (address + i))

# Close the process handle
ctypes.windll.kernel32.CloseHandle(process_handle)
