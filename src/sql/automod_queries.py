async def create_automod_tables(bot):
    async with bot.cursor as cursor:
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS 
                Guilds (
                    guild_id bigint PRIMARY KEY NOT NULL,
                    prefix VARCHAR(5) NOT NULL DEFAULT '.',
                    rep_toggle BOOLEAN NOT NULL DEFAULT FALSE)
            """
        )

        await cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS automod (
                    guild_id bigint PRIMARY KEY,
                    enabled boolean DEFAULT true,
                    spam_threshold integer DEFAULT 4,
                    spam_interval integer DEFAULT 2,
                    spam_message text,
                    capital_threshold integer DEFAULT 100,
                    capital_message text,
                    discord_invites boolean DEFAULT false,
                    links boolean DEFAULT false,
                    links_message text,
                    mass_mentions boolean DEFAULT false,
                    mass_mentions_message text,
                    image_spam boolean DEFAULT true,
                    image_spam_message text,
                    emoji_spam boolean DEFAULT true,
                    emoji_spam_message text,
                    punishment_timeout_minutes integer DEFAULT 5
                )
            """
        )
        await cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS automod_ignored_users (
                    guild_id bigint,
                    user_id bigint,
                    PRIMARY KEY (guild_id, user_id)
                )
            """
        )
        await cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS automod_ignored_channels (
                    guild_id bigint,
                    channel_id bigint,
                    PRIMARY KEY (guild_id, channel_id)
                )
            """
        )
        await cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS automod_ignored_roles (
                    guild_id bigint,
                    role_id bigint,
                    PRIMARY KEY (guild_id, role_id)
                )
            """
        )
        await cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS automod_ignored_words (
                    guild_id bigint,
                    banned_word VARCHAR(30),
                    PRIMARY KEY (guild_id, banned_word)
                )
            """
        )
