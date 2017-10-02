# async adaptor for sqlite, not really async
# TODO: below implementation is so ugly, rewrite new package as aiosqlite

import sqlalchemy as sa
from sqlalchemy.engine import Engine, Connection


class _aiter:
    def __init__(self, iterable):
        self.iterable = iter(iterable)

    def __await__(self):
        return iter([])

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iterable)
        except StopIteration:
            raise StopAsyncIteration


class AioEngine(Engine):
    def acquire(self, **kwargs):
        connection = super().connect(**kwargs)
        connection.__class__ = AioConnection
        return connection

    def release(self, conn):
        pass

    def execute(self, *args, **kwargs):
        result = super().execute(*args, **kwargs)
        return _aiter(result)

    def close(self):
        return super().dispose()

    def terminate(self):
        return self.close()

    async def wait_closed(self):
        return

    async def __aenter__(self):
        return super().__enter__()

    async def __aexit__(self, exc_type, exc, traceback):
        return super().__exit__(exc_type, exc, traceback)


class AioConnection(Connection):
    def execute(self, *args, **kwargs):
        # TODO: put context manager around connection
        result = super().execute(*args, **kwargs)
        return _aiter(result)

    async def __aenter__(self):
        return super().__enter__()

    async def __aexit__(self, exc_type, exc, traceback):
        return super().__exit__(exc_type, exc, traceback)


async def create_engine(*args, **kwargs):
    engine = sa.create_engine(*args, **kwargs)
    engine.__class__ = AioEngine
    return engine
