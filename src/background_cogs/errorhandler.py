import discord
from discord.ext import commands
from typing import Union

from views.error_views import ErrorView


class ErrorHandler(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: Union[commands.Context, discord.ApplicationContext],
        error: Union[commands.CommandError, discord.ApplicationCommandError],
    ) -> None:
        if hasattr(ctx.command, "on_error"):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        error = getattr(error, "original", error)

        self.bot.log.error(
            f"{ctx.author} ran command {ctx.command} with error: {error}"
        )

        # Check if the error is a command error
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Missing Arguments",
                description=f"{ctx.command} requires the following arguments: `{[error.param.name]}`",
                color=0xED4245,
            )
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar.url
            )
            embed.set_thumbnail(url="https://emoji.discord.st/emojis/Error.png")
            embed.set_footer(
                text=f"💡 Tip: Use the {await self.bot.get_prefix(ctx.message)}help {ctx.command.name} command to see the usage of this command!"
            )
            view = ErrorView(ctx, str(ctx.command))
            return await ctx.send(embed=embed, view=view)

        if isinstance(error, commands.BotMissingPermissions):
            permissions = "\n".join(
                [i.replace("_", " ").upper() for i in error.missing_permissions]
            )
            embed = discord.Embed(
                name="I'm missing some permissions!",
                description=f"I need the following permissions to run this command:\n**{permissions}**",
                color=0xED4245,
            )
            await ctx.send(embed=embed)
            return

        try:
            if isinstance(error.original, commands.errors.MissingPermissions):
                permissions = "\n".join(
                    [i.replace("_", " ").upper() for i in error.missing_permissions]
                )
                embed = discord.Embed(
                    name="You're missing some permissions!",
                    description=f"You need the following permissions to run this command:\n**{permissions}**",
                    color=0xED4245,
                )
                await ctx.send(embed=embed)
                return

            if isinstance(error.original, commands.errors.BotMissingPermissions):
                permissions = "\n".join(
                    [i.replace("_", " ").upper() for i in error.missing_permissions]
                )
                embed = discord.Embed(
                    name="I'm missing some permissions!",
                    description=f"I need the following permissions to run this command:\n`{permissions}`",
                    color=0xED4245,
                )
            await ctx.send(embed=embed)
            return
        except AttributeError:
            pass

        if isinstance(error, commands.MissingPermissions):
            permissions = "\n".join(
                [i.replace("_", " ").upper() for i in error.missing_permissions]
            )
            embed = discord.Embed(
                name="You're missing some permissions!",
                description=f"You need the following permissions to run this command:\n**{permissions}**",
                color=0xED4245,
            )
            await ctx.send(embed=embed)
            return


def setup(bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
    bot.add_cog(ErrorHandler(bot))
