import os
import pygame
import cairosvg
import io

def load_svg(file_path, size):
    """
    加载SVG文件并转换为指定大小的Pygame Surface对象
    :param file_path: SVG文件路径
    :param size: 目标大小 (width, height)
    :return: Pygame Surface对象
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"SVG文件不存在: {file_path}")

    # 使用cairosvg将SVG转换为PNG格式的字节流
    png_data = cairosvg.svg2png(
        url=file_path,
        output_width=size[0],
        output_height=size[1]
    )

    # 从字节流创建Surface对象
    png_stream = io.BytesIO(png_data)
    return pygame.image.load(png_stream)

def get_piece_image_path(piece_type, player):
    """
    获取棋子图片的路径
    :param piece_type: 棋子类型
    :param player: 玩家（'red' 或 'blue'）
    :return: 图片路径
    """
    piece_names = {
        'ELEPHANT': 'elephant',
        'LION': 'lion',
        'TIGER': 'tiger',
        'LEOPARD': 'leopard',
        'WOLF': 'wolf',
        'DOG': 'dog',
        'CAT': 'cat',
        'RAT': 'rat'
    }
    
    piece_name = piece_names[piece_type.name]
    return os.path.join('images', f'{piece_name}_{player}.svg')