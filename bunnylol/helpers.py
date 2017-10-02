from aiohttp import web


def split2(query: str):
    splitted = query.split(maxsplit=1)
    if len(splitted) == 0:
        return '', ''
    if len(splitted) == 1:
        return splitted[0], ''
    return splitted


def redirect_to(resource_name, request, query=None):
    url = request.app.router[resource_name].url_for()
    if query:
        url = url.with_query(query)
    return web.HTTPFound(url)


def redirect_help(request, query=None):
    return redirect_to('help', request, query)


async def help(request):
    return redirect_to('query', request, query={
        'q': 'help',
    })
