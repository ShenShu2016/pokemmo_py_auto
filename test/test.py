from subprocess import check_output

# 汇编指令
assembly_code = """
push eax
lea eax, [r9+10]
mov [0x12345678], eax
pop eax
"""

# 调用 NASM 进行汇编
machine_code = check_output(
    ["nasm", "-f", "bin"], input=assembly_code, encoding="ascii"
)

# 将字符串转换为字节码
machine_code = bytes.fromhex(machine_code.strip())

# 打印机器码
print(machine_code)
