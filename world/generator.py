"""
Процедурная генерация ландшафта
"""
import random
import noise
import numpy as np
from world.terrain import Tile, TerrainType
from world.chunk import Chunk
from utils.config import CHUNK_SIZE


class WorldGenerator:
    """Генератор процедурного мира"""
    
    def __init__(self, seed=None):
        if seed is None:
            seed = random.randint(0, 1000000)
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Параметры для noise функций
        self.height_scale = 0.05  # Масштаб для высот
        self.moisture_scale = 0.03  # Масштаб для влажности
        self.temperature_scale = 0.02  # Масштаб для температуры
        
    def generate_chunk(self, chunk):
        """
        Генерирует содержимое чанка.
        
        Args:
            chunk: Chunk объект для заполнения
        """
        if chunk.generated:
            return
        
        min_x, max_x, min_y, max_y = chunk.get_world_bounds()
        
        # Генерируем тайлы для чанка
        for x in range(int(min_x), int(max_x)):
            for y in range(int(min_y), int(max_y)):
                tile = self._generate_tile(x, y)
                chunk.set_tile(x, y, tile)
        
        chunk.generated = True
    
    def _generate_tile(self, x, y):
        """
        Генерирует один тайл на основе координат.
        
        Args:
            x, y: мировые координаты
        
        Returns:
            Tile объект
        """
        # Генерируем высоту с помощью Perlin noise
        height = self._get_height(x, y)
        
        # Генерируем базовую влажность
        moisture = self._get_moisture(x, y)
        
        # Определяем тип местности на основе высоты и влажности
        terrain_type = self._determine_terrain_type(height, moisture)
        
        # Начальный уровень воды зависит от типа местности
        water_level = 0.0
        if terrain_type == TerrainType.WATER:
            water_level = 80.0 + random.uniform(-10, 10)
        elif moisture > 0.6:
            water_level = moisture * 30.0
        
        # Создаем тайл
        tile = Tile(x, y, terrain_type, height, water_level)
        tile.humidity = moisture * 100.0
        
        # Добавляем случайные особенности
        self._add_features(tile, x, y, height, moisture)
        
        return tile
    
    def _get_height(self, x, y):
        """Генерирует высоту для координаты"""
        try:
            # Используем несколько октав noise для более реалистичного ландшафта
            h1 = noise.pnoise2(x * self.height_scale, y * self.height_scale, 
                              octaves=4, persistence=0.5, lacunarity=2.0, 
                              base=self.seed)
            h2 = noise.pnoise2(x * self.height_scale * 2, y * self.height_scale * 2,
                              octaves=2, persistence=0.3, lacunarity=2.0,
                              base=self.seed + 1000)
            
            height = (h1 * 0.7 + h2 * 0.3 + 1.0) / 2.0  # Нормализуем к 0-1
            return height * 50.0  # Масштабируем до 0-50
        except Exception as e:
            # Если noise не работает, используем простую функцию
            import math
            return (math.sin(x * 0.1) + math.cos(y * 0.1)) * 10 + 25
    
    def _get_moisture(self, x, y):
        """Генерирует базовую влажность для координаты"""
        try:
            moisture = noise.pnoise2(x * self.moisture_scale, y * self.moisture_scale,
                                    octaves=3, persistence=0.5, lacunarity=2.0,
                                    base=self.seed + 2000)
            return (moisture + 1.0) / 2.0  # Нормализуем к 0-1
        except Exception as e:
            # Если noise не работает, используем простую функцию
            import math
            return (math.sin(x * 0.05) * math.cos(y * 0.05) + 1.0) / 2.0
    
    def _determine_terrain_type(self, height, moisture):
        """Определяет тип местности на основе высоты и влажности"""
        # Низкие места с высокой влажностью = вода
        if height < 15 and moisture > 0.7:
            return TerrainType.WATER
        
        # Высокие места = камни
        if height > 35:
            return TerrainType.STONE
        
        # Остальное = песок (растительность добавится позже через экологию)
        return TerrainType.SAND
    
    def _add_features(self, tile, x, y, height, moisture):
        """Добавляет случайные особенности к тайлу"""
        # Оазисы (редкие участки с водой)
        if random.random() < 0.001 and moisture > 0.5:
            tile.water_level = 90.0 + random.uniform(-5, 5)
            tile.terrain_type = TerrainType.WATER
        
        # Редкие камни
        if random.random() < 0.01 and height > 20:
            tile.terrain_type = TerrainType.STONE
        
        # Начальная растительность (будет развиваться через экологию)
        if moisture > 0.6 and height < 30:
            tile.plant_density = moisture * 0.3
    
    def generate_oasis(self, x, y, radius=5):
        """
        Генерирует оазис в указанной точке.
        
        Args:
            x, y: центр оазиса
            radius: радиус оазиса
        """
        # Это будет использоваться для генерации специальных структур
        pass
