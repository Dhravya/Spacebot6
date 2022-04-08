from typing import Union, List
import asyncio
import datetime

import discord
from discord.ext import commands, tasks
from utility.db.database import Database

# TODO: ADD WAYS TO CONFIGURE LOGGING
# FIXME: Many logging not working and not tested at all
class LoggingCog(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await asyncio.sleep(10)
        self.database = Database(self.bot)
        self.force_update_logging_cache.start()

    async def check_and_get_channel(
        self, guildID: int, setting: str
    ) -> Union[discord.TextChannel, None]:
        await self.bot.wait_until_ready()
        try:
            channel = await self.database.get_log_settings(guildID, setting)
        except AttributeError:
            return
        if channel is None:
            return None
        return self.bot.get_channel(int(channel))

    @tasks.loop(seconds=120)
    async def force_update_logging_cache(self):
        await asyncio.sleep(10)
        await self.database._logging_cache_set()

    @force_update_logging_cache.before_loop
    async def before_force_update_logging_cache(self):
        await self.bot.wait_until_ready()

    # * TESTED
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild:
            return
        channel = await self.check_and_get_channel(before.guild.id, "message_edit")
        if channel is None:
            return
        embed = discord.Embed(
            description=f"""
            [Message]({before.jump_url}) edited in {before.channel.mention}
            """,
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.blue(),
        )
        if before.content == after.content or not any([before.content, after.content]):
            return
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        embed.set_author(name=before.author, icon_url=before.author.avatar.url)
        embed.set_footer(
            text="Message ID: "
            + str(before.id)
            + " | User ID: "
            + str(before.author.id)
        )
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: List[discord.Message]):
        if not messages[0].guild:
            return
        channel = await self.check_and_get_channel(messages[0].guild.id, "bulk_delete")
        if channel is None:
            return

        embed = discord.Embed(
            description=f"""
            Bulk messages deleted | {len(messages)} messages in {messages[0].channel.mention}
            """,
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=f"{messages[0].author}",
            icon_url=messages[0].author.avatar.url,
        )
        embed.set_footer(
            text="Message ID: "
            + str(messages[0].id)
            + " | User ID: "
            + str(messages[0].author.id)
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        channel_ = await self.check_and_get_channel(channel.guild.id, "channel_create")
        if channel_ is None:
            return
        embed = discord.Embed(
            description=f"{channel.mention} was created",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.green(),
        )
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url)
        embed.set_footer(text=f" Channel ID: {channel.id}")
        await channel_.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        channel_ = await self.check_and_get_channel(channel.guild.id, "channel_delete")
        if channel_ is None:
            return
        embed = discord.Embed(
            description=f"{channel.mention} was deleted",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.green(),
        )
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url)
        await channel_.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ):
        channel = await self.check_and_get_channel(after.guild.id, "channel_update")
        if channel is None:
            return
        embed = discord.Embed(
            description=f"""
            {before.mention}({before.name}) was updated
            """,
            colour=discord.Color.blue(),
        )
        old, new = (
            ("Its a voice channel", "Its a voice channel")
            if not before.type == discord.ChannelType.text
            else (before.topic, after.topic)
        )

        embed.add_field(
            name="Before",
            value=f"""
        **Name**: {before.name}
        **Old Topic**: {old}
        **Position**: {before.position}""",
            inline=False,
        )
        embed.add_field(
            name="After",
            value=f"""
        **Name**: {after.name}
        **New Topic**: {new}
        **Position**: {after.position}""",
            inline=False,
        )
        await channel.send(embed=embed)

        embed.set_author(name=before.guild.name, icon_url=before.guild.icon.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        channel = await self.check_and_get_channel(role.guild.id, "role_create")
        if channel is None:
            return
        embed = discord.Embed(
            description=f"{role.mention} was created",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.green(),
        )
        embed.set_author(name=role.guild.name, icon_url=role.guild.icon.url)
        embed.set_footer(text=f"Role ID: {role.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        channel = await self.check_and_get_channel(role.guild.id, "role_delete")
        if channel is None:
            return
        embed = discord.Embed(
            description=f"{role.mention} was deleted",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.red(),
        )
        embed.set_author(name=role.guild.name, icon_url=role.guild.icon.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        channel = await self.check_and_get_channel(after.guild.id, "role_update")
        if channel is None:
            return
        if (
            before.name == after.name
            and before.permissions == after.permissions
            and before.colour == after.colour
        ):
            return

        embed = discord.Embed(
            title="Role update",
            description=f"""
            Before update:
            {before.mention}({before.name})
            Position : {before.position}
            Permissions : {before.permissions}
            Color : {before.colour}
            Hoist : {before.hoist}
            Mentionable : {before.mentionable}
            
            After update:
            {after.mention}({after.name})
            Position : {after.position}
            Permissions : {after.permissions}
            Color : {after.colour}
            Hoist : {after.hoist}
            Mentionable : {after.mentionable}
            """,
            colour=discord.Color.blue(),
        )
        embed.set_author(name=before.guild.name, icon_url=before.guild.icon.url)
        await channel.send(embed=embed)

    #! ____________________________
    # * Tested uptil here
    #! ____________________________

    @commands.Cog.listener()
    async def on_guild_emojis_update(
        self,
        guild: discord.Guild,
        before: List[discord.Emoji],
        after: List[discord.Emoji],
    ):
        channel = await self.check_and_get_channel(guild.id, "emoji_update")
        if channel is None:
            return

        embed = discord.Embed(
            title="Emoji update",
            description=f"""
            Before update:
            {before}
            After update:
            {after}
            """,
            colour=discord.Color.blue(),
        )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild: discord.Guild):
        pass

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        channel = await self.check_and_get_channel(invite.guild.id, "invite_info")
        if channel is None:
            return
        embed = discord.Embed(
            title="Invite create",
            description=f"""
            {invite.inviter.mention}({invite.inviter.name})
            in : {invite.guild.name}
            channel : {invite.channel.mention} ({invite.channel.name})
            Max age: {invite.max_age}
            Max users: {invite.max_uses}
            is temperory? {invite.temporary}
            expires at: {invite.expires_at}
            """,
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        channel = await self.check_and_get_channel(guild.id, "member_ban")
        if channel is None:
            return
        embed = discord.Embed(
            title="Member ban",
            description=f"""
            {user.mention}({user.name}) was banned
            """,
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = await self.check_and_get_channel(member.guild.id, "member_join")
        if channel is None:
            return
        created_at = discord.utils.format_dt(member.created_at, style="R")
        joined_at = discord.utils.format_dt(member.joined_at, style="R")
        embed = discord.Embed(
            title="Member joined",
            description=f"{member.mention} {member.id} joined the server.\nAccount created: {created_at}\nJoined: {joined_at}",
            timestamp=datetime.datetime.utcnow(),
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = await self.check_and_get_channel(member.guild.id, "member_leave")
        if channel is None:
            return
        created_at = discord.utils.format_dt(member.created_at, style="R")
        joined_at = discord.utils.format_dt(member.joined_at, style="R")
        embed = discord.Embed(
            title="Member left",
            description=f"{member.mention} {member.id} left the server.\nAccount created: {created_at}\nJoined: {joined_at}",
            timestamp=datetime.datetime.utcnow(),
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        channel = await self.check_and_get_channel(guild.id, "member_unban")
        if channel is None:
            return
        embed = discord.Embed(
            title="Member unban",
            description=f"""
            {user.mention}({user.name}) was unbanned
            """,
            colour=discord.Color.green(),
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """This is the on_member_role_add and on_member_role_delete"""
        channel = await self.check_and_get_channel(after.guild.id, "member_role_add")
        if channel is None:
            return
        if before.roles != after.roles:
            embed = discord.Embed(
                title="Member role update",
                description=f"""
                Before update:
                {before.mention}({before.name})
                Roles : {", ".join([role.name for role in before.roles])}
                After update:
                {after.mention}({after.name})
                Roles : {", ".join([role.name for role in after.roles])}
                """,
                colour=discord.Color.blue(),
            )
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        channel = await self.check_and_get_channel(message.guild.id, "message_delete")
        if channel is None:
            return

        embed = discord.Embed(
            title="Message deleted",
            description=f"""
            {message.author.mention}({message.author.name})
            {message.content}
            """,
            timestamp=datetime.datetime.utcnow(),
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        channel = await self.check_and_get_channel(
            member.guild.id, "voice_channel_update"
        )
        if channel is None:
            return
        if before.channel != after.channel:
            embed = discord.Embed(
                title="Voice channel update",
                description=f"""
                Before update:
                {before.channel.mention}({before.channel.name})
                After update:
                {after.channel.mention}({after.channel.name})
                """,
                timestamp=datetime.datetime.utcnow(),
            )
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(LoggingCog(bot))
