"""
Экология: рост растений, распространение растительности, влияние воды на биосферу
"""
import math
from utils.config import PLANT_GROWTH_RATE, PLANT_MIN_WATER, PLANT_MAX_DENSITY
from utils.math_utils import clamp


class Ecology:
    """Система экологии для моделирования роста растений"""
    
    def __init__(self):
        self.growth_rate = PLANT_GROWTH_RATE
        self.carrying_capacity_factor = 1.0  # Фактор несущей способности
    
    def update_chunk(self, chunk, world_manager, dt):
        """
        Обновляет экологию в чанке.
        
        Использует логистическую модель роста: dP/dt = r * P * (1 - P/K)
        где P - плотность популяции, r - скорость роста, K - несущая способность
        
        Args:
            chunk: Chunk для обновления
            world_manager: менеджер мира
            dt: время с последнего обновления
        """
        tiles = chunk.get_all_tiles()
        
        for tile in tiles:
            if tile.terrain_type.value == 'stone':
                continue  # Растения не растут на камнях
            
            # Обновляем рост растений
            self._update_plant_growth(tile, world_manager, dt)
            
            # Обновляем распространение растений
            self._update_plant_spread(tile, world_manager, dt)
            
            # Обновляем влажность почвы на основе воды
            self._update_soil_humidity(tile)
    
    def _update_plant_growth(self, tile, world_manager, dt):
        """
        Обновляет рост растений на тайле.
        
        Логистическая модель: dP/dt = r * P * (1 - P/K)
        где K зависит от уровня воды
        """
        # Несущая способность зависит от уровня воды
        # K = K_max * (water_level / water_optimal)
        optimal_water = 50.0
        water_factor = min(tile.water_level / optimal_water, 1.0)
        carrying_capacity = PLANT_MAX_DENSITY * water_factor * self.carrying_capacity_factor
        
        # Минимальный уровень воды для роста
        if tile.water_level < PLANT_MIN_WATER:
            # Растения умирают при недостатке воды
            tile.plant_density = max(0.0, tile.plant_density - self.growth_rate * dt * 2)
            return
        
        # Скорость роста зависит от воды
        growth_rate = self.growth_rate * water_factor
        
        # Логистический рост
        if carrying_capacity > 0:
            # dP/dt = r * P * (1 - P/K)
            growth = growth_rate * tile.plant_density * (1.0 - tile.plant_density / carrying_capacity) * dt
            tile.plant_density = clamp(
                tile.plant_density + growth,
                0.0,
                PLANT_MAX_DENSITY
            )
    
    def _update_plant_spread(self, tile, world_manager, dt):
        """
        Обновляет распространение растений от соседних тайлов.
        
        Использует диффузионную модель распространения.
        """
        # Получаем соседей
        neighbors = [
            world_manager.get_tile(tile.x + 1, tile.y),
            world_manager.get_tile(tile.x - 1, tile.y),
            world_manager.get_tile(tile.x, tile.y + 1),
            world_manager.get_tile(tile.x, tile.y - 1),
        ]
        
        # Вычисляем среднюю плотность растений у соседей
        neighbor_density_sum = 0.0
        neighbor_count = 0
        
        for neighbor in neighbors:
            if neighbor and neighbor.terrain_type.value != 'stone':
                neighbor_density_sum += neighbor.plant_density
                neighbor_count += 1
        
        if neighbor_count == 0:
            return
        
        avg_neighbor_density = neighbor_density_sum / neighbor_count
        
        # Распространение происходит только если у соседей больше растений
        if avg_neighbor_density > tile.plant_density:
            # Скорость распространения зависит от разности плотностей
            spread_rate = 0.1  # Константа распространения
            density_diff = avg_neighbor_density - tile.plant_density
            
            # Распространение также зависит от уровня воды
            water_factor = min(tile.water_level / PLANT_MIN_WATER, 1.0)
            
            spread = spread_rate * density_diff * water_factor * dt
            tile.plant_density = clamp(
                tile.plant_density + spread,
                0.0,
                PLANT_MAX_DENSITY
            )
    
    def _update_soil_humidity(self, tile):
        """
        Обновляет влажность почвы на основе уровня воды.
        
        Влажность влияет на тип местности и доступность воды для растений.
        """
        # Влажность почвы зависит от уровня воды
        # Используем экспоненциальное затухание
        target_humidity = tile.water_level
        
        # Плавное изменение влажности
        humidity_change = (target_humidity - tile.humidity) * 0.1
        tile.humidity = clamp(tile.humidity + humidity_change, 0.0, 100.0)
    
    def get_biomass_in_radius(self, world_manager, center_x, center_y, radius):
        """
        Вычисляет общую биомассу (растительность) в радиусе.
        
        Args:
            world_manager: менеджер мира
            center_x, center_y: центр области
            radius: радиус
        
        Returns:
            Общая биомасса
        """
        tiles = world_manager.get_tiles_in_radius(center_x, center_y, radius)
        total_biomass = sum(tile.plant_density for tile in tiles)
        return total_biomass
    
    def get_water_availability(self, world_manager, center_x, center_y, radius):
        """
        Вычисляет доступность воды в области.
        
        Args:
            world_manager: менеджер мира
            center_x, center_y: центр области
            radius: радиус
        
        Returns:
            Средний уровень воды в области
        """
        tiles = world_manager.get_tiles_in_radius(center_x, center_y, radius)
        if len(tiles) == 0:
            return 0.0
        
        total_water = sum(tile.water_level for tile in tiles)
        return total_water / len(tiles)
    
    def influence_on_npc_behavior(self, world_manager, x, y):
        """
        Возвращает влияние экологии на поведение NPC.
        
        NPC становятся более дружелюбными в областях с высокой биомассой
        и доступностью воды.
        
        Returns:
            dict с факторами влияния
        """
        biomass = self.get_biomass_in_radius(world_manager, x, y, 10)
        water_availability = self.get_water_availability(world_manager, x, y, 10)
        
        # Фактор дружелюбности (0-1)
        friendliness = min(1.0, (biomass / 10.0 + water_availability / 100.0) / 2.0)
        
        # Фактор агрессивности (обратный дружелюбности)
        aggressiveness = 1.0 - friendliness
        
        return {
            'friendliness': friendliness,
            'aggressiveness': aggressiveness,
            'biomass': biomass,
            'water_availability': water_availability,
        }
