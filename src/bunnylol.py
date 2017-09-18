from aiohttp import web
from commands import Command


async def help(request):
    return web.Response(text='help')


async def history(request):
    return web.Response(text='history')


async def query(request):
    query = request.query.get('q')
    if not query:
        return web.HTTPFound('help')

    query = query.split()
    cmd = Command.from_name(query[0])
    if not cmd:
        cmd = Command.fall_back(skip_first=False)

    return cmd(query, request)


def make_app():
    app = web.Application()

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
