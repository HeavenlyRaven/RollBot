import json
import os

from session_info import vk
from game import *


def end_turn(peer_id, user_id, name):
    try:
        game = Game.load(peer_id)
    except GameDoesNotExistError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной конференции нет игры.")
        return
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


def add_queue(peer_id, queue_name, queue):
    try:
        game = Game.load(peer_id)
    except GameDoesNotExistError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной конференции нет игры.")
    else:
        final_name = game.add_queue(queue, name=queue_name)
        vk.messages.send(random_id=0, peer_id=peer_id, message=f'Очередь {final_name} была успешно добавлена в игру.')
        game.display_queue(final_name, pin=True)
        game.save()


def delete_queue(peer_id, queue_name):
    try:
        game = Game.load(peer_id)
    except GameDoesNotExistError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной конференции нет игры.")
    else:
        try:
            game.delete_queue(queue_name)
        except QueueNotFoundError:
            vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {queue_name}.')
        else:
            vk.messages.send(random_id=0, peer_id=peer_id, message=f'Очередь {queue_name} была успешно удалена.')
            game.save()
                 

def delete_all_queues(peer_id):
    try:
        game = Game.load(peer_id)
    except GameDoesNotExistError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной конференции нет игры.")
    else:
        game.queues.clear()
        vk.messages.send(random_id=0, peer_id=peer_id, message='Все очереди были успешно удалены.')
        game.save()


def shuffle_queue(peer_id, queue_name):
    try:
        game = Game.load(peer_id)
    except GameDoesNotExistError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной конференции нет игры.")
    else:
        try:
            game.shuffle_queue(queue_name)
        except QueueNotFoundError:
            vk.messages.send(random_id=0, peer_id=peer_id, message=f'В данной игре нет очереди с названием {queue_name}.')
        else:
            game.display_queue(queue_name, pin=True)
            game.save()


def create_game(peer_id, user_id, name):
    if Game.exists(peer_id):
        vk.messages.send(random_id=0, peer_id=peer_id, message="В данной конференции уже есть игра.")
    elif Game.exists(name):
        vk.messages.send(random_id=0, peer_id=peer_id, message="Игра с таким названием уже существует.")
    else:
        Game(name=name, chat_id=peer_id, gm_id=user_id).save()
        os.symlink(f"games/{name}.json", f"games/{peer_id}.json")
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
            os.remove(f"games/{name}.json")
            os.remove(f"games/{game.chat_id}.json")


def make_main(profile_data, peer_id, user_id, game_name, hero_name):
    try:
        game = Game.load(game_name)
    except GameDoesNotExistError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="Игры с таким названием не существует.")
    else:
        game.players[user_id] = hero_name
        vk.messages.send(random_id=0, peer_id=peer_id, messgae=f"Теперь вашим главным персонажем в {game_name} является {profile_data['nominative']}")
        game.save()


def notify_about_reaction(peer_id, name):
    try:
        with open(f'heroes/{name}.json', 'r') as profile:
            profile_data = json.load(profile)
        vk.messages.send(random_id=0, peer_id=peer_id, message=f"Запрос на реакцию для [id{profile_data['player_id']}|{profile_data['genitive']}]")
    except FileNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message=f"Запрос на реакцию для персонажа {name}")


def show_profile(peer_id, name):

    def items_edit(items):
        item_list = []
        for item, number in items.items():
            if number == 1:
                n = ''
            else:
                n = f' [{number}]'
            item_list.append(f'{item}{n}')
        return '; '.join(item_list)

    try:
        with open(f'heroes/{name}.json', 'r') as profile:
            jp = json.load(profile)

        skills = '\n'.join(jp['skills'])
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

Атрибуты:
1. Здоровье: {jp['health']}
2. Выносливость: {jp['stamina']}
3. Мана: {jp['mana']}

Характеристики:
1. Удача: {jp['luck']}

