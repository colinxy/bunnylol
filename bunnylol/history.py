from .database import history_tbl
from .helpers import redirect_to


async def history(request):
    return redirect_to('query', request, query={
        'q': 'history',
    })


async def select_history(request):
    db_engine = request.app['db_engine']
    async with db_engine.acquire() as conn:
        return [row async for row in conn.execute(history_tbl.select())]


async def history_middleware_factory(app, handler):
    async def history_middleware(request):
        response = await handler(request)

        db_engine = request.app['db_engine']
        # queries should register request['cmd'], request['fullcmd']
        cmd = request.get('cmd')
        # hardcode DNT command: do not record in history
        if cmd and cmd.lower() != 'dnt':
            async with db_engine.acquire() as conn:
                await conn.execute(history_tbl.insert().values(
                    cmd=cmd,
                    fullcmd=request.get('fullcmd', ''),
                ))
        return response

    return history_middleware
