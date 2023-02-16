import json
import os

from session_info import vk


class GameDoesNotExistError(Exception):
    """Raised when a game with such name or id does not exist"""
    pass


class QueueNotFoundError(Exception):
    """Raised when a queue with such name is not found"""
    pass


class Game:

    def __init__(self, name, chat_id, gm_id, players=None, queues=None):

        self.name = name
        self.chat_id = chat_id
        self.gm_id = gm_id

        if players is not None:
            self.players = players
        else:
            chat_members = vk.messages.getConversationMembers(peer_id=chat_id)
            self.players = {int(item["member_id"]): None for item in chat_members["items"]}

        self.queues = queues if queues is not None else {}

    @classmethod
    def exists(cls, identifier):
        return os.path.isfile(f"games/{identifier}.json")

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

    def add_queue(self, queue, name=None):

        if name is None:
            name = f"Q{len(self.queues)}"

        self.queues[name] = queue

    def delete_queue(self, name):

        try:
            self.queues.pop(name)
        except KeyError:
            raise QueueNotFoundError
