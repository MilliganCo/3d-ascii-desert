"""
Управление миром и координация систем
"""
from world.chunk import ChunkManager
from world.generator import WorldGenerator
from utils.config import VISIBLE_CHUNKS_X, VISIBLE_CHUNKS_Y, CHUNK_SIZE


class WorldManager:
    """Управляет миром, координацией чанков и физических систем"""
    
    def __init__(self, seed=None):
        self.chunk_manager = ChunkManager()
        self.generator = WorldGenerator(seed)
        self.global_water_level = 50.0  # Глобальный уровень воды в пустыне (0-100)
        
    def get_tile(self, x, y):
        """Получает тайл по мировым координатам"""
        tile = self.chunk_manager.get_tile(x, y)
        
        # Если тайл не существует, генерируем чанк
        if tile is None:
            chunk = self.chunk_manager.get_chunk_for_world_pos(x, y)
            if not chunk.generated:
                self.generator.generate_chunk(chunk)
            tile = chunk.get_tile(x, y)
        
        return tile
    
    def set_tile(self, x, y, tile):
        """Устанавливает тайл"""
        self.chunk_manager.set_tile(x, y, tile)
    
    def get_chunks_around(self, center_x, center_y, radius_chunks=None):
        """
        Получает чанки вокруг точки.
        
        Args:
            center_x, center_y: центр в мировых координатах
            radius_chunks: радиус в чанках (по умолчанию из конфига)
        """
        if radius_chunks is None:
            radius_chunks = max(VISIBLE_CHUNKS_X, VISIBLE_CHUNKS_Y) // 2 + 1
        
        chunks = self.chunk_manager.get_chunks_in_radius(
            center_x, center_y, radius_chunks
        )
        
        # Убеждаемся, что все чанки сгенерированы
        for chunk in chunks:
            if not chunk.generated:
                self.generator.generate_chunk(chunk)
        
        return chunks
    
    def get_tiles_in_radius(self, center_x, center_y, radius):
        """
        Получает все тайлы в радиусе от точки.
        
        Args:
            center_x, center_y: центр
            radius: радиус в тайлах
        
        Returns:
            Список тайлов
        """
        tiles = []
        min_x = int(center_x - radius)
        max_x = int(center_x + radius)
        min_y = int(center_y - radius)
        max_y = int(center_y + radius)
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                tile = self.get_tile(x, y)
                if tile:
                    tiles.append(tile)
        
        return tiles
    
    def update(self, dt):
        """Обновляет мир (вызывается каждый кадр)"""
        # Здесь будут обновляться физические системы
        pass
    
    def get_global_water_level(self):
        """Возвращает глобальный уровень воды в пустыне"""
        return self.global_water_level
    
    def set_global_water_level(self, level):
        """Устанавливает глобальный уровень воды"""
        from utils.config import WATER_MIN_LEVEL, WATER_MAX_LEVEL
        from utils.math_utils import clamp
        self.global_water_level = clamp(level, WATER_MIN_LEVEL, WATER_MAX_LEVEL)
