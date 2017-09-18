from aiohttp import web
from urllib.parse import quote as url_quote

_command_map = {}


def get_command(cmd):
    if cmd in _command_map:
        command = _command_map[cmd]
        command = Command.from_name(command)
        return command


class _CommandMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        aliases = attrs.get('aliases', [])
        for cmd in aliases:
            _command_map[cmd] = cls.__name__


class Command(metaclass=_CommandMeta):
    aliases = []
    _commands = []

    @classmethod
    def from_name(cls, name):
        for cmd in cls._commands:
            if name == cmd.__name__:
                return cmd()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Command._commands.append(cls)


class HelpCommand(Command):
    aliases = ['help']

    def __call__(self, _args, _request):
        web.HTTPFound('help')


class RedirectCommand(Command):
    query_key = 'q'

    def __call__(self, args, _request):
        query_str = url_quote(' '.join(map(str, args)))
        url = f'{self.base_url}?{self.query_key}={query_str}'
        return web.HTTPFound(url)


class Google(RedirectCommand):
    aliases = [
        'google',
        'g',
        'goo',
    ]

    base_url = 'https://www.google.com/search'


class Youtube(RedirectCommand):

    def __call__(self, args, request):
        pass
