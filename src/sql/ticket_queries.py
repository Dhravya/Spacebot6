from discord.ext import commands
from typing import Union


async def create_ticket_tables(bot: Union[commands.Bot, commands.AutoShardedBot]):
    async with bot.cursor as cursor:
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS 
            ticket 
                (guild_id BIGINT , 
                count BIGINT, 
                category BIGINT , 
                PRIMARY KEY (guild_id))
            """
        )

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS 
                tickets 
                    (guild_id BIGINT, 
                    channel_id BIGINT, 
                    opener BIGINT, 
                    switch BOOL DEFAULT FALSE, 
                    PRIMARY KEY (guild_id, channel_id))"""
        )
