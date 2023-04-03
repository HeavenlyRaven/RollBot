import json
import os
import random


class GameDoesNotExistError(Exception):
    """Raised when a game with such name or id does not exist"""
    pass


class QueueNotFoundError(Exception):
    """Raised when a queue with such name is not found"""
    pass


class QueueAlreadyExistsError(Exception):
    """Raised when a queue with such name already exists"""
    pass


class HeroNotFoundInQueuesError(Exception):
    """Raised when a hero with such in name is not found in any of the queues"""
    pass


class HeroNotFoundInQueueError(Exception):
    """Raised when a hero with such in name is not found in the queue"""
    pass


class Game:

    def __init__(self, name, chat_id, gm_id, pinned=None, mains=None, queues=None):

        self.name = name
        self.chat_id = chat_id
        self.gm_id = gm_id

        self.__pinned = pinned if pinned is not None else []
        self.__pinned_modified = False
        self.__mains = mains if mains is not None else {}
        self.__queues = queues if queues is not None else {}

    """
    -----------------
    Utility functions
    -----------------
    """

    @staticmethod
    def __can_modify_pinned(method):
        def wrapper(self, queue_name, *args, **kwargs):
            result = method(self, queue_name, *args, **kwargs)
            if queue_name in self.__pinned:
                self.__pinned_modified = True
            return result
        return wrapper
    
    @staticmethod
    def __modifies_pinned(method):
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self.__pinned_modified = True
            return result
        return wrapper
    
    @staticmethod
    def __queue_to_str(name, queue): 
        return f"{name}: {' — '.join(queue)}"
    
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
    def queues_list(self):
        return list(self.__queues.keys())
    
    @property
    def queues(self):
        return self.__queues

    def __get_queue(self, name):
        try:
            return self.__queues[name]
        except KeyError:
            raise QueueNotFoundError
        
    def str_queue(self, name):
        return self.__queue_to_str(name, self.__get_queue(name))
    
    def str_all_queues(self):
        return "\n".join(self.__queue_to_str(name, queue) for name, queue in self.__queues.items())

    def add_queue(self, queue, name=None):
        name = f"Q{len(self.__queues)}" if name is None else name
        if name in self.__queues:
            raise QueueAlreadyExistsError
        self.__queues[name] = queue
        return name

    @__can_modify_pinned
    def edit_queue(self, name, new_queue):
        if name not in self.__queues:
            raise QueueNotFoundError
        self.__queues[name] = new_queue

    def delete_queue(self, name):
        try:
            self.__queues.pop(name)
        except KeyError:
            raise QueueNotFoundError
        if name in self.__pinned:
            self.remove_from_pinned(name)

    def rename_queue(self, old_queue_name, new_queue_name):
        if old_queue_name not in self.__queues:
            raise QueueNotFoundError
        self.__queues = {new_queue_name if name == old_queue_name else name: queue 
                         for name, queue in self.__queues.items()}
        if old_queue_name in self.__pinned:
            self.replace_in_pinned(old_queue_name, new_queue_name)

    def clear_queues(self):
        self.__queues.clear()
        if self.__pinned:
            self.clear_pinned()

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
    
    @__can_modify_pinned
    def shuffle_queue(self, name):
        random.shuffle(self.__get_queue(name))

    @__can_modify_pinned
    def add_to_queue(self, queue_name, hero_name):
        self.__get_queue(queue_name).append(hero_name)

    @__can_modify_pinned
    def remove_from_queue(self, queue_name, hero_name):
        try:
            self.__get_queue(queue_name).remove(hero_name)
        except ValueError:
            raise HeroNotFoundInQueueError
        
    @__can_modify_pinned
    def move_in_queue(self, queue_name, hero_name, position):
        queue = self.__get_queue(queue_name)
        try:
            queue.remove(hero_name)
        except ValueError:
            raise HeroNotFoundInQueueError
        queue.insert(position, hero_name)

    """
    ---------------------------------
    Main heroes functionality methods
    ---------------------------------
    """

    def get_main(self, user_id):
        return self.__mains.get(str(user_id))

    def set_main(self, user_id, hero_name):
        self.__mains[str(user_id)] = hero_name

    """
    -----------------------------------
    Pinned queues functionality methods
    -----------------------------------
    """

    @property
    def pinned_list(self):
        return self.__pinned.copy()
    
    @property
    def pinned_modified(self):
        return self.__pinned_modified

    @__modifies_pinned
    def add_to_pinned(self, queue_name):
        if queue_name not in self.__queues:
            raise QueueNotFoundError
        if queue_name in self.__pinned:
            return
        self.__pinned.append(queue_name)

    @__modifies_pinned
    def remove_from_pinned(self, queue_name):
        try:
            self.__pinned.remove(queue_name)
        except ValueError:
            raise QueueNotFoundError

    @__modifies_pinned
    def replace_in_pinned(self, old_queue_name, new_queue_name):
        if old_queue_name not in self.__pinned:
            raise QueueNotFoundError(f"There is no queue named {old_queue_name} in pinned")
        if new_queue_name not in self.__queues:
            raise QueueNotFoundError(f"There is no queue named {new_queue_name} in queues")
        if new_queue_name in self.__pinned:
            self.__pinned.remove(new_queue_name)
        self.__pinned[self.__pinned.index(old_queue_name)] = new_queue_name

    @__modifies_pinned
    def pin_all(self):
        self.__pinned = self.queues_list

    @__modifies_pinned
    def clear_pinned(self):
        self.__pinned.clear()

    def generate_pinned_message(self):
        return "\n".join(self.__queue_to_str(name, self.__queues[name]) for name in self.__pinned) if self.__pinned else None
