import discord
from discord.ext import commands
from typing import Union


def get_prefix(
    bot: Union[commands.Bot, commands.AutoShardedBot], message: discord.Message
):
    if not message.guild:
        return "."
    try:
        if not str(message.guild.id) in bot.prefix_cache.keys():
            return "."
    except AttributeError:
        return "."
    return bot.prefix_cache[str(message.guild.id)]
