import logging
from typing import Dict, List, Optional, Type, TypeVar, Union  # noqa
import shlex
from urllib.parse import quote as url_quote

from aiohttp import web

from .helpers import redirect_help, redirect_to, split2

logger = logging.getLogger(__name__)


Cmd = TypeVar('Cmd', bound='Command')
CmdType = Type[Cmd]


def resolve_command(query: str, **params) -> Union['Command', 'CommandMixin']:
    cmd_name, _ = split2(query)
    if not cmd_name:
        return Help()

    cmd_class = Command.from_name(cmd_name.lower())
    if not cmd_class:
        cmd_class = Command.fallback()
        params['skip_first'] = False
    cmd = cmd_class(**params)
    return cmd


class CommandMixin:

    def call(self, query, request):
        raise NotImplementedError

    def parse(self, query: str, request):
        raise NotImplementedError

    def __call__(self, query: str, request):
        self.pre_call_hook(request)
        try:
            query = self.parse(query, request)
            result = self.call(query, request)
        finally:
            self.post_call_hook(request)

        return result

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def pre_call_hook(self, request):
        # by convention, non abstract commands should not have
        # `Command' in the class name, e.g. Help, not HelpCommand
        request['cmd'] = self.__class__.__name__.lower()

    def post_call_hook(self, request):
        pass


class Command(CommandMixin):
    aliases: List[str] = []
    _commands: List[CmdType] = []
    _command_map: Dict[str, CmdType] = {}
    _default_cmd: Optional[CmdType] = None

    @classmethod
    def from_name(cls, name):
        cmd = cls._command_map.get(name)
        if cmd:
            return cmd

    @classmethod
    def fallback(cls):
        if cls._default_cmd:
            return cls._default_cmd
        return Help

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Command._commands.append(cls)
        _cmd_map = Command._command_map
        for alias in getattr(cls, 'aliases', []):
            _cmd_map[alias] = cls

        if getattr(cls, 'make_default', False):
            Command._default_cmd = cls


class RawCommandMixin(CommandMixin):

    def parse(self, query: str, request) -> str:
        return query


class SplitCommandMixin(CommandMixin):

    def parse(self, query: str, request) -> List[str]:
        return query.split()


class ShlexCommandMixin(CommandMixin):

    def parse(self, query: str, request) -> List[str]:
        return shlex.split(query)


class DNT(Command):
    """Do not track"""
    aliases = ['dnt']

    def __call__(self, args, request):
        pass


class Help(Command):
    aliases = [
        'help',
        'h',
        'he',
    ]

    def __call__(self, args, request):
        return redirect_help(request, query={
            'q': ' '.join(args),
        })


class History(Command):
    aliases = [
        'history',
        'hist',
    ]

    def __call__(self, _args, request):
        return redirect_to('history', request)


class RedirectCommand(Command):
    query_key = 'q'

    def __init__(self, *, skip_first=True):
        self.skip_first = skip_first

    def parse(self, query: str, request):
        if self.skip_first:
            logger.debug(f'Skipping first argument of {query}')
            cmd_name, query = split2(query)
            if not cmd_name:
                raise redirect_help(request, query={
                    'cmd': self.__class__.__name__.lower(),
                    'q': query,
                })

        return query

    def call(self, query, _request):
        url = f'{self.base_url}?{self.query_key}={url_quote(query)}'
        return web.HTTPFound(url)


class Google(RedirectCommand):
    aliases = [
        'google',
        'g',
        'go',
        'goo',
        'goog',
        'googl',
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


class ShellCommand(Command, ShlexCommandMixin):
    localhost_only = True

    def check_remote(self, request):
        """
        This is only a opportunistic guess that you are talking to localhost.
        To be truly secure, bind app to localhost or use a firewall
        """
        peername = request.transport.get_extra_info('peername')
        print(peername)

    def call(self, query: List[str], request):
        pass
