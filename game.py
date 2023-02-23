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

    class Queue:

        def __init__(self, name, data):
            self.name = name
            self.__data = data

        def __str__(self):
            return f"{self.name}: {' — '.join(self.__data)}"

        def shuffle(self):
            random.shuffle(self.__data)

    def __init__(self, name, chat_id, gm_id, pinned=None, mains=None, queues=None):

        self.name = name
        self.chat_id = chat_id
        self.gm_id = gm_id

        self.__pinned = pinned if pinned is not None else []
        self.__mains = mains if mains is not None else {}
        self.__queues = queues if queues is not None else {}

    """
    ---------------------------
    Basic functionality methods
    ---------------------------
    """

    @staticmethod
    def exists(identifier):
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
            "pinned": self.__pinned,
            "mains": self.__mains,
            "queues": self.__queues
        }

        with open(f"games/{self.name}.json", 'w', encoding="utf-8") as game_file:
            json.dump(game_data, game_file, indent=4, ensure_ascii=False)

    """
    ----------------------------
    Queues functionality methods
    ----------------------------
    """

    @property
    def queues(self):
        return [self.Queue(*queue_data) for queue_data in self.__queues.items()]

    @property
    def queues_names(self):
        return self.__queues.keys()

    def get_queue(self, name):
        try:
            return self.Queue(name, self.__queues[name])
        except KeyError:
            raise QueueNotFoundError

    def set_queue(self, queue, name=None, pin=False):
        if name is None:
            name = f"Q{len(self.__queues)}"
        self.__queues[name] = queue
        if name in self.pinned:
            self.update_pinned_message()
            return name
        if pin:
            self.add_to_pinned([name])
        return name

    def delete_queue(self, name):
        try:
            self.__queues.pop(name)
        except KeyError:
            raise QueueNotFoundError
        try:
            self.remove_from_pinned(name)
        except QueueNotFoundError:
            return

    def clear_queues(self):
        self.__queues.clear()
        if self.__pinned:
            self.__pinned.clear()
            self.update_pinned_message()

    def next_in_queue(self, name):
        for queue in self.__queues.values():
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

    """
    ---------------------------------
    Main heroes functionality methods
    ---------------------------------
    """

    def get_main(self, user_id):
        return self.__mains.get(str(user_id), None)

    def set_main(self, user_id, hero_name):
        self.__mains[str(user_id)] = hero_name

    """
    -----------------------------------
    Pinned queues functionality methods
    -----------------------------------
    """

    @property
    def pinned(self):
        return self.__pinned

    def add_to_pinned(self, queue_names):
        self.__pinned.extend(queue_names)
        self.update_pinned_message()

    def remove_from_pinned(self, queue_name):
        try:
            self.__pinned.remove(queue_name)
        except ValueError:
            raise QueueNotFoundError
        self.update_pinned_message()

    def update_pinned_message(self):
        if self.__pinned:
            message_text = "\n".join(str(self.get_queue(queue_name)) for queue_name in self.__pinned)
            message_id = vk.messages.send(random_id=0, peer_id=self.chat_id, message=message_text)
            vk.messages.pin(peer_id=self.chat_id, message_id=message_id)
        else:
            vk.messages.unpin(peer_id=self.chat_id)
