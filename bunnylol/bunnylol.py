import asyncio
from aiohttp import web

from .executors import execute_query
from .database import init_db
from .helpers import help
from .history import history
from .middlewares import middleware_factories


async def query(request):
    query = request.query.get('q', '')
    return execute_query(query, request)


def make_app(**configs):
    loop = asyncio.get_event_loop()

    debug = configs.pop('debug', False)
    app = web.Application(
        debug=debug,
        middlewares=middleware_factories,
    )

    app.router.add_get('/', query, name='query')
    app.router.add_get('/help', help, name='help')
    app.router.add_get('/history', history, name='history')

    loop.run_until_complete(init_db(app, configs['db_configs']))

    return app
