from discord.ext import commands
from typing import Union


async def create_logging_tables(bot: Union[commands.Bot, commands.AutoShardedBot]):
    async with bot.cursor as cursor:
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logging (
                guild_id bigint PRIMARY KEY,
                enabled boolean DEFAULT true,
                message_delete bigint,
                message_edit bigint,
                image_delete bigint,
                bulk_delete bigint,
                invite_info bigint, 
                moderator_actions bigint,

                member_join bigint,
                member_leave bigint,
                member_role_add bigint, 
                member_role_remove bigint,
                nickname_change bigint, 
                member_ban bigint,
                member_unban bigint,

                role_create bigint,
                role_delete bigint, 
                role_update bigint, 

                channel_create bigint, 
                channel_delete bigint,
                channel_update bigint,

                voice_channel_join bigint,
                voice_channel_leave bigint,
                voice_channel_move bigint)
            """
        )
