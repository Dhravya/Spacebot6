async def create_role_tables(bot):
    async with bot.cursor as cursor:
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS 
                roles(
                    guild_id bigint NOT NULL,
                    role_id bigint NOT NULL,
                    PRIMARY KEY (guild_id, role_id)
                )
            """
        )
