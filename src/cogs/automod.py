import datetime
import re
import asyncio

import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands, tasks

from utility.db.database import Database
from views.automod_views import AutoModSettingsView
from utility.disc.embed_data import description_generator


class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings: dict = {}
        self.message_cache: dict = {}
        self.help_doc = "Auto-mod commands for your server"

    @commands.Cog.listener()
    async def on_ready(self):
        self.database = Database(self.bot)
        self.bot.log.info("AutoMod cog loaded")
        self.settings = self.database.automod_settings
        self.bot.add_application_command(self.automod)

        self._force_update_cache.start()

    @tasks.loop(minutes=5)
    async def _force_update_cache(self):
        await self.database._automod_cache_set()
        self.settings = self.database.automod_settings

    @_force_update_cache.before_loop
    async def before_force_update_cache(self):
        await asyncio.sleep(22)
        await self.bot.wait_until_ready()

    async def timeout_user(
        self,
        user: discord.Member,
        guild: discord.Guild,
        reason: str,
        channel: discord.TextChannel,
    ):
        try:
            time = datetime.timedelta(
                minutes=self.settings[guild.id]["punishment_timeout_minutes"]
            )
            await user.timeout_for(time, reason=reason)
            await channel.send(
                f"{user.mention} has been timed out for {time} for {reason}"
            )
        except discord.errors.Forbidden:
            self.bot.log.error(f"Could not timeout user {user.id} in guild {guild.id}")

    async def cog_before_invoke(self, ctx: discord.ApplicationContext) -> None:
        self.bot.log.info(f"{ctx.author} used {ctx.command} in {ctx.guild}")
        return

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Automoderator every message"""
        try:
            if message.guild is None or not self.database:
                return
        except AttributeError:
            return
        if not message.guild.id in self.settings:
            await self.database.maybe_initiate_automod(message.guild.id)
        try:
            _ = self.settings[message.guild.id]
        except KeyError:
            return

        if self.settings[message.guild.id]["enabled"]:
            # message is spam if there are more than spam_threshold messages in the spam_interval
            if (
                message.author.bot
                or message.author.id in self.settings[message.guild.id]["ignored_users"]
                or message.channel.id
                in self.settings[message.guild.id]["ignored_channels"]
                or any(
                    role.id in self.settings[message.guild.id]["ignored_roles"]
                    for role in message.author.roles
                )
            ):
                return

            if (
                self.settings[message.guild.id]["spam_interval"] == 0
                or self.settings[message.guild.id]["spam_threshold"] == 0
            ):
                return

            if message.channel.id not in self.message_cache:
                self.message_cache[message.channel.id] = {}

                self.message_cache[message.channel.id][message.author.id] = [
                    [message.content, message.created_at]
                ]
            else:
                if not message.author.id in self.message_cache[message.channel.id]:
                    self.message_cache[message.channel.id][message.author.id] = []
                self.message_cache[message.channel.id][message.author.id].append(
                    [message.content, message.created_at]
                )
            if (
                len(self.message_cache[message.channel.id][message.author.id])
                > self.settings[message.guild.id]["spam_threshold"]
            ):
                # if the first message in cache is older than spam_interval, remove it
                if self.message_cache[message.channel.id][message.author.id][0][1] < (
                    # Make both times the same timezone
                    datetime.datetime.now(datetime.timezone.utc)
                    - datetime.timedelta(
                        seconds=self.settings[message.guild.id]["spam_interval"]
                    )
                ):
                    self.message_cache[message.channel.id][message.author.id].pop(0)
                # if there are more than spam_threshold messages in the spam_interval, punish
                else:
                    await self.timeout_user(
                        message.author,
                        message.guild,
                        "Spamming",
                        message.channel,
                    )

                    self.message_cache[message.channel.id][message.author.id].pop(0)
                    history = []
                    async for message__ in message.channel.history(
                        limit=self.settings[message.guild.id]["spam_threshold"]
                    ):
                        if message__.author == message.author:
                            # FIXME: bulk delete instead of individual delete
                            await message__.delete()
                        if message__.author == message.guild.me:
                            history.append(message__.content)
                    if not self.settings[message.guild.id]["spam_message"] in history:
                        await message.channel.send(
                            f"{message.author.mention} {self.settings[message.guild.id]['spam_message']}"
                        )
            if (
                100 >= self.settings[message.guild.id]["capital_threshold"] > 0
                and len(message.content) > 30
            ):
                # _message = remove all nums, spaces, and punctuation, mentions
                _message = message.content.translate(
                    str.maketrans(
                        "", "", "1234567890!@#$%^&*()-_=+[]{};:,./<>?|`~ " + "\n"
                    )
                )
                if len(_message) > 0:
                    if (
                        len([c for c in _message if c.isupper()]) / len(_message)
                    ) * 100 >= self.settings[message.guild.id]["capital_threshold"]:
                        await message.channel.send(
                            message.author.mention
                            + self.settings[message.guild.id]["capital_message"]
                        )
                        await self.timeout_user(
                            message.author,
                            message.guild,
                            "capitals in in #" + message.channel.name,
                            message.channel,
                        )

            # Check for discord invites
            if self.settings[message.guild.id]["discord_invites"]:
                INVITE_REGEX = r"(https?://)?(www.)?(discord.(gg|io|me|li)|discordapp.com/invite)/[^\s/]+?(?=\b)"
                invites = re.findall(INVITE_REGEX, message.content)
                if len(invites) > 0:
                    await message.delete()
                    await self.timeout_user(
                        message.author,
                        message.guild,
                        "Discord invite in #" + message.channel.name,
                        message.channel,
                    )
                    return

            # Check for links
            if self.settings[message.guild.id]["links"]:
                # using regex
                LINK_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

                # Use the regex to detect links
                if re.findall(LINK_REGEX, message.content):
                    await message.channel.send(
                        message.author.mention
                        + self.settings[message.guild.id]["links_message"]
                    )
                    await self.timeout_user(
                        message.author,
                        message.guild,
                        "Links in #" + message.channel.name,
                        message.channel,
                    )
                    await message.delete()

            # Check for mentions
            if self.settings[message.guild.id]["mass_mentions"]:
                # get all roles mentioned in message
                number_of_users_mentioned = len(message.mentions) or len(
                    [
                        user
                        for user in message.guild.members
                        if any(
                            [role in message.role_mentions for role in list(user.roles)]
                        )
                    ]
                )

                if (
                    message.mention_everyone or message.mention_everyone is True
                ) and not message.author.bot:
                    await message.channel.send(
                        message.author.mention
                        + self.settings[message.guild.id]["mass_mentions_message"]
                    )
                    await self.timeout_user(
                        message.author,
                        message.guild,
                        "pinged everyone in #" + message.channel.name,
                        message.channel,
                    )
                    await message.delete()
                elif number_of_users_mentioned >= 20:
                    await message.channel.send(
                        message.author.mention
                        + self.settings[message.guild.id]["mass_mentions_message"]
                    )
                    await self.timeout_user(
                        message.author,
                        message.guild,
                        "Mass mentioning in #" + message.channel.name,
                        message.channel,
                    )
                    await message.delete()

            # Check for image spams
            if self.settings[message.guild.id]["image_spam"]:
                if message.attachments.__len__() > 2:
                    await message.channel.send(
                        message.author.mention
                        + self.settings[message.guild.id]["image_spam_message"]
                    )
                    await self.timeout_user(
                        message.author,
                        message.guild,
                        "too many images in #" + message.channel.name,
                        message.channel,
                    )
                    await message.delete()
                elif (
                    len(
                        re.findall(
                            r"(https?:\/\/.*\.(?:png|jpg|gif|jpeg))", message.content
                        )
                    )
                    > 2
                ):
                    await message.channel.send(
                        message.author.mention
                        + self.settings[message.guild.id]["image_spam_message"]
                    )
                    await self.timeout_user(
                        message.author,
                        message.guild,
                        "too many images in #" + message.channel.name,
                        message.channel,
                    )
                    await message.delete()

            # check for too many emoji
            if self.settings[message.guild.id]["emoji_spam"]:
                EMOJI_REGEX = r"/<a?:.+:\d+>/gm"
                if len(re.findall(EMOJI_REGEX, message.content)) > 5:
                    await message.channel.send(
                        message.author.mention
                        + self.settings[message.guild.id]["emoji_spam_message"]
                    )
                    await self.timeout_user(
                        message.author,
                        message.guild,
                        "too many emojis in #" + message.channel.name,
                        message.channel,
                    )
                    await message.delete()

        if any(
            word in message.content
            for word in self.settings[message.guild.id]["ignored_words"]
        ):
            await message.delete()
            await self.timeout_user(
                message.author,
                message.guild,
                "blacklisted word in #" + message.channel.name,
                message.channel,
            )

    automod = SlashCommandGroup(
        "automod", "Automoderation commands"
    )
    config = automod.create_subgroup(
        "config", "Automod configuration commands"
    )

    toggle = automod.create_subgroup(
        "toggle", "Toggle automod features"
    )

    @config.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def add_new_blacklist_word(
        self, ctx, word: Option(str, "The word you want to banned. 30chars max")
    ):
        """Add a New blacklisted word"""
        await ctx.defer()
        if len(word) > 30:
            return await ctx.respond(
                "Word is too long, please enter a shorter word", ephemeral=True
            )
        if word in self.settings[ctx.guild.id]["ignored_words"]:
            return await ctx.respond("This word is already blacklisted", ephemeral=True)
        await self.database.add_automod_ignored_word(str(ctx.guild.id), word)
        await ctx.respond(f"{word} added to blacklist")

    @config.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def remove_blacklisted_word(self, ctx, word: Option(str, "Word to remove")):
        """Remove a blacklisted word"""
        await ctx.defer()
        if word not in self.settings[ctx.guild.id]["ignored_words"]:
            return await ctx.respond("This word is not blacklisted", ephemeral=True)
        await self.database.remove_automod_ignored_word(str(ctx.guild.id), word)
        await ctx.respond(f"{word} removed from blacklist")

    @config.command()
    async def get_blacklisted_words(self, ctx):
        """Get all blacklisted words"""
        await ctx.defer()
        embed = discord.Embed(
            title="Blacklisted words",
            description="\n".join(
                [f"`{word}`" for word in self.settings[ctx.guild.id]["ignored_words"]]
            ),
            colour=self.bot.theme_colour["default"],
        )

        await ctx.respond(embed=embed)

    @config.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def add_ignored_role(self, ctx, role: discord.Role):
        """Add a role to the ignored roles"""
        await ctx.defer()
        if role.id in self.settings[ctx.guild.id]["ignored_roles"]:
            return await ctx.respond("This role is already ignored", ephemeral=True)
        await self.database.add_automod_ignored_role(str(ctx.guild.id), str(role.id))
        await ctx.respond(f"{role.name} added to ignored roles")

    @config.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def remove_ignored_role(self, ctx, role: discord.Role):
        """Remove a role from the ignored roles"""
        await ctx.defer()
        if role.id not in self.settings[ctx.guild.id]["ignored_roles"]:
            return await ctx.respond("This role is not ignored", ephemeral=True)
        await self.database.remove_automod_ignored_role(str(ctx.guild.id), str(role.id))
        await ctx.respond(f"{role.name} removed from ignored roles")

    @config.command()
    async def get_ignored_roles(self, ctx):
        """Get all ignored roles"""
        await ctx.defer()
        embed = discord.Embed(
            title="Ignored roles",
            description="\n".join(
                [
                    f"{(discord.utils.get(ctx.guild.roles, id=role)).mention}"
                    for role in self.settings[ctx.guild.id]["ignored_roles"]
                ]
            ),
            colour=self.bot.theme_colour["default"],
        )

        await ctx.respond(embed=embed)

    @config.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def add_ignored_channel(self, ctx, channel: discord.TextChannel):
        """Add a channel to the ignored channels"""
        await ctx.defer()
        if channel.id in self.settings[ctx.guild.id]["ignored_channels"]:
            return await ctx.respond("This channel is already ignored", ephemeral=True)
        await self.database.add_automod_ignored_channel(
            str(ctx.guild.id), str(channel.id)
        )
        await ctx.respond(f"{channel.name} added to ignored channels")

    @config.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def remove_ignored_channel(self, ctx, channel: discord.TextChannel):
        """Remove a channel from the ignored channels"""
        await ctx.defer()
        if channel.id not in self.settings[ctx.guild.id]["ignored_channels"]:
            return await ctx.respond("This channel is not ignored", ephemeral=True)
        await self.database.remove_automod_ignored_channel(
            str(ctx.guild.id), str(channel.id)
        )
        await ctx.respond(f"{channel.name} removed from ignored channels")

    @config.command()
    async def get_ignored_channels(self, ctx):
        """Get all ignored channels"""
        await ctx.defer()
        embed = discord.Embed(
            title="Ignored channels",
            description="\n".join(
                [
                    f"{(discord.utils.get(ctx.guild.channels, id=channel)).mention}"
                    for channel in self.settings[ctx.guild.id]["ignored_channels"]
                ]
            ),
            colour=self.bot.theme_colour["default"],
        )

        await ctx.respond(embed=embed)

    @config.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def add_ignored_user(self, ctx, user: discord.User):
        """Add a user to the ignored users"""
        await ctx.defer()
        if user.id in self.settings[ctx.guild.id]["ignored_users"]:
            return await ctx.respond("This user is already ignored", ephemeral=True)
        await self.database.add_automod_ignored_user(str(ctx.guild.id), str(user.id))
        await ctx.respond(f"{user.name} added to ignored users")

    @config.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def remove_ignored_user(self, ctx, user: discord.User):
        """Remove a user from the ignored users"""
        await ctx.defer()
        if user.id not in self.settings[ctx.guild.id]["ignored_users"]:
            return await ctx.respond("This user is not ignored", ephemeral=True)
        await self.database.remove_automod_ignored_user(str(ctx.guild.id), str(user.id))
        await ctx.respond(f"{user.name} removed from ignored users")

    @config.command()
    async def get_ignored_users(self, ctx):
        """Get all ignored users"""
        await ctx.defer()
        embed = discord.Embed(
            title="Ignored users",
            description="\n".join(
                [
                    f"{discord.utils.get(ctx.guild.members, id=user).mention}"
                    for user in self.settings[ctx.guild.id]["ignored_users"]
                ]
            ),
            colour=self.bot.theme_colour["default"],
        )

        await ctx.respond(embed=embed)

    @automod.command()
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        """
        Get the current automod settings.
        """
        await ctx.defer()
        latest_settings = await self.database.get_automod_settings(str(ctx.guild.id))
        embed = description_generator(latest_settings)

        view = AutoModSettingsView(ctx, latest_settings, self.database)
        await ctx.respond(embed=embed, view=view)

    @toggle.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def automod_(self, ctx):
        """
        Toggle automod on or off
        """
        await ctx.defer()
        await self.database.toggle_automod(str(ctx.guild.id))
        await ctx.respond(
            "Automod is now "
            + ("on" if self.settings[ctx.guild.id]["enabled"] else "off")
        )

    @toggle.command()
    @commands.has_permissions(manage_guild=True)
    async def message_spam(self, ctx):
        """
        Toggles the message spam detection feature
        """
        await ctx.defer(ephemeral=True)
        await self.database.set_particular_automod_settings(
            ctx.guild.id,
            [
                "spam_threshold",
                0 if self.settings[ctx.guild.id]["spam_threshold"] else 4,
            ],
        )
        await ctx.respond(
            f"Message spam detection is now {'enabled' if self.settings[ctx.guild.id]['spam_threshold'] else 'disabled'}",
            ephemeral=True,
        )

    @toggle.command()
    @commands.has_permissions(manage_guild=True)
    async def invite_detection(self, ctx: discord.ApplicationContext):
        """Turns on/off the invite detection"""
        await ctx.defer(ephemeral=True)
        await self.database.set_particular_automod_settings(
            ctx.guild.id,
            ["discord_invites", not self.settings[ctx.guild.id]["discord_invites"]],
        )
        await ctx.respond(
            f"Invite detection is now {'enabled' if self.settings[ctx.guild.id]['discord_invites'] else 'disabled'}",
            ephemeral=True,
        )

    @toggle.command()
    @commands.has_permissions(manage_guild=True)
    async def link_detection(self, ctx):
        """Turns on/off the link detection"""
        await ctx.defer(ephemeral=True)
        await self.database.set_particular_automod_settings(
            ctx.guild.id, ["links", not self.settings[ctx.guild.id]["links"]]
        )
        await ctx.respond(
            f"Link detection is now {'enabled' if self.settings[ctx.guild.id]['links'] else 'disabled'}",
            ephemeral=True,
        )

    @toggle.command()
    @commands.has_permissions(manage_guild=True)
    async def mass_mention_detection(self, ctx: discord.ApplicationContext):
        """Turns on/off the mass mentions detector"""
        await ctx.defer(ephemeral=True)
        await self.database.set_particular_automod_settings(
            ctx.guild.id,
            ["mass_mentions", not self.settings[ctx.guild.id]["mass_mentions"]],
        )
        await ctx.respond(
            f"Mass mentions Detector is now {'enabled' if self.settings[ctx.guild.id]['mass_mentions'] else 'disabled'}",
            ephemeral=True,
        )

    @toggle.command()
    @commands.has_permissions(manage_guild=True)
    async def image_spam_detection(self, ctx: discord.ApplicationContext):
        """Turns on/off the image spam detection"""
        await ctx.defer(ephemeral=True)
        await self.database.set_particular_automod_settings(
            ctx.guild.id, ["image_spam", not self.settings[ctx.guild.id]["image_spam"]]
        )
        await ctx.respond(
            f"Image spam detector is now {'enabled' if self.settings[ctx.guild.id]['image_spam'] else 'disabled'}",
            ephemeral=True,
        )

    @toggle.command()
    @commands.has_permissions(manage_guild=True)
    async def emoji_spam_detection(self, ctx: discord.ApplicationContext):
        """Turns on/off the image spam detection"""
        await ctx.defer(ephemeral=True)
        await self.database.set_particular_automod_settings(
            ctx.guild.id, ["emoji_spam", not self.settings[ctx.guild.id]["emoji_spam"]]
        )
        await ctx.respond(
            f"Emoji spam detector is now {'enabled' if self.settings[ctx.guild.id]['emoji_spam'] else 'disabled'}",
            ephemeral=True,
        )


def setup(bot: commands.Bot):
    bot.add_cog(AutoMod(bot))
