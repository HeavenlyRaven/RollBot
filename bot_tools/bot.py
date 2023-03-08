import vk_api
import json
import re

class Command:

    def __init__(self, pattern, function):
        self.pattern = re.compile(pattern)
        self.function = function

    def parse(self, string):
        match = self.pattern.fullmatch(string)
        return match if match is None else match.groups()
    
    def __call__(self, context, *args, **kwargs):
        return self.function(context, *args, **kwargs)

class Context:

    def __init__(self, peer_id, user_id, text):
        self.peer_id = peer_id
        self.user_id = user_id
        self.text = text

class Bot:

    def __init___(self, token, group_id, admin_id):
        self.group_id = group_id
        self.admin_id = admin_id
        self.__session = vk_api.VkApi(token=token)
        self.__api = self.__session.get_api()
        self.__cmds = []

    @classmethod
    def from_config(cls, config):
        with open(config, "r") as config_file:
            return cls(**json.load(config_file))

    def send_message(self, peer_id, text):
        return self.__api.messages.send(random_id=0, peer_id=peer_id, message=text)
    
    def pin_message(self, peer_id, message_id):
        return self.__api.messages.pin(peer_id=peer_id, message_id=message_id)
    
    def command(self, pattern):
        def decorator(function):
            self.__cmds.append(Command(pattern, function))
            return function
        return decorator

    def polling(self):
        for event in vk_api.VkBotLongPoll(self.__session, self.group_id).listen():
            if event.type == vk_api.VkBotEventType.MESSAGE_NEW:
                context = Context(
                    text=event.message['text'],
                    peer_id=event.message['peer_id'],
                    user_id=event.message['from_id']
                )
                for match in re.finditer(r"\[([^])]", context.text):
                    for command in self.__cmds:
                        if (args := command.parse(match[1])) is None:
                            continue
                        else:
                            command(context, *args)
                            break
