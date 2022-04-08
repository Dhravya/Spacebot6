import discord
from discord.ext import commands
from typing import Union, Optional
from discord.commands import slash_command, Option
import datetime


class BugReportModal(discord.ui.Modal):
    def __init__(
        self,
        bot: Union[commands.Bot, commands.AutoShardedBot],
        attachment: Optional[discord.Attachment],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.screenshot = attachment

        self.add_item(
            discord.ui.InputText(
                label="Title",
                placeholder="Title of the bug",
            )
        )

        self.add_item(
            discord.ui.InputText(
                label="Description",
                placeholder="Describe the bug. Give a brief explanation of the bug.",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            title = self.children[0].value
            description = self.children[1].value
            embed = discord.Embed(
                title=f"New Bug: {title}",
                description=description,
                color=discord.Color.red(),
            ).set_footer(
                text=f"Reported by {interaction.user} ({interaction.user.id})\n in {interaction.guild.name} ({interaction.guild.id})",
                icon_url=interaction.user.avatar.url,
            )
            embed.timestamp = datetime.datetime.now()
            embed.set_image(url=self.screenshot.url) if self.screenshot else None
            SPACEDOGGO = await self.bot.fetch_user(881861601756577832)
            await SPACEDOGGO.send(embed=embed)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=":white_check_mark: Bug reported successfully!",
                    color=discord.Color.green(),
                )
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f":x: Error: {str(e).capitalize()}",
                    color=discord.Color.red(),
                )
            )


class SlashCommands(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]):
        self.bot = bot

        self.help_doc = "Slash commands"

    @slash_command()
    async def bug_report(
        self,
        ctx: discord.ApplicationContext,
        screenshot: Option(
            discord.Attachment,
            "Provide a screenshot of the bug",
            required=False,
            default=None,
        ),
    ):
        """Report a bug"""
        file_formats = ["png", "jpg", "jpeg", "gif", "webp"]
        if not screenshot.filename.split(".")[-1].lower() in file_formats:
            return await ctx.send(
                embed=discord.Embed(
                    description=f":x: Error: Invalid file format. Please provide a valid screenshot.",
                    color=discord.Color.red(),
                )
            )
        screenshot = screenshot or None
        await ctx.interaction.response.send_modal(
            BugReportModal(self.bot, screenshot, title="Report a bug")
        )


def setup(bot):
    bot.add_cog(SlashCommands(bot))
