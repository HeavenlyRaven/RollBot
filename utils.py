import json

from session_info import vk
from game import Game

EQUIP_LIST = r'(right hand|left hand|waist|clothes|inventory)'

PROFILE_TEMPLATE = r'''Имя: (.*)
Пол: (мужской|женский)(?:
Ведущая рука: (правая|левая)
Статы:
Сила: ([0-9][0-9]?|100)
Ловкость: ([0-9][0-9]?|100)
Магия: ([0-9][0-9]?|100)
Харизма: ([0-9][0-9]?|100)
Выносливость: ([0-9][0-9]?|100)
Интеллект: ([0-9][0-9]?|100)
Восприятие: ([0-9][0-9]?|100))?'''


def accessible_profile_data(user_id, peer_id, name):

    try:
        with open(f'heroes/{name}.json', 'r') as profile:
            profile_data = json.load(profile)
        if profile_data["player_id"] != user_id:
            vk.messages.send(random_id=0, peer_id=peer_id,
                             message='У вас нет права доступа к профилю этого персонажа.')
            return None
        else:
            return profile_data
    except FileNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="Такого персонажа нет в журнале")
        return None


def game_required_in_chat(command):
    def wrapper(peer_id, *args, **kwargs):
        if Game.exists(peer_id):
            command(peer_id, *args, **kwargs)
        else:
            vk.messages.send(random_id=0, peer_id=peer_id, message="В данной конференции нет игры.")
    return wrapper