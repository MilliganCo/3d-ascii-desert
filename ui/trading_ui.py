"""
Интерфейс торговли
"""
import pygame
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT
from engine.colors import Colors


class TradingUI:
    """Интерфейс торговли"""
    
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
        self.is_open = False
        self.current_npc = None
        self.selected_offer_index = 0
    
    def open(self, npc, trading_system, world_manager):
        """Открывает интерфейс торговли"""
        self.is_open = True
        self.current_npc = npc
        self.selected_offer_index = 0
        
        # Генерируем торговые предложения
        if npc:
            npc.trade_offers = trading_system.generate_trade_offers(npc, world_manager)
    
    def close(self):
        """Закрывает интерфейс торговли"""
        self.is_open = False
        self.current_npc = None
        self.selected_offer_index = 0
    
    def handle_input(self, keys, player):
        """Обрабатывает ввод в интерфейсе торговли"""
        if not self.is_open:
            return
        
        # ESC для закрытия
        if keys[pygame.K_ESCAPE]:
            self.close()
            return
        
        # Стрелки вверх/вниз для выбора предложения
        if keys[pygame.K_UP]:
            if self.selected_offer_index > 0:
                self.selected_offer_index -= 1
        if keys[pygame.K_DOWN]:
            if self.current_npc and self.selected_offer_index < len(self.current_npc.trade_offers) - 1:
                self.selected_offer_index += 1
        
        # Enter для подтверждения сделки
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self._execute_trade(player)
    
    def _execute_trade(self, player):
        """Выполняет выбранную сделку"""
        if not self.current_npc or not self.current_npc.trade_offers:
            return
        
        if 0 <= self.selected_offer_index < len(self.current_npc.trade_offers):
            offer = self.current_npc.trade_offers[self.selected_offer_index]
            if offer.execute(player):
                # Удаляем выполненное предложение
                self.current_npc.trade_offers.pop(self.selected_offer_index)
                if self.selected_offer_index >= len(self.current_npc.trade_offers):
                    self.selected_offer_index = max(0, len(self.current_npc.trade_offers) - 1)
    
    def render(self, player):
        """Рендерит интерфейс торговли"""
        if not self.is_open or not self.current_npc:
            return
        
        # Фон
        panel_width = 600
        panel_height = 500
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, Colors.UI_BACKGROUND, panel_rect)
        pygame.draw.rect(self.screen, Colors.UI_BORDER, panel_rect, 3)
        
        # Заголовок
        title_text = self.font.render(f"Торговля с {self.current_npc.name}", True, Colors.UI_TEXT)
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 30))
        self.screen.blit(title_text, title_rect)
        
        # Вода игрока
        water_text = self.font.render(
            f"Ваша вода: {player.inventory.water:.1f}",
            True,
            Colors.WATER_BAR
        )
        self.screen.blit(water_text, (panel_x + 20, panel_y + 60))
        
        # Список предложений
        y_offset = panel_y + 100
        if self.current_npc.trade_offers:
            for i, offer in enumerate(self.current_npc.trade_offers):
                color = Colors.UI_SELECTED if i == self.selected_offer_index else Colors.UI_TEXT
                
                # Проверяем, может ли игрок позволить себе сделку
                can_afford = offer.can_afford(player.inventory.water)
                if not can_afford:
                    color = (100, 100, 100)  # Серый для недоступных
                
                offer_text = f"{i + 1}. {offer.description}"
                text_surface = self.font.render(offer_text, True, color)
                self.screen.blit(text_surface, (panel_x + 40, y_offset + i * 40))
        else:
            no_offers_text = self.font.render("Нет доступных предложений", True, Colors.UI_TEXT)
            self.screen.blit(no_offers_text, (panel_x + 40, y_offset))
        
        # Инструкции
        instructions = [
            "Стрелки ↑↓ - выбор предложения",
            "Enter/Space - подтвердить сделку",
            "ESC - закрыть"
        ]
        y_instructions = panel_y + panel_height - 80
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, Colors.UI_TEXT)
            self.screen.blit(text, (panel_x + 20, y_instructions + i * 20))
