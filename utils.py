import os
import pygame
import sys

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller创建临时文件夹,将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_image(file_path, size):
    """加载图片文件并转换为指定大小的Pygame Surface对象"""
    # 获取资源文件的实际路径
    actual_path = get_resource_path(file_path)
    if not os.path.exists(actual_path):
        raise FileNotFoundError(f"图片文件不存在: {actual_path}")

    # 加载图片并缩放到指定大小
    image = pygame.image.load(actual_path)
    return pygame.transform.scale(image, size)

def get_piece_image_path(piece_type, player):
    """获取棋子图片的路径"""
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
    return os.path.join('images', f'{piece_name}.png')
    return os.path.join('images', f'{piece_name}_{player}.png')