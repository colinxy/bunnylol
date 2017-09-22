# TODO : make it plugable, so that other engines can be used
# TODO : replace with aiopg
from sqlalchemy import create_engine

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


async def init_db():
    # debug with echo=True
    engine = create_engine('sqlite:///bunnylol.db', echo=True)
    Base.metadata.create_all(engine)
    return engine.connect()
