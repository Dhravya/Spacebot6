import discord
from discord.ext import commands
import asyncio
from typing import *


async def memberCheck(guild: discord.Guild) -> List[int]:
    """Returns the memberList which contains memberIDs of all members combined"""
    memberList = []
    for member in guild.members:
        memberList.append(member.id)
    return memberList


class TicketPanelView(discord.ui.View):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="Create Ticket",
        style=discord.ButtonStyle.grey,
        emoji="📩",
        custom_id="panel",
    )
    async def ticket_open_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        embed = discord.Embed(
            description="**<a:loading:911568431315292211> Creating ticket**",
            color=0x2F3136,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        message = await interaction.original_message()
        await self.bot.cursor.execute(
            "SELECT count FROM ticket WHERE guild_id=%s", (str(interaction.guild_id),)
        )
        data = await self.bot.cursor.fetchone()
        if not data:
            await self.bot.cursor.execute(
                "INSERT INTO ticket(guild_id, count) VALUES(%s,%s)",
                (str(interaction.guild_id), 1),
            )
        if data:
            await self.bot.cursor.execute(
                "UPDATE ticket SET count = count + 1 WHERE guild_id=%s",
                (str(interaction.guild_id),),
            )

        await self.bot.cursor.execute(
            "SELECT category FROM ticket WHERE guild_id=%s",
            (str(interaction.guild_id),),
        )
        categoryCheck = await self.bot.cursor.fetchone()

        if not categoryCheck:
            await self.bot.cursor.execute(
                "SELECT * FROM ticket WHERE guild_id=%s", (str(interaction.guild_id),)
            )
            ticket_num = await self.bot.cursor.fetchone()
            ticket_channel = await interaction.guild.create_text_channel(
                f"ticket-{ticket_num[1]}"
            )
            perms = ticket_channel.overwrites_for(interaction.guild.default_role)
            perms.view_channel = False
            await ticket_channel.set_permissions(
                interaction.guild.default_role, overwrite=perms
            )
            perms2 = ticket_channel.overwrites_for(interaction.user)
            perms2.view_channel = True
            perms2.read_message_history = True
            await ticket_channel.set_permissions(interaction.user, overwrite=perms2)
            embed = discord.Embed(
                description=f"**:white_check_mark: Successfully created a ticket at {ticket_channel.mention}**",
                color=discord.Color.green(),
            )
            await message.edit(embed=embed)
            embed1 = discord.Embed(
                description=f"**Support will be with you shortly.\nTo close this ticket react with 🔒**",
                color=discord.Color.green(),
            ).set_footer(
                text=f"{self.bot.user.name} - Ticket System",
                icon_url=self.bot.user.avatar.url,
            )
            await ticket_channel.send(
                content=interaction.user.mention,
                embed=embed1,
                view=TicketCloseTop(self.bot),
            )
            await self.bot.cursor.execute(
                "INSERT INTO tickets (guild_id, channel_id, opener, switch) VALUES(%s,%s,%s,%s)",
                (
                    str(interaction.guild_id),
                    str(ticket_channel.id),
                    str(interaction.user.id),
                    True,
                ),
            )
            await self.bot.conn.commit()

        if categoryCheck:
            await self.bot.cursor.execute(
                "SELECT * FROM ticket WHERE guild_id=%s", (str(interaction.guild_id),)
            )
            data = await self.bot.cursor.fetchone()
            category = discord.utils.get(interaction.guild.categories, id=data[2])
            ticketChannel = await interaction.guild.create_text_channel(
                name=f"ticket-{data[1]}", category=category
            )
            perms = ticketChannel.overwrites_for(interaction.user)
            perms.view_channel = True
            perms.send_messages = True
            perms.read_message_history = True
            try:
                await ticketChannel.set_permissions(interaction.user, overwrite=perms)
            except discord.Forbidden:
                return await interaction.message.channel.send(
                    "I do not have the permissions to manage the ticket channel. Please contact the administrator of this server."
                )
            embed = discord.Embed(
                description=f"**:white_check_mark: Successfully created a ticket at {ticketChannel.mention}**",
                color=discord.Color.green(),
            )
            await message.edit(embed=embed)
            embed1 = discord.Embed(
                description=f"**Support will be with you shortly.\nTo close this ticket react with 🔒**",
                color=discord.Color.green(),
            ).set_footer(
                text=f"{self.bot.user.name} - Ticket System",
                icon_url=self.bot.user.avatar.url,
            )
            await ticketChannel.send(
                content=interaction.user.mention,
                embed=embed1,
                view=TicketCloseTop(self.bot),
            )
            await self.bot.cursor.execute(
                "INSERT INTO tickets (guild_id, channel_id, opener, switch) VALUES(%s,%s,%s,%s)",
                (
                    str(interaction.guild_id),
                    str(ticketChannel.id),
                    str(interaction.user.id),
                    True,
                ),
            )
            await self.bot.conn.commit()


class TicketCloseTop(discord.ui.View):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot] = None):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="Close", style=discord.ButtonStyle.gray, emoji="🔒", custom_id="top:close"
    )
    async def close_callback(
        self, button: discord.Button, interaction: discord.Interaction
    ):
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(interaction.guild_id), str(str(interaction.channel_id))),
        )
        data = await self.bot.cursor.fetchone()
        if data[3] == "closed":
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"**:x: The ticket is already closed!**",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
        await interaction.response.send_message(
            embed=discord.Embed(
                description="**Are you sure you want to close the ticket%s**",
                color=discord.Color.orange(),
            )
        )
        message = await interaction.original_message()
        await message.edit(view=TicketCloseTop2(interaction.user, message, self.bot))


