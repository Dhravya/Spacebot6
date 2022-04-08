from discord.ext import commands
from typing import Union


async def create_rep_tables(bot: Union[commands.Bot, commands.AutoShardedBot]):
    async with bot.cursor as cursor:
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS 
            reputation (
                user_id BIGINT UNSIGNED NOT NULL,
                reputation INT NOT NULL DEFAULT 0,
                last_rep_time TIME,
                PRIMARY KEY (user_id)
            )
        """
        )
