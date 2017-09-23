# TODO : make it plugable, so that other engines can be used
# TODO : replace with aiopg
# from sqlalchemy import create_engine

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class HistoryItem(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    cmd = Column(String)
    fullcmd = Column(String)

    # TODO : verify time stamp is calculated at DB side
    # TODO : use utc time
    time_created = Column(DateTime, server_default=func.now())


history_tbl = HistoryItem.__table__


async def init_db(app, db_configs):
    # debug with echo=True
    dsn = db_configs.pop('dsn')
    from .db.sqlite import create_engine
    engine = await create_engine(dsn, **db_configs)
    # TODO : use async with this
    Base.metadata.create_all(engine)

    app['db_engine'] = engine


async def cleanup_db(app):
    if app.get('db_engine'):
        await app['db_engine'].close()
