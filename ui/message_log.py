"""
Система логов сообщений для игры
"""
import pygame
from collections import deque
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT
from engine.colors import Colors


class MessageLog:
    """Система логов сообщений"""
    
    def __init__(self, screen, max_messages=10):
        self.screen = screen
        self.max_messages = max_messages
        self.messages = deque(maxlen=max_messages)
        self.font = pygame.font.SysFont('consolas', 16)
        self.console_height = 150
        self.console_y = SCREEN_HEIGHT - self.console_height
        
    def add_message(self, message, color=None):
        """
        Добавляет сообщение в лог.
        
        Args:
            message: текст сообщения
            color: цвет сообщения (по умолчанию белый)
        """
        if color is None:
            color = Colors.UI_TEXT
        self.messages.append({
            'text': str(message),
            'color': color,
            'timestamp': pygame.time.get_ticks()
        })
    
    def render(self):
        """Рендерит консоль сообщений внизу экрана"""
        # Фон консоли
        console_rect = pygame.Rect(0, self.console_y, SCREEN_WIDTH, self.console_height)
        pygame.draw.rect(self.screen, (20, 20, 20), console_rect)
        pygame.draw.rect(self.screen, Colors.UI_BORDER, console_rect, 2)
        
        # Заголовок консоли
        title_text = self.font.render("События:", True, Colors.UI_SELECTED)
        self.screen.blit(title_text, (10, self.console_y + 5))
        
        # Рендерим сообщения снизу вверх (новые сообщения внизу)
        line_height = 18
        start_y = SCREEN_HEIGHT - 15  # Начинаем снизу консоли
        
        # Рендерим сообщения в обратном порядке (последние внизу)
        visible_messages = list(self.messages)
        for i, msg in enumerate(reversed(visible_messages)):
            y_pos = start_y - (i * line_height)
            
            # Проверяем, не вышли ли за верхнюю границу консоли
            if y_pos < self.console_y + 25:
                break
            
            # Обрезаем длинные сообщения
            text = msg['text']
            max_width = SCREEN_WIDTH - 20
            if len(text) > 80:
                text = text[:77] + "..."
            
            try:
                text_surface = self.font.render(text, True, msg['color'])
                if text_surface:
                    self.screen.blit(text_surface, (10, y_pos))
            except Exception:
                # Пропускаем проблемные сообщения
                continue
