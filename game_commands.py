import asyncio
import os
from functools import wraps

from typing import Callable

from bot_tools import Commander, Context
from bot_tools.task_manager import TaskManager
from game_system import *

from config import avk, GROUP_ID

# UTILITIES

def game_required_in_chat(command: Callable) -> Callable:
    @wraps(command)
    async def wrapper(context: Context, **kwargs) -> None:
        if Game.exists(context.peer_id):
            command(context, **kwargs)
        else:
            await avk.send_message(peer_id=context.peer_id, text="В данной конференции нет игры.")
    return wrapper

async def update_pinned(game: Game) -> None:
    if (pinned_message := game.generate_pinned_message()) is None:
        await avk.unpin_message(game.chat_id)
    else:
        await avk.send_and_pin_message(game.chat_id, pinned_message)

async def turn_timer(task_manager: TaskManager, game_chat_id: int, hero_name: str, player_id: int, genitive_name: str):
    await asyncio.sleep(43199)
    await avk.send_message(peer_id=game_chat_id, text=f"Осталось 12 часов на написание поста за [id{player_id}|{genitive_name}]")
    await asyncio.sleep(43198)
    await avk.send_message(peer_id=game_chat_id, text=f"Soap trusted [id{player_id}|you]...")
    context = Context(peer_id=game_chat_id, user_id=GROUP_ID, text=f"[end turn for {hero_name}]", manager=task_manager)
    task_manager.spawn_task(
        coro=end_turn(context=context, name=hero_name),
        payload={"fake_context": context.light(), "coro_args": {"hero_name": hero_name}}
    )

# MAIN COMMANDER

cmdr = Commander()

# COMMANDS

@cmdr.register(r'\[add (?P<hero_name>[^]]*) to (?P<queue_name>[^]]*)]')
@game_required_in_chat
async def add_to_queue(context: Context, hero_name: str, queue_name: str) -> None:
    game = Game.load(context.peer_id)
    try:
        game.add_to_queue(queue_name, hero_name)
    except QueueNotFoundError:
        await avk.send_message(context.peer_id, f'В данной игре нет очереди с названием {queue_name}.')
        return
    await avk.send_message(context.peer_id, f'Персонаж {hero_name} был успешно добавлен в очередь {queue_name}.')
    if game.pinned_modified:
        update_pinned(game)
    game.save()


@cmdr.register(r'\[remove (?P<hero_name>[^]]*) from (?P<queue_name>[^]]*)]')
@game_required_in_chat
async def remove_from_queue(context: Context, hero_name: str, queue_name: str) -> None:
    game = Game.load(context.peer_id)
    try:
        game.remove_from_queue(queue_name, hero_name)
    except QueueNotFoundError:
        await avk.send_message(context.peer_id, f'В данной игре нет очереди с названием {queue_name}.')
        return
    except HeroNotFoundInQueueError:
        await avk.send_message(context.peer_id, f'В данной очереди нет персонажа с именем {hero_name}.')
        return
    await avk.send_message(context.peer_id, f'Персонаж {hero_name} был успешно удалён из очереди {queue_name}.')
    if game.pinned_modified:
        update_pinned(game)
    game.save()


@cmdr.register(r'\[move (?P<hero_name>[^]]*) in (?P<queue_name>[^]]*): (?P<pos>\d+)]')
@game_required_in_chat
async def move_in_queue(context: Context, hero_name: str, queue_name: str, pos: int):
    game = Game.load(context.peer_id)
    try:
        game.move_in_queue(queue_name, hero_name, int(pos))
    except QueueNotFoundError:
        await avk.send_message(context.peer_id, f'В данной игре нет очереди с названием {queue_name}.')
        return
    except HeroNotFoundInQueueError:
        await avk.send_message(context.peer_id, f'В данной очереди нет персонажа с именем {hero_name}.')
        return
    await avk.send_message(context.peer_id, f'Персонаж {hero_name} был успешно подвинут в очереди {queue_name} на возицию {pos}.')
    if game.pinned_modified:
        update_pinned(game)
    game.save()


