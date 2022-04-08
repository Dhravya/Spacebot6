import asyncio

from discord import utils, Embed, Color, Interaction, SelectOption
from discord.ui import View, Select
from discord.ext.commands import Command, Cog, HelpCommand, Context, Group

ignored_cogs = [
    "jishaku",
    "loggingcog",
    "errorhandler",
    "ipcroutes",
    "background",
    "errorhandler",
    "funslash",
]


class MyHelp(HelpCommand):
    def __init__(self):
        super().__init__()

    async def command_callback(self, ctx, *, cmd=None):
        """
        To make the help for Cog case-insensitive
        """
        await self.prepare_help_command(ctx, cmd)
        bot = ctx.bot

        if cmd is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        # Check if it's a cog
        cog = None
        _cog = [cog for cog in ctx.bot.cogs if cog.lower() == cmd.lower()]
        if _cog:
            cog = _cog[0]
        if cog is not None:
            return await self.send_cog_help(ctx.bot.get_cog(cog))

        maybe_coro = utils.maybe_coroutine

        # If it's not a cog then it's a command.
        # Since we want to have detailed errors when someone
        # passes an invalid subcommand, we need to walk through
        # the command group chain ourselves.
        keys = cmd.split(" ")
        cmd = bot.all_commands.get(keys[0])
        if cmd is None:
            string = await maybe_coro(
                self.command_not_found, self.remove_mentions(keys[0])
            )
            return await self.send_error_message(string)

        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)
            except AttributeError:
                string = await maybe_coro(
                    self.subcommand_not_found, cmd, self.remove_mentions(key)
                )
                return await self.send_error_message(string)
            else:
                if found is None:
                    string = await maybe_coro(
                        self.subcommand_not_found, cmd, self.remove_mentions(key)
                    )
                    return await self.send_error_message(string)
                cmd = found

        if isinstance(cmd, Group):
            return await self.send_group_help(cmd)
        else:
            return await self.send_command_help(cmd)

    async def send_bot_help(self, mapping):
        """
        Bot's main help command
        """
        _bot = self.context.bot

        embed = Embed(
            color=Color.og_blurple(),
            description=_bot.description
            + f"Prefix: `{await _bot.get_prefix(self.context.message)}`",
            timestamp=self.context.message.created_at,
        )
        for cog_name in _bot.cogs:
            if cog_name.lower() in ignored_cogs:
                continue
            cog: Cog = _bot.get_cog(cog_name)
            try:
                cog_help = cog.help_doc
            except AttributeError:
                cog_help = None
            embed.add_field(
                name=f"{cog.qualified_name.capitalize()} category ({len(cog.get_commands())} commands)",
                value=f"> {cog_help or 'No help text'}",  # FIXED #14
                inline=False,
            )

        embed.set_author(name=f"Bot help", icon_url=_bot.user.display_avatar.url)
        embed.set_footer(
            text=f"Requested by {self.context.author}",
            icon_url=self.context.author.display_avatar.url,
        )
        embed.set_thumbnail(url=_bot.user.display_avatar.url)
        view = HelpView()
        view.add_item(NavigatorMenu(self.context))
        view.message = await self.context.reply(
            embed=embed, mention_author=False, view=view
        )
        await asyncio.sleep(180)
        for views in view.children:
            views.disabled = True
        await view.message.edit(embed=embed, view=view)

    async def send_command_help(self, cmd: Command):
        """
        Called when a command arg is given
        """
        command_help_dict = {
            "aliases": " ,".join(cmd.aliases) or "No aliases for this command",
            "description": cmd.description
            or cmd.brief
            or cmd.short_doc
            or "No command help",
        }
        command_signature = ""
        for arg in cmd.signature.split(" ")[: len(cmd.params) - 2]:
            if "=" in arg:
                parsed_arg = "{" + arg.split("=")[0].strip("[]<>]") + "}"
            else:
                parsed_arg = "[" + arg.strip("[]<>") + "]"
                if parsed_arg == "[]":
                    parsed_arg = ""
            command_signature += parsed_arg + " "
        usage = f"```py\n{await self.context.bot.get_prefix(self.context.message)}{cmd.name} {command_signature}\n```"
        embed = Embed(
            color=Color.og_blurple(),
            description="\n".join(
                f"`{key}` : {command_help_dict[key]}"
                for key in command_help_dict.keys()
            ),
        )
        embed.set_author(
            name=f"`{cmd.name}` command",
            icon_url=self.context.bot.user.display_avatar.url,
        )
        embed.add_field(name="Usage:", value=usage)
        embed.set_footer(
            text="[] means required arguments | {} means optional arguments"
        )
        await self.context.reply(embed=embed, mention_author=False)

    async def send_group_help(self, group: Group):
        """
        Group command help
        """
        desc = "\n".join(
            f"`{cmd.name}` : {cmd.short_doc or 'No help text'}"
            for cmd in group.commands
        )
        embed = Embed(
            description=group.description
            or f"`{group.qualified_name.capitalize()}` group" + desc,
            color=Color.og_blurple(),
        )
        await self.context.reply(embed=embed, mention_author=False)

    async def send_cog_help(self, cog: Cog):
        """
        Help for a specific cog, gets embed with 'cog_embed'
        """
        embed = await cog_embed(cog, self.context)
        await self.context.reply(embed=embed, mention_author=False)


class HelpView(View):
    def __init__(self):
        super().__init__(timeout=180)


class NavigatorMenu(Select):
    def __init__(self, ctx: Context) -> None:
        self.context: Context = ctx
        options = []
        for cog_name in ctx.bot.cogs:
            if cog_name.lower() in ignored_cogs:
                continue
            cog: Cog = ctx.bot.get_cog(cog_name)
            options.append(
                SelectOption(
                    label=f"{cog.qualified_name.capitalize()} commands",
                    description=cog.description.replace("cog", "module"),
                )
            )
        super().__init__(placeholder="Navigate to a category", options=options)

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.context.author.id:
            return await interaction.response.send_message(
                f"This is not your help command.",
                ephemeral=True,
            )
        cog_s = [
            self.context.bot.get_cog(cog)
            for cog in self.context.bot.cogs
            if self.values[0].lower().replace(" commands", "")
            == self.context.bot.get_cog(cog).qualified_name.lower()
        ]
        embed = await cog_embed(cog_s[0], self.context)
        await interaction.response.defer()
        await interaction.message.edit(embed=embed)


async def cog_embed(cog: Cog, ctx: Context):
    desc = "\n".join(
        f"`{cmd.name}` - {cmd.description or cmd.short_doc or 'No command help'}"
        for cmd in cog.get_commands()
    )
    embed = (
        Embed(
            color=Color.og_blurple(),
            description=f"Use `{await ctx.bot.get_prefix(ctx.message)}help <command>` for more info about commands\n\n"
            + desc,
        )
        .set_author(
            name=f"{cog.qualified_name.capitalize()} category",
            icon_url=ctx.bot.user.display_avatar.url,
        )
        .set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url
        )
    )
    return embed


def setup(bot):
    pass
