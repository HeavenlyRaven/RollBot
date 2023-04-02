import logging
logging.disable()

from bot_tools import AsyncLongPollBot

from config import avk, GROUP_ID, ADMIN_ID
from game_commands import cmdr as game_commander
from hero_commands import cmdr as hero_commander
from basic_commands import cmdr as basic_commander

bot = AsyncLongPollBot(avk=avk, group_id=GROUP_ID, admin_id=ADMIN_ID)
bot.extend_commander(game_commander)
bot.extend_commander(hero_commander)
bot.extend_commander(basic_commander)


bot.polling()
