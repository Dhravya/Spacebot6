import discord
from discord.ext import commands


class ErrorView(discord.ui.View):
    def __init__(self, ctx: commands.Context, command_name: str) -> None:
        super().__init__()
        self.ctx = ctx
        self.command_name = command_name

    @discord.ui.button(label="Get help", style=discord.ButtonStyle.gray, emoji="💡")
    async def get_help(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )
        command = self.ctx.bot.get_command(self.command_name)
        if command is None:
            return await interaction.response.send_message(
                f"I don't know how to {self.command_name}!"
            )
        # Get command help
        help = command.help
        if help is None:
            return await interaction.response.send_message("Couldnt get help")
        alias_string = ", ".join([f"`{i}`" for i in command.aliases])
        embed = discord.Embed(
            title=f"Help for {self.command_name}",
            description=f"{help}\n\nAliases: {alias_string}",
            color=0x57F287,
        )

        embed.add_field(
            name="Usage",
            value=f"{self.ctx.prefix}{self.command_name} `{command.usage}`",
            inline=True,
        )
        if command.params:
            for param in command.params:
                if not param in ["self", "ctx"]:
                    embed.add_field(
                        name=f"{param}", value=f"{command.params[param]}", inline=True
                    )

        await interaction.response.send_message(embed=embed)
        for button in self.children:
            button.disabled = True
        await interaction.message.edit(view=self)
