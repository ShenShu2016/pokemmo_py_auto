import time
from ctypes import byref, c_ubyte, windll
from ctypes.wintypes import HWND, RECT

import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

GetDC = windll.user32.GetDC
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
GetClientRect = windll.user32.GetClientRect
CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
SelectObject = windll.gdi32.SelectObject
BitBlt = windll.gdi32.BitBlt
SRCCOPY = 0x00CC0020
GetBitmapBits = windll.gdi32.GetBitmapBits
DeleteObject = windll.gdi32.DeleteObject
ReleaseDC = windll.user32.ReleaseDC

# 防止UI放大导致截图不完整
windll.user32.SetProcessDPIAware()


def capture(handle: HWND):
    """窗口客户区截图

    Args:
        handle (HWND): 要截图的窗口句柄

    Returns:
        numpy.ndarray: 截图数据
    """
    # 获取窗口客户区的大小
    r = RECT()
    GetClientRect(handle, byref(r))
    width, height = r.right, r.bottom
    print(f"width {width}, height {height}")
    # 开始截图
    dc = GetDC(handle)
    cdc = CreateCompatibleDC(dc)
    bitmap = CreateCompatibleBitmap(dc, width, height)
    SelectObject(cdc, bitmap)
    BitBlt(cdc, 0, 0, width, height, dc, 0, 0, SRCCOPY)
    # 截图是BGRA排列，因此总元素个数需要乘以4
    total_bytes = width * height * 4
    buffer = bytearray(total_bytes)
    byte_array = c_ubyte * total_bytes
    GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
    DeleteObject(bitmap)
    DeleteObject(cdc)
    ReleaseDC(handle, dc)
    # 返回截图数据为numpy.ndarray
    return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)


def get_area_text(area, config="--psm 6", lang="eng"):
    gray = cv2.cvtColor(area, cv2.COLOR_BGRA2GRAY)  # 转为灰度图
    text = pytesseract.image_to_string(gray, config=config, lang=lang)
    print("=========================================")
    print(text)
    print("=========================================")


if __name__ == "__main__":
    import cv2

    handle = windll.user32.FindWindowW(None, "РokеМMO")
    # 截图时要保证游戏窗口的客户区大小是1334×750
    image = capture(handle)

    city_img_area = image[0:25, 30:250]
    current_money_img_area = image[30:45, 37:130]
    get_area_text(city_img_area)
    get_area_text(
        current_money_img_area,
        config="--psm 6 -c tessedit_char_whitelist=0123456789",
        lang="eng",
    )

    # Print the textsss
    # print something to split the text

    # cv2.imshow("Match Template", image)
    # cv2.waitKey()
