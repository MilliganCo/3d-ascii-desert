"""
Цветовая схема для ASCII графики
"""
from utils.config import (
    COLOR_SAND, COLOR_WATER, COLOR_STONE, COLOR_PLANT,
    COLOR_PLAYER, COLOR_NPC
)


class Colors:
    """Цветовая палитра игры"""
    
    # Цвета тайлов
    SAND = COLOR_SAND
    WATER = COLOR_WATER
    STONE = COLOR_STONE
    PLANT = COLOR_PLANT
    
    # Цвета персонажей
    PLAYER = COLOR_PLAYER
    NPC = COLOR_NPC
    
    # UI цвета
    UI_BACKGROUND = (20, 20, 20)
    UI_TEXT = (255, 255, 255)
    UI_BORDER = (100, 100, 100)
    UI_SELECTED = (255, 200, 0)
    
    # Статус-бар
    HEALTH_BAR = (255, 0, 0)
    WATER_BAR = (64, 164, 223)
    BAR_BACKGROUND = (50, 50, 50)
    
    # Дополнительные цвета для сообщений
    PLANT = COLOR_PLANT
    
    @staticmethod
    def get_tile_color(tile_type):
        """Возвращает цвет для типа тайла"""
        color_map = {
            'sand': Colors.SAND,
            'water': Colors.WATER,
            'stone': Colors.STONE,
            'plant': Colors.PLANT,
        }
        return color_map.get(tile_type, Colors.SAND)
    
    @staticmethod
    def get_ascii_char(tile_type):
        """Возвращает ASCII символ для типа тайла"""
        from utils.config import (
            ASCII_SAND, ASCII_WATER, ASCII_STONE, ASCII_PLANT
        )
        char_map = {
            'sand': ASCII_SAND,
            'water': ASCII_WATER,
            'stone': ASCII_STONE,
            'plant': ASCII_PLANT,
        }
        return char_map.get(tile_type, ASCII_SAND)
