import discord
import datetime
from discord.ext import commands
from discord.commands import slash_command, Option
from random import choice

reasons = ["being a pain in already painful world", "not knowing how to be civil"]


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.help_doc = "Moderation commands"

    mod = discord.SlashCommandGroup("mod", "commands for moderation")

    @mod.command()
    @commands.has_guild_permissions(kick_members=True)
    async def reason(self, ctx: commands.Context, case_id: int, reason: str):
        """
        Edit the reason for a case
        """
        await self.bot.cursor.execute(
            "SELECT * FROM cases WHERE case_number = %s", (case_id,)
        )
        case = await self.bot.cursor.fetchone()
        if not case:
            await ctx.respond("Case not found")
            return
        if not str(case[0]) == str(ctx.guild.id):
            await ctx.respond("You can only edit cases in this guild")
            return
        await self.bot.cursor.execute(
            "UPDATE cases SET reason = %s WHERE case_number = %s", (reason, case_id)
        )
        await ctx.respond("Case updated")
        await self.bot.conn.commit()
        message_id = case[7]
        if message_id:
            await self.bot.cursor.execute(
                "SELECT moderator_actions FROM logging WHERE guild_id = %s",
                (str(ctx.guild.id),),
            )
            channel_ = await self.bot.cursor.fetchone()
            channel_ = self.bot.get_channel(channel_[0])
            if channel_:
                message = await channel_.fetch_message(message_id)
                if message:
                    embed = message.embeds[0]
                    embed.add_field(
                        name=f"Reason [Edited by {ctx.author.mention}]", value=reason
                    )
                    await message.edit(embed=embed)

    @slash_command(description="Kick a user from the server.")
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.Member, "Id or mention", required=True),
        reason: Option(str, "Reason for the kick", required=False, default=None),
    ):
        """Kick a user from the server."""
        if user.id == ctx.author.id:
            await ctx.respond("You can't kick yourself bozo.")
            return
        if user.id == self.bot.user.id:
            await ctx.respond("I can't kick myself bozo.")
            return
        if user.top_role.position >= ctx.author.top_role.position:
            await ctx.respond("Imagine kicking someone higher than you.")
            return
        if reason is None:
            reason = (
                choice(reasons)
                + " (Change reason by using `/mod reason <case_number>` command)"
            )
        await user.kick(reason=reason)
        await self.bot.cursor.execute(
            "INSERT INTO cases (guild_id, offence_type, time, reason, moderator, offender) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                str(ctx.guild.id),
                "kick",
                datetime.datetime.utcnow(),
                reason if reason else "Not provided",
                str(ctx.author.id),
                str(user.id),
            ),
        )
        await self.bot.cursor.execute(
            "SELECT moderator_actions FROM logging WHERE guild_id = %s",
            (str(ctx.guild.id),),
        )
        f = await self.bot.cursor.fetchone()
        if not f:
            await ctx.send(
                "A log channel hasn't been set for moderator actions yet. Use `/config moderation channel` to set one "
            )
            return
        channel = self.bot.get_channel(int(f[0]))
        if channel is None:
            await ctx.send(
                "I couldn't find the channel for the log channel. Please check if I have the right permissions and the channel is set correctly."
            )
            return
        await self.bot.cursor.execute(
            "SELECT case_number, time FROM cases WHERE guild_id = %s AND offender = %s",
            (str(ctx.guild.id), str(user.id)),
        )
        case_number = await self.bot.cursor.fetchone()
        embed = discord.Embed(
            "Kicked",
            f"{user.mention} has been kicked. Reason:  {reason}",
            color=0xFF0000,
        )
        embed.set_author(name=f"Case #{case_number[0]}", icon_url=user.avatar_url)
        embed.set_footer(
            text=f"Edit the reason by using `/mod reason <case_number>`",
            icon_url=user.avatar_url,
        )
        await ctx.respond(embed=embed)

        embed = discord.Embed(
            title="User kicked",
            description=f"{user.mention} has been kicked from the server.",
            color=discord.Color.red(),
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        embed.set_footer(text=f"Case ID: {case_number[0]}")
        embed.timestamp = case_number[1]
        msg = await channel.send(embed=embed)

        await self.bot.cursor.execute(
            "UPDATE cases SET message_id = %s WHERE guild_id = %s AND case_number = %s",
            (str(msg.id), str(ctx.guild.id), str(case_number[0])),
        )
        await self.bot.conn.commit()

    # TODO: BAN SHOULD ALSO SEND A MESSAGE TO THE CHANNEL like kick
    @slash_command(description="Ban a user from the server.")
    @commands.has_guild_permissions(ban_members=True)
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.Member, "Id or mention", required=True),
        *,
        reason: Option(str, "Reason for the ban", required=False, default=None),
    ):
        """Ban a user from the server."""
        if user.id == ctx.author.id:
            await ctx.send("You can't ban yourself bozo.")
            return
        if user.id == self.bot.user.id:
            await ctx.send("I can't ban myself bozo.")
            return
        if user.top_role.position >= ctx.author.top_role.position:
            await ctx.send("Imagine banning someone higher than you.")
            return
        if reason is None:
            reason = choice(reasons)
        await user.ban(reason=reason)
        await ctx.send(f"{user.mention} has been banned from the server for, {reason}.")

    # TODO: SEND A MESSAGE TO THE CHANNEL LIKE KICK
    @slash_command(description="Timeout a user from the server.")
    @commands.has_guild_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.Member, "Id or mention", required=True),
        duration: Option(
            str,
            "Duration of the timeout.",
            choices=[
                "1 min",
                "5 mins",
                "15 mins",
                "30 mins",
                "1 hour",
                "3 hours",
                "12 hours",
                "1 day",
                "1 week",
            ],
            required=True,
        ),
        *,
        reason: Option(str, "Reason for the timeout", required=False, default=None),
    ):
        """Timeout a member"""

        def duration_time(duration: str):
            switch = {
                "1 min": 1,
                "5 mins": 5,
                "15 mins": 15,
                "30 mins": 30,
                "1 hour": 60,
                "3 hours": 180,
                "12 hours": 720,
                "1 day": 1440,
                "1 week": 10080,
            }
            minutes = switch.get(duration)
            return datetime.timedelta(minutes=minutes)

        if user.id == ctx.author.id:
            await ctx.send("You can't timeout yourself bozo.")
            return
        if user.id == self.bot.user.id:
            await ctx.send("I can't timeout myself bozo.")
            return
        if user.top_role.position >= ctx.author.top_role.position:
            await ctx.send("Imagine timeouting someone higher than you.")
            return
        if reason is None:
            reason = choice(reasons)

        await user.timeout_for(duration_time(duration))
        await ctx.send(
            f"{user.mention} has been timed out for, {duration} for, {reason}."
        )


# TODO: unban command
# TODO: softban command


def setup(bot):
    bot.add_cog(Moderation(bot))
