"""
Run application in debug mode
"""

from .bunnylol import make_app

from aiohttp import web
import aiohttp_debugtoolbar


app = make_app(
    debug=True,
    db_configs={
        'dsn': 'sqlite:///bunnylol.db',
        'echo': True,
    },
)
aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

web.run_app(app, host='localhost', port=12345)
