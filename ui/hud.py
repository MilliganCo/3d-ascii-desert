"""
HUD (Head-Up Display) - интерфейс игрока
"""
import pygame
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT
from engine.colors import Colors


class HUD:
    """Статус-бар и интерфейс игрока"""
    
    def __init__(self, screen):
        self.screen = screen
        try:
            self.font = pygame.font.Font(None, 24)
        except Exception:
            try:
                self.font = pygame.font.SysFont('arial', 24)
            except Exception:
                self.font = pygame.font.SysFont(None, 24)
        try:
            self.small_font = pygame.font.Font(None, 18)
        except Exception:
            try:
                self.small_font = pygame.font.SysFont('arial', 18)
            except Exception:
                self.small_font = pygame.font.SysFont(None, 18)
    
    def render(self, player, world_manager):
        """
        Рендерит HUD.
        
        Args:
            player: объект Player
            world_manager: менеджер мира
        """
        # Фон для HUD (смещён выше, чтобы не перекрывать консоль)
        hud_height = 100
        console_height = 150  # Высота консоли сообщений
        hud_rect = pygame.Rect(0, SCREEN_HEIGHT - hud_height - console_height, SCREEN_WIDTH, hud_height)
        pygame.draw.rect(self.screen, Colors.UI_BACKGROUND, hud_rect)
        pygame.draw.rect(self.screen, Colors.UI_BORDER, hud_rect, 2)
        
        # Здоровье
        self._render_health_bar(player, 10, SCREEN_HEIGHT - hud_height + 10)
        
        # Уровень воды в организме
        self._render_water_level_bar(player, 10, SCREEN_HEIGHT - hud_height + 40)
        
        # Вода в инвентаре
        self._render_inventory_water(player, 10, SCREEN_HEIGHT - hud_height + 70)
        
        # Координаты
        self._render_coordinates(player, SCREEN_WIDTH - 200, SCREEN_HEIGHT - hud_height + 10)
        
        # Глобальный уровень воды
        self._render_global_water(world_manager, SCREEN_WIDTH - 200, SCREEN_HEIGHT - hud_height + 40)
    
    def _render_health_bar(self, player, x, y):
        """Рендерит полосу здоровья"""
        bar_width = 200
        bar_height = 20
        
        # Фон полосы
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, Colors.BAR_BACKGROUND, bg_rect)
        
        # Полоса здоровья
        health_percent = player.health / 100.0
        health_width = int(bar_width * health_percent)
        health_rect = pygame.Rect(x, y, health_width, bar_height)
        pygame.draw.rect(self.screen, Colors.HEALTH_BAR, health_rect)
        
        # Граница
        pygame.draw.rect(self.screen, Colors.UI_BORDER, bg_rect, 1)
        
        # Текст
        text = self.font.render(f"Здоровье: {player.health:.1f}/100", True, Colors.UI_TEXT)
        self.screen.blit(text, (x, y - 25))
    
    def _render_water_level_bar(self, player, x, y):
        """Рендерит полосу уровня воды в организме"""
        bar_width = 200
        bar_height = 20
        
        # Фон полосы
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, Colors.BAR_BACKGROUND, bg_rect)
        
        # Полоса воды
        from utils.config import PLAYER_MAX_WATER
        water_percent = player.water_level / PLAYER_MAX_WATER
        water_width = int(bar_width * water_percent)
        water_rect = pygame.Rect(x, y, water_width, bar_height)
        pygame.draw.rect(self.screen, Colors.WATER_BAR, water_rect)
        
        # Граница
        pygame.draw.rect(self.screen, Colors.UI_BORDER, bg_rect, 1)
        
        # Текст
        text = self.font.render(f"Вода (организм): {player.water_level:.1f}/{PLAYER_MAX_WATER}", True, Colors.UI_TEXT)
        self.screen.blit(text, (x, y - 25))
    
    def _render_inventory_water(self, player, x, y):
        """Рендерит количество воды в инвентаре"""
        text = self.font.render(
            f"Вода (инвентарь): {player.inventory.water:.1f}",
            True,
            Colors.WATER_BAR
        )
        self.screen.blit(text, (x, y))
    
    def _render_coordinates(self, player, x, y):
        """Рендерит координаты игрока"""
        text = self.small_font.render(
            f"Координаты: ({player.x:.1f}, {player.y:.1f})",
            True,
            Colors.UI_TEXT
        )
        self.screen.blit(text, (x, y))
    
    def _render_global_water(self, world_manager, x, y):
        """Рендерит глобальный уровень воды в пустыне"""
        global_water = world_manager.get_global_water_level()
        text = self.small_font.render(
            f"Глобальная вода: {global_water:.1f}%",
            True,
            Colors.WATER_BAR
        )
        self.screen.blit(text, (x, y))
