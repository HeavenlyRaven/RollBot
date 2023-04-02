from asyncio.base_events import BaseEventLoop
from asyncio import Task, new_event_loop

from typing import Coroutine, Any, Callable


class TaskManager:

    _loop: BaseEventLoop
    tasks: dict[Task, Any]
    _done_callback: Callable[[Task], Any] | None
    
    def __init__(self, done_callback: Callable[[Task], Any] | None = None) -> None:
        self._loop = new_event_loop()
        self.tasks = {}
        self._done_callback = done_callback

    def spawn_task(self, coro: Coroutine, payload: Any = None) -> Task:
        task = self._loop.create_task(coro=coro, name=coro.__name__)
        self.tasks[task] = payload
        if self._done_callback is not None:
            task.add_done_callback(self._done_callback)
        task.add_done_callback(self.tasks.pop)
        return task

    def run_loop(self, coro: Coroutine) -> None:
        self._loop.run_until_complete(coro)

    def __repr__(self) -> str:
        return f"Manager with tasks:\n"+ "\n".join(f"<name={task.get_name()}, payload={self.tasks[task]}>" for task in self.tasks)
