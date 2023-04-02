import json

from bot_tools import AVK

from typing import Final

# TODO: Change to getting config variables as environment variable
with open("config.json", 'r') as config_file:
    config = json.load(config_file)

TOKEN: Final[str] = config['token']
ADMIN_ID: Final[int] = config['admin_id']
GROUP_ID: Final[int] = config['group_id']

avk = AVK(TOKEN)