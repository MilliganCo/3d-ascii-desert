"""
Механики выживания: влияние температуры, истощение, смерть
"""
from utils.math_utils import clamp


class SurvivalMechanics:
    """Управляет механиками выживания"""
    
    def __init__(self):
        self.base_temperature = 30.0  # Базовая температура пустыни
        self.temperature_variation = 10.0  # Вариация температуры
    
    def calculate_water_drain_from_temperature(self, temperature, base_drain_rate):
        """
        Вычисляет дополнительный расход воды от температуры.
        
        При высокой температуре игрок потеет больше и теряет больше воды.
        
        Args:
            temperature: текущая температура
            base_drain_rate: базовый расход воды
        
        Returns:
            Модифицированный расход воды
        """
        # Нормальная температура для комфорта
        comfortable_temp = 25.0
        
        # Если температура выше комфортной, увеличиваем расход
        if temperature > comfortable_temp:
            temp_diff = temperature - comfortable_temp
            multiplier = 1.0 + (temp_diff / 10.0) * 0.5  # +5% на каждые 10 градусов
            return base_drain_rate * multiplier
        
        return base_drain_rate
    
    def calculate_health_loss_from_thirst(self, water_level, dt):
        """
        Вычисляет потерю здоровья от жажды.
        
        Args:
            water_level: текущий уровень воды в организме
            dt: время с последнего кадра
        
        Returns:
            Потеря здоровья
        """
        if water_level > 20:
            return 0.0  # Нет потери здоровья при достаточном уровне воды
        
        # Критический уровень воды
        if water_level <= 0:
            return 10.0 * dt  # Сильная потеря здоровья
        
        # Постепенная потеря здоровья при низком уровне воды
        health_loss = (20.0 - water_level) / 20.0 * 5.0 * dt
        return health_loss
    
    def calculate_exhaustion(self, is_moving, water_level, dt):
        """
        Вычисляет усталость игрока.
        
        Args:
            is_moving: движется ли игрок
            water_level: уровень воды
            dt: время
        
        Returns:
            Уровень усталости (0-100)
        """
        exhaustion_rate = 0.0
        
        if is_moving:
            exhaustion_rate = 5.0 * dt  # Усталость при движении
        
        # Низкий уровень воды увеличивает усталость
        if water_level < 30:
            exhaustion_rate *= (30.0 - water_level) / 30.0 + 1.0
        
        return exhaustion_rate
    
    def can_perform_action(self, water_level, health):
        """
        Проверяет, может ли игрок выполнять действия.
        
        Args:
            water_level: уровень воды
            health: здоровье
        
        Returns:
            (can_act, reason) - может ли действовать и причина если нет
        """
        if health <= 0:
            return False, "Вы мертвы"
        
        if water_level <= 0:
            return False, "Критическое обезвоживание"
        
        if water_level < 10:
            return False, "Сильная жажда"
        
        return True, None
    
    def get_survival_status(self, player):
        """
        Возвращает статус выживания игрока.
        
        Args:
            player: объект Player
        
        Returns:
            dict с информацией о статусе
        """
        status = {
            'health': player.health,
            'water_level': player.water_level,
            'is_alive': player.is_alive(),
            'thirst_level': self._get_thirst_level(player.water_level),
            'health_status': self._get_health_status(player.health),
        }
        
        return status
    
    def _get_thirst_level(self, water_level):
        """Определяет уровень жажды"""
        if water_level > 50:
            return "Норма"
        elif water_level > 30:
            return "Легкая жажда"
        elif water_level > 15:
            return "Жажда"
        elif water_level > 5:
            return "Сильная жажда"
        else:
            return "Критическое обезвоживание"
    
    def _get_health_status(self, health):
        """Определяет статус здоровья"""
        if health > 75:
            return "Отлично"
        elif health > 50:
            return "Хорошо"
        elif health > 25:
            return "Ранен"
        elif health > 0:
            return "Критическое состояние"
        else:
            return "Мертв"
