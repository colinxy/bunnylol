
from .commands import resolve_command
from .helpers import redirect_help


def execute_query(query: str, request):
    request['fullcmd'] = query
    if not query:
        return redirect_help(request)

    cmd = resolve_command(query)

    cmd.pre_call_hook(request)
    result = cmd(query, request)
    cmd.post_call_hook(request)
    return result
