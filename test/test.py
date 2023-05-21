# -*- coding: utf-8 -*-
# import ctypes

# # 定义内存地址
# address = 0xEAF15EDA

# # 读取内存数据
# data = (ctypes.c_ushort * 1)()
# ctypes.memmove(data, address, 2)

# # 获取数据值并以十六进制字符串形式表示
# data_value = data[0]
# data_hex = format(data_value, "04X")

# print(data_hex)


import ctypes

print(("jsdklfjsdlfk"))


def read_memory(address):
    # Cast the address to a pointer
    ptr = ctypes.cast(address, ctypes.POINTER(ctypes.c_int))

    # Dereference the pointer
    return ptr.contents.value


address = 0x222F10381F1  # the address you want to read
print(read_memory(address))
print(("jsdklfjsdlfk"))
