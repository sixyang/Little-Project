# -*- coding: UTF-8 -*-

import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import string
from os.path import join


init_chars = string.ascii_letters + string.digits
default_font = "arial.ttf"                               # 验证码字体


# 生成验证码接口
def generate_verify_image(size=(120, 30),
                          chars=init_chars,
                          img_type="PNG",
                          mode="RGB",
                          bg_color=(200, 200, 200),
                          fg_color=(0, 0, 255),
                          font_size=18,
                          font_type=default_font,
                          length=5,
                          draw_lines=True,
                          n_line=(3, 4),
                          draw_points=True,
                          point_chance=5,
                          image_name=None,
                          save_img=False,
                          ):

    """
    生成验证码图片
    :param size: 图片的大小，格式（宽，高），默认为(120, 30)
    :param chars: 允许的字符集合，格式字符串
    :param img_type: 图片保存的格式，默认为GIF，可选的为GIF，JPEG，TIFF，PNG
    :param mode: 图片模式，默认为RGB
    :param bg_color: 背景颜色，默认为白色
    :param fg_color: 前景色，验证码字符颜色，默认为蓝色#0000FF
    :param font_size: 验证码字体大小
    :param font_type: 验证码字体，默认为 arial.ttf
    :param length: 验证码字符个数
    :param draw_lines: 是否划干扰线, 默认为True
    :param n_line: 干扰线的条数范围，格式元组，默认为(1, 2)，只有draw_lines为True时有效
    :param draw_points: 是否画干扰点
    :param point_chance: 干扰点出现的概率，大小范围[0, 100]
    :param save_img: 是否保存为图片
    :return: [0]: 验证码字节流, [1]: 验证码图片中的字符串
    """

    width, height = size
    img = Image.new(mode, size, bg_color)  # 创建图形
    draw = ImageDraw.Draw(img)  # 创建画笔

    def get_chars():
        """生成给定长度的字符串，返回列表格式"""

        return random.sample(chars, length)

    def create_lines():
        """绘制干扰线"""

        line_num = random.randint(*n_line)  # 干扰线条数

        for i in range(line_num):
            # 起始点
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            # 结束点
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(5, 5, 5))

    def create_points():
        """绘制干扰点"""

        chance = min(100, max(0, int(point_chance)))  # 大小限制在[0, 100]

        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs():
        """绘制验证码字符"""

        c_chars = get_chars()
        strs = ' %s ' % ' '.join(c_chars)  # 每个字符前后以空格隔开

        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)
        draw.text(((width - font_width) / 3, 2* (height - font_height) / 5),
                strs[:length//2], font=font, fill=fg_color)
        draw.text((2*(width - font_width) / 3, 2* (height - font_height) / 5),
                  strs[length//2:], font=font, fill='green')

        return ''.join(c_chars)

    if draw_lines:
        create_lines()
    if draw_points:
        create_points()
    strs = create_strs()

    # 图形扭曲参数
    params = [1 - float(random.randint(5, 10)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)  # 创建扭曲

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # 滤镜，边界加强（阈值更大）

    mstream = BytesIO()
    img.save(mstream, img_type)

    if save_img:
        pic_path = join('app/static/pictures/',image_name)
        img.save(pic_path, img_type)

    return strs


if __name__ == "__main__":
    mstream, strs = generate_verify_image(image_name="validate.png",save_img=True)
    print(strs)