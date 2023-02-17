import json
from session_info import vk


def end_turn(peer_id, name):

    with open("queues.json", "r") as shuffle_file:
        shuffle_lists = json.load(shuffle_file)

    try:
        for queue in shuffle_lists[str(peer_id)].values():
            try:
                name_index = queue.index(name)
                if name_index == len(queue)-1:
                    next_turn_character = queue[0]
                else:
                    next_turn_character = queue[name_index+1]
                try:
                    with open(f'heroes/{next_turn_character}.json', 'r') as profile:
                        profile_data = json.load(profile)
                    vk.messages.send(random_id=0, peer_id=peer_id,
                                     message=f'Ход окончен. Теперь ход [id{profile_data["player_id"]}|{profile_data["genitive"]}]')
                    return
                except FileNotFoundError:
                    vk.messages.send(random_id=0, peer_id=peer_id,
                                     message=f'Ход окончен. Теперь ход персонажа {next_turn_character}')
                    return
            except ValueError:
                continue
        vk.messages.send(random_id=0, peer_id=peer_id, message='Ход персонажа вне очереди окончен.')
    except KeyError:
        vk.messages.send(random_id=0, peer_id=peer_id, message='Ход персонажа вне очереди окончен.')
