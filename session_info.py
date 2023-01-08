import vk_api

with open("token.txt", 'r') as file:
    token = file.read()
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
