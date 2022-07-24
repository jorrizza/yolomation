from pyrcb2 import IRCBot, Event
import asyncio
import aiojobs
from . import vm


class YoloMationBot:
    def __init__(self):
        # You can set log_communication to False to disable logging.
        self.bot = IRCBot(log_communication=True)
        self.bot.load_events(self)

    async def run(self):
        self.scheduler = await aiojobs.create_scheduler()
        async def init():
            await self.bot.connect("irc.oftc.net", 6697)
            await self.bot.register("yolomation")
            await self.bot.join("#yolocation")
            # More code here (optional)...
        await self.bot.run(init())

    @Event.privmsg
    async def on_privmsg(self, sender, channel, message):
        if channel is None:
            # Message was sent in a private query.
            self.bot.privmsg(sender, "Whatever, man. I'm not a helpdesk.")
            return

        # Message was sent in a channel.
        await self.scheduler.spawn(self.acknowledge(sender))

    async def acknowledge(self, sender):
        self.bot.privmsg(sender, "Making a VM for you. Drink more water while you're waiting.")
        instance = await vm.create()
        self.bot.privmsg(sender, f"Done! Details: {instance}")
