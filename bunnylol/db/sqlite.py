# async adaptor for sqlite, not really async
import sqlalchemy as sa
from sqlalchemy.engine import Engine, Connection


class aiter:
    def __init__(self, iterable):
        self.iterable = iterable

    def __aiter__(self):
        self.iterable = iter(self.iterable)
        return self

    async def __anext__(self):
        try:
            return next(self.iterable)
        except StopIteration:
            raise StopAsyncIteration


class AioEngine(Engine):
    def connect(self, **kwargs):
        connection = super().connect(**kwargs)
        connection.__class__ = AioConnection
        return connection

    async def close(self):
        return super().dispose()

    async def __aenter__(self):
        return super().__enter__()

    async def __aexit__(self, exc_type, exc, traceback):
        return super().__exit__(exc_type, exc, traceback)


class AioConnection(Connection):
    async def execute(self, *args, **kwargs):
        result = super().execute(*args, **kwargs)
        return aiter(result)

    async def __aenter__(self):
        return super().__enter__()

    async def __aexit__(self, exc_type, exc, traceback):
        return super().__exit__(exc_type, exc, traceback)


async def create_engine(*args, **kwargs):
    engine = sa.create_engine(*args, **kwargs)
    engine.__class__ = AioEngine
    return engine