@cmdr.register(r'\[rename (?P<old_name>[^]]*): (?P<new_name>[^]]*)]')
@game_required_in_chat
async def rename_queue(context: Context, old_name: str, new_name: str):
    game = Game.load(context.peer_id)
    try:
        game.rename_queue(old_name, new_name)
    except QueueNotFoundError:
        await avk.send_message(context.peer_id, f'В данной игре нет очереди с названием {old_name}.')
        return
    await avk.send_message(context.peer_id, f'Очередь {old_name} была успешно переименована в {new_name}.')
    if game.pinned_modified:
        update_pinned(game)
    game.save()

@cmdr.register(r'\[pin (?P<name>[^]]*)]')
@game_required_in_chat
async def pin_queue(context: Context, name: str):
    game = Game.load(context.peer_id)
    if name == "all":
        game.pin_all()
        update_pinned(game)
        game.save()
        return
    try:
        game.add_to_pinned(name)
    except QueueNotFoundError:
        await avk.send_message(context.peer_id, f'В данной игре нет очереди с названием {name}.')
        return
    update_pinned(game)
    game.save()


@cmdr.register(r'\[unpin (?P<name>[^]]*)]')
@game_required_in_chat
async def unpin_queue(context: Context, name: str):
    game = Game.load(context.peer_id)
    if name == "all":
        game.clear_pinned()
        update_pinned(game)
        game.save()
        return
    try:
        game.remove_from_pinned(name)
    except QueueNotFoundError:
        await avk.send_message(context.peer_id, f'Очередь {name} не закреплена.')
        return
    update_pinned(game)
    game.save()


@cmdr.register(r'\[show all queues]')
@game_required_in_chat
async def show_all_queues(context: Context):
    if queues_text := Game.load(context.peer_id).str_all_queues():
        await avk.send_message(context.peer_id, queues_text)
        return
    await avk.send_message(context.peer_id, "В данной игре нет ни одной очереди")


@cmdr.register(r'\[delete all queues]')
@game_required_in_chat
async def delete_all_queues(context):
    game = Game.load(context.peer_id)
    game.clear_queues()
    await avk.send_message(context.peer_id, 'Все очереди были успешно удалены.')
    update_pinned(game)
    game.save()


@cmdr.register(r'\[end turn(?: for (?P<name>[^]]*))?]')
@game_required_in_chat
async def end_turn(context: Context, name: str | None):
    game = Game.load(context.peer_id)
    hero_name = game.get_main(context.user_id) if name is None else name
    if hero_name is None:
        await avk.send_message(context.peer_id, "В данной игре у вас нет основного персонажа.")
        return
    try:
        next_turn_hero_name = game.next_in_queue(hero_name)
    except HeroNotFoundInQueuesError:
        await avk.send_message(context.peer_id, "В данной игре персонажа с таким именем нет ни в одной очереди.")
        return
    manager = context.manager
    for task in manager.tasks:
        if task.get_name() == "turn_timer":
            payload = manager.tasks[task]
            if payload["game_chat_id"] == context.peer_id and payload["hero_name"] == hero_name:
                task.cancel()
                break
    try:
        next_turn_hero = Hero.load(next_turn_hero_name)
        player_id = next_turn_hero.player_id
        genitive_name = next_turn_hero.genitive
    except HeroDoesNotExistError:
        if next_turn_hero == "GM":
            player_id = game.gm_id
            genitive_name = "Гейм Мастера"
        else:
            await avk.send_message(context.peer_id, f'Ход окончен. Теперь ход персонажа {next_turn_hero}')
            return
    await avk.send_message(context.peer_id, f'Ход окончен. Теперь ход [id{player_id}|{genitive_name}]')
    manager.spawn_task(coro=turn_timer(context.peer_id, next_turn_hero_name, player_id, genitive_name), 
                       payload={"game_chat_id": context.peer_id, "hero_name": next_turn_hero_name})
    

@cmdr.register(r'\[add queue(?: (?P<name>[^]]*))?: (?P<queue>[^]]*)]')
@game_required_in_chat
async def add_queue(context: Context, name: str, queue: str):
    queue_list = queue.split(", ")
    game = Game.load(context.peer_id)
    try:
        final_name = game.add_queue(queue_list, name=name)
    except QueueAlreadyExistsError:
        await avk.send_message(context.peer_id, f'Очередь с названием {name} уже существует.')
        return
    await avk.send_message(context.peer_id, f'Очередь {final_name} была успешно добавлена в игру.')
    game.save()


