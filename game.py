import json


class GameDoesNotExistError(Exception):
    """Raised when a game with such name or id does not exist"""
    pass


class Game:

    def __init__(self, name, chat_id, gm_id=None, players=None, queues=None):

        self.name = name
        self.chat_id = chat_id
        self.gm_id = gm_id
        self.players = players if players is not None else []
        self.queues = queues if queues is not None else []

    @classmethod
    def load(cls, identifier):
        try:
            with open(f"games/{identifier}.json", 'r') as game_file:
                game_data = json.load(game_file)
        except FileNotFoundError:
            raise GameDoesNotExistError
        else:
            return cls(**game_data)

    def save(self):

        game_data = {
            "name": self.name,
            "chat_id": self.chat_id,
            "gm_id": self.gm_id,
            "players": self.players,
            "queues": self.queues
        }

        with open(f"games/{self.name}.json", 'w', encoding="utf-8") as game_file:
            json.dump(game_data, game_file, indent=4, ensure_ascii=False)
