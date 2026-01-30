from typing import Any, Protocol


class AsyncSessionP(Protocol):
    def add(self, instance: Any) -> None:
        pass

    async def flush(self) -> None:
        pass

    async def get[T](self, entity: type[T], ident: Any) -> T | None:
        pass

    async def delete(self, instance: Any) -> None:
        pass
