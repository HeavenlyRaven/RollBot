import json
import os

from utils import game_required_in_chat
from session_info import vk
from game import Game, GameDoesNotExistError, QueueNotFoundError, HeroNotFoundInQueuesError, HeroNotFoundInQueueError


@game_required_in_chat
def add_to_queue(peer_id, hero_name, queue_name, pos):
    game = Game.load(peer_id)
    try:
        game.get_queue(queue_name).add(hero_name, pos)
    except QueueNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {queue_name}.')
        return
    if queue_name in game.pinned:
        game.update_pinned_message()
    vk.messages.send(random_id=0, peer_id=peer_id,
                     message=f'Персонаж {hero_name} был успешно добавлен в очередь {queue_name}.')
    game.save()

@game_required_in_chat
def remove_from_queue(peer_id, hero_name, queue_name):
    game = Game.load(peer_id)
    try:
        queue = game.get_queue(queue_name)
    except QueueNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {queue_name}.')
        return
    try:
        queue.remove(hero_name)
    except HeroNotFoundInQueueError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной очереди нет персонажа с именем {hero_name}.')
        return
    if queue_name in game.pinned:
        game.update_pinned_message()
    vk.messages.send(random_id=0, peer_id=peer_id,
                     message=f'Персонаж {hero_name} был успешно удалён из очереди {queue_name}.')
    game.save()


@game_required_in_chat
def move_in_queue(peer_id, hero_name, queue_name, pos):
    game = Game.load(peer_id)
    try:
        queue = game.get_queue(queue_name)
    except QueueNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {queue_name}.')
        return
    try:
        queue.move(hero_name, pos)
    except HeroNotFoundInQueueError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной очереди нет персонажа с именем {hero_name}.')
        return
    if queue_name in game.pinned:
        game.update_pinned_message()
    game.save()


@game_required_in_chat
def rename_queue(peer_id, name, new_name):
    game = Game.load(peer_id)
    try:
        game.rename_queue(name, new_name)
    except QueueNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {name}.')
    vk.messages.send(random_id=0, peer_id=peer_id, message=f'Очередь {name} была успешно переименована в {new_name}.')
    game.save()


@game_required_in_chat
def pin_queue(peer_id, name):
    game = Game.load(peer_id)
    if name == "all":
        game.pin_all()
        game.save()
        return
    try:
        game.add_to_pinned(name)
    except QueueNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {name}.')
        return
    game.save()


@game_required_in_chat
def unpin_queue(peer_id, name):
    game = Game.load(peer_id)
    if name == "all":
        game.clear_pinned()
        game.save()
        return
    try:
        game.remove_from_pinned(name)
    except QueueNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'Очередь {name} не закреплена.')
        return
    game.save()


@game_required_in_chat
def show_all_queues(peer_id):
    if queues_text := "\n".join(str(queue) for queue in Game.load(peer_id).queues):
        vk.messages.send(random_id=0, peer_id=peer_id, message=queues_text)
    else:
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной игре нет ни одной очереди")


@game_required_in_chat
def end_turn(peer_id, user_id, name):
    game = Game.load(peer_id)
    hero_name = game.get_main(user_id) if name is None else name
    if hero_name is None:
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной игре у вас нет основного персонажа.")
        return
    try:
        next_turn_hero = game.next_in_queue(hero_name)
    except HeroNotFoundInQueuesError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной игре персонажа с таким именем нет ни в одной очереди.")
        return
    try:
        with open(f'heroes/{next_turn_hero}.json', 'r') as profile:
            profile_data = json.load(profile)
        player_id = profile_data["player_id"]
        genitive_name = profile_data["genitive"]
    except FileNotFoundError:
        if next_turn_hero == "GM":
            player_id = game.gm_id
            genitive_name = "Гейм Мастера"
        else:
            vk.messages.send(random_id=0, peer_id=peer_id, message=f'Ход окончен. Теперь ход персонажа {next_turn_hero}')
            return
    vk.messages.send(random_id=0, peer_id=peer_id, message=f'Ход окончен. Теперь ход [id{player_id}|{genitive_name}]')


@game_required_in_chat
def add_queue(peer_id, queue_name, queue):
    game = Game.load(peer_id)
    if queue_name in game.queues_names:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'Очередь с названием {queue_name} уже существует.')
        return
    final_name = game.set_queue(queue, name=queue_name, pin=True)
    vk.messages.send(random_id=0, peer_id=peer_id, message=f'Очередь {final_name} была успешно добавлена в игру.')
    game.save()


@game_required_in_chat
def delete_queue(peer_id, queue_name):
    game = Game.load(peer_id)
    try:
        game.delete_queue(queue_name)
    except QueueNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {queue_name}.')
        return
    vk.messages.send(random_id=0, peer_id=peer_id, message=f'Очередь {queue_name} была успешно удалена.')
    game.save()


@game_required_in_chat
def edit_queue(peer_id, queue_name, new_queue):
    game = Game.load(peer_id)
    if queue_name not in game.queues_names:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {queue_name}.')
        return
    game.set_queue(new_queue, name=queue_name)
    vk.messages.send(random_id=0, peer_id=peer_id, message=f'Очередь {queue_name} была успешно отредактирована.')
    game.save()
                 

