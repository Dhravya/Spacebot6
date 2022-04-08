import discord
import datetime


def help_embed():
    em = discord.Embed(
        title="🔴 ***SPACEBOT HELP***",
        description=f"""
        > SpaceBot is an open source feature packed discord bot. Navigate the help menu to see all commands!
    
        Use <@881862674051391499> help `command` to get more information about a command.

        [Invite](https://dsc.gg/spacebt) | [Spacebot is Open Source!](https://github.com/dhravya/spacebot)
        """,
    )
    em.set_image(
        url="https://images-ext-2.discordapp.net/external/MWmqAGeEWIpEaaq9rcMCrPYzMEScRGxEOB4ao9Ph2s0/https/media.discordapp.net/attachments/888798533459775491/903219469650890862/standard.gif"
    )
    em.set_footer(text="Join the Coding horizon now!!")
    # use custom colour
    em.colour = 0x2F3136
    return em


def cog_help_generator(bot: discord.ext.commands.Bot, cog_name, title):
    """Generates the string with all command names with their description"""
    cog = bot.get_cog(cog_name)
    if cog is None:
        return f"{cog_name} is not a valid cog!"
    else:
        commands = cog.get_commands()
        if len(commands) == 0:
            return f"{cog_name} has no commands!"
        else:
            help_string = ""
            for command in commands:
                help_string += f"**{command.name}** - {command.help}\n"
            description = help_string
    return discord.Embed(
        title=title, description=description, color=0x2F3136
    ).set_footer(
        text="Use `@Spacebot help <command>` to get additional help on a specific command."
    )


class HelpOptions(discord.ui.View):
    def __init__(self, user, bot):
        super().__init__()
        self.user = user
        self.bot = bot
        self.add_item(
            discord.ui.Button(
                label="Join discord.io/code",
                url="https://discord.io/code",
                row=2,
            )
        )
        self.add_item(
            discord.ui.Button(label="Meet the Developer", url="https://dhravya.me")
        )
        self.add_item(
            discord.ui.Button(
                label="Hosted on Epikhost",
                url="https://discord.gg/vTpkbk8Q64",
                row=2,
                emoji="<:epikhostlogo:859403955531939851>",
                style=discord.ButtonStyle.success,
            )
        )

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, emoji="🗑️", row=3)
    async def delete_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.user:
            return await interaction.response.send_message(
                "You didn't ask for the help command!", ephemeral=True
            )
        await interaction.message.delete()

    @discord.ui.button(
        label="Back to home", style=discord.ButtonStyle.primary, emoji="🏠", row=3
    )
    async def back_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.user:
            return await interaction.response.send_message(
                "You didn't ask for the help command!", ephemeral=True
            )
        view = HelpOptions(user=interaction.user, bot=self.bot)
        await interaction.message.edit(embed=help_embed(), view=view)

    @discord.ui.select(
        placeholder="Select a Command Category",
        min_values=1,
        max_values=1,
        # One option for every cog
        # Generate a list of cog names with their values being the cog name
        options=[discord.SelectOption(label="Fun commands", value="Fun", emoji="😂")],
    )
    async def select_callback(self, select, interaction):
        if not interaction.user == self.user:
            return await interaction.response.send_message(
                "You didn't ask for the help command!", ephemeral=True
            )

        if select.values[0]:
            await interaction.response.edit_message(
                embed=cog_help_generator(
                    self.bot, select.values[0], f"**{select.values[0]}** Help!"
                )
            )
