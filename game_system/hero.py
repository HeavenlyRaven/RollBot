import json
import os


class HeroDoesNotExistError(Exception):
    """Raised when a hero with such name does not exist"""
    pass


class Hero:

    def __init__(self, name, player_id, nominative, genitive, gender, dominant_hand,
                 strength, agility, magic, charisma, endurance, intelligence, perception, luck,
                 game_chat_id, ready_action=None):
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
    def exists(name):
        return os.path.isfile(f"heroes/{name}.json")

    @classmethod
    def load(cls, name):
        try:
            with open(f"../heroes/{name}.json", 'r') as hero_file:
                hero_data = json.load(hero_file)
        except FileNotFoundError:
            raise HeroDoesNotExistError
        else:
            return cls(**hero_data)

    def save(self):

        hero_data = {
            "name": self.name,
            "player_id": self.player_id,
            "nominative": self.nominative,
            "genitive": self.genitive,
            "gender": self.gender,
            "dominant hand": self.dominant_hand,
            "strength": self.strength,
            "agility": self.agility,
            "magic": self.magic,
            "charisma": self.charisma,
            "endurance": self.endurance,
            "intelligence": self.intelligence,
            "perception": self.perception,
            "luck": self.luck,
            "ready action": self.ready_action,
            "game_chat_id": self.game_chat_id
        }

        with open(f"../heroes/{self.name}.json", 'w', encoding="utf-8") as hero_file:
            json.dump(hero_data, hero_file, indent=4, ensure_ascii=False)
