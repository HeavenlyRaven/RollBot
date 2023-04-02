import random

from bot_tools import Commander, Context

from config import avk

cmdr = Commander()


@cmdr.register(r'\[get id]')
async def get_id(context: Context) -> None:
    await avk.send_message(context.peer_id, f"ID этой конференции: {context.peer_id}")


@cmdr.register(r'\[choose: (?P<options>[^]]*)]')
async def choose(context: Context, options: str) -> None:
    await avk.send_message(context.peer_id, f"[{random.choice(options.split(',')).strip()}]")