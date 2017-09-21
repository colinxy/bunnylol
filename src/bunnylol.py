from aiohttp import web
from commands import execute_query
from helpers import help
from history import history
from middlewares import middleware_factories


async def query(request):
    query = request.query.get('q', '')
    return execute_query(query, request)


def make_app():
    app = web.Application(middlewares=middleware_factories)

    app.router.add_get('/', query, name='query')
    app.router.add_get('/help', help, name='help')
    app.router.add_get('/history', history, name='history')

    return app


app = make_app()

if __name__ == '__main__':
    # debug
    import aiohttp_debugtoolbar
    aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    web.run_app(app, host='localhost', port=12345)
