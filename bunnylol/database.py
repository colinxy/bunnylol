import importlib
import logging
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from .db.common import create_tables

logger = logging.getLogger(__name__)

Base = declarative_base()


class HistoryItem(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    cmd = Column(String)
    fullcmd = Column(String)

    # TODO : use utc time
    time_created = Column(DateTime, server_default=func.now())


history_tbl = HistoryItem.__table__


async def _init_db(db_configs):
    dialect = db_configs.pop('dialect', 'sqlite')
    try:
        create_engine = getattr(
            importlib.import_module(f'.db.{dialect}', package='bunnylol'),
            'create_engine',
        )
    except ImportError:
        raise ValueError(f'Db dialect {dialect} not found')

    dsn = db_configs.pop('dsn')
    engine = await create_engine(dsn, **db_configs)
    logger.info(f'Connected to DB {engine.url}')

    create_table = db_configs.pop('create_table', False)
    if create_table:
        await create_tables(engine, Base.metadata.sorted_tables)

    return engine


async def init_db(app, db_configs):
    app['db_engine'] = await _init_db(db_configs)
    app.on_cleanup.append(cleanup_db)


async def cleanup_db(app):
    db_engine = app.get('db_engine')
    if db_engine:
        db_engine.close()
        await db_engine.wait_closed()
