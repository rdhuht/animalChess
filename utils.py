import os
import pygame

def load_image(file_path, size):
    """
    加载图片文件并转换为指定大小的Pygame Surface对象
    :param file_path: 图片文件路径
    :param size: 目标大小 (width, height)
    :return: Pygame Surface对象
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"图片文件不存在: {file_path}")

    # 加载图片并缩放到指定大小
    image = pygame.image.load(file_path)
    return pygame.transform.scale(image, size)

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
    return os.path.join('images', f'{piece_name}_{player}.png')