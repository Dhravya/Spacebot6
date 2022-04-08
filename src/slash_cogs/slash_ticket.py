import discord
from discord.ext import commands
from typing import Union
from views.ticket_views import *
from discord.commands import SlashCommandGroup, Option


class SlashTickets(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.bot.add_application_command(self.panel)
        self.bot.add_application_command(self.ticket)

    panel = SlashCommandGroup(
        "panel", "Ticket panel related commands"
    )

    @panel.command(description="Get help related to ticket panel")
    async def help(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Panel",
            description="**--> `panel create`: Creates a panel\nUsage: `panel create <channel> [name]`\nExample: `panel create #ticket Get a ticket`\n\n--> `panel delete`: Deletes a panel\nUsage: `panel delete <channel> [panel_id]`\nExample: `panel delete #ticket 987654321123456789`\n\n--> `panel edit`: Edits the name of a panel\nUsage: `panel edit <channel> [panel_id] (name)`\nExample: `panel edit #ticket 987654321123456789 I just changed the name of the panel!`**",
            color=discord.Color.green(),
        )
        await ctx.respond(embed=embed)

    ticket = SlashCommandGroup(
        "ticket", "Ticket related commands"
    )

    @ticket.command(description="Get help related to ticket")
    async def help(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Ticket",
            description="**--> `ticket role add` Adds a role to ticket channel. By doing this the role you add can view tickets! By default it is available for only admins\nUsage: `ticket role add <role>`\nExample: `ticket role add @MODS`\n\n--> `ticket role remove` Just the vice versa of the one stated above. Removes a role from viewing ticket\nUsage: `ticket role remove <role>`\nExample: `ticket role remove @MODS`\n\n--> `ticket reset` Resets the ticket count!\nUsage: `ticket reset`\n\n--> `ticket clean` Delete all tickets in the server\nUsage: `ticket clean`\n\n--> `ticket category` Get tickets inside a category. If you want to keep ticket view permissions, make sure to change the category permissions.\nUsage: `ticket category <category_id>`\nExample: `ticket category 98765432123456789`\n\n--> `ticket close` Closes the ticket. Use the command inside a ticket only\nUsage: `ticket close`\n\n--> `ticket add` Adds a user in the ticket. Use the command inside a ticket only\nUsage: `ticket add <user>`\nExample: `ticket add @SpaceDoggo`\n\n--> `ticket remove` Removes a user from the ticket. Use the command inside a ticket only\nUsage: `ticket remove <user>`\nExample: `ticket remove @SpaceDoggo`**",
            color=discord.Color.green(),
        )
        await ctx.respond(embed=embed)

    @panel.command(name="create", aliases=["c", "make", "add"])
    async def create_(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            discord.TextChannel,
            "The channel you want to create the panel in",
            required=True,
            default=None,
        ),
        *,
        name=Option(str, "The name of the panel", required=True, default=None),
    ):
        """Creates a panel in a channel through which users can interact and open tickets"""
        if not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="Error",
                description=":x: You don't have the permissions to create a panel in this server!",
                color=discord.Color.red(),
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        if not channel:
            embed = discord.Embed(
                description="**:x: Please enter a channel to make the panel in!**",
                color=discord.Color.red(),
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        if not name:
            embed = discord.Embed(
                description="**:x: Please enter a name!**", color=discord.Color.red()
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        if channel == ctx.channel:
            panel = discord.Embed(
                title=name,
                description="To create a ticket react with 📩",
                color=discord.Color.green(),
            )
            panel.set_footer(
                text=f"{self.bot.user.name} - Ticket Panel",
                icon_url=self.bot.user.avatar.url,
            )

            message = await channel.send(embed=panel, view=TicketPanelView(self.bot))
            await ctx.respond(
                embed=discord.Embed(
                    description=":white_check_mark: Panel created!",
                    color=discord.Color.green(),
                )
            )
            try:
                await ctx.author.send(
                    embed=discord.Embed(
                        description=f"**Panel id** of the panel you just created in <#{channel.id}>: `{message.id}`",
                        color=discord.Color.green(),
                    )
                )
            except discord.Forbidden:
                pass
            return
        if channel != ctx.channel:
            panel1 = discord.Embed(
                title=name,
                description="To create a ticket react with 📩",
                color=discord.Color.green(),
            )
            panel1.set_footer(
                text=f"{self.bot.user.name} - Ticket Panel",
                icon_url=self.bot.user.avatar.url,
            )

            message = await channel.send(embed=panel1, view=TicketPanelView(self.bot))
            embed2 = discord.Embed(
                description=f"**:white_check_mark: Successfully posted the panel in {channel.mention}\n\nPanel ID: `{message.id}`**",
                color=discord.Color.green(),
            )
            await ctx.respond(embed=embed2)

    @panel.command(name="delete", aliases=["del"])
    @commands.has_permissions(manage_channels=True)
    async def delete_(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            discord.TextChannel,
            "The channel where the panel is located",
            required=True,
            default=None,
        ),
        panel_id: Option(int, "The panel id", required=True, default=None),
    ):
        """Deletes a previously built panel in the server. Requires the `panel_id`"""
        # Fixed this error
        #! discord.errors.ExtensionFailed: Extension 'slash_cogs.slash_ticket' raised an error: ValidationError: Command description must be 1-100 characters long.
        await ctx.defer()
        message = await channel.fetch_message(panel_id)
        try:
            await message.delete()
            embed = discord.Embed(
                description="**:white_check_mark: Successfully deleted the panel!**",
                color=discord.Color.green(),
            )
            await ctx.respond(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                description="**:x: I couldn't do that!**", color=discord.Color.green()
            )
            await ctx.respond(embed=embed, ephemeral=True)
        except discord.NotFound:
            embed = discord.Embed(
                description=f"**:x: I couldn't find a panel with id `{panel_id}`! Please try again after checking the id!**"
            )
            await ctx.rspond(embed=embed, ephemeral=True)

    @panel.command(name="edit", aliases=["e"])
    async def edit_(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            discord.TextChannel,
            "The channel in which the panel is created",
            required=True,
            default=None,
        ),
        panel_id: Option(int, "The id of the panel", required=True, default=None),
        *,
        name: Option(str, "The name of the panel", required=True, default=None),
    ):
        """Edits a previously built panel in the server. Requires the `panel_id`"""
        await ctx.defer()
        message = await channel.fetch_message(panel_id)
        try:
            embed1 = discord.Embed(
                title=name,
                description="To create a ticket react with 📩",
                color=discord.Color.green(),
            )
            await message.edit(embed=embed1)
            embed = discord.Embed(
                description="**:white_check_mark: Successfully edited the panel!**",
                color=discord.Color.green(),
            )
            await ctx.respond(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                description="**:x: I couldn't do that!**", color=discord.Color.green()
            )
            await ctx.respond(embed=embed, ephemeral=True)
        except discord.NotFound:
            embed = discord.Embed(
                description=f"**:x: I couldn't find a panel with id `{panel_id}`! Please try again after checking the id!**"
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @ticket.command(name="reset")
    @commands.has_permissions(manage_channels=True)
    async def reset_(self, ctx: discord.ApplicationContext):
        """Resets the ticket count set of the server"""
        embed = discord.Embed(
            description=f"Are you sure you want to reset the **Ticket Count**?\n------------------------------------------------\nRespond Within **15** seconds!",
            color=discord.Color.orange(),
        )
        await ctx.respond(embed=embed)
        message = await ctx.interaction.original_message()
        await message.edit(embed=embed, view=TicketResetView(ctx, message, self.bot))

    @ticket.command(name="category")
    @commands.has_permissions(manage_channels=True)
    async def category_(
        self,
        ctx: discord.ApplicationContext,
        category_id: Option(
            int,
            "The category ID of the category you want to set the tickets to",
            required=False,
            default=None,
        ),
    ):
        """Sets the category for tickets. Highly reccomended."""
        try:
            if category_id is None:
                await self.bot.cursor.execute(
                    "SELECT category FROM ticket WHERE guild_id=%s",
                    (str(ctx.guild.id),),
                )
                dataCheck = await self.bot.cursor.fetchone()
                if not dataCheck:
                    return await ctx.respond(
                        embed=discord.Embed(
                            description="**:x: You have not assigned a category to tickets yet**",
                            color=discord.Color.red(),
                        ),
                        ephemeral=True,
                    )

                await self.bot.cursor.execute(
                    "SELECT * FROM ticket WHERE guild_id=%s", (str(ctx.guild.id),)
                )
                categoryFind = await self.bot.cursor.fetchone()
                cat = categoryFind[2]
                return await ctx.respond(
                    embed=discord.Embed(
                        description=f"**The category_id set for this server is {cat}**",
                        color=discord.Color.green(),
                    )
                )

            await self.bot.cursor.execute(
                "SELECT category FROM ticket WHERE guild_id=%s", (str(ctx.guild.id),)
            )
            data = await self.bot.cursor.fetchone()
            if not data:
                await self.bot.cursor.execute(
                    "SELECT * FROM ticket WHERE guild_id=%s", (str(ctx.guild.id),)
                )
                dataCheck2 = await self.bot.cursor.fetchone()
                if not dataCheck2[0]:
                    await self.bot.cursor.execute(
                        "INSERT INTO ticket (guild_id, category) VALUES(%s,%s)",
                        (str(ctx.guild.id), str(category_id)),
                    )
                else:
                    await self.bot.cursor.execute(
                        "INSERT INTO ticket (category) VALUES(%s) WHERE guild_id=%s",
                        (str(category_id), str(ctx.guild.id)),
                    )
            if data:
                await self.bot.cursor.execute(
                    "UPDATE ticket SET category = %s WHERE guild_id=%s",
                    (str(category_id), str(ctx.guild.id)),
                )
            await self.bot.conn.commit()
            try:
                category = discord.utils.get(ctx.guild.categories, id=category_id)
                overwrite = {
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        send_messages=False, view_channel=False
                    ),
                    ctx.guild.me: discord.PermissionOverwrite(
                        send_messages=True, manage_channels=True
                    ),
                }
                await category.edit(overwrites=overwrite)
            except discord.Forbidden:
                await ctx.respond(
                    embed=discord.Embed(
                        description="**Permissions missing**\n I need the `manage_channels` permission to function properly",
                        color=discord.Color.green(),
                    ),
                    ephemeral=True,
                )
            embed = discord.Embed(
                description=f"**:white_check_mark: Successfully added `{category}` as the ticket category!\n\nIf you want to keep ticket view permissions, make sure to change the category permissions.**",
                color=discord.Color.green(),
            )
            await ctx.respond(embed=embed)
        except Exception as e:
            self.bot.log.error(e)

    @ticket.command()
    @commands.has_permissions(manage_channels=True)
    async def close(self, ctx: discord.ApplicationContext):
        """Closes the ticket"""
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(ctx.guild.id), str(ctx.channel.id)),
        )
        data = await self.bot.cursor.fetchone()
        if data[3] == "close":
            return await ctx.respond(
                embed=discord.Embed(
                    description="**:x: The ticket is already closed**",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
        if ctx.channel.id != data[1]:
            return await ctx.respond(
                embed=discord.Embed(
                    description="**:x: Looks like either this channel is not a ticket channel or you aren't in the same channel**",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
        embed = discord.Embed(
            description="**Are you sure you want to close the ticket%s**",
            color=discord.Color.orange(),
        )
        await ctx.respond(embed=embed)
        message = await ctx.interaction.original_message()
        await message.edit(view=TicketCloseTop2(ctx.author, message, self.bot))

    @ticket.command()
    async def add(
        self,
        ctx: discord.ApplicationContext,
        user: Option(
            discord.Member,
            "The user you want to add to the ticket",
            required=True,
            default=None,
        ),
    ):
        """Adds a user in the ticket"""
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(ctx.guild.id), str(ctx.channel.id)),
        )
        data = await self.bot.cursor.fetchone()

        if ctx.channel.id != data[1]:
            return await ctx.respond(
                embed=discord.Embed(
                    description="**:x: Looks like either this channel is not a ticket channel or you aren't in the same channel**",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

        if user in ctx.channel.members:
            return await ctx.respond(
                embed=discord.Embed(
                    description="**:x: That user is already in the ticket**",
                    color=discord.Color.red,
                ),
                ephemeral=True,
            )

        channel: discord.TextChannel = ctx.channel
        perms = channel.overwrites_for(user)
        perms.view_channel = True
        perms.send_messages = True
        perms.read_message_history = True
        await channel.set_permissions(user, overwrite=perms)
        embed = discord.Embed(
            description=f"**:white_check_mark: Successfully added {user.mention} in the ticket!**",
            color=discord.Color.green(),
        )
        await ctx.respond(embed=embed)

    @ticket.command(aliases=["rm"])
    async def remove(
        self,
        ctx: discord.ApplicationContext,
        user: Option(
            discord.Member,
            "The user you want to remove from the ticket",
            required=True,
            default=None,
        ),
    ):
        """Removes a user from a ticket."""
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(ctx.guild.id), str(ctx.channel.id)),
        )
        data = await self.bot.cursor.fetchone()

        if ctx.channel.id != data[1]:
            return await ctx.respond(
                embed=discord.Embed(
                    description="**:x: Looks like either this channel is not a ticket channel or you aren't in the same channel**",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

        if user.id == data[2]:
            embed2 = discord.Embed(
                description=f"**:x: {user.mention} is the one who opened a ticket\nYou can't remove them from the ticket!**",
                color=discord.Color.red(),
            )
            return await ctx.respond(embed=embed2, ephemeral=True)

        if (
            user.guild_permissions.administrator
            or user.guild_permissions.manage_channels
        ):
            return await ctx.respond(
                embed=discord.Embed(
                    description="**:x: That user is a *MOD/ADMIN*.**",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

        if not user in ctx.channel.members:
            return await ctx.respond(
                embed=discord.Embed(
                    description="**:x: That user is already not in the ticket**",
                    color=discord.Color.red,
                ),
                ephemeral=True,
            )

        channel: discord.TextChannel = ctx.channel
        perms = channel.overwrites_for(user)
        perms.view_channel = False
        perms.send_messages = False
        perms.read_message_history = False
        await channel.set_permissions(user, overwrite=perms)
        embed = discord.Embed(
            description=f"**:white_check_mark: Successfully removed {user.mention} from the ticket!**",
            color=discord.Color.green(),
        )
        await ctx.respond(embed=embed)

    @ticket.command(hidden=True)
    @commands.is_owner()
    async def set(
        self,
        ctx: discord.ApplicationContext,
        *,
        num: Option(int, "The ticket count to set", required=True, default=None),
    ):
        await self.bot.cursor.execute(
            "UPDATE ticket SET count=%s WHERE guild_id=%s", (num, str(ctx.guild.id))
        )
        await self.bot.conn.commit()
        await ctx.respond(
            embed=discord.Embed(
                description=f"**:white_check_mark: Set the Ticket Count to -> `{num}`**",
                color=discord.Color.green(),
            )
        )

    @ticket.command(aliases=["how", "guide"])
    @commands.has_permissions(manage_channels=True)
    async def setup(self, ctx: discord.ApplicationContext):
        """Complete guide that shows us how to setup the perfect ticket system in the server"""
        embed = discord.Embed(
            title="__Ticket Setup__",
            description="""**How to setup a ticket system :-**

--> Create a panel by using `panel create <channel> [name]`
--> Use command `ticket category <category_id>` to setup a category (I highly reccomend using ticket categories. They are way better and you can personalize their permissions and stuff
--> You are good to go. Use `ticket` or `panel` for more info!)""",
            color=discord.Color.green(),
        ).set_footer(
            text=f"{self.bot.user.name} - Ticket System",
            icon_url=self.bot.user.avatar.url,
        )
        await ctx.respond(embed=embed)

    @ticket.command()
    async def role(
        self,
        ctx: discord.ApplicationContext,
        switch: str,
        *,
        role: Option(
            discord.Role, "The role to add or remove", required=True, default=None
        ),
    ):
        """Adds a role or removes the role from a server.\nExample: `ticket role add @SOMEROLE` `ticket role remove remove @SOMEROLE`"""
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(ctx.guild.id), str(ctx.channel.id)),
        )
        data = await self.bot.cursor.fetchone()

        if ctx.channel.id != data[1]:
            return await ctx.respond(
                embed=discord.Embed(
                    description="**:x: Looks like either this channel is not a ticket channel or you aren't in the same channel**",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

        if switch.lower() == "add":
            channel: discord.Channel = ctx.channel
            perms = channel.overwrites_for(role)
            perms.view_channel = True
            perms.send_messages = True
            perms.read_message_history = True
            await channel.set_permissions(role, overwrite=perms)
            embed = discord.Embed(
                description=f"**:white_check_mark: Successfully added {role.mention} in the ticket!**",
                color=discord.Color.green(),
            )
            await ctx.respond(embed=embed)

        if switch.lower() == "remove":
            channel: discord.Channel = ctx.channel
            perms = channel.overwrites_for(role)
            perms.view_channel = False
            perms.send_messages = False
            perms.read_message_history = False
            await channel.set_permissions(role, overwrite=perms)
            embed = discord.Embed(
                description=f"**:white_check_mark: Successfully added {role.mention} in the ticket!**",
                color=discord.Color.green(),
            )
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(SlashTickets(bot))
