"""
Метеорология: дожди, испарение, конденсация, песчаные бури
"""
import random
import math
from utils.config import (
    RAIN_PROBABILITY, RAIN_INTENSITY_MIN, RAIN_INTENSITY_MAX,
    WATER_EVAPORATION_RATE, SANDSTORM_THRESHOLD
)


class Meteorology:
    """Система метеорологии"""
    
    def __init__(self):
        self.temperature = 30.0  # Температура воздуха (градусы Цельсия)
        self.humidity = 50.0  # Влажность воздуха (0-100)
        self.wind_speed = 5.0  # Скорость ветра (м/с)
        
        # Активные погодные явления
        self.active_rain = None  # (center_x, center_y, intensity, radius, duration)
        self.active_sandstorm = None  # (center_x, center_y, intensity, radius, duration)
        
        self.time_since_last_rain = 0.0
        self.time_since_last_sandstorm = 0.0
    
    def update(self, dt, world_manager):
        """
        Обновляет метеорологическую систему.
        
        Args:
            dt: время с последнего обновления
            world_manager: менеджер мира
        """
        self.time_since_last_rain += dt
        self.time_since_last_sandstorm += dt
        
        # Обновляем активные погодные явления
        self._update_rain(dt, world_manager)
        self._update_sandstorm(dt, world_manager)
        
        # Проверяем вероятность новых явлений
        self._check_rain_probability(dt, world_manager)
        self._check_sandstorm_probability(dt, world_manager)
        
        # Обновляем испарение
        self._update_evaporation(dt, world_manager)
        
        # Обновляем конденсацию
        self._update_condensation(dt, world_manager)
    
    def _update_rain(self, dt, world_manager):
        """Обновляет активный дождь"""
        if self.active_rain is None:
            return
        
        center_x, center_y, intensity, radius, duration = self.active_rain
        duration -= dt
        
        if duration <= 0:
            self.active_rain = None
            return
        
        # Добавляем воду в область дождя
        self._add_rain_water(world_manager, center_x, center_y, intensity, radius, dt)
        
        self.active_rain = (center_x, center_y, intensity, radius, duration)
    
    def _add_rain_water(self, world_manager, center_x, center_y, intensity, radius, dt):
        """Добавляет воду от дождя в область"""
        # Получаем тайлы в радиусе дождя
        tiles = world_manager.get_tiles_in_radius(center_x, center_y, radius)
        
        for tile in tiles:
            # Вычисляем расстояние от центра
            dist = ((tile.x - center_x)**2 + (tile.y - center_y)**2)**0.5
            
            if dist <= radius:
                # Интенсивность уменьшается с расстоянием
                local_intensity = intensity * (1.0 - dist / radius)
                water_amount = local_intensity * dt
                tile.add_water(water_amount)
                tile.needs_update = True
        
        # Увеличиваем влажность воздуха
        self.humidity = min(100.0, self.humidity + intensity * dt * 0.1)
    
    def _check_rain_probability(self, dt, world_manager):
        """Проверяет вероятность дождя"""
        if self.active_rain is not None:
            return
        
        # Вероятность дождя зависит от влажности
        rain_chance = RAIN_PROBABILITY * (1.0 + self.humidity / 100.0)
        
        if random.random() < rain_chance * dt * 60:  # Нормализуем к кадрам
            # Создаем дождь в случайной точке
            center_x = random.uniform(-100, 100)
            center_y = random.uniform(-100, 100)
            intensity = random.uniform(RAIN_INTENSITY_MIN, RAIN_INTENSITY_MAX)
            radius = random.uniform(10, 30)
            duration = random.uniform(5, 15)  # секунды
            
            self.active_rain = (center_x, center_y, intensity, radius, duration)
            self.time_since_last_rain = 0.0
    
    def _update_sandstorm(self, dt, world_manager):
        """Обновляет активную песчаную бурю"""
        if self.active_sandstorm is None:
            return
        
        center_x, center_y, intensity, radius, duration = self.active_sandstorm
        duration -= dt
        
        if duration <= 0:
            self.active_sandstorm = None
            return
        
        # Песчаная буря увеличивает испарение и уменьшает видимость
        self._apply_sandstorm_effects(world_manager, center_x, center_y, intensity, radius, dt)
        
        self.active_sandstorm = (center_x, center_y, intensity, radius, duration)
    
    def _apply_sandstorm_effects(self, world_manager, center_x, center_y, intensity, radius, dt):
        """Применяет эффекты песчаной бури"""
        tiles = world_manager.get_tiles_in_radius(center_x, center_y, radius)
        
        for tile in tiles:
            dist = ((tile.x - center_x)**2 + (tile.y - center_y)**2)**0.5
            if dist <= radius:
                # Усиленное испарение в зоне бури
                evaporation_multiplier = 1.0 + intensity * (1.0 - dist / radius)
                evaporation = WATER_EVAPORATION_RATE * evaporation_multiplier * dt
                tile.remove_water(evaporation)
                tile.needs_update = True
    
    def _check_sandstorm_probability(self, dt, world_manager):
        """Проверяет вероятность песчаной бури"""
        if self.active_sandstorm is not None:
            return
        
        global_water = world_manager.get_global_water_level()
        
        # Песчаная буря более вероятна при низком уровне воды
        if global_water < SANDSTORM_THRESHOLD:
            sandstorm_chance = (SANDSTORM_THRESHOLD - global_water) / SANDSTORM_THRESHOLD * 0.001
            
            if random.random() < sandstorm_chance * dt * 60:
                center_x = random.uniform(-100, 100)
                center_y = random.uniform(-100, 100)
                intensity = random.uniform(1.0, 3.0)
                radius = random.uniform(15, 40)
                duration = random.uniform(10, 30)
                
                self.active_sandstorm = (center_x, center_y, intensity, radius, duration)
                self.time_since_last_sandstorm = 0.0
    
    def _update_evaporation(self, dt, world_manager):
        """
        Обновляет испарение воды.
        
        Использует уравнение: E = k * (es - ea) * f(u)
        где es - давление насыщенного пара, ea - текущее давление пара,
        f(u) - функция скорости ветра
        """
        # Упрощенная модель испарения
        # Давление насыщенного пара зависит от температуры (уравнение Клаузиуса-Клапейрона)
        es = self._saturation_vapor_pressure(self.temperature)
        
        # Текущее давление пара зависит от влажности
        ea = es * (self.humidity / 100.0)
        
        # Функция скорости ветра
        wind_factor = 1.0 + self.wind_speed * 0.1
        
        # Константа испарения
        k = WATER_EVAPORATION_RATE
        
        # Вычисляем скорость испарения
        evaporation_rate = k * (es - ea) * wind_factor
        
        # Применяем испарение к тайлам (только к видимым чанкам для оптимизации)
        # В реальной игре это должно применяться ко всем тайлам постепенно
        pass  # Испарение применяется через обновление тайлов
    
    def _saturation_vapor_pressure(self, temperature):
        """
        Вычисляет давление насыщенного пара по уравнению Клаузиуса-Клапейрона.
        
        Упрощенная формула: es = 0.611 * exp(17.27 * T / (T + 237.3))
        где T - температура в градусах Цельсия
        """
        if temperature <= 0:
            return 0.0
        
        # Формула Магнуса для давления насыщенного пара
        es = 0.611 * math.exp(17.27 * temperature / (temperature + 237.3))
        return es
    
    def _update_condensation(self, dt, world_manager):
        """
        Обновляет конденсацию (образование росы).
        
        Конденсация происходит, когда влажность достигает 100% (точка росы).
        """
        # Точка росы вычисляется из температуры и влажности
        dew_point = self._calculate_dew_point(self.temperature, self.humidity)
        
        # Если температура ниже точки росы, происходит конденсация
        if self.temperature < dew_point:
            condensation_rate = (dew_point - self.temperature) * 0.01 * dt
            # Конденсация увеличивает влажность почвы
            # Это будет применяться к тайлам через обновление мира
    
    def _calculate_dew_point(self, temperature, humidity):
        """
        Вычисляет точку росы.
        
        Формула: Td = (b * alpha) / (a - alpha)
        где alpha = (a * T) / (b + T) + ln(RH/100)
        a = 17.27, b = 237.7
        """
        if humidity <= 0:
            return -273.15  # Абсолютный ноль
        
        a = 17.27
        b = 237.7
        alpha = (a * temperature) / (b + temperature) + math.log(humidity / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        
        return dew_point
    
    def get_weather_at_position(self, x, y):
        """
        Возвращает погодные условия в указанной позиции.
        
        Returns:
            dict с информацией о погоде
        """
        weather = {
            'temperature': self.temperature,
            'humidity': self.humidity,
            'wind_speed': self.wind_speed,
            'is_raining': False,
            'is_sandstorm': False,
        }
        
        if self.active_rain:
            cx, cy, _, radius, _ = self.active_rain
            dist = ((x - cx)**2 + (y - cy)**2)**0.5
            if dist <= radius:
                weather['is_raining'] = True
        
        if self.active_sandstorm:
            cx, cy, _, radius, _ = self.active_sandstorm
            dist = ((x - cx)**2 + (y - cy)**2)**0.5
            if dist <= radius:
                weather['is_sandstorm'] = True
        
        return weather
