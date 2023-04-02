import os
import re

from bot_tools import Commander, Context
from game_system import Hero, HeroDoesNotExistError, Game, GameDoesNotExistError

from config import avk
from roll import roll

# UTILITIES

def auto_stat(value: str | None) -> int:
    return int(value) if value is not None else 60

# MAIN COMMANDER

cmdr = Commander()

# COMMANDS

@cmdr.register(r'(?P<command>\[[^]]*\btry [^]]*])')
async def try_command(context: Context, command: str):
    # WARNING: LEGACY CODE
    await roll(avk, command, context.user_id, context.peer_id)


@cmdr.register(r'\[reaction for (?P<name>[^]]*)]')
async def notify_about_reaction(context: Context, name: str):
    try:
        hero = Hero.load(name)
    except HeroDoesNotExistError:
        await avk.send_message(context.peer_id, f"Запрос на реакцию для персонажа {name}")
    else:
        await avk.send_message(context.peer_id, f"Запрос на реакцию для [id{hero.player_id}|{hero.genitive}]")


@cmdr.register(r'\[show profile: (?P<name>[^]]*)]')
async def show_profile(context: Context, name: str):
    try:
        hero = Hero.load(name)
    except HeroDoesNotExistError:
        await avk.send_message(context.peer_id, "Персонажа с таким именем не существует.")
    else:
        await avk.send_message(context.peer_id, hero.profile_text)


@cmdr.register(r'\[delete profile: (?P<name>[^]]*)]')
async def delete_profile(context: Context, name: str):
    try:
        hero = Hero.load(name)
    except HeroDoesNotExistError:
        await avk.send_message(context.peer_id, "Персонажа с таким именем не существует.")
        return
    if hero.player_id != context.user_id:
        await avk.send_message(context.peer_id, "У вас нет доступа данному персонажу")
        return
    await avk.send_message(context.peer_id, f'Профиль {hero.genitive} успешно удален.')
    os.remove(f'heroes/{name}.json')


@cmdr.register(r'\[reveal ra: (?P<name>[^]]*)]')
async def reveal_ra(context: Context, name: str):
    try:
        hero = Hero.load(name)
    except HeroDoesNotExistError:
        await avk.send_message(context.peer_id, "Персонажа с таким именем не существует.")
        return
    if hero.player_id != context.user_id:
        await avk.send_message(context.peer_id, "У вас нет доступа данному персонажу")
        return
    if hero.ready_action is None:
        await avk.send_message(context.peer_id, "Этот персонаж ещё не подготовил никакого действия")
        return
    await avk.send_message(context.peer_id, f'Подготовленное действие {hero.genitive}: {hero.ready_action}')
    hero.ready_action = None
    hero.save()


@cmdr.register(r'\[reveal ra: (?P<name>[^]]*)]')
async def clear_ra(context: Context, name: str):
    try:
        hero = Hero.load(name)
    except HeroDoesNotExistError:
        await avk.send_message(context.peer_id, "Персонажа с таким именем не существует.")
        return
    if hero.player_id != context.user_id:
        await avk.send_message(context.peer_id, "У вас нет доступа данному персонажу")
        return
    await avk.send_message(context.peer_id, f'Подготовленное действие {hero.genitive} было отменено')
    hero.ready_action = None
    hero.save()


@cmdr.register(r'\[set ra: (?P<name>[^]]*): (?P<ready_action>[^]]*)]')
async def set_ra(context: Context, name: str, ready_action: str):
    try:
        hero = Hero.load(name)
    except HeroDoesNotExistError:
        await avk.send_message(context.peer_id, "Персонажа с таким именем не существует.")
        return
    if hero.player_id != context.user_id:
        await avk.send_message(context.peer_id, "У вас нет доступа данному персонажу")
        return
    if hero.ready_action is not None:
        await avk.send_message(context.peer_id, "Этот персонаж уже подготовил какое-то действие")
        return
    await avk.send_message(hero.game_chat_id, 
                           f'{hero.nominative} подготовил{"a" if hero.gender == "женский" else ""} какое-то действие')
    hero.ready_action = ready_action
    hero.save()


@cmdr.register(create_profile_pattern := r'\[create(?P<main> main)? profile(?: in (?P<game_name>[^]]*))?: (?P<hero_name>[^}]*)]')
async def create_profile(context: Context, main: bool, game_name: str | None, hero_name: str):
    command_match = re.search(create_profile_pattern, context.text)
    template_text = context.text[command_match.end():].strip()
    if (template_match := re.fullmatch(Hero.PROFILE_TEMPLATE, template_text)) is None:
        await avk.send_message(context.peer_id, 'Профиль не соответствует шаблону.')
        return
    if hero_name == "GM":
        await avk.send_message(context.peer_id, 'Имя GM зарезервировано для Гейм Мастера. Выберите, пожалуйста, другое.')
        return
    if Hero.exists(hero_name):
        await avk.send_message(context.peer_id, 'Профиль с таким именем уже существует')
        return
    try:
        game = Game.load(context.peer_id if game_name is None else game_name)
    except GameDoesNotExistError:
        await avk.send_message(context.peer_id, "Персонажа можно создать только в существующей игре")
        return
    if main:
        game.set_main(context.user_id, hero_name)
        game.save()
    hero_params = template_match.groupdict()
    dominant_hand = hero_params["dominant_hand"]
    Hero(
        player_id=context.user_id,
        nominative=hero_params["nominative"],
        genitive=hero_params["genitive"],
        gender=hero_params["gender"],
        dominant_hand="правая" if dominant_hand is None else dominant_hand,
        strength=auto_stat(hero_params["strength"]),
        agility=auto_stat(hero_params["agility"]),
        magic=auto_stat(hero_params["magic"]),
        charisma=auto_stat(hero_params["charisma"]),
        endurance=auto_stat(hero_params["endurance"]),
        intelligence=auto_stat(hero_params["intelligence"]),
        perception=auto_stat(hero_params["perception"]),
        luck=60,
        ready_action=None,
        game_chat_id=game.chat_id
    ).save()