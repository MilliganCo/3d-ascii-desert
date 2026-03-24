"""
Типы местности и тайлы
"""
from enum import Enum


class TerrainType(Enum):
    """Типы местности"""
    SAND = "sand"
    WATER = "water"
    STONE = "stone"
    PLANT = "plant"


class Tile:
    """Представляет один тайл в мире"""
    
    def __init__(self, x, y, terrain_type=TerrainType.SAND, height=0.0, water_level=0.0):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.height = height  # Высота тайла
        self.water_level = water_level  # Уровень воды (0-100)
        self.plant_density = 0.0  # Плотность растительности (0-1)
        self.humidity = 0.0  # Влажность почвы (0-100)
        self.needs_update = True  # Флаг для оптимизации обновлений
    
    def get_effective_terrain(self):
        """Возвращает эффективный тип местности с учетом воды"""
        if self.water_level > 50:
            return TerrainType.WATER
        elif self.plant_density > 0.3:
            return TerrainType.PLANT
        elif self.terrain_type == TerrainType.STONE:
            return TerrainType.STONE
        else:
            return TerrainType.SAND
    
    def add_water(self, amount):
        """Добавляет воду к тайлу"""
        from utils.config import WATER_MAX_LEVEL
        old_level = self.water_level
        self.water_level = min(self.water_level + amount, WATER_MAX_LEVEL)
        if abs(self.water_level - old_level) > 0.01:
            self.needs_update = True
    
    def remove_water(self, amount):
        """Удаляет воду из тайла"""
        from utils.config import WATER_MIN_LEVEL
        old_level = self.water_level
        self.water_level = max(self.water_level - amount, WATER_MIN_LEVEL)
        if abs(self.water_level - old_level) > 0.01:
            self.needs_update = True
