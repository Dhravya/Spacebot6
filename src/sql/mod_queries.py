from discord.ext import commands
from typing import Union


async def create_mod_tables(bot: Union[commands.Bot, commands.AutoShardedBot]):

    async with bot.cursor as cursor:

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS 
                cases (
                    guild_id BIGINT NOT NULL, 
                    case_number INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
                    offence_type ENUM('kick', 'ban', 'warn', 'mute', 'softban') NOT NULL,
                    time DATETIME NOT NULL,
                    reason VARCHAR(300) DEFAULT "NA", 
                    moderator BIGINT NOT NULL,
                    offender BIGINT NOT NULL,
                    message_id BIGINT
                )
        """
        )
