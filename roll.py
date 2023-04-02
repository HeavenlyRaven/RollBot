from random import randint
import re

from game_system import Hero, HeroDoesNotExistError


async def roll(avk, toss, user_id, peer_id):
    profile_player = False
    std_stat = True
    sval = re.search(r'\(\d+\)', toss)
    if sval is not None:
        toss = re.sub(r'\(\d+\)', '', toss)
    sdiff = re.search(r'{(?:\d+|r)}', toss, flags=re.IGNORECASE)
    if sdiff is not None:
        toss = re.sub(r'{(?:\d+|r)}', '', toss, flags=re.IGNORECASE)
        diff = sdiff[0].lower()
        if diff == '{r}':
            diff_val = randint(3, 220)
        else:
            diff_val = int(diff[1:-1])
    else:
        diff_val = 120
    inp = namestat(toss, char_flag=True).strip()
    inp_char = inp.lower()
    if inp_char == 'strength':
        char = ' на силу'
    elif inp_char == 'perception':
        char = ' на восприятие'
    elif inp_char == 'endurance':
        char = ' на стойкость'
    elif inp_char == 'charisma':
        char = ' на харизму'
    elif inp_char == 'intelligence':
        char = ' на интеллект'
    elif inp_char == 'agility':
        char = ' на ловкость'
    elif inp_char == 'luck':
        char = ' на удачу'
    elif inp_char == 'magic':
        char = ' на магию'
    else:
        std_stat = False
        char = f': {inp}'
    if re.search(r'\b[Ff][Oo][Rr]\s[^\]]*\]', toss) is not None:
        playername = namestat(toss).strip()
        try:
            hero = Hero.load(playername)
        except HeroDoesNotExistError:
            name = f'персонажа {playername}'
        else:
            name = hero.genitive
            profile_player = True
    elif user_id > 0:
        info = (await avk.users.get(user_ids=[user_id], name_case="gen"))[0]
        name = info.first_name+' '+info.last_name
    else:
        name = "бота какого-то"
    rn = randint(1, 120)
    if sval is not None:
        val = int(sval[0][1:-1])
    elif std_stat and profile_player:
        val = hero.__getattribute__(inp_char)
    else:
        val = 60
    if val == 0:
        t = 'ПОЛНЫЙ ПРОВАЛ, ВАМ НЕ СТОИЛО ДАЖЕ ПЫТАТЬСЯ.\n'
    elif rn + val >= diff_val:
        if rn == 120:
            t = 'ГРАНДИОЗНЫЙ УСПЕХ! ВЫ ПОДОБНЫ БОГАМ! ВАМ ЗАВИДУЕТ ДАЖЕ РИХТЕР!\n'
        elif rn > 115:
            t = 'НЕВЕРОЯТНЫЙ УСПЕХ! ВЫ СЕГОДНЯ ЯВНО В УДАРЕ!\n'
        else:
            t = 'УСПЕХ.\n'
    elif rn == 1:
        t = 'ГРАНДИОЗНЫЙ ПРОВАЛ. ЗЕМЛЯ ВАМ ПУХОМ.\n'
    elif rn < 6:
        t = 'КРИТИЧЕСКИЙ ПРОВАЛ.\n'
    else:
        t = 'ПРОВАЛ.\n'
    await avk.send_message(peer_id, f'Проверка с d120 для {name}{char} со значением {val} (сложность: {diff_val}): {rn}. {t}')


def namestat(inp, char_flag=False):
    if char_flag:
        first = r'\b[Tt][Rr][Yy]\b[^\]]*\]'
        second = r'\s[Ff][Oo][Rr]\s[^\]]*\]'
    else:
        first = r'\b[Ff][Oo][Rr]\b[^\]]*\]'
        second = r'\s[Tt][Rr][Yy]\s[^\]]*\]'
    res = re.search(first, inp)[0]
    if re.search(second, res) is not None:
        inp = re.sub(second, '', res)[4:]
    else:
        inp = res[4:-1]
    return inp
