from aiohttp import web
import shlex
from urllib.parse import quote as url_quote


class Command:
    aliases = []
    _commands = []
    _command_map = {}
    _default_cmd = None

    @classmethod
    def from_name(cls, name):
        cmd = cls._command_map.get(name)
        if cmd:
            return cmd()

    @classmethod
    def fall_back(cls, **kwargs):
        if cls._default_cmd:
            return cls._default_cmd(**kwargs)
        return HelpCommand(**kwargs)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Command._commands.append(cls)
        _cmd_map = Command._command_map
        for alias in getattr(cls, 'aliases', []):
            _cmd_map[alias] = cls

        if getattr(cls, 'make_default', False):
            Command._default_cmd = cls

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


class HelpCommand(Command):
    aliases = [
        'help',
        'h',
    ]

    def __call__(self, args, request):
        url = request.app.router['help'].url_for().with_query(
            {'q': ' '.join(args)},
        )
        return web.HTTPFound(url)


class HistoryCommand(Command):
    aliases = [
        'history',
        'hist',
    ]

    def __call__(self, _args, request):
        url = request.app.router['history'].url_for()
        return web.HTTPFound(url)


class RedirectCommand(Command):
    query_key = 'q'

    def __init__(self, skip_first=True):
        self.skip_first = skip_first

    def __call__(self, args, _request):
        if self.skip_first:
            args = args[1:]
        query_str = url_quote(' '.join(map(str, args)))
        url = f'{self.base_url}?{self.query_key}={query_str}'
        return web.HTTPFound(url)


class Google(RedirectCommand):
    aliases = [
        'google',
        'g',
        'goo',
    ]
    make_default = True

    base_url = 'https://www.google.com/search'


class Duckduckgo(RedirectCommand):
    aliases = [
        'duckduckgo',
        'ddg',
        'dd',
    ]

    base_url = 'https://duckduckgo.com/'


class Youtube(RedirectCommand):
    aliases = [
        'youtube',
        'yt',
    ]

    def __call__(self, args, request):
        return web.Response(text='youtube feature to be added')


class ShellCommand(Command):
    localhost_only = True

    def check_remote(self, request):
        """
        This is only a opportunistic guess that you are talking to localhost.
        To be truly secure, bind app to localhost or use a firewall
        """
        peername = request.transport.get_extra_info('peername')
        print(peername)

    def __call__(self, args, request):
        cmdline = ' '.join(args)
        args = shlex.split(cmdline)
