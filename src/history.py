from aiohttp import web
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class HistoryItem(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    cmd = Column(String)
    full_cmd = Column(String)


async def history(request):
    return web.Response(text='history')
