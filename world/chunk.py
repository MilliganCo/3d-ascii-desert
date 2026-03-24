"""
Система чанков для бесконечного мира
"""
from world.terrain import Tile, TerrainType
from utils.config import CHUNK_SIZE


class Chunk:
    """Представляет один чанк мира"""
    
    def __init__(self, chunk_x, chunk_y):
        self.chunk_x = chunk_x  # Координаты чанка
        self.chunk_y = chunk_y
        self.tiles = {}  # Словарь тайлов: (x, y) -> Tile
        self.generated = False
        self.last_accessed = 0  # Время последнего доступа (для выгрузки)
        
    def get_tile(self, x, y):
        """
        Получает тайл по мировым координатам.
        
        Args:
            x, y: мировые координаты тайла
        
        Returns:
            Tile или None если тайл не существует
        """
        key = (x, y)
        return self.tiles.get(key)
    
    def set_tile(self, x, y, tile):
        """Устанавливает тайл в чанке"""
        key = (x, y)
        self.tiles[key] = tile
    
    def get_world_bounds(self):
        """Возвращает границы чанка в мировых координатах"""
        min_x = self.chunk_x * CHUNK_SIZE
        max_x = (self.chunk_x + 1) * CHUNK_SIZE
        min_y = self.chunk_y * CHUNK_SIZE
        max_y = (self.chunk_y + 1) * CHUNK_SIZE
        return min_x, max_x, min_y, max_y
    
    def get_all_tiles(self):
        """Возвращает все тайлы в чанке"""
        return list(self.tiles.values())
    
    def is_coord_in_chunk(self, x, y):
        """Проверяет, находится ли координата в этом чанке"""
        min_x, max_x, min_y, max_y = self.get_world_bounds()
        return min_x <= x < max_x and min_y <= y < max_y


class ChunkManager:
    """Управляет загрузкой и выгрузкой чанков"""
    
    def __init__(self):
        self.chunks = {}  # (chunk_x, chunk_y) -> Chunk
        self.max_loaded_chunks = 100  # Максимум загруженных чанков
        self.access_counter = 0  # Счетчик для отслеживания времени доступа
        self.chunk_cache = {}  # Кэш для оптимизации доступа
    
    def get_chunk(self, chunk_x, chunk_y):
        """
        Получает чанк по координатам чанка.
        Создает новый чанк, если его нет.
        """
        key = (chunk_x, chunk_y)
        if key not in self.chunks:
            chunk = Chunk(chunk_x, chunk_y)
            self.chunks[key] = chunk
            self._check_memory_limit()
        
        chunk = self.chunks[key]
        chunk.last_accessed = self.access_counter
        self.access_counter += 1
        return chunk
    
    def get_chunk_for_world_pos(self, world_x, world_y):
        """Получает чанк для мировых координат"""
        chunk_x = int(world_x // CHUNK_SIZE)
        chunk_y = int(world_y // CHUNK_SIZE)
        return self.get_chunk(chunk_x, chunk_y)
    
    def get_tile(self, world_x, world_y):
        """Получает тайл по мировым координатам"""
        chunk = self.get_chunk_for_world_pos(world_x, world_y)
        return chunk.get_tile(int(world_x), int(world_y))
    
    def set_tile(self, world_x, world_y, tile):
        """Устанавливает тайл по мировым координатам"""
        chunk = self.get_chunk_for_world_pos(world_x, world_y)
        chunk.set_tile(int(world_x), int(world_y), tile)
    
    def get_chunks_in_radius(self, center_x, center_y, radius_chunks):
        """
        Возвращает все чанки в радиусе от центра.
        
        Args:
            center_x, center_y: центр в мировых координатах
            radius_chunks: радиус в чанках
        """
        center_chunk_x = int(center_x // CHUNK_SIZE)
        center_chunk_y = int(center_y // CHUNK_SIZE)
        
        chunks = []
        for dx in range(-radius_chunks, radius_chunks + 1):
            for dy in range(-radius_chunks, radius_chunks + 1):
                chunk_x = center_chunk_x + dx
                chunk_y = center_chunk_y + dy
                chunk = self.get_chunk(chunk_x, chunk_y)
                chunks.append(chunk)
        
        return chunks
    
    def _check_memory_limit(self):
        """Проверяет лимит памяти и выгружает старые чанки"""
        if len(self.chunks) <= self.max_loaded_chunks:
            return
        
        # Сортируем чанки по времени последнего доступа
        sorted_chunks = sorted(
            self.chunks.items(),
            key=lambda item: item[1].last_accessed
        )
        
        # Выгружаем самые старые чанки
        chunks_to_unload = len(self.chunks) - self.max_loaded_chunks
        for i in range(chunks_to_unload):
            key, chunk = sorted_chunks[i]
            # Не выгружаем сгенерированные чанки, которые еще не были использованы
            if chunk.generated:
                del self.chunks[key]
