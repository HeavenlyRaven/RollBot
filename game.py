import json
import os
import random

from session_info import vk


class GameDoesNotExistError(Exception):
    """Raised when a game with such name or id does not exist"""
    pass


class QueueNotFoundError(Exception):
    """Raised when a queue with such name is not found"""
    pass


class HeroNotFoundInQueuesError(Exception):
    """Raised when a hero with such in name is not found in any of the queues"""
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
        return name

    def delete_queue(self, name):

        try:
            self.queues.pop(name)
        except KeyError:
            raise QueueNotFoundError
    
    def display_queue(self, name, pin=False):
        message_text = ""
        if name == "all":
            for queue_name, queue in self.queues.items():
                message_text += f"{queue_name}: {' — '.join(queue)}\n"
        else:
            try:
                message_text = f"{name}: {' — '.join(self.queues[name])}" 
            except KeyError:
                raise QueueNotFoundError      
        message_id = vk.messages.send(random_id=0, peer_id=self.chat_id, message=message_text)
        if pin:
            vk.messages.pin(peer_id=self.chat_id, message_id=message_id)

    def shuffle_queue(self, name):

        if name == "all":
            for queue in self.queues.values():
                random.shuffle(queue)
        else:
            try:
                random.shuffle(self.queues[name])
            except KeyError:
                raise QueueNotFoundError

    def get_main(self, user_id):
        return self.players.get(user_id, None)

    def next_in_queue(self, name):
        for queue in self.queues.values():
            try:
                name_index = queue.index(name)
            except ValueError:
                continue
            else:
                next_hero = queue[0] if name_index == len(queue)-1 else queue[name_index+1]
                break
        else:
            raise HeroNotFoundInQueuesError
        return next_hero