class TicketCloseTop2(discord.ui.View):
    def __init__(
        self,
        buttonUser: discord.Member,
        msg: discord.Message,
        bot: Union[commands.Bot, commands.AutoShardedBot],
    ):
        super().__init__(timeout=15)
        self.user = buttonUser
        self.msg = msg
        self.bot = bot

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger)
    async def yes_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if interaction.user != self.user:
            return await interaction.channel.send(
                embed=discord.Embed(
                    description=f"**:x: You can't do that {interaction.user.mention}**",
                    color=discord.Color.red(),
                )
            )
        for child in self.children:
            child.disabled = True
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(interaction.guild_id), str(interaction.channel_id)),
        )
        member_id = await self.bot.cursor.fetchone()
        memCheck = await memberCheck(interaction.guild)
        if member_id[2] not in memCheck:
            await self.bot.cursor.execute(
                "UPDATE tickets SET switch = %s WHERE guild_id=%s AND channel_id=%s",
                (False, str(interaction.guild_id), str(interaction.channel_id)),
            )
            await self.bot.conn.commit()
            await self.msg.delete()
            await interaction.channel.send(
                embed=discord.Embed(
                    description=f"**Ticket closed by {interaction.user.mention}**",
                    color=discord.Color.orange(),
                )
            )
            return
        member = interaction.guild.get_member(member_id[2])
        if (
            member.guild_permissions.administrator
            or member.guild_permissions.manage_channels
        ):
            pass
        else:
            perms = interaction.channel.overwrites_for(member)
            perms.view_channel = False
            perms.send_messages = False
            perms.read_message_history = False
            await interaction.channel.set_permissions(member, overwrite=perms)
        await self.bot.cursor.execute(
            "UPDATE tickets SET switch = %s WHERE guild_id=%s AND channel_id=%s",
            (False, str(interaction.guild_id), str(interaction.channel_id)),
        )
        await self.bot.conn.commit()
        await self.msg.delete()
        await interaction.channel.send(
            embed=discord.Embed(
                description=f"**Ticket closed by {interaction.user.mention}**",
                color=discord.Color.orange(),
            )
        )

    @discord.ui.button(label="No", style=discord.ButtonStyle.gray)
    async def no_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if interaction.user != self.user:
            return await interaction.channel.send(
                embed=discord.Embed(
                    description=f"**:x: You can't do that {interaction.user.mention}**",
                    color=discord.Color.red(),
                )
            )
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            embed=discord.Embed(
                description=f"**:white_check_mark: Canceled closing {interaction.channel.mention}**",
                color=discord.Color.green(),
            ),
            view=self,
        )

    async def on_timeout(self):
        try:
            for child in self.children:
                if child.disabled:
                    return
            for child in self.children:
                child.disabled = True
            embed = discord.Embed(
                description=f"**:x: Oops you didn't respond within time! So, Canceled closing the ticket!**",
                color=discord.Color.red(),
            )
            await self.msg.edit(embed=embed, view=self)
        except discord.errors.NotFound:
            print("The ticket was deleted")


