import discord
from typing import Union
from discord.ext import commands
from discord.ext.commands import slash_command
import re
from utility.db.database import Database


class Reputation(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.help_docs = (
            "Reputation system. Collect reputation from your server members!"
        )
        self.bot = bot
        self.database = Database(bot)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        # Check for thank words in the message
        if message.author.bot:
            return

        has_thank = await self.look_for_word(message.content)
        if has_thank:

            await self.bot.cursor.execute(
                "SELECT guild_id, rep_toggle FROM Guilds WHERE guild_id = %s",
                (str(message.guild.id),),
            )
            guild_info = await self.bot.cursor.fetchone()
            if not guild_info:
                await self.bot.cursor.execute(
                    "INSERT INTO Guilds (guild_id, rep_toggle) VALUES (%s, %s)",
                    (str(message.guild.id), "0"),
                )
                return
            if not guild_info[1]:
                return
            try:
                thank_whom = message.mentions[0]
            except IndexError:
                return
            if thank_whom == message.author:
                return

            up = await self.database.add_reputation(thank_whom.id)
            if not up == 0:
                await message.channel.send(
                    f"{thank_whom.name} has been thanked! They now have {up} reputation!"
                )

    @staticmethod
    async def look_for_word(string: str):
        """Returns true if string has a thank word uring regex"""
        pattern = r"\b(thank|thanks|thx|thnx|thnks|thnk|thnkz|thnksz|tysm|ty)\b"

        return re.compile(pattern, flags=re.IGNORECASE).search(string)

    @slash_command()
    async def rep(self, ctx: commands.Context, user: discord.User = None):
        """Get the reputation of a user"""
        if user is None:
            user = ctx.author
        rep = await self.bot.cursor.execute(
            "SELECT reputation FROM reputation WHERE user_id = %s", (str(user.id),)
        )
        # rep = rep.fetchone()
        if rep is None:
            rep = 0
        await ctx.respond(f"{user.name} has **{rep}** reputation!")

    @slash_command()
    async def rep_leaderboard(self, ctx: discord.ApplicationContext):
        """Get the reputation leaderboard"""
        await ctx.defer()
        member_ids = [str(member.id) for member in ctx.guild.members]

        # Get the reputation of each member
        await self.bot.cursor.execute(
            "SELECT user_id, reputation FROM reputation WHERE user_id IN %s",
            (tuple(member_ids),),
        )
        rep = await self.bot.cursor.fetchall()
        rep = {str(r[0]): r[1] for r in rep}

        # Sort the reputation
        rep = sorted(rep.items(), key=lambda x: x[1], reverse=True)

        # Get the top 10
        rep = rep[:10]

        # Get the member objects
        members = [ctx.guild.get_member(int(r[0])) for r in rep]

        # Make the embed
        embed = discord.Embed(
            title="Reputation Leaderboard",
            description="Top 10 members with the most reputation",
            color=0x2F3136,
        )
        for i, member in enumerate(members):
            embed.add_field(
                name=f"#{i + 1} {member.name}{member.discriminator}",
                value=f"`{rep[i][1]}` **rep**",
                inline=False,
            )
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Reputation(bot))
