from aiohttp import web
import aiojobs
from aiojobs.aiohttp import atomic, setup
from .irc import YoloMationBot
from .vm import execute_callback
import logging

@atomic
async def handle_callback(request):
    payload = await request.json()

    if "hostname" in payload:
        irc_sender = await execute_callback(payload["hostname"], payload)
    else:
        raise aiohttp.web.HTTPBadRequest()
    
    logging.info(f"Responding callback for IRC user {irc_sender}")
    return web.Response(text=irc_sender)

async def server():
    scheduler = await aiojobs.create_scheduler()
    
    bot = YoloMationBot()
    await scheduler.spawn(bot.run())
    
    wa = web.Application()
    wa.add_routes([web.post('/', handle_callback)])
    wa.on_shutdown.append(scheduler.close)

    setup(wa)

    return wa