Снаряжение:
Правая рука: {jp['right hand'][0] if jp['right hand'] else ''}
Левая рука: {jp['left hand'][0] if jp['left hand'] else ''}
Пояс: {items_edit(jp['waist'])}
Одежда/доспехи: {'; '.join(jp['clothes'])}

Скиллы:
{skills}

Инвентарь: {items_edit(jp['inventory'])}'''

        for j in range(0, len(profile_text), 4096):
            vk.messages.send(random_id=0, peer_id=peer_id, message=profile_text[j:j + 4096])
    except FileNotFoundError:
        vk.messages.send(random_id=0, peer_id=peer_id, message="Такого персонажа нет в журнале")


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


def learn(profile_data, peer_id, name, skill):
    if skill in profile_data['skills']:
        vk.messages.send(random_id=0, peer_id=peer_id,
                         message=f'{profile_data["nominative"]} уже владеет скиллом "{skill}".')
    else:
        profile_data['skills'].append(skill)
        vk.messages.send(random_id=0, peer_id=peer_id,
                         message=f'{profile_data["nominative"]} изучает новый скилл: {skill}!')
        with open(f'heroes/{name}.json', 'w') as json_profile:
            json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)


def unlearn(profile_data, peer_id, name, skill):
    if skill not in profile_data['skills']:
        vk.messages.send(random_id=0, peer_id=peer_id,
                         message=f'{profile_data["nominative"]} не владеет скиллом "{skill}".')
    else:
        profile_data['skills'].remove(skill)
        vk.messages.send(random_id=0, peer_id=peer_id,
                         message=f'{profile_data["nominative"]} больше не может использовать скилл "{skill}"')
        with open(f'heroes/{name}.json', 'w') as json_profile:
            json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)


def equip(profile_data, peer_id, name, item, number, first_container, second_container):

    def inner_equip(first_container, second_container, item, number, profile_data, name, peer_id):
        if second_container in ('left hand', 'right hand'):
            if second_container == 'left hand':
                hand = 'левую'
            else:
                hand = 'правую'
            if profile_data[second_container]:
                if first_container in ('left hand', 'right hand', 'clothes'):
                    profile_data[first_container].append(profile_data[second_container][0])
                elif profile_data[second_container][0] in profile_data[first_container]:
                    profile_data[first_container][profile_data[second_container][0]] += 1
                else:
                    profile_data[first_container].update({profile_data[second_container][0]: 1})
                profile_data[second_container][0] = item
            else:
                profile_data[second_container].append(item)
            vk.messages.send(random_id=0, peer_id=peer_id,
                             message=f'{profile_data["nominative"]} берет в {hand} руку: {item}')
            with open(f'heroes/{name}.json', 'w') as json_profile:
                json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)
        elif second_container == 'clothes':
            if len(profile_data['clothes']) < 24:
                if item not in profile_data['clothes']:
                    profile_data['clothes'].append(item)
                    vk.messages.send(random_id=0, peer_id=peer_id,
                                     message=f'{profile_data["nominative"]} надевает: {item}')
                    with open(f'heroes/{name}.json', 'w') as json_profile:
                        json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)
                else:
                    vk.messages.send(random_id=0, peer_id=peer_id,
                                     message=f'{profile_data["nominative"]} уже носит на себе: {item}')
            else:
                vk.messages.send(random_id=0, peer_id=peer_id,
                                 message='Вы не можете носить на себе более 24 различных предметов одежды.')
        elif second_container == 'waist':
            if item in profile_data['waist']:
                profile_data['waist'][item] += number
                vk.messages.send(random_id=0, peer_id=peer_id,
                                 message=f'{profile_data["nominative"]} вешает на пояс: {item} [{number}].')
                with open(f'heroes/{name}.json', 'w') as json_profile:
                    json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)
            elif len(profile_data['waist']) < 12:
                profile_data['waist'].update({item: number})
                vk.messages.send(random_id=0, peer_id=peer_id,
                                 message=f'{profile_data["nominative"]} вешает на пояс: {item} [{number}].')
                with open(f'heroes/{name}.json', 'w') as json_profile:
                    json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)
            else:
                vk.messages.send(random_id=0, peer_id=peer_id,
                                 message='Вы не можете носить на поясе более 12 различных предметов!')
        else:
            add_item(profile_data, peer_id, name, item, number, equip_flag=True)

    if first_container != second_container:
        if item in profile_data[first_container]:
            if first_container in ('left hand', 'right hand', 'clothes'):
                profile_data[first_container].remove(item)
                inner_equip(first_container, second_container, item, number, profile_data, name, peer_id)
            else:
                if number <= profile_data[first_container][item]:
                    if number < profile_data[first_container][item]:
                        profile_data[first_container][item] -= number
                    elif number == profile_data[first_container][item]:
                        profile_data[first_container].pop(item)
                    inner_equip(first_container, second_container, item, number, profile_data, name, peer_id)
                else:
                    vk.messages.send(random_id=0, peer_id=peer_id,
                                     message=f'У {profile_data["genitive"]} недостаточно экземпляров указанного предмета.')
        else:
            vk.messages.send(random_id=0, peer_id=peer_id,
                             message=f'Указанного предмета нет в данном списке снаряжения {profile_data["genitive"]}.')
    else:
        vk.messages.send(random_id=0, peer_id=peer_id, message='Это действие не дало никакого эффекта.')


def add_item(profile_data, peer_id, name, item, number, equip_flag=False):
    if item in profile_data['inventory']:
        profile_data['inventory'][item] += number
    else:
        profile_data['inventory'].update({item: number})
    if equip_flag:
        add_message = f'{profile_data["nominative"]} убирает в инвентарь: {item} [{number}].'
    else:
        add_message = f'Добавлено в инвентарь {profile_data["genitive"]}: {item} [{number}]'
    vk.messages.send(random_id=0, peer_id=peer_id, message=add_message)
    with open(f'heroes/{name}.json', 'w') as json_profile:
        json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)


def remove_item(profile_data, peer_id, name, item, number):
    if item in profile_data['inventory'] or item in profile_data['waist']:
        if item in profile_data['inventory']:
            slot = 'inventory'
        else:
            slot = 'waist'
        if number <= profile_data[slot][item]:
            if number < profile_data[slot][item]:
                profile_data[slot][item] -= number
            elif number == profile_data[slot][item]:
                profile_data[slot].pop(item)
            vk.messages.send(random_id=0, peer_id=peer_id,
                             message=f'Убрано {"из инвентаря" if slot == "inventory" else "с пояса"} {profile_data["genitive"]}: {item} [{number}]')
            with open(f'heroes/{name}.json', 'w') as json_profile:
                json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)
        else:
            vk.messages.send(random_id=0, peer_id=peer_id,
                             message=f'У {profile_data["genitive"]} недостаточно экземпляров указанного предмета.')
    elif item in profile_data['right hand'] or item in profile_data['left hand'] or item in profile_data['clothes']:
        if number > 1:
            vk.messages.send(random_id=0, peer_id=peer_id, message='В этом слоте не может быть повторяющихся предметов')
        else:
            if item in profile_data['right hand']:
                slot = 'right hand'
            elif item in profile_data['left hand']:
                slot = 'left hand'
            else:
                slot = 'clothes'
            profile_data[slot].remove(item)
            vk.messages.send(random_id=0, peer_id=peer_id,
                             message=f'{profile_data["nominative"]}{" снимает с себя и" if slot == "clothes" else ""} выбрасывает: {item}')
            with open(f'heroes/{name}.json', 'w') as json_profile:
                json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)
    else:
        vk.messages.send(random_id=0, peer_id=peer_id,
                         message=f'Указанного предмета нет ни в одном из слотов снаряжения {profile_data["genitive"]}.')
