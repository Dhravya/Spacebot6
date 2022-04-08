import discord
from discord.ext import commands
from typing import Union

from views.help_views import *
from .help import MyHelp


class BotCommands(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        super().__init__()
        self.bot = bot
        self.bot.help_command = MyHelp()
        self.help_doc = "Some bot-commands that don't fit in other categories"

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        """Check the ping of the bot"""
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")


def setup(bot):
    bot.add_cog(BotCommands(bot))
