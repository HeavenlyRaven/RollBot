import random

from bot_tools import Commander, Context

from config import vk

cmdr = Commander()


@cmdr.register(r'\[get id]')
def get_id(context: Context) -> None:
    vk.send_message(context.peer_id, f"ID этой конференции: {context.peer_id}")


@cmdr.register(r'\[choose: (?P<options>[^]]*)]')
def choose(context: Context, options: str) -> None:
    vk.send_message(context.peer_id, f"[{random.choice(options.split(',')).strip()}]")