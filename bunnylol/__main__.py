from . import app

from aiohttp import web
import aiohttp_debugtoolbar
aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

web.run_app(app, host='localhost', port=12345)
