import re
from asyncio.exceptions import CancelledError
from asyncio import iscoroutine

from typing import Callable

from .commanding import Commander, Command
from .task_manager import TaskManager, Task
from .vk import VK, AVK, VkBotLongPoll, VkBotEventType, AsyncVkBotLongPoll, AsyncVkBotEventType
from .context import Context


class LongPollBot:

    vk: VK
    group_id: int
    admin_id: int
    commander: Commander

    def __init__(self, vk: VK, group_id: int, admin_id: int, commander: Commander | None = None) -> None:
        self.vk = vk
        self.group_id = group_id
        self.admin_id = admin_id
        self.commander = Commander()
        if commander is not None:
            self.extend_commander(commander)

    def extend_commander(self, commander: Commander) -> None:
        self.commander.extend(commander)

    def command(self, pattern: str) -> Callable[[Callable], Callable]:
        def decorator(function: Callable) -> Callable:
            self.commander.append(Command(pattern, function))
            return function
        return decorator
    
    def motify_admin(self, message: str) -> None:
        self.vk.send_message(peer_id=self.admin_id, text=message)
        
    def polling(self) -> None:
        for event in VkBotLongPoll(vk=self.vk.session, group_id=self.group_id).listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                context = Context(
                    peer_id=event.message['peer_id'],
                    user_id=event.message['from_id'],
                    text=event.message['text']
                )
                try:
                    for command_text in re.findall(r'\[[^]]+]', context.text):
                        for command in self.commander:
                            parsed = command.parse(command_text)
                            if parsed is not None:
                                command.execute(context=context, **parsed)
                                break
                except BaseException as error:
                    self.vk.send_message(peer_id=context.peer_id, text="Короче, Егор, опять какой-то кринж с ботом произошёл. Отправил всю инфу в лс.")
                    self.notify_admin(f"Данные запроса:\n\n{event.raw}\n\nИнфа об ошибке:\n\n{repr(error)}")


class AsyncLongPollBot:

    avk: AVK
    group_id: int
    admin_id: int
    _commander: Commander
    _manager: TaskManager

    def __init__(self, avk: AVK, vk: VK, group_id: int, admin_id: int, commander: Commander | None = None) -> None:
        self.avk = avk
        self.vk = vk
        self.group_id = group_id
        self.admin_id = admin_id
        self._commander = Commander()
        if commander is not None:
            self.extend_commander(commander)
        self._manager = TaskManager(done_callback=self._exception_handling_callback)
            
    def extend_commander(self, commander: Commander) -> None:
        self._commander.extend(commander)

    def command(self, pattern: str) -> Callable[[Callable], Callable]:
        def cmd_decorator(cmd_function: Callable) -> Callable:
            self._commander.append(Command(pattern, cmd_function))
            return cmd_function
        return cmd_decorator
    
    def notify_admin(self, message: str) -> None:
        self.vk.send_message(peer_id=self.admin_id, text=message)
    
    def _exception_handling_callback(self, task: Task) -> None:
        try:
            error = task.exception()
        except CancelledError:
            return
        if error is None:
            return
        payload = self._manager.tasks[task]
        self.notify_admin(f"Произошёл кринж.\n\nДанные:\n{payload}\n\nЗадача:\n{task.get_name()}\n\nИнфа об ошибке:\n{repr(error)}")

    async def _polling(self) -> None:
        async for event in AsyncVkBotLongPoll(api=self.avk, group_id=self.group_id).listen():
            for update in event["updates"]:
                if update["type"] != AsyncVkBotEventType.MESSAGE_NEW:
                    continue
                obj = update["object"]["message"]
                context = Context(
                    peer_id=obj['peer_id'],
                    user_id=obj['from_id'],
                    text=obj['text'],
                    manager=self._manager
                )
                for command_text in re.findall(r'\[[^]]+]', context.text):
                    for command in self._commander:
                        parsed = command.parse(command_text)
                        if parsed is not None:
                            try:
                                command_exec = command.execute(context=context, **parsed)
                            except BaseException as error:
                                self.vk.send_message(context.peer_id, "Короче, Егор, опять какой-то кринж с ботом произошёл. Отправил всю инфу в лс.")
                                self.notify_admin(f"Контекст:\n\n{context}\n\nКоманда: {command.function.__name__}\n\nИнфа об ошибке:\n\n{repr(error)}")
                                break
                            if iscoroutine(command_exec):
                                self._manager.spawn_task(coro=command_exec, payload={"context": context.light(), "coro_args": parsed})
                            break

    def polling(self) -> None:
        self._manager.run_loop(self._polling())
