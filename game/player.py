"""
Система игрока
"""
import pygame
from utils.config import (
    PLAYER_START_WATER, PLAYER_START_HEALTH, PLAYER_MAX_WATER,
    PLAYER_MAX_HEALTH, PLAYER_WATER_DRAIN_RATE, PLAYER_MOVE_SPEED
)
from utils.math_utils import clamp
from game.inventory import Inventory


class Player:
    """Игрок"""
    
    def __init__(self, start_x=0, start_y=0):
        self.x = float(start_x)
        self.y = float(start_y)
        self.z = 0.0  # Высота игрока
        
        self.health = PLAYER_START_HEALTH
        self.water_level = PLAYER_START_WATER  # Уровень воды в организме
        
        self.inventory = Inventory()
        
        self.move_speed = PLAYER_MOVE_SPEED
        self.is_moving = False
        
        # Время с последнего обновления
        self.last_update_time = 0.0
        
    def update(self, dt, world_manager):
        """
        Обновляет состояние игрока.
        
        Args:
            dt: время с последнего кадра в секундах
            world_manager: менеджер мира для проверки коллизий
        """
        # Расход воды со временем
        self._drain_water(dt)
        
        # Обновляем высоту на основе тайла под игроком
        tile = world_manager.get_tile(int(self.x), int(self.y))
        if tile:
            self.z = tile.height + 0.5  # Игрок немного выше тайла
        
        self.last_update_time += dt
    
    def _drain_water(self, dt):
        """Расходует воду со временем"""
        drain_amount = PLAYER_WATER_DRAIN_RATE * dt
        if self.is_moving:
            drain_amount *= 1.5  # Больше расход при движении
        
        self.water_level = clamp(
            self.water_level - drain_amount,
            0.0,
            PLAYER_MAX_WATER
        )
        
        # Если воды нет, теряем здоровье
        if self.water_level <= 0:
            health_loss = 5.0 * dt  # Потеря здоровья при жажде
            self.health = clamp(self.health - health_loss, 0.0, PLAYER_MAX_HEALTH)
    
    def move(self, dx, dy, dt, world_manager):
        """
        Перемещает игрока.
        
        Args:
            dx, dy: направление движения
            dt: время с последнего кадра
            world_manager: менеджер мира для проверки коллизий
        """
        # Нормализуем вектор направления
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            dx /= length
            dy /= length
        
        # Вычисляем новую позицию
        new_x = self.x + dx * self.move_speed * dt
        new_y = self.y + dy * self.move_speed * dt
        
        # Проверяем коллизии (можно ходить по воде и песку, но не по камням)
        tile = world_manager.get_tile(int(new_x), int(new_y))
        if tile and tile.terrain_type.value != 'stone':
            self.x = new_x
            self.y = new_y
            self.is_moving = True
        else:
            self.is_moving = False
    
    def drink_water(self, amount):
        """
        Питье воды из инвентаря.
        
        Args:
            amount: количество воды для питья
        
        Returns:
            Фактически выпитое количество воды
        """
        if not self.inventory.has_water(amount):
            amount = self.inventory.water
        
        if amount > 0:
            self.inventory.remove_water(amount)
            self.water_level = clamp(
                self.water_level + amount * 0.8,  # 80% эффективность
                0.0,
                PLAYER_MAX_WATER
            )
            
            # Восстановление здоровья при питье
            if self.health < PLAYER_MAX_HEALTH:
                self.health = clamp(
                    self.health + amount * 0.1,
                    0.0,
                    PLAYER_MAX_HEALTH
                )
            
            # Возвращаем сообщение для лога
            return amount, f"Выпито {amount:.1f} воды. Уровень воды: {self.water_level:.1f}"
        
        return 0, "Нет воды в инвентаре"
    
    def collect_water(self, amount):
        """Собирает воду в инвентарь"""
        self.inventory.add_water(amount)
    
    def is_alive(self):
        """Проверяет, жив ли игрок"""
        return self.health > 0
    
    def handle_input(self, keys, dt, world_manager):
        """
        Обрабатывает ввод игрока.
        
        Args:
            keys: словарь нажатых клавиш (pygame.key.get_pressed())
            dt: время с последнего кадра
            world_manager: менеджер мира
        """
        dx = 0
        dy = 0
        
        # WASD или стрелки
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        
        if dx != 0 or dy != 0:
            self.move(dx, dy, dt, world_manager)
        else:
            self.is_moving = False
        
        # Автоматическое питье при низком уровне воды (опционально)
        if self.water_level < 20 and self.inventory.water > 0:
            self.drink_water(10)
