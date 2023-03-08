import json
import os

from session_info import vk
from game_system.game import Game, GameDoesNotExistError


def auto_stat(value):
    return int(value) if value is not None else 60


def init(peer_id, user_id, template_match, eng_name, gen_name, game_name, main):

    if eng_name == "GM":
        vk.messages.send(random_id=0, peer_id=peer_id, message='Имя GM зарезервировано. Выберите, пожалуйста, другое.')
        return
    if os.path.isfile(f"heroes/{eng_name}.json"):
        vk.messages.send(random_id=0, peer_id=peer_id, message='Профиль с таким именем уже существует')
        return
    if game_name is None:
        game_identifier = peer_id
    else:
        game_identifier = game_name
    try:
        game = Game.load(game_identifier)
    except GameDoesNotExistError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="Игры с таким названием или в данной конференции не существует.")
        return
    rp_id = game.chat_id
    if main:
        game.set_main(user_id, eng_name)
        game.save()
    vk.messages.send(random_id=0, peer_id=peer_id, message=f'Профиль {gen_name} успешно создан.')

    tm = template_match
    profile_data = {
                    "player_id": user_id,
                    "nominative": tm[1],
                    "genitive": gen_name,
                    "gender": tm[2].lower(),
                    "dominant hand": tm[3].lower() if tm[3] is not None else "правая",

                    "strength": auto_stat(tm[4]),
                    "agility": auto_stat(tm[5]),
                    "magic": auto_stat(tm[6]),
                    "charisma": auto_stat(tm[7]),
                    "endurance": auto_stat(tm[8]),
                    "intelligence": auto_stat(tm[9]),
                    "perception": auto_stat(tm[10]),

                    "luck": 60,

                    "ready action": "",
                    "RP_id": rp_id
                }
    with open(f'heroes/{eng_name}.json', 'x', encoding="utf-8") as json_profile:
        json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)
