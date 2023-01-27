from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import re
from random import choice

from session_info import vk, vk_session, GROUP_ID, ADMIN_ID
from utils import EQUIP_LIST, PROFILE_TEMPLATE, accessible_profile_data
from roll import roll
from profile_init import init
import bot_commands as bc
import turn_tools as tt

longpoll = VkBotLongPoll(vk_session, GROUP_ID)

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.message["text"]:
        peer_id = event.message['peer_id']
        text = event.message['text']
        user_id = event.message['from_id']
        try:
            if commands := re.findall(r'\[[^]]+]', text):
                for command in commands:
                    if re.match(r'\[[^]]*\btry [^]]*]', command) is not None:
                        roll(command, user_id, peer_id)
                    elif (m := re.match(r'\[end turn for ([^]]*)]', command)) is not None:
                        tt.end_turn(peer_id, name=m[1])
                    elif (m := re.match(r'\[shuffle ([^]]*)]', command)) is not None:
                        tt.shuffle_queue(peer_id, queue_name=m[1])
                    elif (m := re.match(r'\[reaction for ([^]]*)]', command)) is not None:
                        bc.notify_about_reaction(peer_id, name=m[1])
                    elif (m := re.match(r'\[set ra: ([^]]*): ([^]]*)]', command)) is not None:
                        if (profile_data := accessible_profile_data(user_id, peer_id, name=m[2])) is not None:
                            bc.set_ra(profile_data, peer_id, name=m[2], ready_action=m[1])
                    elif (m := re.match(r'\[reveal ra: ([^]]*)]', command)) is not None:
                        if (profile_data := accessible_profile_data(user_id, peer_id, name=m[1])) is not None:
                            bc.reveal_ra(profile_data, name=m[1])
                    elif (m := re.match(r'\[clear ra: ([^]]*)]', command)) is not None:
                        if (profile_data := accessible_profile_data(user_id, peer_id, name=m[1])) is not None:
                            bc.clear_ra(profile_data, name=m[1])
                    elif (m := re.match(r'\[show profile: ([^]]*)]', command)) is not None:
                        bc.show_profile(peer_id, name=m[1])
                    elif (m := re.match(r'\[delete profile: ([^]]*)]', command)) is not None:
                        if (profile_data := accessible_profile_data(user_id, peer_id, name=m[1])) is not None:
                            bc.delete_profile(profile_data, peer_id, name=m[1])
                    elif (m := re.match(r'\[choose: ([^]]*)]', command)) is not None:
                        vk.messages.send(random_id=0, peer_id=peer_id, message=f"[{choice(m[1].split(',')).strip()}]")
                    elif (m := re.match(r'\[add queue\s?([^]]*): ([^]]*)]', command)) is not None:
                        tt.add_queue(peer_id, queue_name=m[1], queue=m[2].split(', '))
                    elif (m := re.match(r'\[delete queue: ([^]]*)]', command)) is not None:
                        tt.delete_queue(peer_id, queue_name=m[1])
                    elif re.match(r'\[delete all queues]', command) is not None:
                        tt.delete_all_queues(peer_id)
                    elif (m := re.match(r'\[add ((?:(?!{\d+})[^]])*)(\s{(\d+)})?: ([^]]*)]', command)) is not None:
                        if (profile_data := accessible_profile_data(user_id, peer_id, name=m[4])) is not None:
                            bc.add_item(profile_data, peer_id, name=m[4], item=m[1], number=int(m[3]) if m[2] else 1)
                    elif (m := re.match(r'\[remove ((?:(?!{\d+})[^]])*)(\s{(\d+)})?: ([^]]*)]', command)) is not None:
                        if (profile_data := accessible_profile_data(user_id, peer_id, name=m[4])) is not None:
                            bc.remove_item(profile_data, peer_id, name=m[4], item=m[1], number=int(m[3]) if m[2] else 1)
                    elif (m := re.match(r'\[equip \('+EQUIP_LIST+r' > '+EQUIP_LIST+r'\) ((?:(?!{\d+})[^]])*)\s?({(\d+)})?\s?: ([^]]*)]', command)) is not None:
                        if (profile_data := accessible_profile_data(user_id, peer_id, name=m[6])) is not None:
                            bc.equip(profile_data, peer_id, name=m[6], item=m[3], number=int(m[5]) if m[4] else 1, first_container=m[1],
                                     second_container=m[2])
                    elif (m := re.match(r'\[learn ([^]]*): ([^]]*)]', command)) is not None:
                        if (profile_data := accessible_profile_data(user_id, peer_id, name=m[2])) is not None:
                            bc.learn(profile_data, peer_id, name=m[2], skill=m[1])
                    elif (m := re.match(r'\[unlearn ([^]]*): ([^]]*)]', command)) is not None:
                        if (profile_data := accessible_profile_data(user_id, peer_id, name=m[2])) is not None:
                            bc.unlearn(profile_data, peer_id, name=m[2], skill=m[1])
                    elif re.match(r'\[get id]', command) is not None:
                        vk.messages.send(random_id=0, peer_id=peer_id, message=f"ID этой конференции: {peer_id}")
            if (pm := re.match(r'{create profile: ([^]]*), ([^]]*)}', text)) is not None:
                if (template_match := re.fullmatch(PROFILE_TEMPLATE, text[pm.end():].strip(), flags=re.IGNORECASE)) is not None:
                    try:
                        init(user_id, peer_id, template_match, eng_name=pm[1], gen_name=pm[2])
                        vk.messages.send(random_id=0, peer_id=peer_id, message=f'Профиль {pm[2]} успешно создан.')
                    except FileExistsError:
                        vk.messages.send(random_id=0, peer_id=peer_id, message='Профиль с таким именем уже существует')
                else:
                    vk.messages.send(random_id=0, peer_id=peer_id, message='Профиль не соответствует шаблону.')
        except BaseException as error:
            vk.messages.send(random_id=0, peer_id=peer_id,
                             message="Короче, Егор, опять какой-то кринж с ботом произошёл. Отправил всю инфу в лс.")
            vk.messages.send(random_id=0, peer_id=ADMIN_ID,
                             message=f"Данные запроса:\n\n{event.raw}\n\nИнфа об ошибке:\n\n{str(error)}")
