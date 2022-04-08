from discord.ext import commands
from pycord.ext import ipc
from typing import Union


class IpcRoutes(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot

    @ipc.server.route()
    async def get_member_count(self, data: dict):
        guild = self.bot.get_guild(
            data.guild_id
        )  # get the guild object using parsed guild_id

        return guild.member_count  # return the member count to the client


def setup(bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
    bot.add_cog(IpcRoutes(bot))
