"""
@author: Viet Nguyen <nhviet1009@gmail.com>
"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from utils import get_data


def get_args():
    parser = argparse.ArgumentParser("Image to ASCII")
    parser.add_argument("--input", type=str, default="data/ding_he.jpg", help="Path to input image")
    parser.add_argument("--output", type=str, default="data/ding_he_img.jpg", help="Path to output text file")
    parser.add_argument("--language", type=str, default="english")
    parser.add_argument("--mode", type=str, default="standard")
    parser.add_argument("--background", type=str, default="black", choices=["black", "white"],
                        help="background's color")
    parser.add_argument("--num_cols", type=int, default=300, help="number of character for output's width")
    args = parser.parse_args()
    return args


def main(opt):
    # 设置背景颜色
    if opt.background == "white":
        bg_code = 255  # 白色背景
    else:
        bg_code = 0  # 黑色背景

    # 获取字符列表、字体、示例字符和缩放比例
    char_list, font, sample_character, scale = get_data(opt.language, opt.mode)

    # 获取字符的宽度和高度
    bbox = font.getbbox(sample_character)
    char_width = bbox[2] - bbox[0]
    char_height = bbox[3] - bbox[1]

    # 图像尺寸和单元格大小
    num_chars = len(char_list)
    num_cols = opt.num_cols
    image = cv2.imread(opt.input)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 转为灰度图
    height, width = image.shape

    cell_width = width / num_cols
    cell_height = scale * cell_width
    num_rows = int(height / cell_height)

    # 如果行列数超过了图像的尺寸，则使用默认设置
    if num_cols > width or num_rows > height:
        print("Too many columns or rows. Use default setting")
        cell_width = 6
        cell_height = 12
        num_cols = int(width / cell_width)
        num_rows = int(height / cell_height)

    # 输出图像的宽度和高度
    out_width = char_width * num_cols
    out_height = scale * char_height * num_rows
    out_image = Image.new("L", (out_width, out_height), bg_code)
    draw = ImageDraw.Draw(out_image)

    # 填充图像
    for i in range(num_rows):
        line = "".join([char_list[min(int(np.mean(image[int(i * cell_height):min(int((i + 1) * cell_height), height),
                                                  int(j * cell_width):min(int((j + 1) * cell_width),
                                                                          width)]) / 255 * num_chars), num_chars - 1)]
                        for j in range(num_cols)]) + "\n"
        # 绘制每一行的字符
        draw.text((0, i * char_height), line, fill=255 - bg_code, font=font)

    # 裁剪图像并保存
    if opt.background == "white":
        cropped_image = ImageOps.invert(out_image).getbbox()
    else:
        cropped_image = out_image.getbbox()
    out_image = out_image.crop(cropped_image)
    out_image.save(opt.output)


if __name__ == '__main__':
    opt = get_args()
    main(opt)
