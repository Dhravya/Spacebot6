from typing import Union
from discord.ext import commands
from discord.ext import tasks
import asyncio


class Background(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot
        self.cursor = self.bot.cursor
        self.background_task.start()

    @tasks.loop(minutes=1)
    async def background_task(self):
        try:
            await self.bot.conn.ping(reconnect=True)

        except:
            await self.bot.connect_to_db(self.bot)

    @background_task.before_loop
    async def before_background_task(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(10)


def setup(bot):
    bot.add_cog(Background(bot))
