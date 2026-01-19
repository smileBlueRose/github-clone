from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from application.ports.command import BaseCommand

C = TypeVar("C", bound=BaseCommand)


class AbstractUseCase(ABC, Generic[C]):
    @abstractmethod
    async def execute(self, command: C) -> Any:
        pass
