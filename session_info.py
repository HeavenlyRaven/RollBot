import vk_api
import json

with open("config.json", 'r') as config_file:
    config = json.load(config_file)

TOKEN = config['token']
ADMIN_ID = config['admin_id']
GROUP_ID = config['group_id']

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
