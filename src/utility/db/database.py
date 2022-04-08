import json
from discord.ext import commands
import asyncio
from asyncmy.errors import IntegrityError
import datetime


class Database:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cursor = bot.cursor
        self.conn = bot.conn
        self.automod_settings: dict = {}
        self.prefix_cache: dict = {}
        self.logging_cache: dict = {}

    # TODO: Add more settings
    async def _prefix_cache_set(self):
        """
        Sets the prefix cache.
        """
        await self.bot.wait_until_ready()
        await self.cursor.execute("SELECT guild_id, prefix FROM Guilds")
        temp_var = await self.cursor.fetchall()
        for guild in temp_var:
            self.prefix_cache[str(guild[0])] = guild[1]
        self.bot.prefix_cache = self.prefix_cache

    async def _logging_cache_set(self):
        """
        Sets the cache for logging table
        """
        try:
            await self.cursor.execute("SELECT * FROM logging")
            recieved = True
        except:
            print("trying to build cache")

        temp_var = await self.cursor.fetchall()

        for guild in enumerate(temp_var):
            self.logging_cache[str(guild[1][0])] = {
                "enabled": guild[1][1],
                "message_delete": guild[1][2],
                "message_edit": guild[1][3],
                "image_delete": guild[1][4],
                "bulk_delete": guild[1][5],
                "invite_info": guild[1][6],
                "moderator_actions": guild[1][7],
                "member_join": guild[1][8],
                "member_leave": guild[1][9],
                "member_role_add": guild[1][10],
                "member_role_remove": guild[1][11],
                "member_nickname_change": guild[1][12],
                "member_ban": guild[1][13],
                "member_unban": guild[1][14],
                "role_create": guild[1][15],
                "role_delete": guild[1][16],
                "role_update": guild[1][17],
                "channel_create": guild[1][18],
                "channel_delete": guild[1][19],
                "channel_update": guild[1][20],
                "voice_channel_move": guild[1][21],
                "guild_update": guild[1][22],
                "voice_channel_update": guild[1][23],
            }

    async def _automod_cache_set(self):
        """
        Sets the automod cache.
        """
        try:
            await self.cursor.execute("SELECT * FROM automod")
            recieved = True
        except:
            print("failed trying to build automod cache")
        temp_var = await self.cursor.fetchall()

        # add ignored users, roles, channels
        await self.cursor.execute("SELECT guild_id, user_id FROM automod_ignored_users")
        temp_var2 = await self.cursor.fetchall()

        await self.cursor.execute("SELECT guild_id, role_id FROM automod_ignored_roles")
        temp_var3 = await self.cursor.fetchall()

        await self.cursor.execute(
            "SELECT guild_id, channel_id FROM automod_ignored_channels"
        )
        temp_var4 = await self.cursor.fetchall()

        await self.cursor.execute(
            "SELECT guild_id, banned_word FROM automod_ignored_words"
        )
        temp_var5 = await self.cursor.fetchall()

        # add ignored users, roles, channels
        for guild in temp_var:
            self.automod_settings[guild[0]] = {
                "enabled": guild[1],
                "spam_threshold": guild[2],
                "spam_interval": guild[3],
                "spam_message": guild[4],
                "capital_threshold": guild[5],
                "capital_message": guild[6],
                "discord_invites": guild[7],
                "links": guild[8],
                "links_message": guild[9],
                "mass_mentions": guild[10],
                "mass_mentions_message": guild[11],
                "image_spam": guild[12],
                "image_spam_message": guild[13],
                "emoji_spam": guild[14],
                "emoji_spam_message": guild[15],
                "punishment_timeout_minutes": guild[16],
                "ignored_users": [user[1] for user in temp_var2 if user[0] == guild[0]],
                "ignored_roles": [role[1] for role in temp_var3 if role[0] == guild[0]],
                "ignored_channels": [
                    channel[1] for channel in temp_var4 if channel[0] == guild[0]
                ],
                "ignored_words": [word[1] for word in temp_var5 if word[0] == guild[0]],
            }

    async def get_automod_settings_by_name(self, guildID, name):
        """
        Gets the automod settings by name for a guild.
        :param guildID: The guild ID.
        :param name: The name of the setting.
        :return: The setting value.
        """
        await self.cursor.execute(
            "SELECT %s FROM automod WHERE guild_id = %s", (name, guildID)
        )
        return await self.cursor.fetchone()[0]

    async def get_prefix(self, guildID):
        """
        Gets the prefix for a guild.
        :param guildID: The guild ID.
        :return: The prefix.
        """
        await self.cursor.execute(
            "SELECT prefix FROM Guilds WHERE guild_id = %s", (guildID,)
        )
        return await self.cursor.fetchone()[0]

    async def set_prefix(self, guildID, prefix) -> None:
        """
        Sets the prefix for a guild.
        :param guildID: The guild ID.
        :param prefix: The prefix.
        """
        await self.cursor.execute(
            "SELECT guild_id FROM Guilds WHERE guild_id = %s", (guildID,)
        )
        guild_info = await self.cursor.fetchone()
        if not guild_info:
            await self.cursor.execute(
                "INSERT INTO Guilds (guild_id, prefix) VALUES (%s, %s)",
                (guildID, prefix),
            )
        else:
            await self.cursor.execute(
                "UPDATE Guilds SET prefix = %s WHERE guild_id = %s", (prefix, guildID)
            )
        await self.conn.commit()
        await self._prefix_cache_set()

    async def get_automod_settings(self, guildID):
        """
        Gets the automod settings for a guild.
        :param guildID: The guild ID.
        :return: A dictionary with the automod settings.
        """
        await self.cursor.execute(
            "SELECT * FROM automod WHERE guild_id = %s", (str(guildID),)
        )
        # Convert to dict
        guild = await self.cursor.fetchone()
        if guild is None:
            return None

        await self.cursor.execute("SELECT guild_id, user_id FROM automod_ignored_users")
        temp_var2 = await self.cursor.fetchall()

        await self.cursor.execute("SELECT guild_id, role_id FROM automod_ignored_roles")
        temp_var3 = await self.cursor.fetchall()

        await self.cursor.execute(
            "SELECT guild_id, channel_id FROM automod_ignored_channels"
        )
        temp_var4 = await self.cursor.fetchall()

        await self.cursor.execute(
            "SELECT guild_id, banned_word FROM automod_ignored_words"
        )
        temp_var5 = await self.cursor.fetchall()

        return {
            "enabled": guild[1],
            "spam_threshold": guild[2],
            "spam_interval": guild[3],
            "spam_message": guild[4],
            "capital_threshold": guild[5],
            "capital_message": guild[6],
            "discord_invites": guild[7],
            "links": guild[8],
            "links_message": guild[9],
            "mass_mentions": guild[10],
            "mass_mentions_message": guild[11],
            "image_spam": guild[12],
            "image_spam_message": guild[13],
            "emoji_spam": guild[14],
            "emoji_spam_message": guild[15],
            "punishment_timeout_minutes": guild[16],
            "ignored_users": [user[1] for user in temp_var2 if user[0] == guild[0]],
            "ignored_roles": [role[1] for role in temp_var3 if role[0] == guild[0]],
            "ignored_channels": [
                channel[1] for channel in temp_var4 if channel[0] == guild[0]
            ],
            "ignored_words": [word[1] for word in temp_var5 if word[0] == guild[0]],
        }

    async def maybe_initiate_automod(self, guildId):
        """
        Checks if guild id is in the cache if not adds it to the database
        :param guildID: the guild ID"""

        with open("./src/sql/defaults.json", "r") as f:
            defaults = json.load(f)
        guildId = str(guildId)
        if not self.automod_settings:
            return
        if guildId not in self.automod_settings:
            await self.cursor.execute(
                """INSERT INTO automod 
                                            (guild_id, 
                                            spam_message, 
                                            capital_message, 
                                            links_message, 
                                            mass_mentions_message, 
                                            emoji_spam_message) 
                                            VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    guildId,
                    defaults["spam_message"],
                    defaults["capital_message"],
                    defaults["links_message"],
                    defaults["mass_mentions_message"],
                    defaults["emoji_spam_message"],
                ),
            )
            await self.conn.commit()
            await self._automod_cache_set()

    async def set_automod_settings(self, guildID, settings: dict) -> None:
        """
        Sets the automod settings for a guild.
        :param guildID: The guild ID.
        :param settings: A dictionary with the automod settings.
        """

        with open("./src/sql/defaults.json", "r") as f:
            defaults = json.load(f)

        await self.cursor.execute(
            """UPDATE automod SET
            enabled = %s,
            spam_threshold = %s,
            spam_interval = %s,
            spam_message = %s,
            capital_threshold = %s,
            capital_message = %s,
            discord_invites = %s,
            links = %s,
            links_message = %s,
            mass_mentions = %s,
            mass_mentions_message = %s,
            image_spam = %s,
            image_spam_message = %s,
            emoji_spam = %s,
            emoji_spam_message = %s,
            punishment_timeout_minutes = %s where guild_id = %s""",
            (
                settings["enabled"],
                settings["spam_threshold"],
                settings["spam_interval"],
                settings["spam_message"] or defaults["spam_message"],
                settings["capital_threshold"],
                settings["capital_message"] or defaults["capital_message"],
                settings["discord_invites"],
                settings["links"],
                settings["links_message"] or defaults["links_message"],
                settings["mass_mentions"],
                settings["mass_mentions_message"] or defaults["mass_mentions_message"],
                settings["image_spam"],
                settings["image_spam_message"],
                settings["emoji_spam"],
                settings["emoji_spam_message"] or defaults["emoji_spam_message"],
                settings["punishment_timeout_minutes"],
            ),
        )

        await self.conn.commit()
        await self._automod_cache_set()

    async def set_particular_automod_settings(self, guildID, settings: list) -> None:
        """
        Sets the automod settings for a guild.
        :param guildID: The guild ID.
        :param settings: A dictionary with the automod settings.
        """
        guildID = str(guildID)
        await self.cursor.execute(
            "UPDATE automod SET " + settings[0] + " = %s WHERE guild_id = %s",
            (settings[1], guildID),
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def get_automod_ignored_users(self, guildID):
        """
        Gets the automod ignored users for a guild.
        :param guildID: The guild ID.
        :return: A list with the user IDs.
        """
        await self.cursor.execute(
            "SELECT user_id FROM automod_ignored_users WHERE guild_id = %s", (guildID,)
        )
        return [row[0] for row in await self.cursor.fetchall()]

    async def add_automod_ignored_user(self, guildID, userID) -> None:
        """
        Adds a user to the automod ignored users for a guild.
        :param guildID: The guild ID.
        :param userID: The user ID.
        """
        await self.cursor.execute(
            "INSERT INTO automod_ignored_users (guild_id, user_id) VALUES (%s, %s)",
            (guildID, userID),
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def remove_automod_ignored_user(self, guildID, userID) -> None:
        """
        Removes a user from the automod ignored users for a guild.
        :param guildID: The guild ID.
        :param userID: The user ID.
        """
        await self.cursor.execute(
            "DELETE FROM automod_ignored_users WHERE guild_id = %s AND user_id = %s",
            (guildID, userID),
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def get_automod_ignored_roles(self, guildID):
        """
        Gets the automod ignored roles for a guild.
        :param guildID: The guild ID.
        :return: A list with the role IDs.
        """
        await self.cursor.execute(
            "SELECT role_id FROM automod_ignored_roles WHERE guild_id = %s", (guildID,)
        )
        return [row[0] for row in await self.cursor.fetchall()]

    async def add_automod_ignored_role(self, guildID, roleID) -> None:
        """
        Adds a role to the automod ignored roles for a guild.
        :param guildID: The guild ID.
        :param roleID: The role ID.
        """
        await self.cursor.execute(
            "INSERT INTO automod_ignored_roles (guild_id, role_id) VALUES (%s, %s)",
            (guildID, roleID),
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def remove_automod_ignored_role(self, guildID, roleID) -> None:
        """
        Removes a role from the automod ignored roles for a guild.
        :param guildID: The guild ID.
        :param roleID: The role ID.
        """
        await self.cursor.execute(
            "DELETE FROM automod_ignored_roles WHERE guild_id = %s AND role_id = %s",
            (guildID, roleID),
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def get_automod_ignored_channels(self, guildID):
        """
        Gets the automod ignored channels for a guild.
        :param guildID: The guild ID.
        :return: A list with the channel IDs.
        """
        await self.cursor.execute(
            "SELECT channel_id FROM automod_ignored_channels WHERE guild_id = %s",
            (guildID,),
        )
        return [row[0] for row in await self.cursor.fetchall()]

    async def add_automod_ignored_channel(self, guildID, channelID) -> None:
        """
        Adds a channel to the automod ignored channels for a guild.
        :param guildID: The guild ID.
        :param channelID: The channel ID.
        """
        await self.cursor.execute(
            "INSERT INTO automod_ignored_channels (guild_id, channel_id) VALUES (%s, %s)",
            (guildID, channelID),
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def remove_automod_ignored_channel(self, guildID, channelID) -> None:
        """
        Removes a channel from the automod ignored channels for a guild.
        :param guildID: The guild ID.
        :param channelID: The channel ID.
        """
        await self.cursor.execute(
            "DELETE FROM automod_ignored_channels WHERE guild_id = %s AND channel_id = %s",
            (guildID, channelID),
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def get_automod_ignored_words(self, guildID):
        """
        Gets the automod ignored words for a guild.
        :param guildID: The guild ID.
        :return: A list with the word IDs.
        """
        await self.cursor.execute(
            "SELECT banned_word FROM automod_ignored_words WHERE guild_id = %s",
            (guildID,),
        )
        return [row[0] for row in await self.cursor.fetchall()]

    async def add_automod_ignored_word(self, guildID, word) -> None:
        """
        Adds a word to the automod ignored words for a guild.
        :param guildID: The guild ID.
        :param word: The word.
        """
        await self.cursor.execute(
            "INSERT INTO automod_ignored_words (guild_id, banned_word) VALUES (%s, %s)",
            (guildID, word),
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def remove_automod_ignored_word(self, guildID, word) -> None:
        """
        Removes a word from the automod ignored words for a guild.
        :param guildID: The guild ID.
        :param word: The word.
        """
        await self.cursor.execute(
            "DELETE FROM automod_ignored_words WHERE guild_id = %s AND banned_word = %s",
            (guildID, word),
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def toggle_automod(self, guildID) -> None:
        """
        Toggles automod for a guild.
        :param guildID: The guild ID.
        """
        await self.cursor.execute(
            "UPDATE automod SET enabled = NOT enabled WHERE guild_id = %s", (guildID,)
        )
        await self.conn.commit()
        await self._automod_cache_set()

    async def get_log_settings(self, guildID: str, settings: str):
        """
        Gets the logging settings of the particular guild
        :param guildID: The guild ID
        :param settings: The settings to get
        :return: The settings
        """
        try:
            return self.logging_cache[str(guildID)][settings]
        except KeyError:
            return None

    async def add_role(self, role_id: str, guild_id: str) -> None:
        """
        Adds a role to the database
        """
        role_id, guild_id = str(role_id), str(guild_id)
        try:
            await self.cursor.execute(
                "INSERT INTO roles(role_id, guild_id) VALUES (%s, %s)",
                (role_id, guild_id),
            )
            await self.conn.commit()
        except IntegrityError:
            pass

    async def get_reputation(self, user_id: str):
        """
        Gets the reputation of a user
        :param user_id: The user ID
        :return: The reputation
        """
        user_id = str(user_id)
        await self.cursor.execute(
            "SELECT reputation FROM reputation WHERE user_id = %s", (user_id,)
        )
        return await self.cursor.fetchone()
        # except TypeError:
        #     return 0
        # except KeyError:
        #     return 0

    async def add_reputation(self, user_id: str, amount: int = 1) -> None:
        """
        Adds a reputation to a user
        :param user_id: The user ID
        :param amount: The amount to add
        """
        user_id, amount = str(user_id), int(amount)
        current_time = datetime.datetime.utcnow()

        # Check if the last_reputation was in the last 10 seconds
        await self.cursor.execute(
            "SELECT * FROM reputation WHERE user_id = %s", (user_id,)
        )

        user_rep = await self.cursor.fetchone()

        if not user_rep:
            await self.cursor.execute(
                "INSERT INTO reputation(user_id, reputation, last_rep_time) VALUES (%s, %s, %s)",
                (user_id, amount, current_time),
            )
            await self.bot.conn.commit()
            return 1
        new_reputation = user_rep[1] + amount

        # new_time =  current time value in HH:MM:SS format
        new_time = current_time.strftime("%H:%M:%S")

        # TODO: Check if the last_reputation was in the last 10 seconds

        await self.cursor.execute(
            "UPDATE reputation SET reputation = %s, last_rep_time = %s WHERE user_id = %s",
            (new_reputation, new_time, user_id),
        )
        await self.bot.conn.commit()
        return new_reputation
