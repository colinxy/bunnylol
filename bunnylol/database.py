from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from .db.common import create_tables

Base = declarative_base()


class HistoryItem(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    cmd = Column(String)
    fullcmd = Column(String)

    # TODO : use utc time
    time_created = Column(DateTime, server_default=func.now())


history_tbl = HistoryItem.__table__


async def init_db(app, db_configs):
    # debug with echo=True
    dsn = db_configs.pop('dsn')
    from .db.sqlite import create_engine
    engine = await create_engine(dsn, **db_configs)
    await create_tables(engine, Base.metadata.sorted_tables)
    # Base.metadata.create_all(engine)

    app['db_engine'] = engine


async def cleanup_db(app):
    db_engine = app.get('db_engine')
    if db_engine:
        db_engine.close()
        await db_engine.wait_closed()
