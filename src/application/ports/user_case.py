from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from application.ports.command import BaseCommand
from typing import Any

C = TypeVar("C", bound=BaseCommand)


class AbstractUseCase(ABC, Generic[C]):
    @abstractmethod
    async def execute(self, command: C) -> Any:
        pass
