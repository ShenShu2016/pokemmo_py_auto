from __future__ import annotations

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录的绝对路径
package_path = os.path.join(current_dir, "..")  # 获取上级目录的路径
sys.path.append(package_path)  # 将上级目录添加到模块搜索路径中
from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PokeMMO


class Mail_Ditto:
    def __init__(self, pokeMMO_instance: PokeMMO, to_send="Hodson", total_to_send=5):
        self.p = pokeMMO_instance
        self.multiselect = False
        self.to_send = to_send
        self.content = ""
        self.total_to_send = total_to_send

    def check_multiselect(self):
        # 检查是否开启了多选
        self.p.find_items(temp_BRG=self.p.no_132_BRG, max_matches=60, threshold=0.98)

        raise NotImplementedError

    def select_inbox_sprite(self, img_BRG, count):
        sprite_BRG = getattr(self.p, f"{img_BRG}_BRG")
        coords_list = self.p.find_items(
            temp_BRG=sprite_BRG,
            max_matches=60,
            threshold=0.98,
        )
        if len(coords_list) >= count:
            print("ready to mail")
            for coords in coords_list[:count]:
                self.p.controller.click_center(coords, wait=0.1)

            sleep(0.2)
            print("正在右键")
            self.p.controller.click_center(coords, button="right")
            sleep(0.2)
            mail_box_coords_list = self.p.find_items(
                temp_BRG=self.p.mail_box_word_BRG,
                max_matches=1,
                threshold=0.98,
                top_l=(0, 0),
                bottom_r=(1360, 700),
            )
            if len(mail_box_coords_list) == 1:
                self.p.controller.click_center(mail_box_coords_list[0], wait=1)

            else:
                raise ValueError(f"没找到邮箱按钮")

        else:
            raise ValueError(f"not enough {img_BRG} in inbox")

    def send_email(self, i):
        result_list = self.p.find_items(
            temp_BRG=self.p.send_email_BRG,
            max_matches=2,
            threshold=0.98,
            top_l=(414, 392),
            bottom_r=(1062, 660),
        )
        if len(result_list) == 1:
            self.p.controller.click(x=868, y=601, wait=0.2)
            # 这个时候光标应该移动到了收件人的输入框
            self.p.controller.send_keys(self.to_send, wait=0.2)

            self.p.controller.click(x=868, y=601, wait=0.2)
            # 这个时候光标应该移动到了内容的输入框
            new_content = f"{5*(i)+1}to{5*(i)+5}" + self.content
            self.p.controller.send_keys(new_content, wait=0.2)
            self.p.controller.click(x=868, y=601, wait=0.2)

    def close_email(self):
        self.p.controller.click(x=923, y=151, wait=0.2)

    def run(self):
        divided_value = self.total_to_send // 5  # 除以5的结果
        remainder = self.total_to_send % 5  # 除以5的余数

        for i in range(divided_value):
            print(f"第{i+1}次")
            self.select_inbox_sprite("no_132", 5)
            self.send_email(i)
            self.close_email()
            print(f"第{i+1}次结束")

        print(f"余数是{remainder}")
        return


if __name__ == "__main__":
    from main import PokeMMO

    p = PokeMMO()
    mail_ditto = Mail_Ditto(p, to_send="Hodson", total_to_send=10)
