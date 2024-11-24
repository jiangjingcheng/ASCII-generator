import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageOps


def sort_chars(char_list, font, language):
    # 使用示例字符计算宽度和高度
    sample_char = {
        "chinese": "制",
        "korean": "ㅊ",
        "japanese": "あ",
        "russian": "Ш",
    }.get(language, "A")  # 默认用 "A"

    # 获取字符的边界框
    # left (bbox[0])：字符的 左边缘 x 坐标
    # upper (bbox[1])：字符的 上边缘 y 坐标
    # right (bbox[2])：字符的 右边缘 x 坐标
    # lower (bbox[3])：字符的 下边缘 y 坐标
    bbox = font.getbbox(sample_char)
    char_width = bbox[2] - bbox[0]
    char_height = bbox[3] - bbox[1]

    num_chars = min(len(char_list), 100)
    out_width = char_width * len(char_list)
    out_height = char_height

    # 创建输出图像
    out_image = Image.new("L", (out_width, out_height), 255)
    draw = ImageDraw.Draw(out_image)

    # 在图像上绘制字符列表
    draw.text((0, 0), char_list, fill=0, font=font)

    # 裁剪非空白区域
    cropped_bbox = ImageOps.invert(out_image).getbbox()
    out_image = out_image.crop(cropped_bbox)

    # 计算每个字符的亮度
    brightness = [
        np.mean(np.array(out_image)[:, char_width * i : char_width * (i + 1)])
        for i in range(len(char_list))
    ]

    # 对字符按照亮度排序
    zipped_lists = sorted(zip(brightness, char_list))
    result = ""
    counter = 0

    # 计算步长
    incremental_step = (zipped_lists[-1][0] - zipped_lists[0][0]) / num_chars
    current_value = zipped_lists[0][0]

    for value, char in zipped_lists:
        if value >= current_value:
            result += char
            counter += 1
            current_value += incremental_step
        if counter == num_chars:
            break

    if result[-1] != zipped_lists[-1][1]:
        result += zipped_lists[-1][1]

    return result


def get_data(language, mode):
    # 字符与字体配置
    font_path = {
        "chinese": "fonts/simsun.ttc",
        "korean": "fonts/arial-unicode.ttf",
        "japanese": "fonts/arial-unicode.ttf",
        "russian": "fonts/DejaVuSansMono-Bold.ttf",
    }.get(language, "fonts/DejaVuSansMono-Bold.ttf")

    font_size = 10 if language in ["chinese", "korean", "japanese"] else 20
    font = ImageFont.truetype(font_path, size=font_size)

    try:
        # 根据语言加载对应字符集
        if language == "general":
            from alphabets import GENERAL as character
            sample_character = "A"
            scale = 2
        else:
            module = __import__("alphabets", fromlist=[language.upper()])
            character = getattr(module, language.upper())
            sample_character = {"russian": "Ш", "chinese": "制", "korean": "ㅊ", "japanese": "お"}.get(language, "A")
            scale = 1 if language in ["chinese", "korean", "japanese"] else 2
    except ImportError:
        print(f"Invalid language: {language}")
        return None, None, None, None

    try:
        char_list = character[mode] if mode in character else character["standard"]
    except KeyError:
        print(f"Invalid mode for {language}")
        return None, None, None, None

    if language != "general":
        char_list = sort_chars(char_list, font, language)

    return char_list, font, sample_character, scale
