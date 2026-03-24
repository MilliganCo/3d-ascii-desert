"""
Главное меню
"""
import pygame
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT
from engine.colors import Colors


class Menu:
    """Главное меню игры"""
    
    def __init__(self, screen):
        self.screen = screen
        try:
            self.font = pygame.font.Font(None, 48)
        except Exception:
            try:
                self.font = pygame.font.SysFont('arial', 48)
            except Exception:
                self.font = pygame.font.SysFont(None, 48)
        try:
            self.small_font = pygame.font.Font(None, 24)
        except Exception:
            try:
                self.small_font = pygame.font.SysFont('arial', 24)
            except Exception:
                self.small_font = pygame.font.SysFont(None, 24)
        self.is_open = True
        self.selected_item = 0
        self.menu_items = ["Новая игра", "Настройки", "Выход"]
    
    def handle_input(self, keys):
        """Обрабатывает ввод в меню"""
        if not self.is_open:
            return None
        
        # Стрелки вверх/вниз
        if keys[pygame.K_UP]:
            self.selected_item = (self.selected_item - 1) % len(self.menu_items)
        if keys[pygame.K_DOWN]:
            self.selected_item = (self.selected_item + 1) % len(self.menu_items)
        
        # Enter для выбора - возвращаем None, чтобы избежать повторных вызовов
        # Реальная обработка будет через события KEYDOWN
        return None
    
    def handle_keydown(self, key):
        """Обрабатывает нажатие клавиши (вызывается из события KEYDOWN)"""
        if not self.is_open:
            return None
        
        if key == pygame.K_RETURN or key == pygame.K_SPACE:
            selected = self.menu_items[self.selected_item]
            return selected
        
        return None
    
    def handle_mouse_click(self, pos):
        """
        Обрабатывает клик мыши в меню.
        
        Args:
            pos: позиция мыши (x, y)
        
        Returns:
            Выбранный пункт меню или None
        """
        if not self.is_open:
            return None
        
        from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT
        
        mouse_x, mouse_y = pos
        menu_y = SCREEN_HEIGHT // 2
        
        # Проверяем, кликнули ли на какой-то пункт меню
        for i, item in enumerate(self.menu_items):
            item_y = menu_y + i * 60
            # Примерная высота пункта меню (можно сделать точнее)
            item_height = 48
            
            if item_y - item_height // 2 <= mouse_y <= item_y + item_height // 2:
                # Клик по пункту меню
                self.selected_item = i
                return item
        
        return None
    
    def handle_mouse_motion(self, pos):
        """
        Обрабатывает движение мыши для подсветки пунктов меню.
        
        Args:
            pos: позиция мыши (x, y)
        """
        if not self.is_open:
            return
        
        from utils.config import SCREEN_HEIGHT
        
        mouse_x, mouse_y = pos
        menu_y = SCREEN_HEIGHT // 2
        
        # Проверяем, находится ли мышь над каким-то пунктом меню
        for i, item in enumerate(self.menu_items):
            item_y = menu_y + i * 60
            item_height = 48
            
            if item_y - item_height // 2 <= mouse_y <= item_y + item_height // 2:
                self.selected_item = i
                break
    
    def render(self):
        """Рендерит главное меню"""
        if not self.is_open:
            return
        
        # Фон
        self.screen.fill(Colors.UI_BACKGROUND)
        
        # Заголовок
        title_text = self.font.render("Пустыня: Вода как валюта", True, Colors.UI_TEXT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)
        
        # Подзаголовок
        subtitle_text = self.small_font.render("3D ASCII игра на выживание", True, Colors.UI_TEXT)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 50))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Пункты меню
        menu_y = SCREEN_HEIGHT // 2
        for i, item in enumerate(self.menu_items):
            color = Colors.UI_SELECTED if i == self.selected_item else Colors.UI_TEXT
            item_text = self.font.render(item, True, color)
            item_rect = item_text.get_rect(center=(SCREEN_WIDTH // 2, menu_y + i * 60))
            self.screen.blit(item_text, item_rect)
        
        # Инструкции
        instructions = [
            "Стрелки ↑↓ или мышь - навигация",
            "Enter или клик мыши - выбрать"
        ]
        y_instructions = SCREEN_HEIGHT - 100
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, Colors.UI_TEXT)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_instructions + i * 25))
            self.screen.blit(text, text_rect)
    
    def close(self):
        """Закрывает меню"""
        self.is_open = False
    
    def open(self):
        """Открывает меню"""
        self.is_open = True
        self.selected_item = 0
