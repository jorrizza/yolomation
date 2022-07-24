from aiohttp import web
import aiojobs
from aiojobs.aiohttp import atomic, setup
from .irc import YoloMationBot
from .vm import execute_callback

@atomic
async def handle_callback(request):
    payload = await request.json()

    if "hostname" in payload:
        await execute_callback(payload["hostname"], payload)
    else:
        raise aiohttp.web.HTTPBadRequest()
    
    return web.Response()

async def server():
    scheduler = await aiojobs.create_scheduler()
    
    bot = YoloMationBot()
    await scheduler.spawn(bot.run())
    
    wa = web.Application()
    wa.add_routes([web.post('/', handle_callback)])
    wa.on_shutdown.append(scheduler.close)

    setup(wa)

    return wa
