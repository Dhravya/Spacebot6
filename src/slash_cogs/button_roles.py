import discord
from discord.commands import slash_command
from discord.ext import commands
from views.button_roles_views import ModalButton
from utility.db.database import Database


class ButtonRoles(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.help_doc = "Auto-roles for your server."
        self.databaseInstance = Database(self.bot)

    @slash_command()
    async def button_roles(self, ctx: discord.ApplicationContext):
        view = discord.ui.View()
        view.add_item(ModalButton(databaseInstance=self.databaseInstance))
        await ctx.respond("Click the button below to set up button roles", view=view)


def setup(bot):
    bot.add_cog(ButtonRoles(bot))
