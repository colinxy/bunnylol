from aiohttp import web
import commands


def help(request):
    return web.Response(text='help')


def history(request):
    return web.Response(text='history')


async def query(request):
    query = request.query.get('q')
    if not query:
        return web.HTTPFound('help')

    query = query.split()
    command = commands.get_command(query[0])
    if command is None:
        return web.HTTPFound('help')

    return command(query[1:], request)


def make_app():
    app = web.Application()

    app.router.add_get('/', query, name='query')
    app.router.add_get('/help', help, name='help')
    app.router.add_get('/history', history, name='history')

    return app


if __name__ == '__main__':
    app = make_app()

    # debug
    import aiohttp_debugtoolbar
    aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    web.run_app(app, host='localhost', port=12345)
