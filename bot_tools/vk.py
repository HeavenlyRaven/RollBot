from vk_api.vk_api import VkApi, VkApiMethod
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from vkbottle.api import API
from vkbottle.polling import BotPolling as AsyncVkBotLongPoll
from vkbottle_types.events import GroupEventType as AsyncVkBotEventType


class VK:

    session: VkApi
    api: VkApiMethod

    def __init__(self, token: str) -> None:
        self.session = VkApi(token=token)
        self.api = self.session.get_api()

    def send_message(self, peer_id: int, text: str) -> int:
        return self.api.messages.send(random_id=0, peer_id=peer_id, message=text)

    def pin_message(self, peer_id: int, message_id: int):
        return self.api.messages.pin(peer_id=peer_id, message_id=message_id)
    
    def unpin_message(self, peer_id: int) -> int:
        return self.api.messages.unpin(peer_id=peer_id)

    def send_and_pin_message(self, peer_id: int, text: str):
        return self.pin_message(peer_id=peer_id, message_id=self.send_message(peer_id=peer_id, text=text))


class AVK(API):

    async def send_message(self, peer_id: int, text: str) -> int:
        return await self.messages.send(random_id=0, peer_id=peer_id, message=text)
    
    async def pin_message(self, peer_id: int, message_id: int):
        return await self.messages.pin(peer_id=peer_id, message_id=message_id)
    
    async def unpin_message(self, peer_id: int) -> int:
        return await self.messages.unpin(peer_id=peer_id)
    
    async def send_and_pin_message(self, peer_id: int, text: str):
        return await self.pin_message(peer_id=peer_id, message_id=await self.send_message(peer_id=peer_id, text=text))
    
    async def delete_message(self, peer_id: int, message_id: int):
        return await self.messages.delete(peer_id=peer_id, message_ids=[message_id], delete_for_all=True)
    
    async def send_and_delete_message(self, peer_id: int, text: str):
        return await self.delete_message(peer_id=peer_id, message_id=await self.send_message(peer_id=peer_id, text=text))
