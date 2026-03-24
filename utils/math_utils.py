"""
Математические утилиты для изометрической проекции
"""
import math
import numpy as np


def world_to_isometric(x, y, z=0, scale=20.0):
    """
    Преобразует мировые координаты в изометрические экранные координаты.
    
    Args:
        x: X координата в мире
        y: Y координата в мире
        z: Z координата (высота) в мире
        scale: Масштаб для изометрической проекции
    
    Returns:
        (screen_x, screen_y) - координаты на экране
    """
    # Изометрическая проекция: поворот на 45 градусов и сжатие по Y
    iso_x = (x - y) * math.cos(math.pi / 4) * scale
    iso_y = (x + y) * math.sin(math.pi / 4) * scale - z * scale * 0.5
    
    return iso_x, iso_y


def isometric_to_world(screen_x, screen_y):
    """
    Преобразует изометрические экранные координаты в мировые координаты.
    
    Args:
        screen_x: X координата на экране
        screen_y: Y координата на экране
    
    Returns:
        (world_x, world_y) - координаты в мире
    """
    # Обратное преобразование
    world_x = (screen_x / math.cos(math.pi / 4) + screen_y / math.sin(math.pi / 4)) / 2
    world_y = (screen_y / math.sin(math.pi / 4) - screen_x / math.cos(math.pi / 4)) / 2
    
    return world_x, world_y


def distance_3d(x1, y1, z1, x2, y2, z2):
    """Вычисляет расстояние между двумя точками в 3D пространстве."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)


def distance_2d(x1, y1, x2, y2):
    """Вычисляет расстояние между двумя точками в 2D пространстве."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def clamp(value, min_value, max_value):
    """Ограничивает значение между min и max."""
    return max(min_value, min(value, max_value))


def lerp(a, b, t):
    """Линейная интерполяция между a и b."""
    return a + (b - a) * t


def smoothstep(edge0, edge1, x):
    """Smoothstep функция для плавных переходов."""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)
