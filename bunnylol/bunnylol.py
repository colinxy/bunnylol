import asyncio
from aiohttp import web

from commands import execute_query
from database import init_db
from helpers import help
from history import history
from middlewares import middleware_factories


async def query(request):
    query = request.query.get('q', '')
    return execute_query(query, request)


async def make_app():

    app = web.Application(middlewares=middleware_factories)

    app.router.add_get('/', query, name='query')
    app.router.add_get('/help', help, name='help')
    app.router.add_get('/history', history, name='history')

    app['db'] = await init_db()

    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(make_app())

    # debug
    import aiohttp_debugtoolbar
    aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    web.run_app(app, host='localhost', port=12345)
