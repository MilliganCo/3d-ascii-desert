"""
Система инвентаря и ресурсов
"""
from utils.config import PLAYER_MAX_WATER


class Inventory:
    """Инвентарь игрока"""
    
    def __init__(self):
        self.water = PLAYER_MAX_WATER / 2  # Начальное количество воды
        self.stones = 0
        self.sand = 0
        self.devices = []  # Устройства для добычи воды
        
    def add_water(self, amount):
        """Добавляет воду в инвентарь"""
        from utils.config import PLAYER_MAX_WATER
        from utils.math_utils import clamp
        self.water = clamp(self.water + amount, 0, PLAYER_MAX_WATER)
    
    def remove_water(self, amount):
        """Удаляет воду из инвентаря"""
        from utils.math_utils import clamp
        self.water = clamp(self.water - amount, 0, PLAYER_MAX_WATER)
        return min(amount, self.water)
    
    def has_water(self, amount):
        """Проверяет, есть ли достаточно воды"""
        return self.water >= amount
    
    def add_resource(self, resource_type, amount):
        """Добавляет ресурс"""
        if resource_type == 'stone':
            self.stones += amount
        elif resource_type == 'sand':
            self.sand += amount
    
    def get_resource(self, resource_type):
        """Получает количество ресурса"""
        if resource_type == 'stone':
            return self.stones
        elif resource_type == 'sand':
            return self.sand
        elif resource_type == 'water':
            return self.water
        return 0
