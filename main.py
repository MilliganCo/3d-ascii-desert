"""
Главный файл игры "Пустыня: Вода как валюта"
"""
import pygame
import sys
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from engine.renderer import Renderer
from world.world_manager import WorldManager
from game.player import Player
from game.npc import NPCManager
from game.trading import TradingSystem
from physics.hydrodynamics import Hydrodynamics
from physics.meteorology import Meteorology
from physics.ecology import Ecology
from ui.hud import HUD
from ui.trading_ui import TradingUI
from ui.menu import Menu
from ui.message_log import MessageLog
from engine.colors import Colors
import random


class Game:
    """Главный класс игры"""
    
    def __init__(self):
        try:
            print("Инициализация pygame...")
            pygame.init()
            print("Создание экрана...")
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Пустыня: Вода как валюта")
            self.clock = pygame.time.Clock()
            
            print("Инициализация систем...")
            # Инициализация систем
            print("  - Renderer...")
            self.renderer = Renderer(self.screen)
            print("  - WorldManager...")
            self.world_manager = WorldManager(seed=random.randint(0, 1000000))
            print("  - Player...")
            self.player = Player(0, 0)
            print("  - NPCManager...")
            self.npc_manager = NPCManager()
            print("  - TradingSystem...")
            self.trading_system = TradingSystem()
            
            print("Инициализация физических систем...")
            # Физические системы
            self.hydrodynamics = Hydrodynamics()
            self.meteorology = Meteorology()
            self.ecology = Ecology()
            
            print("Инициализация UI...")
            # UI
            self.hud = HUD(self.screen)
            self.trading_ui = TradingUI(self.screen)
            self.menu = Menu(self.screen)
            self.message_log = MessageLog(self.screen)
            
            print("Установка состояния игры...")
            # Состояние игры
            self.running = True
            self.in_menu = True
            self.game_started = False
            
            print("Спавн NPC...")
            # Спавн NPC
            self._spawn_initial_npcs()
            print("Инициализация завершена успешно!")
        except Exception as e:
            print(f"ОШИБКА при инициализации: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _spawn_initial_npcs(self):
        """Создает начальных NPC"""
        try:
            for i in range(5):
                x = random.uniform(-50, 50)
                y = random.uniform(-50, 50)
                self.npc_manager.spawn_npc(x, y, f"Торговец {i+1}")
        except Exception as e:
            print(f"Ошибка при спавне NPC: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_events(self):
        """Обрабатывает события"""
        try:
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Обработка мыши в меню
                if self.in_menu:
                    if event.type == pygame.MOUSEMOTION:
                        self.menu.handle_mouse_motion(event.pos)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Левая кнопка мыши
                            menu_action = self.menu.handle_mouse_click(event.pos)
                            if menu_action == "Новая игра":
                                self.start_game()
                            elif menu_action == "Выход":
                                self.running = False
                
                if event.type == pygame.KEYDOWN:
                    # Обработка меню
                    if self.in_menu:
                        menu_action = self.menu.handle_keydown(event.key)
                        if menu_action == "Новая игра":
                            self.start_game()
                        elif menu_action == "Выход":
                            self.running = False
                    else:
                        # E для взаимодействия с NPC или объектами мира
                        if event.key == pygame.K_e:
                            self._try_interact()
                        
                        # I для инвентаря
                        if event.key == pygame.K_i:
                            self.message_log.add_message(f"Инвентарь: Вода={self.player.inventory.water:.1f}, Камни={self.player.inventory.stones}, Песок={self.player.inventory.sand}", Colors.UI_TEXT)
                        
                        # Q для питья воды
                        if event.key == pygame.K_q:
                            amount, message = self.player.drink_water(10)
                            if amount > 0:
                                self.message_log.add_message(message, Colors.WATER_BAR)
                            else:
                                self.message_log.add_message("Нет воды в инвентаре для питья", Colors.HEALTH_BAR)
                        
                        # R для сбора воды из источника
                        if event.key == pygame.K_r:
                            self._try_collect_water()
                        
                        # ESC для возврата в меню или закрытия торговли
                        if event.key == pygame.K_ESCAPE:
                            if self.trading_ui.is_open:
                                self.trading_ui.close()
                            else:
                                self.in_menu = True
                                self.menu.open()
            
            # Обработка непрерывного ввода в игре (не в меню)
            if not self.in_menu:
                if not self.trading_ui.is_open:
                    self.player.handle_input(keys, self.clock.get_time() / 1000.0, self.world_manager)
                self.trading_ui.handle_input(keys, self.player)
            
            # Обработка навигации в меню (стрелки)
            if self.in_menu:
                self.menu.handle_input(keys)
        except Exception as e:
            print(f"Ошибка в handle_events: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _try_interact(self):
        """Пытается взаимодействовать с ближайшим NPC или объектами мира"""
        # Сначала проверяем NPC
        npc = self.npc_manager.get_nearby_npc(self.player.x, self.player.y, radius=3)
        if npc:
            self._interact_with_npc(npc)
            return
        
        # Проверяем объекты мира
        tile = self.world_manager.get_tile(int(self.player.x), int(self.player.y))
        if tile:
            self._interact_with_tile(tile)
            return
        
        self.message_log.add_message("Рядом нет объектов для взаимодействия", Colors.UI_TEXT)
    
    def _interact_with_npc(self, npc):
        """Взаимодействие с NPC"""
        interaction = npc.interact(self.player, self.world_manager)
        
        # Добавляем сообщение о взаимодействии
        self.message_log.add_message(interaction['message'], Colors.UI_TEXT)
        
        if interaction['is_aggressive']:
            water_loss = random.uniform(5, 15)
            self.message_log.add_message(f"{npc.name} напал на вас! Потеряно {water_loss:.1f} воды.", Colors.HEALTH_BAR)
            # Даже если агрессивен, можно попробовать торговать
            if random.random() < 0.3:  # 30% шанс что агрессивный NPC все же согласится торговать
                self.trading_ui.open(npc, self.trading_system, self.world_manager)
                self.message_log.add_message(f"{npc.name} передумал и согласился торговать!", Colors.WATER_BAR)
                self.message_log.add_message("Используйте стрелки для выбора, Enter для подтверждения, ESC для выхода.", Colors.UI_TEXT)
        else:
            # Всегда открываем торговлю, если NPC не агрессивен
            if interaction['can_trade']:
                self.trading_ui.open(npc, self.trading_system, self.world_manager)
                self.message_log.add_message(f"Открыт интерфейс торговли с {npc.name}.", Colors.WATER_BAR)
                self.message_log.add_message("Стрелки - выбор, Enter - купить, ESC - выход", Colors.UI_TEXT)
            elif interaction['can_quest']:
                quests = interaction.get('quests', [])
                if quests:
                    quest = quests[0]
                    self.message_log.add_message(f"{npc.name} предлагает квест: {quest.description}", Colors.UI_SELECTED)
                    self.message_log.add_message(f"Награда: {quest.reward_water} воды", Colors.WATER_BAR)
                    # Автоматически добавляем квест, если его еще нет
                    if quest not in npc.quests:
                        npc.quests.append(quest)
    
    def _interact_with_tile(self, tile):
        """Взаимодействие с тайлом мира"""
        terrain_type = tile.get_effective_terrain()
        
        if terrain_type.value == 'water':
            if tile.water_level > 30:
                collectable = min(tile.water_level * 0.1, 20)
                self.player.collect_water(collectable)
                tile.remove_water(collectable)
                self.message_log.add_message(f"Собрано {collectable:.1f} воды из источника", Colors.WATER_BAR)
            else:
                self.message_log.add_message("Источник воды почти иссяк", Colors.UI_TEXT)
        
        elif terrain_type.value == 'plant':
            if tile.plant_density > 0.5:
                self.message_log.add_message("Пышная растительность. Здесь много воды в почве.", Colors.PLANT)
            else:
                self.message_log.add_message("Скудная растительность. Воды мало.", Colors.UI_TEXT)
        
        elif terrain_type.value == 'stone':
            # Можно собирать камни
            if random.random() < 0.3:  # 30% шанс найти камень
                self.player.inventory.add_resource('stone', 1)
                self.message_log.add_message("Найден камень", Colors.STONE)
            else:
                self.message_log.add_message("Только камни. Ничего полезного.", Colors.UI_TEXT)
        
        else:  # sand
            if tile.water_level > 20:
                self.message_log.add_message("Песок влажный. Возможно, здесь есть подземный источник.", Colors.WATER_BAR)
            else:
                self.message_log.add_message("Сухой песок. Воды нет.", Colors.UI_TEXT)
    
    def _try_collect_water(self):
        """Пытается собрать воду из источника"""
        tile = self.world_manager.get_tile(int(self.player.x), int(self.player.y))
        if tile and tile.water_level > 30:
            collectable = min(tile.water_level * 0.2, 30)
            self.player.collect_water(collectable)
            tile.remove_water(collectable)
            self.message_log.add_message(f"Собрано {collectable:.1f} воды из источника (R)", Colors.WATER_BAR)
        else:
            self.message_log.add_message("Здесь нет источника воды для сбора", Colors.UI_TEXT)
    
    def start_game(self):
        """Начинает новую игру"""
        print("start_game() вызван...")
        try:
            print("  Установка флагов...")
            self.in_menu = False
            self.game_started = True
            print("  Закрытие меню...")
            self.menu.close()
            print("  Меню закрыто")
            
            print("  Инициализация камеры...")
            # Инициализируем камеру на позиции игрока (сразу, без плавного перехода)
            self.renderer.camera.set_target(self.player.x, self.player.y)
            # Устанавливаем камеру сразу на цель при старте
            from utils.math_utils import world_to_isometric
            from utils.config import ISO_SCALE
            iso_x, iso_y = world_to_isometric(self.player.x, self.player.y, 0, ISO_SCALE)
            self.renderer.camera.x = iso_x
            self.renderer.camera.y = iso_y
            self.renderer.camera.target_x = iso_x
            self.renderer.camera.target_y = iso_y
            print("  Камера инициализирована")
            
            print("  Добавление приветственных сообщений...")
            # Добавляем приветственное сообщение
            self.message_log.add_message("Добро пожаловать в пустыню!", Colors.UI_SELECTED)
            self.message_log.add_message("Вода здесь - самая ценная валюта. Используйте WASD для движения.", Colors.UI_TEXT)
            self.message_log.add_message("E - взаимодействие с NPC/объектами, R - собрать воду, Q - выпить воду, I - инвентарь", Colors.UI_TEXT)
            print("  Сообщения добавлены")
            
            print("  Генерация начальных чанков...")
            # Генерируем начальные чанки вокруг игрока (меньше для производительности)
            chunks = self.world_manager.get_chunks_around(self.player.x, self.player.y, radius_chunks=1)
            print(f"  Получено {len(chunks)} чанков")
            for i, chunk in enumerate(chunks):
                try:
                    if not chunk.generated:
                        print(f"  Генерация чанка {i+1}...")
                        self.world_manager.generator.generate_chunk(chunk)
                        print(f"  Чанк {i+1} сгенерирован")
                except Exception as e:
                    print(f"Ошибка при генерации чанка {i+1}: {e}")
                    import traceback
                    traceback.print_exc()
            
            print("  Добавление финального сообщения...")
            self.message_log.add_message("Мир сгенерирован. Ищите источники воды и торгуйте с NPC!", Colors.WATER_BAR)
            print("start_game() завершен успешно!")
        except Exception as e:
            print(f"Ошибка при запуске игры: {e}")
            import traceback
            traceback.print_exc()
            self.in_menu = True
            self.menu.open()
            self.game_started = False
    
    def update(self, dt):
        """Обновляет игровое состояние"""
        try:
            if not self.game_started:
                return
            
            # Обновление игрока
            old_water = self.player.water_level
            old_health = self.player.health
            self.player.update(dt, self.world_manager)
            
            # Проверяем изменения состояния игрока для сообщений
            if self.player.water_level < 20 and old_water >= 20:
                self.message_log.add_message("Внимание! Уровень воды критически низок!", Colors.HEALTH_BAR)
            if self.player.health < 30 and old_health >= 30:
                self.message_log.add_message("Внимание! Здоровье критически низко!", Colors.HEALTH_BAR)
            
            # Проверяем, находится ли игрок на воде
            tile = self.world_manager.get_tile(int(self.player.x), int(self.player.y))
            if tile:
                if tile.water_level > 50:
                    if not hasattr(self, '_on_water') or not self._on_water:
                        self.message_log.add_message("Вы нашли источник воды! Нажмите R для сбора воды.", Colors.WATER_BAR)
                        self._on_water = True
                else:
                    if hasattr(self, '_on_water') and self._on_water:
                        self._on_water = False
                
                # Проверяем тип местности для сообщений
                terrain_type = tile.get_effective_terrain()
                if terrain_type.value == 'plant' and (not hasattr(self, '_on_plant') or not self._on_plant):
                    self.message_log.add_message("Вы нашли растительность! Здесь больше воды.", Colors.PLANT)
                    self._on_plant = True
                elif terrain_type.value != 'plant':
                    if hasattr(self, '_on_plant') and self._on_plant:
                        self._on_plant = False
            
            # Проверяем близость к NPC
            nearby_npcs = self.npc_manager.get_npcs_in_radius(self.player.x, self.player.y, radius=5)
            if nearby_npcs and (not hasattr(self, '_nearby_npc_warning') or not self._nearby_npc_warning):
                npc = nearby_npcs[0]
                self.message_log.add_message(f"Рядом {npc.name}. Нажмите E для взаимодействия.", Colors.UI_SELECTED)
                self._nearby_npc_warning = True
            elif not nearby_npcs:
                if hasattr(self, '_nearby_npc_warning'):
                    self._nearby_npc_warning = False
            
            # Обновление камеры
            self.renderer.camera.set_target(self.player.x, self.player.y)
            self.renderer.camera.update(dt)
            
            # Обновление NPC
            self.npc_manager.update(dt, self.world_manager)
            
            # Обновление физических систем (оптимизировано - только для видимых чанков)
            # Обновляем физику реже для оптимизации производительности
            if not hasattr(self, '_physics_update_counter'):
                self._physics_update_counter = 0.0
            
            self._physics_update_counter += dt
            
            # Обновляем физику каждые 0.2 секунды вместо каждого кадра (реже для производительности)
            if self._physics_update_counter >= 0.2:
                self._update_physics(self._physics_update_counter)
                self._physics_update_counter = 0.0
            
            # Обновление мира
            self.world_manager.update(dt)
            
            # Случайные события
            self._check_random_events(dt)
        except Exception as e:
            print(f"Ошибка в update: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _check_random_events(self, dt):
        """Проверяет случайные события"""
        if not hasattr(self, '_event_timer'):
            self._event_timer = 0.0
        
        self._event_timer += dt
        
        # События каждые 5-10 секунд
        if self._event_timer >= random.uniform(5, 10):
            self._event_timer = 0.0
            
            # Проверяем погоду
            weather = self.meteorology.get_weather_at_position(self.player.x, self.player.y)
            if weather['is_raining']:
                if not hasattr(self, '_rain_message_shown') or not self._rain_message_shown:
                    self.message_log.add_message("Начался дождь! Вода пополняется.", Colors.WATER_BAR)
                    self._rain_message_shown = True
            else:
                if hasattr(self, '_rain_message_shown') and self._rain_message_shown:
                    self._rain_message_shown = False
                    
            if weather['is_sandstorm']:
                if not hasattr(self, '_sandstorm_message_shown') or not self._sandstorm_message_shown:
                    self.message_log.add_message("Песчаная буря! Вода испаряется быстрее.", Colors.HEALTH_BAR)
                    self._sandstorm_message_shown = True
            else:
                if hasattr(self, '_sandstorm_message_shown') and self._sandstorm_message_shown:
                    self._sandstorm_message_shown = False
            
            # Случайные события
            if random.random() < 0.15:  # 15% шанс
                events = [
                    "Ветер принес запах воды издалека...",
                    "Вы заметили следы на песке. Кто-то проходил здесь недавно.",
                    "Вдали виднеется что-то блестящее...",
                    "Температура поднимается. Вода испаряется быстрее.",
                    "Вы слышите шум вдалеке. Возможно, это торговый караван?",
                    "Песок под ногами горячий. Нужно экономить воду.",
                    "На горизонте виднеется оазис... или это мираж?",
                    "Вы нашли старый колодец, но он сухой.",
                ]
                self.message_log.add_message(random.choice(events), Colors.UI_TEXT)
            
            # Случайные события
            if random.random() < 0.15:  # 15% шанс
                events = [
                    "Ветер принес запах воды издалека...",
                    "Вы заметили следы на песке. Кто-то проходил здесь недавно.",
                    "Вдали виднеется что-то блестящее...",
                    "Температура поднимается. Вода испаряется быстрее.",
                    "Вы слышите шум вдалеке. Возможно, это торговый караван?",
                    "Песок под ногами горячий. Нужно экономить воду.",
                    "На горизонте виднеется оазис... или это мираж?",
                    "Вы нашли старый колодец, но он сухой.",
                ]
                self.message_log.add_message(random.choice(events), Colors.UI_TEXT)
            
            # Проверяем близость к NPC
            nearby_npcs = self.npc_manager.get_npcs_in_radius(self.player.x, self.player.y, radius=5)
            if nearby_npcs and not hasattr(self, '_nearby_npc_warning'):
                npc = nearby_npcs[0]
                self.message_log.add_message(f"Рядом {npc.name}. Нажмите E для взаимодействия.", Colors.UI_SELECTED)
                self._nearby_npc_warning = True
            elif not nearby_npcs:
                if hasattr(self, '_nearby_npc_warning'):
                    self._nearby_npc_warning = False
    
    def _update_physics(self, dt):
        """Обновляет физические системы только для видимых чанков"""
        # Получаем видимые чанки вокруг игрока (уменьшено для производительности)
        chunks = self.world_manager.get_chunks_around(
            self.player.x, self.player.y,
            radius_chunks=1  # Обновляем только ближайшие чанки
        )
        
        # Обновляем физику для каждого чанка (оптимизация: обновляем по очереди)
        if not hasattr(self, '_chunk_update_index'):
            self._chunk_update_index = 0
        
        # Обновляем только один чанк за раз для гидродинамики
        if chunks:
            chunk = chunks[self._chunk_update_index % len(chunks)]
            self.hydrodynamics.update_chunk(chunk, self.world_manager, dt)
            self._chunk_update_index += 1
        
        # Экология обновляется реже (каждый 5-й чанк)
        if chunks and self._chunk_update_index % 5 == 0:
            chunk = chunks[(self._chunk_update_index // 5) % len(chunks)]
            self.ecology.update_chunk(chunk, self.world_manager, dt)
        
        # Метеорология обновляется глобально, но реже
        if not hasattr(self, '_meteorology_timer'):
            self._meteorology_timer = 0.0
        self._meteorology_timer += dt
        if self._meteorology_timer >= 0.5:  # Обновляем каждые 0.5 секунды
            self.meteorology.update(self._meteorology_timer, self.world_manager)
            self._meteorology_timer = 0.0
    
    def render(self):
        """Рендерит игру"""
        try:
            self.renderer.clear()
            
            if self.in_menu or not self.game_started:
                # Показываем меню если мы в меню или игра еще не запущена
                try:
                    self.menu.render()
                except Exception as e:
                    print(f"Ошибка при рендеринге меню: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                # Рендерим игру только если она запущена
                try:
                    # Рендерим мир
                    self._render_world()
                    
                    # Рендерим NPC
                    self._render_npcs()
                    
                    # Рендерим игрока
                    from utils.config import ASCII_PLAYER, COLOR_PLAYER
                    self.renderer.render_entity(
                        self.player.x, self.player.y, self.player.z,
                        ASCII_PLAYER, COLOR_PLAYER
                    )
                    
                    # Финальная отрисовка (Z-сортировка)
                    self.renderer.flush()
                    
                    # Рендерим UI
                    self.hud.render(self.player, self.world_manager)
                    self.trading_ui.render(self.player)
                    # Рендерим консоль сообщений
                    self.message_log.render()
                except Exception as e:
                    print(f"Ошибка при рендеринге игры: {e}")
                    import traceback
                    traceback.print_exc()
                    # Не закрываем игру при ошибке рендеринга, просто возвращаемся в меню
                    self.in_menu = True
                    self.menu.open()
                    self.game_started = False
            
            try:
                pygame.display.flip()
            except pygame.error as e:
                print(f"Ошибка pygame.display.flip(): {e}")
                import traceback
                traceback.print_exc()
                self.running = False
        except pygame.error as e:
            print(f"Ошибка pygame при рендеринге: {e}")
            import traceback
            traceback.print_exc()
            self.running = False
        except Exception as e:
            print(f"Неожиданная ошибка при рендеринге: {e}")
            import traceback
            traceback.print_exc()
            self.in_menu = True
            self.menu.open()
            self.game_started = False
    
    def _render_world(self):
        """Рендерит видимую часть мира"""
        try:
            # Получаем видимые чанки (увеличено для лучшей видимости)
            chunks = self.world_manager.get_chunks_around(
                self.player.x, self.player.y,
                radius_chunks=2  # Увеличено для видимости большего количества тайлов
            )
            
            # Получаем границы видимой области один раз
            min_x, max_x, min_y, max_y = self.renderer.camera.get_view_bounds()
            
            # Ограничиваем количество рендеримых тайлов для производительности
            max_tiles_per_frame = 1000  # Увеличено для лучшей видимости
            tiles_rendered = 0
            
            # Рендерим тайлы из видимых чанков
            for chunk in chunks:
                if not chunk or not chunk.generated:
                    continue
                if tiles_rendered >= max_tiles_per_frame:
                    break
                try:
                    tiles = chunk.get_all_tiles()
                    if not tiles:
                        continue
                    for tile in tiles:
                        if tiles_rendered >= max_tiles_per_frame:
                            break
                        if tile is None:
                            continue
                        # Более мягкая проверка видимости - рендерим все тайлы в чанке
                        # Проверка расстояния от игрока
                        dist = ((tile.x - self.player.x)**2 + (tile.y - self.player.y)**2)**0.5
                        if dist <= 50:  # Рендерим тайлы в радиусе 50 единиц
                            terrain_type = tile.get_effective_terrain()
                            if terrain_type:
                                self.renderer.render_tile(
                                    tile.x, tile.y, tile.height,
                                    terrain_type.value
                                )
                                tiles_rendered += 1
                except Exception as e:
                    # Пропускаем проблемные чанки
                    continue
        except Exception as e:
            print(f"Ошибка при рендеринге мира: {e}")
            import traceback
            traceback.print_exc()
    
    def _render_npcs(self):
        """Рендерит NPC"""
        npcs = self.npc_manager.get_npcs_in_radius(
            self.player.x, self.player.y, radius=50
        )
        
        for npc in npcs:
            render_info = npc.get_render_info()
            self.renderer.render_entity(
                render_info['x'], render_info['y'], render_info['z'],
                render_info['char'], render_info['color']
            )
    
    def run(self):
        """Главный цикл игры"""
        print("Вход в метод run()...")
        print(f"self.running = {self.running}")
        print(f"self.in_menu = {self.in_menu}")
        print(f"self.game_started = {getattr(self, 'game_started', 'не установлен')}")
        try:
            frame_count = 0
            last_error_frame = 0
            
            while self.running:
                try:
                    dt = self.clock.tick(FPS) / 1000.0  # Время в секундах
                    frame_count += 1
                    
                    try:
                        self.handle_events()
                    except Exception as e:
                        print(f"Ошибка в handle_events (кадр {frame_count}): {e}")
                        import traceback
                        traceback.print_exc()
                        # Продолжаем выполнение
                    
                    # Проверяем, не завершилась ли игра после обработки событий
                    if not self.running:
                        break
                    
                    try:
                        self.update(dt)
                    except Exception as e:
                        print(f"Ошибка в update (кадр {frame_count}): {e}")
                        import traceback
                        traceback.print_exc()
                        # Продолжаем выполнение
                    
                    try:
                        self.render()
                    except Exception as e:
                        print(f"Ошибка в render (кадр {frame_count}): {e}")
                        import traceback
                        traceback.print_exc()
                        # Продолжаем выполнение
                    
                    # Проверяем, не завершилась ли игра
                    if not self.running:
                        break
                    
                except KeyboardInterrupt:
                    print("Игра прервана пользователем")
                    break
                except SystemExit:
                    print("Получен SystemExit")
                    raise
                except Exception as e:
                    if frame_count != last_error_frame:
                        print(f"Ошибка в игровом цикле (кадр {frame_count}): {e}")
                        import traceback
                        traceback.print_exc()
                        last_error_frame = frame_count
                    # Не закрываем игру, возвращаемся в меню
                    self.in_menu = True
                    self.menu.open()
                    self.game_started = False
                    # Продолжаем цикл вместо выхода
                    continue
        except SystemExit:
            raise
        except Exception as e:
            print(f"Критическая ошибка в главном цикле: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("Завершение игры (finally блок)...")
            try:
                pygame.quit()
            except Exception as e:
                print(f"Ошибка при закрытии pygame: {e}")
            # Не вызываем sys.exit() здесь, чтобы увидеть все ошибки


if __name__ == "__main__":
    import sys
    import traceback
    
    # Перенаправляем stderr в stdout для лучшего отображения ошибок
    sys.stderr = sys.stdout
    
    try:
        print("Инициализация игры...")
        game = None
        try:
            game = Game()
            print("Игра инициализирована, запуск главного цикла...")
        except Exception as e:
            print(f"ОШИБКА при инициализации игры: {e}")
            traceback.print_exc()
            input("\nНажмите Enter для выхода...")
            sys.exit(1)
        
        print("Вызов game.run()...")
        try:
            game.run()
            print("game.run() завершился")
        except SystemExit as e:
            print(f"SystemExit в game.run(): {e}")
            raise
        except Exception as e:
            print(f"ОШИБКА в game.run(): {e}")
            traceback.print_exc()
            input("\nНажмите Enter для выхода...")
    except SystemExit:
        print("Игра завершена")
    except KeyboardInterrupt:
        print("\nИгра прервана пользователем")
    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("\nПолный traceback:")
        traceback.print_exc()
        print("\n" + "="*50)
        input("\nНажмите Enter для выхода...")  # Чтобы консоль не закрылась сразу