@game_required_in_chat
def delete_all_queues(peer_id):
    game = Game.load(peer_id)
    game.clear_queues()
    vk.messages.send(random_id=0, peer_id=peer_id, message='Все очереди были успешно удалены.')
    game.save()


@game_required_in_chat
def shuffle_queue(peer_id, name):
    game = Game.load(peer_id)
    if name == "all":
        for queue in game.queues:
            queue.shuffle()
        game.update_pinned_message()
        game.save()
        return
    try:
        game.get_queue(name).shuffle()
    except QueueNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {name}.')
        return
    if name in game.pinned:
        game.update_pinned_message()
    game.save()


def create_game(peer_id, user_id, name):
    if Game.exists(peer_id):
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной конференции уже есть игра.")
    elif Game.exists(name):
        vk.messages.send(random_id=0, peer_id=peer_id, message="Игра с таким названием уже существует.")
    else:
        Game(name=name, chat_id=peer_id, gm_id=user_id).save()
        os.symlink(f"{name}.json", f"games/{peer_id}.json")
        vk.messages.send(random_id=0, peer_id=peer_id, message=f"Игра с названием {name} была успешно создана в текущей конференции.")


def delete_game(peer_id, user_id, name):
    try:
        game = Game.load(name)
    except GameDoesNotExistError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="Игры с таким названием не существует.")
    else:
        if game.gm_id != user_id:
            vk.messages.send(random_id=0, peer_id=peer_id,
                             message="У вас нет права доступа. Только ГМ может удалить игру.")
        else:
            vk.messages.send(random_id=0, peer_id=peer_id, message="Игра с названием {name} была успешно удалена.")
            os.remove(f"games/{name}.json")
            os.remove(f"games/{game.chat_id}.json")


def make_main(profile_data, peer_id, user_id, game_name, hero_name):
    try:
        game = Game.load(game_name)
    except GameDoesNotExistError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="Игры с таким названием не существует.")
    else:
        game.set_main(user_id, hero_name)
        vk.messages.send(random_id=0, peer_id=peer_id, messgae=f"Теперь вашим главным персонажем в {game_name} является {profile_data['nominative']}")
        game.save()


def notify_about_reaction(peer_id, name):
    try:
        with open(f'heroes/{name}.json', 'r') as profile:
            profile_data = json.load(profile)
        vk.messages.send(random_id=0, peer_id=peer_id, message=f"Запрос на реакцию для [id{profile_data['player_id']}|{profile_data['genitive']}]")
    except FileNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f"Запрос на реакцию для персонажа {name}")


@game_required_in_chat
def request_result(peer_id):
    vk.messages.send(random_id=0, peer_id=peer_id, 
                     message=f"Запрос на описание результата действия для [id{Game.load(peer_id).gm_id}|Гейм Мастера]")


@game_required_in_chat
def request_description(peer_id):
    vk.messages.send(random_id=0, peer_id=peer_id, 
                     message=f"Запрос на описание локации/предмета для [id{Game.load(peer_id).gm_id}|Гейм Мастера]")
    

def show_profile(peer_id, name):

    try:
        with open(f'heroes/{name}.json', 'r') as profile:
            jp = json.load(profile)
    except FileNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="Такого персонажа нет в журнале")
    else:
        profile_text = f'''Имя: {jp['nominative']}

Пол: {jp['gender']}
Ведущая рука: {jp['dominant hand']}

Статы:
1. Сила: {jp['strength']}
2. Ловкость: {jp['agility']}
3. Магия: {jp['magic']}
4. Харизма: {jp['charisma']}
5. Стойкость: {jp['endurance']}
6. Интеллект: {jp['intelligence']}
7. Восприятие: {jp['perception']}

Характеристики:
1. Удача: {jp['luck']}'''

        for j in range(0, len(profile_text), 4096):
            vk.messages.send(random_id=0, peer_id=peer_id, message=profile_text[j:j + 4096])


def reveal_ra(profile_data, name):
    vk.messages.send(random_id=0, peer_id=profile_data["RP_id"],
                     message=f'Подготовленное действие {profile_data["genitive"]}: {profile_data["ready action"]}')
    profile_data["ready action"] = ""
    with open(f'heroes/{name}.json', 'w') as json_profile:
        json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)


def clear_ra(profile_data, name):
    vk.messages.send(random_id=0, peer_id=profile_data["RP_id"],
                     message=f'Подготовленное действие {profile_data["genitive"]} было отменено')
    profile_data["ready action"] = ""
    with open(f'heroes/{name}.json', 'w') as json_profile:
        json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)


def delete_profile(profile_data, peer_id, name):
    vk.messages.send(random_id=0, peer_id=peer_id,
                     message=f'Профиль {profile_data["genitive"]} успешно удален.')
    os.remove(f'heroes/{name}.json')


def set_ra(profile_data, peer_id, name, ready_action):
    if profile_data["ready action"]:
        vk.messages.send(random_id=0, peer_id=peer_id, message="Этот персонаж уже подготовил какое-то действие")
    else:
        profile_data["ready action"] = ready_action
        vk.messages.send(random_id=0, peer_id=profile_data["RP_id"],
                         message=f'{profile_data["nominative"]} подготовил{"a" if  profile_data["gender"] == "женский" else ""} какое-то действие')
    with open(f'heroes/{name}.json', 'w') as json_profile:
        json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)
