from aiohttp import web

from .database import history_tbl


async def history(request):
    return web.Response(text='history')


async def history_middleware_factory(app, handler):
    async def history_middleware(request):
        response = await handler(request)

        db_engine = request.app['db_engine']
        # queries should register request['cmd'], request['fullcmd']
        cmd = request.get('cmd')
        if cmd:
            with db_engine.connect() as conn:
                conn.execute(history_tbl.insert().values(
                    cmd=cmd,
                    fullcmd=request.get('fullcmd', ''),
                ))
        return response

    return history_middleware