class TicketControlsView(discord.ui.View):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot] = None):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="Open",
        style=discord.ButtonStyle.gray,
        emoji="🔓",
        custom_id="controls:open",
    )
    async def open_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description=f":x: You can't do that {interaction.user.mention}!",
                    color=discord.Color.red(),
                )
            )
        await self.bot.cursor.execute(
            "SELECT * FROM tickets WHERE guild_id=%s AND channel_id=%s",
            (str(interaction.guild_id), str(interaction.channel_id)),
        )
        member_id = await self.bot.cursor.fetchone()
        memCheck = await memberCheck(interaction.guild)
        if member_id[2] not in memCheck:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description="**:x: This user is no more in this server!\n------------------------------------------\nThere is no use of opening this ticket!**",
                    color=discord.Color.red(),
                )
            )
        member = interaction.guild.get_member(member_id[2])
        perms = interaction.channel.overwrites_for(member)
        perms.view_channel = True
        perms.send_messages = True
        perms.read_message_history = True
        await interaction.channel.set_permissions(member, overwrite=perms)
        await self.bot.cursor.execute(
            "UPDATE tickets SET switch = %s WHERE guild_id=%s AND channel_id=%s",
            (True, str(interaction.guild_id), str(interaction.channel_id)),
        )
        await self.bot.conn.commit()
        await interaction.response.edit_message(
            embed=discord.Embed(
                description=f"**Ticket opened by {interaction.user.mention}**",
                color=discord.Color.green(),
            ),
            view=None,
        )

    @discord.ui.button(
        label="Delete",
        style=discord.ButtonStyle.gray,
        emoji="⛔",
        custom_id="controls:close",
    )
    async def delete_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description=f":x: You can't do that!", color=discord.Color.red()
                ),
                ephemeral=True,
            )
        try:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=f"**:white_check_mark: The ticket will be deleted soon**",
                    color=discord.Color.orange(),
                ),
                view=None,
            )
            await asyncio.sleep(3)
            await interaction.channel.delete()
            await self.bot.cursor.execute(
                "DELETE FROM tickets WHERE guild_id=%s AND channel_id=%s",
                (str(interaction.guild_id), str(interaction.channel_id)),
            )
            await self.bot.conn.commit()
        except discord.NotFound:
            print("The ticket was deleted")


class TicketResetView(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        message: discord.Message,
        bot: Union[commands.Bot, commands.AutoShardedBot],
    ):
        super().__init__(timeout=15)
        self.ctx = ctx
        self.msg = message
        self.bot = bot

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, emoji="✅")
    async def confirm_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if interaction.user != self.ctx.author:
            embed = discord.Embed(
                description=f":x: You can't do that {interaction.user.mention}!",
                color=discord.Color.red(),
            )
            return await self.ctx.send(embed=embed, delete_after=5)
        for child in self.children:
            child.disabled = True
        await self.bot.cursor.execute(
            "UPDATE ticket SET count = 0 WHERE guild_id=%s",
            (str(interaction.guild_id),),
        )
        await self.bot.conn.commit()
        embed = discord.Embed(
            description="**:white_check_mark: Succesfully resetted the ticket count!**",
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red, emoji="❌")
    async def decline_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if interaction.user != self.ctx.author:
            embed = discord.Embed(
                description=f":x: You can't do that {interaction.user.mention}!",
                color=discord.Color.red(),
            )
            return await self.ctx.send(embed=embed, delete_after=5)
        for child in self.children:
            child.disabled = True
        embed_ = discord.Embed(
            description="**:white_check_mark: Canceled resetting ticket count!**",
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed_, view=self)

    async def on_timeout(self):
        try:
            for child in self.children:
                if child.disabled:
                    return
            for child in self.children:
                child.disabled = True
            embed = discord.Embed(
                description=f"**:x: Oops you didn't respond within time! So, Canceled resetting ticket count!**",
                color=discord.Color.red(),
            )
            await self.msg.edit(embed=embed, view=self)
        except discord.NotFound:
            pass
