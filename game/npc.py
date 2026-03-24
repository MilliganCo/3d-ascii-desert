"""
NPC персонажи с поведением, зависящим от уровня воды
"""
import random
import math
from utils.config import COLOR_NPC, ASCII_NPC
from physics.ecology import Ecology


class Quest:
    """Квест от NPC"""
    
    def __init__(self, quest_type, description, target_item=None, target_amount=0, reward_water=0):
        self.quest_type = quest_type  # 'deliver', 'collect', 'explore'
        self.description = description
        self.target_item = target_item
        self.target_amount = target_amount
        self.reward_water = reward_water
        self.completed = False
    
    def check_completion(self, player):
        """Проверяет, выполнен ли квест"""
        if self.completed:
            return True
        
        if self.quest_type == 'deliver':
            # Проверяем, есть ли у игрока нужный предмет
            if self.target_item == 'water':
                if player.inventory.water >= self.target_amount:
                    return True
        elif self.quest_type == 'collect':
            # Проверяем инвентарь игрока
            if player.inventory.get_resource(self.target_item) >= self.target_amount:
                return True
        
        return False
    
    def complete(self, player):
        """Завершает квест и выдает награду"""
        if self.completed:
            return False
        
        if self.check_completion(player):
            # Выдаем награду
            player.inventory.add_water(self.reward_water)
            
            # Убираем предметы из инвентаря для квестов на доставку
            if self.quest_type == 'deliver':
                if self.target_item == 'water':
                    player.inventory.remove_water(self.target_amount)
            
            self.completed = True
            return True
        
        return False


class NPC:
    """NPC персонаж"""
    
    def __init__(self, x, y, name="NPC"):
        self.x = float(x)
        self.y = float(y)
        self.z = 0.0
        self.name = name
        
        self.friendliness = 0.5  # Дружелюбность (0-1)
        self.aggressiveness = 0.0  # Агрессивность (0-1)
        self.water_need = random.uniform(20, 80)  # Потребность в воде
        
        self.quests = []
        self.trade_offers = []
        
        self.last_interaction_time = 0.0
    
    def update(self, dt, world_manager, ecology_system):
        """
        Обновляет поведение NPC.
        
        Args:
            dt: время с последнего кадра
            world_manager: менеджер мира
            ecology_system: система экологии для влияния на поведение
        """
        # Получаем влияние экологии на поведение
        ecology_influence = ecology_system.influence_on_npc_behavior(
            world_manager, self.x, self.y
        )
        
        # Обновляем дружелюбность и агрессивность на основе экологии
        self.friendliness = ecology_influence['friendliness']
        self.aggressiveness = ecology_influence['aggressiveness']
        
        # Обновляем высоту на основе тайла
        tile = world_manager.get_tile(int(self.x), int(self.y))
        if tile:
            self.z = tile.height + 0.5
        
        self.last_interaction_time += dt
    
    def generate_quest(self, world_manager):
        """Генерирует квест для игрока"""
        quest_types = ['deliver', 'collect']
        quest_type = random.choice(quest_types)
        
        if quest_type == 'deliver':
            # Квест на доставку воды
            amount = random.randint(10, 50)
            reward = amount * random.uniform(1.2, 1.5)  # Награда больше стоимости
            quest = Quest(
                'deliver',
                f"Доставьте {amount} единиц воды в соседний лагерь",
                'water',
                amount,
                reward
            )
        elif quest_type == 'collect':
            # Квест на сбор ресурсов
            resource = random.choice(['stone', 'sand'])
            amount = random.randint(5, 20)
            reward = random.randint(15, 30)
            quest = Quest(
                'collect',
                f"Соберите {amount} {resource}",
                resource,
                amount,
                reward
            )
        
        self.quests.append(quest)
        return quest
    
    def get_available_quests(self):
        """Возвращает список доступных (не выполненных) квестов"""
        return [q for q in self.quests if not q.completed]
    
    def interact(self, player, world_manager):
        """
        Взаимодействие с игроком.
        
        Args:
            player: объект Player
            world_manager: менеджер мира
        
        Returns:
            dict с информацией о взаимодействии
        """
        # Получаем доступность воды в регионе
        from physics.ecology import Ecology
        ecology = Ecology()
        water_availability = ecology.get_water_availability(world_manager, self.x, self.y, 10)
        
        interaction = {
            'can_trade': self.friendliness > 0.3,
            'can_quest': self.friendliness > 0.5,
            'is_aggressive': self.aggressiveness > 0.7,
            'message': self._get_interaction_message(water_availability),
            'quests': self.get_available_quests(),
        }
        
        # Если NPC агрессивен, игрок может потерять воду
        if interaction['is_aggressive']:
            water_loss = random.uniform(5, 15)
            player.inventory.remove_water(water_loss)
            interaction['message'] = f"{self.name}: Уходи! У меня нет воды для тебя!"
        
        return interaction
    
    def _get_interaction_message(self, water_availability):
        """Возвращает сообщение при взаимодействии"""
        messages_friendly = [
            f"{self.name}: Привет, путник! Вода здесь редка, но я могу помочь.",
            f"{self.name}: Добро пожаловать! Хочешь торговать?",
            f"{self.name}: Вижу, ты ищешь воду. Могу предложить сделку.",
            f"{self.name}: В этой пустыне вода - всё. Что тебе нужно?",
        ]
        
        messages_neutral = [
            f"{self.name}: Здравствуй. Могу предложить сделку.",
            f"{self.name}: Вода здесь дорога. Что у тебя есть?",
            f"{self.name}: Нужна помощь? У меня есть ресурсы.",
        ]
        
        messages_aggressive = [
            f"{self.name}: Уходи! У меня нет воды для тебя!",
            f"{self.name}: Не подходи! Вода только для своих!",
            f"{self.name}: В этой пустыне каждый сам за себя!",
        ]
        
        if self.aggressiveness > 0.7:
            return random.choice(messages_aggressive)
        elif self.friendliness > 0.7:
            return random.choice(messages_friendly)
        elif self.friendliness > 0.5:
            return random.choice(messages_neutral)
        else:
            if water_availability < 20:
                return f"{self.name}: Вода здесь кончилась... Уходи."
            else:
                return f"{self.name}: ..."
    
    def get_render_info(self):
        """Возвращает информацию для рендеринга"""
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'char': ASCII_NPC,
            'color': COLOR_NPC,
        }


class NPCManager:
    """Управляет NPC в мире"""
    
    def __init__(self):
        self.npcs = []
        self.ecology_system = Ecology()
    
    def spawn_npc(self, x, y, name=None):
        """Создает нового NPC"""
        if name is None:
            name = f"NPC_{len(self.npcs)}"
        
        npc = NPC(x, y, name)
        self.npcs.append(npc)
        return npc
    
    def get_npcs_in_radius(self, center_x, center_y, radius):
        """Возвращает NPC в радиусе"""
        npcs = []
        for npc in self.npcs:
            dist = math.sqrt((npc.x - center_x)**2 + (npc.y - center_y)**2)
            if dist <= radius:
                npcs.append(npc)
        return npcs
    
    def update(self, dt, world_manager):
        """Обновляет всех NPC"""
        for npc in self.npcs:
            npc.update(dt, world_manager, self.ecology_system)
    
    def get_nearby_npc(self, x, y, radius=5):
        """Получает ближайшего NPC"""
        npcs = self.get_npcs_in_radius(x, y, radius)
        if npcs:
            # Возвращаем ближайшего
            npcs.sort(key=lambda n: math.sqrt((n.x - x)**2 + (n.y - y)**2))
            return npcs[0]
        return None
