import ctypes


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong),
    ]


def read_memory(address, size):
    kernel32 = ctypes.windll.kernel32
    buffer = ctypes.create_string_buffer(size)
    mbi = MEMORY_BASIC_INFORMATION()
    if kernel32.VirtualQuery(
        ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)
    ):
        if kernel32.ReadProcessMemory(
            kernel32.GetCurrentProcess(), ctypes.c_void_p(address), buffer, size, 0
        ):
            return buffer.raw


address = 0xF2A133E1
size = 2
print(read_memory(address, size))
