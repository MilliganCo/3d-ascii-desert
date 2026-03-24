"""
Гидродинамика: распространение воды по ландшафту
"""
import numpy as np
from utils.config import WATER_DIFFUSION_RATE, WATER_MAX_LEVEL, WATER_MIN_LEVEL
from utils.math_utils import clamp


class Hydrodynamics:
    """Система гидродинамики для распространения воды"""
    
    def __init__(self):
        self.diffusion_rate = WATER_DIFFUSION_RATE
        self.darcy_constant = 0.5  # Константа для закона Дарси
    
    def update_chunk(self, chunk, world_manager, dt):
        """
        Обновляет распространение воды в чанке.
        
        Использует закон Дарси для просачивания и уравнение диффузии
        для распространения воды.
        
        Args:
            chunk: Chunk для обновления
            world_manager: менеджер мира для доступа к соседним тайлам
            dt: время с последнего обновления
        """
        # Получаем все тайлы чанка
        tiles = chunk.get_all_tiles()
        
        # Создаем копию уровней воды для параллельного обновления
        water_changes = {}
        
        for tile in tiles:
            if not tile.needs_update:
                continue
            
            # Вычисляем изменения воды
            water_change = self._calculate_water_flow(tile, world_manager, dt)
            water_changes[(tile.x, tile.y)] = water_change
        
        # Применяем изменения
        for (x, y), change in water_changes.items():
            tile = chunk.get_tile(x, y)
            if tile:
                tile.water_level = clamp(
                    tile.water_level + change,
                    WATER_MIN_LEVEL,
                    WATER_MAX_LEVEL
                )
                tile.needs_update = True
        
        # Сбрасываем флаги обновления
        for tile in tiles:
            tile.needs_update = False
    
    def _calculate_water_flow(self, tile, world_manager, dt):
        """
        Вычисляет поток воды для тайла на основе закона Дарси.
        
        Закон Дарси: q = -K * ∇h
        где q - поток, K - проницаемость, h - напор
        
        Args:
            tile: тайл для расчета
            world_manager: менеджер мира
            dt: время
        
        Returns:
            Изменение уровня воды
        """
        total_change = 0.0
        
        # Получаем соседние тайлы (4 направления)
        neighbors = [
            world_manager.get_tile(tile.x + 1, tile.y),  # Вправо
            world_manager.get_tile(tile.x - 1, tile.y),  # Влево
            world_manager.get_tile(tile.x, tile.y + 1),  # Вниз
            world_manager.get_tile(tile.x, tile.y - 1),  # Вверх
        ]
        
        for neighbor in neighbors:
            if neighbor is None:
                continue
            
            # Вычисляем градиент напора
            # Напор = высота + уровень воды
            head_current = tile.height + tile.water_level
            head_neighbor = neighbor.height + neighbor.water_level
            
            gradient = head_neighbor - head_current
            
            # Вода течет вниз по градиенту
            if gradient < 0:  # Сосед выше
                # Вода течет от соседа к текущему тайлу
                flow_rate = self.darcy_constant * abs(gradient) * dt
                flow_rate = min(flow_rate, neighbor.water_level * 0.1)  # Ограничиваем поток
                total_change += flow_rate
            elif gradient > 0:  # Текущий тайл выше
                # Вода течет от текущего тайла к соседу
                flow_rate = self.darcy_constant * gradient * dt
                flow_rate = min(flow_rate, tile.water_level * 0.1)
                total_change -= flow_rate
        
        # Диффузия (распространение воды)
        diffusion_change = self._calculate_diffusion(tile, neighbors, dt)
        total_change += diffusion_change
        
        return total_change
    
    def _calculate_diffusion(self, tile, neighbors, dt):
        """
        Вычисляет диффузию воды (уравнение диффузии: ∂u/∂t = D * ∇²u).
        
        Args:
            tile: текущий тайл
            neighbors: список соседних тайлов
            dt: время
        
        Returns:
            Изменение уровня воды от диффузии
        """
        if len(neighbors) == 0:
            return 0.0
        
        # Вычисляем лапласиан (вторую производную)
        neighbor_water_sum = sum(
            n.water_level for n in neighbors if n is not None
        )
        neighbor_count = sum(1 for n in neighbors if n is not None)
        
        if neighbor_count == 0:
            return 0.0
        
        avg_neighbor_water = neighbor_water_sum / neighbor_count
        laplacian = avg_neighbor_water - tile.water_level
        
        # Уравнение диффузии
        diffusion = self.diffusion_rate * laplacian * dt
        
        return diffusion
    
    def add_water_source(self, world_manager, x, y, amount):
        """
        Добавляет источник воды в указанной точке.
        
        Args:
            world_manager: менеджер мира
            x, y: координаты источника
            amount: количество воды
        """
        tile = world_manager.get_tile(x, y)
        if tile:
            tile.add_water(amount)
            tile.needs_update = True
            
            # Помечаем соседние тайлы для обновления
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = world_manager.get_tile(x + dx, y + dy)
                if neighbor:
                    neighbor.needs_update = True
