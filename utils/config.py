"""
Конфигурация игры
"""

# Размеры экрана
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Размеры тайла в пикселях (для изометрической проекции)
TILE_WIDTH = 32
TILE_HEIGHT = 16

# Масштаб для изометрической проекции (увеличивает размер объектов)
ISO_SCALE = 20.0  # Масштаб для изометрической проекции

# Размер чанка (в тайлах)
CHUNK_SIZE = 32  # Уменьшено для лучшей производительности

# Размер видимой области (в чанках)
VISIBLE_CHUNKS_X = 2  # Уменьшено для лучшей производительности
VISIBLE_CHUNKS_Y = 2

# Игрок
PLAYER_START_WATER = 100.0
PLAYER_START_HEALTH = 100.0
PLAYER_MAX_WATER = 200.0
PLAYER_MAX_HEALTH = 100.0
PLAYER_WATER_DRAIN_RATE = 0.5  # Расход воды в секунду
PLAYER_MOVE_SPEED = 2.0  # Тайлов в секунду

# Физика воды
WATER_DIFFUSION_RATE = 0.1
WATER_EVAPORATION_RATE = 0.05
WATER_MIN_LEVEL = 0.0
WATER_MAX_LEVEL = 100.0

# Метеорология
RAIN_PROBABILITY = 0.001  # Вероятность дождя за кадр
RAIN_INTENSITY_MIN = 1.0
RAIN_INTENSITY_MAX = 10.0
SANDSTORM_THRESHOLD = 10.0  # Минимальный уровень воды для песчаной бури

# Экология
PLANT_GROWTH_RATE = 0.01
PLANT_MIN_WATER = 20.0
PLANT_MAX_DENSITY = 1.0

# Цвета (RGB)
COLOR_SAND = (194, 178, 128)
COLOR_WATER = (64, 164, 223)
COLOR_STONE = (128, 128, 128)
COLOR_PLANT = (34, 139, 34)
COLOR_PLAYER = (255, 255, 255)
COLOR_NPC = (255, 200, 100)

# ASCII символы
ASCII_SAND = '.'
ASCII_WATER = '~'
ASCII_STONE = '#'
ASCII_PLANT = '*'
ASCII_PLAYER = '@'
ASCII_NPC = 'N'
