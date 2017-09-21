from aiohttp import web


def redirect_to(request, resource_name, query=None):
    url = request.app.router[resource_name].url_for()
    if query:
        url = url.with_query(query)
    return web.HTTPFound(url)


def redirect_help(request, query=None):
    return redirect_to(request, 'help', query)


async def help(request):
    return web.Response(text='help')
