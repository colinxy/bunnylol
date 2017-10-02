import logging
from typing import Dict, List, Optional, Type, TypeVar, Tuple, Union  # noqa
import shlex
from urllib.parse import quote as url_quote

from aiohttp import web
from tabulate import tabulate

from .helpers import redirect_help, split2
from .history import select_history
from .database import history_tbl

logger = logging.getLogger(__name__)


Cmd = TypeVar('Cmd', bound='Command')
CmdMixin = TypeVar('CmdMixin', bound='CommandMixin')
CmdType = Type[Union[Cmd, CmdMixin]]


def resolve_command(query: str, **params) -> 'CommandMixin':
    cmd_name, _ = split2(query)
    if not cmd_name:
        return Help()

    cmd_class = Command.from_name(cmd_name.lower())
    if not cmd_class:
        cmd_class = Command.fallback()
        params['skip_first'] = False
    cmd = cmd_class(**params)
    return cmd


async def execute_query(query: str, request):
    request['fullcmd'] = query
    if not query:
        return redirect_help(request)

    cmd = resolve_command(query)
    return await cmd(query, request)


class Command:
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


class CommandMixin:

    async def call(self, query, request):
        raise NotImplementedError

    def parse(self, query: str, request):
        raise NotImplementedError

    async def __call__(self, query: str, request):
        await self.pre_call_hook(request)
        try:
            query = self.parse(query, request)
            result = await self.call(query, request)
        finally:
            await self.post_call_hook(request)

        return result

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    async def pre_call_hook(self, request):
        # by convention, non abstract commands should not have
        # `Command' in the class name, e.g. Help, not HelpCommand
        if not request.get('cmd'):
            request['cmd'] = self.__class__.__name__.lower()

    async def post_call_hook(self, request):
        pass


class RawCommandMixin(CommandMixin):

    def parse(self, query: str, request) -> str:
        return query


class SplitCommandMixin(CommandMixin):

    def parse(self, query: str, request) -> List[str]:
        return query.split()


class Split2CommandMixin(CommandMixin):

    def parse(self, query: str, request) -> Tuple[str, str]:
        return split2(query)


class ShlexCommandMixin(CommandMixin):

    def parse(self, query: str, request) -> List[str]:
        return shlex.split(query)


class DNT(Command, Split2CommandMixin):
    """Do not track"""
    aliases = ['dnt']

    async def call(self, query_: Tuple[str, str], request):
        _, query = query_
        return await execute_query(query, request)


class Help(Command, RawCommandMixin):
    aliases = [
        'help',
        'h',
        'he',
    ]

    async def call(self, query, request):
        return redirect_help(request, query={
            'q': query,
        })


class History(Command, SplitCommandMixin):
    aliases = [
        'history',
        'hist',
    ]

    async def call(self, query: List[str], request):
        history = await select_history(request)
        return web.Response(text=tabulate(
            history,
            headers=[
                col.name for col in history_tbl.columns
            ],
            tablefmt='simple',
        ))


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

    async def call(self, query, _request):
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

    async def __call__(self, args, request):
        return web.Response(text='youtube feature to be added')


class ShellCommand(Command, ShlexCommandMixin):
    localhost_only = True
    # TODO

    def check_remote(self, request):
        """
        This is only a opportunistic guess that you are talking to localhost.
        To be truly secure, bind app to localhost or use a firewall
        """
        peername = request.transport.get_extra_info('peername')
        print(peername)

    async def call(self, query: List[str], request):
        pass
