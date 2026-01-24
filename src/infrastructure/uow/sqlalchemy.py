from types import TracebackType
from typing import Callable, Self, cast

from sqlalchemy.ext.asyncio import AsyncSession

from application.ports.uow import AbstractUnitOfWork


class SqlAlchemyUoW(AbstractUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        if exc_type:
            await self.rollback()
        await cast(AsyncSession, self.session).close()

    async def commit(self) -> None:
        await cast(AsyncSession, self.session).commit()

    async def rollback(self) -> None:
        await cast(AsyncSession, self.session).rollback()
