"""
Система торговли с водой как валютой
"""
import random
from utils.math_utils import clamp


class TradeOffer:
    """Предложение торговли"""
    
    def __init__(self, offer_type, offer_item, offer_amount, price_water, description=""):
        self.offer_type = offer_type  # 'resource', 'information', 'service'
        self.offer_item = offer_item  # Название предмета/услуги
        self.offer_amount = offer_amount  # Количество
        self.price_water = price_water  # Цена в воде
        self.description = description
    
    def can_afford(self, player_water):
        """Проверяет, может ли игрок позволить себе эту сделку"""
        return player_water >= self.price_water
    
    def execute(self, player):
        """
        Выполняет сделку.
        
        Args:
            player: объект Player
        
        Returns:
            True если сделка успешна, False иначе
        """
        if not self.can_afford(player.inventory.water):
            return False
        
        # Списываем воду
        player.inventory.remove_water(self.price_water)
        
        # Выдаем предмет/услугу
        if self.offer_type == 'resource':
            player.inventory.add_resource(self.offer_item, self.offer_amount)
        elif self.offer_type == 'information':
            # Информация будет храниться отдельно или передаваться через события
            pass
        elif self.offer_type == 'service':
            # Услуги выполняются сразу
            if self.offer_item == 'heal':
                from utils.config import PLAYER_MAX_HEALTH
                player.health = clamp(player.health + self.offer_amount, 0, PLAYER_MAX_HEALTH)
            elif self.offer_item == 'water_refill':
                player.inventory.add_water(self.offer_amount)
        
        return True


class TradingSystem:
    """Система торговли"""
    
    def __init__(self):
        self.base_prices = {
            'stone': 5.0,  # Вода за единицу камня
            'sand': 1.0,   # Вода за единицу песка
            'information': 10.0,  # Вода за информацию
            'heal': 0.5,   # Вода за единицу здоровья
        }
    
    def generate_trade_offers(self, npc, world_manager):
        """
        Генерирует торговые предложения от NPC.
        
        Цены зависят от доступности воды в регионе.
        
        Args:
            npc: объект NPC
            world_manager: менеджер мира
        
        Returns:
            Список TradeOffer
        """
        offers = []
        
        # Вычисляем доступность воды в регионе NPC
        water_availability = self._get_regional_water_availability(
            world_manager, npc.x, npc.y
        )
        
        # Модификатор цены (выше цена при дефиците воды)
        price_modifier = 2.0 - (water_availability / 100.0)
        price_modifier = clamp(price_modifier, 0.5, 3.0)
        
        # Генерируем предложения ресурсов
        if random.random() < 0.7:
            stone_amount = random.randint(5, 20)
            stone_price = self.base_prices['stone'] * price_modifier * stone_amount
            offers.append(TradeOffer(
                'resource', 'stone', stone_amount, stone_price,
                f"{stone_amount} камней за {stone_price:.1f} воды"
            ))
        
        if random.random() < 0.5:
            sand_amount = random.randint(10, 50)
            sand_price = self.base_prices['sand'] * price_modifier * sand_amount
            offers.append(TradeOffer(
                'resource', 'sand', sand_amount, sand_price,
                f"{sand_amount} песка за {sand_price:.1f} воды"
            ))
        
        # Предложения услуг
        if random.random() < 0.6:
            heal_amount = random.randint(20, 50)
            heal_price = self.base_prices['heal'] * price_modifier * heal_amount
            offers.append(TradeOffer(
                'service', 'heal', heal_amount, heal_price,
                f"Восстановление {heal_amount} здоровья за {heal_price:.1f} воды"
            ))
        
        # Предложения информации
        if random.random() < 0.4:
            info_price = self.base_prices['information'] * price_modifier
            offers.append(TradeOffer(
                'information', 'water_source', 1, info_price,
                f"Информация об источнике воды за {info_price:.1f} воды"
            ))
        
        return offers
    
    def _get_regional_water_availability(self, world_manager, x, y, radius=20):
        """
        Вычисляет доступность воды в регионе.
        
        Args:
            world_manager: менеджер мира
            x, y: центр региона
            radius: радиус
        
        Returns:
            Средний уровень воды в регионе (0-100)
        """
        tiles = world_manager.get_tiles_in_radius(x, y, radius)
        if len(tiles) == 0:
            return 0.0
        
        total_water = sum(tile.water_level for tile in tiles)
        return total_water / len(tiles)
    
    def calculate_dynamic_price(self, base_price, water_availability, demand_factor=1.0):
        """
        Вычисляет динамическую цену на основе доступности воды.
        
        Args:
            base_price: базовая цена
            water_availability: доступность воды в регионе (0-100)
            demand_factor: фактор спроса
        
        Returns:
            Динамическая цена
        """
        # При низкой доступности воды цены выше
        scarcity_factor = 2.0 - (water_availability / 100.0)
        scarcity_factor = clamp(scarcity_factor, 0.5, 3.0)
        
        return base_price * scarcity_factor * demand_factor
    
    def player_sell_water(self, player, amount, price_per_unit):
        """
        Игрок продает воду.
        
        Args:
            player: объект Player
            amount: количество воды для продажи
            price_per_unit: цена за единицу
        
        Returns:
            Выручка (количество полученной воды или других ресурсов)
        """
        if not player.inventory.has_water(amount):
            return 0.0
        
        player.inventory.remove_water(amount)
        # В этой игре вода - валюта, поэтому продажа воды может давать другие ресурсы
        # или просто увеличивать репутацию
        return amount * price_per_unit
