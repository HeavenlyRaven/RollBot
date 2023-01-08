from session_info import vk
import json

EQUIP_LIST = r'(right hand|left hand|waist|clothes|inventory)'

PROFILE_TEMPLATE = r'''Имя:.*\s*
Пол: (мужской|женский)\s*
Ведущая рука: (правая|левая)\s*
Статы:\s*
Сила: ([0-9][0-9]?|100)\s*
Ловкость: ([0-9][0-9]?|100)\s*
Магия: ([0-9][0-9]?|100)\s*
Харизма: ([0-9][0-9]?|100)\s*
Выносливость: ([0-9][0-9]?|100)\s*
Интеллект: ([0-9][0-9]?|100)\s*
Восприятие: ([0-9][0-9]?|100)'''


def accessible_profile_data(user_id, peer_id, name):

    try:
        with open(f'Bot/heroes/{name}.json', 'r') as profile:
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
