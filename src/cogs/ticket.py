import discord
from discord.ext import commands
from typing import Union
from views.ticket_views import *


class Tickets(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot

        self.help_doc = "Ticket commands"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            if (
                message.author.id == self.bot.user.id
                and len(message.embeds) > 0
                and message.embeds[0].description.startswith("**Ticket closed by")
            ):
                await self.bot.cursor.execute(
                    "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
                    (str(message.guild.id), str(message.channel.id)),
                )
                data = await self.bot.cursor.fetchone()
                embed = discord.Embed(
                    description="```py\n[Support team ticket controls]```",
                    color=discord.Color.embed_background(theme="dark"),
                )
                await message.channel.send(
                    embed=embed, view=TicketControlsView(self.bot)
                )
        except AttributeError:
            pass

    @commands.group(name="panel")
    async def panel_(self, ctx: commands.Context):
        """Ticket Panel related commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Panel",
                description="**--> `panel create`: Creates a panel\nUsage: `panel create <channel> [name]`\nExample: `panel create #ticket Get a ticket`\n\n--> `panel delete`: Deletes a panel\nUsage: `panel delete <channel> [panel_id]`\nExample: `panel delete #ticket 987654321123456789`\n\n--> `panel edit`: Edits the name of a panel\nUsage: `panel edit <channel> [panel_id] (name)`\nExample: `panel edit #ticket 987654321123456789 I just changed the name of the panel!`**",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

    @commands.group(name="ticket")
    async def ticket_(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            """Ticket related commands"""
            embed = discord.Embed(
                title="Ticket",
                description="**--> `ticket role add` Adds a role to ticket channel. By doing this the role you add can view tickets! By default it is available for only admins\nUsage: `ticket role add <role>`\nExample: `ticket role add @MODS`\n\n--> `ticket role remove` Just the vice versa of the one stated above. Removes a role from viewing ticket\nUsage: `ticket role remove <role>`\nExample: `ticket role remove @MODS`\n\n--> `ticket reset` Resets the ticket count!\nUsage: `ticket reset`\n\n--> `ticket clean` Delete all tickets in the server\nUsage: `ticket clean`\n\n--> `ticket category` Get tickets inside a category. If you want to keep ticket view permissions, make sure to change the category permissions.\nUsage: `ticket category <category_id>`\nExample: `ticket category 98765432123456789`\n\n--> `ticket close` Closes the ticket. Use the command inside a ticket only\nUsage: `ticket close`\n\n--> `ticket add` Adds a user in the ticket. Use the command inside a ticket only\nUsage: `ticket add <user>`\nExample: `ticket add @SpaceDoggo#0007`\n\n--> `ticket remove` Removes a user from the ticket. Use the command inside a ticket only\nUsage: `ticket remove <user>`\nExample: `ticket remove @SpaceDoggo#0007`**",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

    @panel_.command(name="create", aliases=["c", "make", "add"])
    @commands.has_permissions(manage_channels=True)
    async def create_(
        self, ctx: commands.Context, channel: discord.TextChannel, *, name=None
    ):
        """Creates a panel in a channel through which users can interact and open tickets"""
        if not channel:
            embed = discord.Embed(
                description="**:x: Please enter a channel to make the panel in!**",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=embed)

        if not name:
            embed = discord.Embed(
                description="**:x: Please enter a name!**", color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

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
            try:
                await ctx.author.send(
                    embed=discord.Embed(
                        description=f"**Panel id** of the panel you just created in <#{channel.id}>: `{message.id}`",
                        color=discord.Color.green(),
                    )
                )
            except discord.Forbidden:
                pass
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
            await ctx.send(embed=embed2)

    @panel_.command(name="delete", aliases=["del"])
    @commands.has_permissions(manage_channels=True)
    async def delete_(
        self, ctx: commands.Context, channel: discord.TextChannel, panel_id: int
    ):
        """Deletes a previously built panel in the server. Requires the `panel_id` which is provided at the time of the creation of the panel"""
        message = await channel.fetch_message(panel_id)
        try:
            await message.delete()
            embed = discord.Embed(
                description="**:white_check_mark: Successfully deleted the panel!**",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                description="**:x: I couldn't do that!**", color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(
                description=f"**:x: I couldn't find a panel with id `{panel_id}`! Please try again after checking the id!**"
            )
            await ctx.send(embed=embed)

    @panel_.command(name="edit", aliases=["e"])
    async def edit_(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        panel_id: int,
        *,
        name: str,
    ):
        """Edits a previously built panel in the server. Requires the `panel_id` which is provided at the time of the creation of the panel"""
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
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                description="**:x: I couldn't do that!**", color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(
                description=f"**:x: I couldn't find a panel with id `{panel_id}`! Please try again after checking the id!**"
            )
            await ctx.send(embed=embed)

    @ticket_.command(name="reset")
    @commands.has_permissions(manage_channels=True)
    async def reset_(self, ctx: commands.Context):
        """Resets the ticket count set of the server"""
        embed = discord.Embed(
            description=f"Are you sure you want to reset the **Ticket Count**?\n------------------------------------------------\nRespond Within **15** seconds!",
            color=discord.Color.orange(),
        )
        message = await ctx.send(embed=embed)
        await message.edit(embed=embed, view=TicketResetView(ctx, message, self.bot))

    @ticket_.command(name="category")
    @commands.has_permissions(manage_channels=True)
    async def category_(self, ctx: commands.Context, categoryID: int = None):
        """Sets the category for tickets. Highly reccomended."""
        try:
            if categoryID is None:
                await self.bot.cursor.execute(
                    "SELECT category FROM ticket WHERE guild_id=%s",
                    (str(ctx.guild.id),),
                )
                dataCheck = await self.bot.cursor.fetchone()
                if not dataCheck:
                    return await ctx.send(
                        embed=discord.Embed(
                            description="**:x: You have not assigned a category to tickets yet**",
                            color=discord.Color.red(),
                        )
                    )

                await self.bot.cursor.execute(
                    "SELECT * FROM ticket WHERE guild_id=%s", (str(ctx.guild.id),)
                )
                categoryFind = await self.bot.cursor.fetchone()
                cat = categoryFind[2]
                return await ctx.send(
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
                        (str(ctx.guild.id), str(categoryID)),
                    )
                else:
                    await self.bot.cursor.execute(
                        "INSERT INTO ticket (category) VALUES(%s) WHERE guild_id=%s",
                        (str(categoryID), str(ctx.guild.id)),
                    )
            if data:
                await self.bot.cursor.execute(
                    "UPDATE ticket SET category = %s WHERE guild_id=%s",
                    (str(categoryID), str(ctx.guild.id)),
                )
            await self.bot.conn.commit()
            try:
                category = discord.utils.get(ctx.guild.categories, id=categoryID)
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
                await ctx.send(
                    embed=discord.Embed(
                        description="**Permissions missing**\n I need the `manage_channels` permission to function properly",
                        color=discord.Color.green(),
                    )
                )
            embed = discord.Embed(
                description=f"**:white_check_mark: Successfully added `{category}` as the ticket category!\n\nIf you want to keep ticket view permissions, make sure to change the category permissions.**",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
        except Exception as e:
            self.bot.log.error(e)

    @ticket_.command()
    @commands.has_permissions(manage_channels=True)
    async def close(self, ctx: commands.Context):
        """Closes the ticket"""
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(ctx.guild.id), str(ctx.channel.id)),
        )
        data = await self.bot.cursor.fetchone()
        if data[3] == "close":
            return await ctx.send(
                embed=discord.Embed(
                    description="**:x: The ticket is already closed**",
                    color=discord.Color.red(),
                )
            )
        if ctx.channel.id != data[1]:
            await ctx.send(
                embed=discord.Embed(
                    description="**:x: Looks like either this channel is not a ticket channel or you aren't in the same channel**",
                    color=discord.Color.red(),
                )
            )
        embed = discord.Embed(
            description="**Are you sure you want to close the ticket%s**",
            color=discord.Color.orange(),
        )
        message = await ctx.send(embed=embed)
        await message.edit(view=TicketCloseTop2(ctx.author, message, self.bot))

    @ticket_.command()
    async def add(self, ctx: commands.Context, user: discord.Member):
        """Adds a user in the ticket"""
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(ctx.guild.id), str(ctx.channel.id)),
        )
        data = await self.bot.cursor.fetchone()

        if ctx.channel.id != data[1]:
            await ctx.send(
                embed=discord.Embed(
                    description="**:x: Looks like either this channel is not a ticket channel or you aren't in the same channel**",
                    color=discord.Color.red(),
                )
            )

        if user in ctx.channel.members:
            return await ctx.send(
                embed=discord.Embed(
                    description="**:x: That user is already in the ticket**",
                    color=discord.Color.red,
                )
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
        await ctx.send(embed=embed)

    @ticket_.command(aliases=["rm"])
    async def remove(self, ctx: commands.Context, user: discord.Member):
        """Removes a user from a ticket. Note: It can't be the user who created the ticket or a person with admin"""
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(ctx.guild.id), str(ctx.channel.id)),
        )
        data = await self.bot.cursor.fetchone()

        if ctx.channel.id != data[1]:
            await ctx.send(
                embed=discord.Embed(
                    description="**:x: Looks like either this channel is not a ticket channel or you aren't in the same channel**",
                    color=discord.Color.red(),
                )
            )

        if user.id == data[2]:
            embed2 = discord.Embed(
                description=f"**:x: {user.mention} is the one who opened a ticket\nYou can't remove them from the ticket!**",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed2)

        if (
            user.guild_permissions.administrator
            or user.guild_permissions.manage_channels
        ):
            return await ctx.send(
                embed=discord.Embed(
                    description="**:x: That user is a *MOD/ADMIN*.**",
                    color=discord.Color.red(),
                )
            )

        if not user in ctx.channel.members:
            return await ctx.send(
                embed=discord.Embed(
                    description="**:x: That user is already not in the ticket**",
                    color=discord.Color.red,
                )
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
        await ctx.send(embed=embed)

    @ticket_.command(hidden=True)
    @commands.is_owner()
    async def set(self, ctx: commands.Context, *, num: int):
        await self.bot.cursor.execute(
            "UPDATE ticket SET count=%s WHERE guild_id=%s", (num, str(ctx.guild.id))
        )
        await self.bot.conn.commit()
        await ctx.send(
            embed=discord.Embed(
                description=f"**:white_check_mark: Set the Ticket Count to -> `{num}`**",
                color=discord.Color.green(),
            )
        )

    @ticket_.command(aliases=["how", "guide"])
    @commands.has_permissions(manage_channels=True)
    async def setup(self, ctx: commands.Context):
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
        await ctx.send(embed=embed)

    @ticket_.command()
    async def role(self, ctx: commands.Context, switch: str, *, role: discord.Role):
        """Adds a role or removes the role from a server.\nExample: `ticket role add @SOMEROLE` `ticket role remove remove @SOMEROLE`"""
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(ctx.guild.id), str(ctx.channel.id)),
        )
        data = await self.bot.cursor.fetchone()

        if ctx.channel.id != data[1]:
            await ctx.send(
                embed=discord.Embed(
                    description="**:x: Looks like either this channel is not a ticket channel or you aren't in the same channel**",
                    color=discord.Color.red(),
                )
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
            await ctx.send(embed=embed)

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
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Tickets(bot))
