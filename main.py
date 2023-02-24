from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import re
from random import choice

from session_info import vk, vk_session, GROUP_ID, ADMIN_ID
from utils import PROFILE_TEMPLATE, accessible_profile_data, Context
from roll import roll
from profile_init import init
import bot_commands as bc

longpoll = VkBotLongPoll(vk_session, GROUP_ID)

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        context = Context(
            text=event.message['text'],
            peer_id=event.message['peer_id'],
            user_id=event.message['from_id']
        )
        try:
            for command in re.findall(r'\[[^]]+]', context.text):
                if re.match(r'\[[^]]*\btry [^]]*]', command) is not None:
                    roll(command, context.user_id, context.peer_id)
                elif (m := re.match(r'\[end turn(?: for ([^]]*))?]', command)) is not None:
                    bc.end_turn(context, name=m[1])
                elif (m := re.match(r'\[shuffle ([^]]*)]', command)) is not None:
                    bc.shuffle_queue(context, name=m[1])
                elif (m := re.match(r'\[pin ([^]]*)]', command)) is not None:
                    bc.pin_queue(context, name=m[1])
                elif (m := re.match(r'\[unpin ([^]]*)]', command)) is not None:
                    bc.unpin_queue(context, name=m[1])
                elif (m := re.match(r'\[reaction for ([^]]*)]', command)) is not None:
                    bc.notify_about_reaction(context, name=m[1])
                elif re.match(r'\[request result]', command) is not None:
                    bc.request_result(context)
                elif re.match(r'\[request description]', command) is not None:
                    bc.request_description(context)
                elif (m := re.match(r'\[set ra: ([^]]*): ([^]]*)]', command)) is not None:
                    if (profile_data := accessible_profile_data(context.user_id, context.peer_id, name=m[2])) is not None:
                        bc.set_ra(profile_data, context.peer_id, name=m[2], ready_action=m[1])
                elif (m := re.match(r'\[reveal ra: ([^]]*)]', command)) is not None:
                    if (profile_data := accessible_profile_data(context.user_id, context.peer_id, name=m[1])) is not None:
                        bc.reveal_ra(profile_data, name=m[1])
                elif (m := re.match(r'\[clear ra: ([^]]*)]', command)) is not None:
                    if (profile_data := accessible_profile_data(context.user_id, context.peer_id, name=m[1])) is not None:
                        bc.clear_ra(profile_data, name=m[1])
                elif (m := re.match(r'\[show profile: ([^]]*)]', command)) is not None:
                    bc.show_profile(context, name=m[1])
                elif (m := re.match(r'\[delete profile: ([^]]*)]', command)) is not None:
                    if (profile_data := accessible_profile_data(context.user_id, context.peer_id, name=m[1])) is not None:
                        bc.delete_profile(profile_data, context.peer_id, name=m[1])
                elif (m := re.match(r'\[choose: ([^]]*)]', command)) is not None:
                    vk.messages.send(random_id=0, peer_id=context.peer_id, message=f"[{choice(m[1].split(',')).strip()}]")
                elif (m := re.match(r'\[add queue(?: ([^]]*))?: ([^]]*)]', command)) is not None:
                    bc.add_queue(context, queue_name=m[1], queue=m[2].split(', '))
                elif (m := re.match(r'\[delete queue: ([^]]*)]', command)) is not None:
                    bc.delete_queue(context, queue_name=m[1])
                elif (m := re.match(r'\[edit ([^]]*): ([^]]*)]', command)) is not None:
                    bc.edit_queue(context, queue_name=m[1], new_queue=m[2].split(', '))
                elif (m := re.match(r'\[rename ([^]]*): ([^]]*)]', command)) is not None:
                    bc.rename_queue(context, name=m[1], new_name=m[2])
                elif (m := re.match(r'\[add ([^]]*) to ([^]]*)]', command)) is not None:
                    bc.add_to_queue(context, hero_name=m[1], queue_name=m[2])
                elif (m := re.match(r'\[remove ([^]]*) from ([^]]*)]', command)) is not None:
                    bc.remove_from_queue(context, hero_name=m[1], queue_name=m[2])
                elif (m := re.match(r'\[move ([^]]*) in ([^]]*): (\d+)]', command)) is not None:
                    bc.move_in_queue(context, hero_name=m[1], queue_name=m[2], pos=m[3])
                elif re.match(r'\[delete all queues]', command) is not None:
                    bc.delete_all_queues(context)
                elif re.match(r'\[show all queues]', command) is not None:
                    bc.show_all_queues(context)
                elif re.match(r'\[get id]', command) is not None:
                    vk.messages.send(random_id=0, peer_id=context.peer_id, message=f"ID этой конференции: {context.peer_id}")
                elif (m := re.match(r'\[create game: ([^]]*)]', command)) is not None:
                    bc.create_game(context, name=m[1])
                elif (m := re.match(r'\[delete game: ([^]]*)]', command)) is not None:
                    bc.delete_game(context, name=m[1])
                elif (m := re.match(r'\[make main in ([^]]*): ([^]]*)]', command)) is not None:
                    if (profile_data := accessible_profile_data(context.user_id, context.peer_id, name=m[2])) is not None:
                        bc.make_main(profile_data, context.peer_id, context.user_id, game_name=m[1], hero_name=m[2])
            if (pm := re.match(r'{create( main)? profile(?: in ([^}]*))?: ([^}]*), ([^}]*)}', context.text)) is not None:
                if (template_match := re.fullmatch(PROFILE_TEMPLATE, context.text[pm.end():].strip(), flags=re.IGNORECASE)) is None:
                    vk.messages.send(random_id=0, peer_id=context.peer_id, message='Профиль не соответствует шаблону.')
                else:
                    init(context.peer_id, context.user_id, template_match, eng_name=pm[3], gen_name=pm[4], game_name=pm[2], main=False if pm[1] is None else True)
        except BaseException as error:
            vk.messages.send(random_id=0, peer_id=context.peer_id,
                             message="Короче, Егор, опять какой-то кринж с ботом произошёл. Отправил всю инфу в лс.")
            vk.messages.send(random_id=0, peer_id=ADMIN_ID,
                             message=f"Данные запроса:\n\n{event.raw}\n\nИнфа об ошибке:\n\n{str(error)}")
