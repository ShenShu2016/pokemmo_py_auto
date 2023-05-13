if __name__ == "__main__":
    import cv2

    from tools.list_window_name import get_window_name

    window_name = get_window_name()

    handle = windll.user32.FindWindowW(None, window_name)
    # 截图时要保证游戏窗口的客户区大小是1334×750
    image = capture(handle)
    # if using color image
    image_color = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    # Load the template with color
    template_color = cv2.imread(
        r"C:\Users\Shen\Documents\GitHub\pokemmo_py_auto\data\Pokemon_Summary_Exit_Button.png",
        cv2.IMREAD_COLOR,
    )
    result = cv2.matchTemplate(image_color, template_color, cv2.TM_CCORR_NORMED)

    threshold = 0.95
    # Apply the threshold to the result
    _, result = cv2.threshold(result, threshold, 1.0, cv2.THRESH_BINARY)
    result = np.where(result >= threshold)

    h, w = template_color.shape[:2]
    for index, pt in enumerate(zip(*result[::-1])):
        # Draw a rectangle on the original image
        cv2.rectangle(image_color, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        # print all the coordinates and values
        print(
            index,
            pt[0],
            pt[1],
        )
    cv2.imshow("Match Template", image_color)
    cv2.waitKey()
