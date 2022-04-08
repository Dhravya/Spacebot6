import discord
from typing import Union
from discord.ext import commands
import logging
import random
import asyncio


class RoastAgainButton(discord.ui.View):
    def __init__(
        self,
        user: discord.Member,
        target: discord.Member,
        context: commands.Context,
        bot: Union[commands.Bot, commands.AutoShardedBot],
    ) -> None:
        super().__init__()
        self.user = user
        self.ctx = context
        self.target = target
        self.bot = bot

    async def on_timeout(self) -> None:

        for button in self.children:
            button.disabled = True
        return await super().on_timeout()

    @discord.ui.button(label="Roast Back", style=discord.ButtonStyle.green, emoji="😂")
    async def roast_again(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.user:
            return await interaction.response.send_message(
                "That roast wasn't against you!", ephemeral=True
            )

        await self.ctx.invoke(self.bot.get_command("roast"), user=self.target)

        for button in self.children:
            button.disabled = True
        await interaction.message.edit(view=self)


class DarkJokeAgainButton(discord.ui.View):
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__()
        self.ctx = ctx

    async def on_timeout(self) -> None:

        for button in self.children:
            button.disabled = True
        return await super().on_timeout()

    @discord.ui.button(label="Get one more", style=discord.ButtonStyle.green, emoji="💀")
    async def dark_joke_again(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )

        await self.ctx.invoke(self.ctx.bot.get_command("darkjoke"))

        for button in self.children:
            button.disabled = True
        await interaction.message.edit(view=self)


class DadJokeAgainButton(discord.ui.View):
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__()
        self.ctx = ctx

    async def on_timeout(self) -> None:

        for button in self.children:
            button.disabled = True
        return await super().on_timeout()

    @discord.ui.button(
        label="Get one more",
        style=discord.ButtonStyle.green,
        emoji="<:harold:906787943841140766>",
    )
    async def dad_joke_again(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )

        await self.ctx.invoke(self.ctx.bot.get_command("dadjoke"))

        for button in self.children:
            button.disabled = True
        await interaction.message.edit(view=self)


class GetComicAgainButton(discord.ui.View):
    def __init__(self, ctx, url: str):
        super().__init__()
        self.ctx = ctx
        self.url = url

        self.add_item(discord.ui.Button(label="Link", url=self.url))

    async def on_timeout(self) -> None:

        for button in self.children:
            button.disabled = True
        return await super().on_timeout()

    @discord.ui.button(label="Get one more", style=discord.ButtonStyle.green, emoji="📖")
    async def get_comic_again(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )
        try:
            self.children[0].disabled = True
            await interaction.message.edit(view=self)
        except Exception as e:
            # Log the error
            logging.log(logging.ERROR, e, exc_info=True)

        await self.ctx.invoke(self.ctx.bot.get_command("comic"))


class BeerOfferView(discord.ui.View):
    def __init__(self, ctx: commands.Context, user: discord.Member) -> None:
        super().__init__(timeout=120)

        self.user = user
        self.ctx = ctx
        self.reacted = False

    async def on_timeout(self) -> None:

        for button in self.children:
            button.disabled = True
        return await super().on_timeout()

    async def on_timeout(self) -> None:
        if not self.reacted:
            for button in self.children:
                button.disabled = True
            embed = discord.Embed(
                title="Beer Offer",
                description=f"{self.user.mention} doesn't want to have beer with you :( ",
                color=discord.Color.red(),
            )
            embed.set_author(
                name=self.ctx.author.name, icon_url=self.ctx.author.avatar.url
            )
            await self.ctx.send(embed=embed)
        return await super().on_timeout()

    @discord.ui.button(label="Beer", style=discord.ButtonStyle.green, emoji="🍺")
    async def beer_callback(
        self, button: discord.Button, interaction: discord.Interaction
    ):
        if not interaction.user.id == self.user.id:
            return await interaction.response.send_message(
                "That's not your beer!", ephemeral=True
            )

        for button in self.children:
            button.disabled = True
        await interaction.message.edit(view=self)
        self.reacted = True
        return await interaction.response.send_message(
            f"{self.user.mention} has a *Parrtyyyyyyyy* with {self.ctx.author.mention}! :beer:"
        )


class CoinFlipAgainView(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__()
        self.ctx = ctx

    async def on_timeout(self) -> None:

        for button in self.children:
            button.disabled = True
        return await super().on_timeout()

    @discord.ui.button(label="Flip Again", style=discord.ButtonStyle.green, emoji="🎲")
    async def flip_again(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )

        await interaction.response.send_message(
            "You flipped again!", ephemeral=True, delete_after=0.2
        )
        return await self.ctx.invoke(
            self.ctx.bot.get_command("coinflip"), message=interaction.message
        )


class BeerPartyView(discord.ui.View):
    def __init__(self, msg: discord.Message, ctx: commands.Context):
        super().__init__(timeout=60)
        self.msg = msg
        self.clicked = [ctx.author.id]
        self.ctx = ctx

    @discord.ui.button(
        label="Join the Party", style=discord.ButtonStyle.green, emoji="🍻"
    )
    async def callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if interaction.user == self.ctx.author:
            embed = discord.Embed(
                description="**:x: You are already chilling in the party cuz the party is your's lol :beers:**",
                color=discord.Color.red(),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.user.id in self.clicked:
            embed = discord.Embed(
                description="**:x: You are already chilling in the party :beers:**",
                color=discord.Color.red(),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        self.clicked.append(interaction.user.id)
        embed = discord.Embed(
            description=f"**{interaction.user.mention} has just joined the party 🍻!**",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        embed = discord.Embed(
            title="The Party Ended",
            description=f"**The party :beers: was joined by:\n\n{self.joins(self.clicked)}**",
            color=discord.Color.green(),
        )
        await self.msg.channel.send(embed=embed)
        embed2 = discord.Embed(
            title="The Beer Party Ended, if you didn't join wait for the next one :beers:!",
            color=discord.Color.orange(),
        )
        await self.msg.edit(embed=embed2, view=self)

    def joins(self, list: list):
        return "\n".join([f"<@{i}>" for i in list])
