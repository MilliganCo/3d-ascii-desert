"""
Изометрический ASCII рендерер
"""
import pygame
from utils.math_utils import world_to_isometric
from utils.config import TILE_WIDTH, TILE_HEIGHT, ISO_SCALE
from engine.colors import Colors
from engine.camera import Camera


class Renderer:
    """Изометрический ASCII рендерер с Z-сортировкой"""
    
    def __init__(self, screen):
        self.screen = screen
        self.camera = Camera()
        try:
            self.font = pygame.font.Font(None, 24)  # Базовый шрифт
        except Exception:
            # Если не удалось загрузить шрифт, используем системный
            try:
                self.font = pygame.font.SysFont('arial', 24)
            except Exception:
                self.font = pygame.font.SysFont(None, 24)
        self.render_queue = []  # Очередь для Z-сортировки
        
    def clear(self):
        """Очищает экран"""
        self.screen.fill((0, 0, 0))
        self.render_queue.clear()
    
    def add_to_queue(self, world_x, world_y, world_z, char, color):
        """
        Добавляет объект в очередь рендеринга для Z-сортировки.
        
        Args:
            world_x, world_y, world_z: координаты в мире
            char: ASCII символ для отображения
            color: цвет символа (RGB)
        """
        # Преобразуем в изометрические координаты с масштабом
        iso_x, iso_y = world_to_isometric(world_x, world_y, world_z, ISO_SCALE)
        
        # Преобразуем в экранные координаты
        screen_x, screen_y = self.camera.world_to_screen(iso_x, iso_y)
        
        # Добавляем в очередь с приоритетом по Z (дальние объекты рендерятся первыми)
        self.render_queue.append({
            'screen_x': screen_x,
            'screen_y': screen_y,
            'z': world_z,
            'char': char,
            'color': color
        })
    
    def render_tile(self, world_x, world_y, world_z, tile_type):
        """
        Рендерит тайл в изометрической проекции.
        
        Args:
            world_x, world_y, world_z: координаты тайла в мире
            tile_type: тип тайла ('sand', 'water', 'stone', 'plant')
        """
        char = Colors.get_ascii_char(tile_type)
        color = Colors.get_tile_color(tile_type)
        self.add_to_queue(world_x, world_y, world_z, char, color)
    
    def render_entity(self, world_x, world_y, world_z, char, color):
        """
        Рендерит сущность (игрок, NPC и т.д.).
        
        Args:
            world_x, world_y, world_z: координаты сущности
            char: ASCII символ
            color: цвет (RGB)
        """
        self.add_to_queue(world_x, world_y, world_z, char, color)
    
    def flush(self):
        """Отрисовывает все объекты из очереди с Z-сортировкой"""
        try:
            # Сортируем по Z (от дальних к ближним)
            self.render_queue.sort(key=lambda item: item['z'], reverse=True)
            
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            
            # Рендерим все объекты
            for item in self.render_queue:
                try:
                    screen_x = int(item['screen_x'])
                    screen_y = int(item['screen_y'])
                    char = item['char']
                    color = item['color']
                    
                    # Проверяем, находится ли объект в видимой области
                    if (0 <= screen_x < screen_width and 
                        0 <= screen_y < screen_height):
                        # Рендерим текст
                        if char:  # Проверяем, что символ не пустой
                            try:
                                text_surface = self.font.render(str(char), True, color)
                                if text_surface:
                                    self.screen.blit(text_surface, (screen_x, screen_y))
                            except Exception as e:
                                # Пропускаем проблемные символы
                                continue
                except Exception as e:
                    # Пропускаем проблемные объекты
                    continue
            
            self.render_queue.clear()
        except Exception as e:
            print(f"Ошибка при flush рендерера: {e}")
            import traceback
            traceback.print_exc()
            self.render_queue.clear()  # Очищаем очередь при ошибке
    
    def render_text(self, x, y, text, color=None):
        """
        Рендерит текст на экране (для UI).
        
        Args:
            x, y: экранные координаты
            text: текст для отображения
            color: цвет текста (по умолчанию белый)
        """
        if color is None:
            color = Colors.UI_TEXT
        
        text_surface = self.font.render(str(text), True, color)
        self.screen.blit(text_surface, (x, y))
    
    def render_rect(self, x, y, width, height, color, filled=True):
        """Рендерит прямоугольник (для UI)"""
        rect = pygame.Rect(x, y, width, height)
        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, 1)
