from dependency_injector import containers, providers

from infrastructure.database.db_helper import db_helper
from infrastructure.uow.sqlalchemy import SqlAlchemyUoW


class DatabaseContainer(containers.DeclarativeContainer):
    session_factory = providers.Callable(lambda: db_helper.async_sessionmaker)
    uow = providers.Factory(
        SqlAlchemyUoW,
        session_factory=session_factory,
    )