@cmdr.register(r'\[delete queue: (?P<name>[^]]*)]')
@game_required_in_chat
async def delete_queue(context: Context, name: str):
    game = Game.load(context.peer_id)
    try:
        game.delete_queue(name)
    except QueueNotFoundError:
        await avk.send_message(context.peer_id, f'В данной игре нет очереди с названием {name}.')
        return
    await avk.send_message(context.peer_id, f'Очередь {name} была успешно удалена.')
    if game.pinned_modified:
        update_pinned(game)
    game.save()


@cmdr.register(r'\[edit (?P<name>[^]]*): (?P<queue>[^]]*)]')
@game_required_in_chat
async def edit_queue(context: Context, name: str, queue: str):
    queue_list = queue.split(", ")
    game = Game.load(context.peer_id)
    try:
        game.edit_queue(name, queue_list)
    except QueueNotFoundError:
        await avk.send_message(context.peer_id, f'В данной игре нет очереди с названием {name}.')
        return
    await avk.send_message(context.peer_id, f'Очередь {name} была успешно отредактирована.')
    if game.pinned_modified:
        update_pinned(game)
    game.save()


@cmdr.register(r'\[shuffle (?P<name>[^]]*)]')
@game_required_in_chat
async def shuffle_queue(context: Context, name: str):
    game = Game.load(context.peer_id)
    if name == "all":
        for queue_name in game.queues_list:
            game.shuffle_queue(queue_name)
        update_pinned(game)
        game.save()
        return
    try:
        game.shuffle_queue(name)
    except QueueNotFoundError:
        await avk.send_message(context.peer_id, f'В данной игре нет очереди с названием {name}.')
        return
    if game.pinned_modified:
        update_pinned(game)
    game.save()


@cmdr.register(r'\[requesdt result]')
@game_required_in_chat
async def request_result(context: Context):
    await avk.send_message(context.peer_id, f"Запрос на описание результата действия для [id{Game.load(context.peer_id).gm_id}|Гейм Мастера]")


@cmdr.register(r'\[request description]')
@game_required_in_chat
async def request_description(context: Context):
    await avk.send_message(context.peer_id, f"Запрос на описание локации/предмета для [id{Game.load(context.peer_id).gm_id}|Гейм Мастера]")


@cmdr.register(r'\[create game: (?P<name>[^]]*)]')
async def create_game(context: Context, name: str):
    if Game.exists(context.peer_id):
        await avk.send_message(context.peer_id, "В данной конференции уже есть игра.")
        return
    elif Game.exists(name):
        await avk.send_message(context.peer_id, "Игра с таким названием уже существует.")
        return
    Game(name=name, chat_id=context.peer_id, gm_id=context.user_id).save()
    os.symlink(f"{name}.json", f"games/{context.peer_id}.json")
    await avk.send_message(context.peer_id, f"Игра с названием {name} была успешно создана в текущей конференции.")


@cmdr.register(r'\[delete game: (?P<name>[^]]*)]')
async def delete_game(context: Context, name: str):
    try:
        game = Game.load(name)
    except GameDoesNotExistError:
        await avk.send_message(context.peer_id, "Игры с таким названием не существует.")
        return
    if game.gm_id != context.user_id:
        await avk.send_message(context.peer_id, "У вас нет права доступа. Только ГМ может удалить игру.")
        return
    await avk.send_message(context.peer_id, "Игра с названием {name} была успешно удалена.")
    os.remove(f"games/{name}.json")
    os.remove(f"games/{game.chat_id}.json")


@cmdr.register(r'\[make main in (?P<game_name>[^]]*): (?P<hero_name>[^]]*)]')
async def make_main(context: Context, game_name: str, hero_name: str):
    try:
        game = Game.load(game_name)
    except GameDoesNotExistError:
        await avk.send_message(context.peer_id, "Игры с таким названием не существует.")
        return
    try:
        hero = Hero.load(hero_name)
    except HeroDoesNotExistError:
        await avk.send_message(context.peer_id, "Персонажа с таким именем не существует.")
        return
    if hero.player_id != context.user_id:
        await avk.send_message(context.peer_id, "У вас нет доступа данному персонажу")
        return
    game.set_main(context.user_id, hero_name)
    await avk.send_message(context.peer_id, f"Теперь вашим главным персонажем в {game_name} является {hero.nominative}")
    game.save()
