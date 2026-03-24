"""
Управление камерой
"""
import pygame
import math
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT, ISO_SCALE
from utils.math_utils import lerp, world_to_isometric


class Camera:
    """Камера, следующая за игроком"""
    
    def __init__(self):
        self.x = 0.0  # Изометрическая X координата камеры
        self.y = 0.0  # Изометрическая Y координата камеры
        self.target_x = 0.0
        self.target_y = 0.0
        self.smoothness = 0.2  # Скорость следования (увеличено для более быстрой реакции)
        
    def set_target(self, world_x, world_y):
        """
        Устанавливает цель для камеры в мировых координатах.
        
        Args:
            world_x, world_y: мировые координаты цели
        """
        # Преобразуем мировые координаты в изометрические для камеры
        iso_x, iso_y = world_to_isometric(world_x, world_y, 0, ISO_SCALE)
        self.target_x = iso_x
        self.target_y = iso_y
    
    def update(self, dt):
        """Обновляет позицию камеры"""
        # Плавное следование за целью
        self.x = lerp(self.x, self.target_x, self.smoothness * dt * 60)
        self.y = lerp(self.y, self.target_y, self.smoothness * dt * 60)
    
    def world_to_screen(self, iso_x, iso_y):
        """
        Преобразует изометрические координаты в экранные.
        
        Args:
            iso_x, iso_y: изометрические координаты (уже преобразованные из мировых)
        """
        screen_x = iso_x - self.x + SCREEN_WIDTH // 2
        screen_y = iso_y - self.y + SCREEN_HEIGHT // 2
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x, screen_y):
        """Преобразует экранные координаты в мировые"""
        world_x = screen_x + self.x - SCREEN_WIDTH // 2
        world_y = screen_y + self.y - SCREEN_HEIGHT // 2
        return world_x, world_y
    
    def get_view_bounds(self):
        """
        Возвращает границы видимой области в мировых координатах.
        Используется для фильтрации тайлов перед рендерингом.
        """
        # Упрощенная оценка видимой области - используем большой радиус
        # чтобы гарантировать видимость тайлов
        margin_world = 100  # Увеличен запас в мировых координатах
        
        # Преобразуем изометрические координаты камеры обратно в мировые
        # Используем обратное преобразование из world_to_isometric
        iso_scale_inv = 1.0 / ISO_SCALE
        center_world_x = (self.x * iso_scale_inv) / math.cos(math.pi / 4)
        center_world_y = (self.y * iso_scale_inv) / math.sin(math.pi / 4)
        
        # Учитываем размер экрана в мировых координатах
        screen_margin_x = (SCREEN_WIDTH * iso_scale_inv) / 2
        screen_margin_y = (SCREEN_HEIGHT * iso_scale_inv) / 2
        
        min_x = center_world_x - screen_margin_x - margin_world
        max_x = center_world_x + screen_margin_x + margin_world
        min_y = center_world_y - screen_margin_y - margin_world
        max_y = center_world_y + screen_margin_y + margin_world
        
        return min_x, max_x, min_y, max_y
