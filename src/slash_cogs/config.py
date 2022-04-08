import discord
from discord.ext import commands
from discord.commands import slash_command, Option, SlashCommandGroup
from typing import Union

from utility.db.database import Database
from views.config_views import LoggingConfigModal
import asyncio


async def sleep(seconds: int) -> None:
    await asyncio.sleep(seconds)


class Config(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot
        self.help_doc = "Config commands to customize SpaceBot for your server"

        self.database = Database(self.bot)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await asyncio.sleep(5)
        self.database = Database(self.bot)

        self.bot.add_application_command(self.config)

    config = SlashCommandGroup(
        "config",
        "Commands to configure the bot to your needs",
    )

    # Logging commands
    logging = config.create_subgroup("logging", "Commands to configure logging")

    @logging.command()
    async def setup(self, ctx: discord.ApplicationContext) -> None:
        """
        Setup the logging for the bot
        """
        await ctx.interaction.response.send_modal(LoggingConfigModal(self.bot))

    @config.command()
    async def prefix(self, ctx: commands.Context, *, prefix: str) -> None:
        """
        Set the bot's prefix
        """
        await ctx.defer(ephemeral=True)
        if len(prefix) > 5:
            await ctx.send("Prefix must be less than 5 characters")
            return
        await self.database.set_prefix(str(ctx.guild.id), prefix)

        await ctx.respond("Prefix set to `{}`".format(prefix), ephemeral=True)

    @config.command()
    async def toggle_rep(self, ctx: discord.ApplicationContext):
        """
        Toggle the rep system on or off
        """
        await ctx.defer(ephemeral=True)

        await self.bot.cursor.execute(
            "SELECT guild_id, rep_toggle FROM Guilds WHERE guild_id = %s",
            (str(ctx.guild.id),),
        )
        guild_info = await self.bot.cursor.fetchone()
        if not guild_info:
            await self.bot.cursor.execute(
                "INSERT INTO Guilds (guild_id, rep_toggle) VALUES (%s, %s)",
                (str(ctx.guild.id), "1"),
            )
            return await ctx.respond("Reputation system turned on")
        toggle = guild_info[1]

        await self.bot.cursor.execute(
            "UPDATE Guilds SET rep_toggle = NOT rep_toggle WHERE guild_id = %s",
            (str(ctx.guild.id),),
        )

        await ctx.respond(
            f"Rep system turned {'off' if toggle else 'on'}", ephemeral=True
        )


def setup(bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
    bot.add_cog(Config(bot))
