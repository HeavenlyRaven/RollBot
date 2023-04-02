from typing import NamedTuple

from .task_manager import TaskManager

class Context(NamedTuple):
    peer_id: int
    user_id: int
    text: str
    manager: TaskManager | None = None

    def light(self) -> dict[str, int | str]:
        """Returns a dict out of context without loop wrapper"""
        return {
            "peer_id": self.peer_id,
            "user_id": self.user_id,
            "text": self.text
        }
