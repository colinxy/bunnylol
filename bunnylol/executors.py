
from .commands import resolve_command
from .helpers import redirect_help


async def execute_query(query: str, request):
    request['fullcmd'] = query
    if not query:
        return redirect_help(request)

    cmd = resolve_command(query)
    return await cmd(query, request)
