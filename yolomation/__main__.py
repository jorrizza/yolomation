import logging
from aiohttp import web
from .app import server


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(server())
