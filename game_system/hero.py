import json
import os

from typing import Literal, Self, Final

class HeroDoesNotExistError(Exception):
    """Raised when a hero with such name does not exist"""
    pass


class Hero:

    name: str
    player_id: int
    nominative: str
    genitive: str
    gender: Literal["мужской", "женский"]
    dominant_hand: Literal["правая", "левая"]
    strength: int
    agility: int
    magic: int
    charisma: int
    endurance: int
    intelligence: int
    perception: int
    luck: int
    ready_action: str | None
    game_chat_id: int

    PROFILE_TEMPLATE: Final[str] = r'''Имя: (?P<nominative>.*), (?P<genitive>.*)
Пол: (?P<gender>мужской|женский)(?:
Ведущая рука: (?P<dominant_hand>правая|левая)
Статы:
Сила: (?P<strength>[0-9][0-9]?|100)
Ловкость: (?P<agility>[0-9][0-9]?|100)
Магия: (?P<magic>[0-9][0-9]?|100)
Харизма: (?P<charisma>[0-9][0-9]?|100)
Выносливость: (?P<endurance>[0-9][0-9]?|100)
Интеллект: (?P<intelligence>[0-9][0-9]?|100)
Восприятие: (?P<perception>[0-9][0-9]?|100))?'''


    def __init__(self, name: str, player_id: int, nominative: str, genitive: str, 
                 gender: Literal["мужской", "женский"], 
                 dominant_hand: Literal["правая", "левая"],
                 strength: int, agility: int, magic: int, charisma: int, endurance: int, intelligence: int, perception: int, luck: int,
                 game_chat_id: int, ready_action: str | None = None) -> None:
        self.name = name
        self.player_id = player_id
        self.nominative = nominative
        self.genitive = genitive
        self.gender = gender
        self.dominant_hand = dominant_hand
        self.strength = strength
        self.agility = agility
        self.magic = magic
        self.charisma = charisma
        self.endurance = endurance
        self.intelligence = intelligence
        self.perception = perception
        self.luck = luck
        self.ready_action = ready_action
        self.game_chat_id = game_chat_id

    @staticmethod
    def exists(name: str) -> bool:
        return os.path.isfile(f"heroes/{name}.json")

    @classmethod
    def load(cls, name: str) -> Self:
        try:
            with open(f"heroes/{name}.json", 'r') as hero_file:
                hero_data = json.load(hero_file)
        except FileNotFoundError:
            raise HeroDoesNotExistError
        else:
            return cls(**hero_data)

    def save(self) -> None:

        hero_data = {
            "name": self.name,
            "player_id": self.player_id,
            "nominative": self.nominative,
            "genitive": self.genitive,
            "gender": self.gender,
            "dominant_hand": self.dominant_hand,
            "strength": self.strength,
            "agility": self.agility,
            "magic": self.magic,
            "charisma": self.charisma,
            "endurance": self.endurance,
            "intelligence": self.intelligence,
            "perception": self.perception,
            "luck": self.luck,
            "ready_action": self.ready_action,
            "game_chat_id": self.game_chat_id
        }

        with open(f"heroes/{self.name}.json", 'w', encoding="utf-8") as hero_file:
            json.dump(hero_data, hero_file, indent=4, ensure_ascii=False)

    @property
    def profile_text(self) -> str:

        return f'''Имя: {self.nominative}

Пол: {self.gender}
Ведущая рука: {self.dominant_hand}

Статы:
1. Сила: {self.strength}
2. Ловкость: {self.agility}
3. Магия: {self.magic}
4. Харизма: {self.charisma}
5. Стойкость: {self.endurance}
6. Интеллект: {self.intelligence}
7. Восприятие: {self.perception}

Характеристики:
1. Удача: {self.luck}'''
