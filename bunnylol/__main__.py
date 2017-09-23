"""
Run application in debug mode
"""

import logging
import colorlog

from .bunnylol import make_app

from aiohttp import web
import aiohttp_debugtoolbar

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# formatter = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
# )
ch = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
ch.setFormatter(formatter)
logger.addHandler(ch)


app = make_app(
    debug=True,
    db_configs={
        'dialect': 'sqlite',
        'url': 'sqlite:///bunnylol.db',
        'echo': False,
    },
)
aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

web.run_app(app, host='localhost', port=12345)
