import discord
from discord.ext import commands
from discord.commands import slash_command, SlashCommandGroup, Option
from typing import Union

from utility.text.safe_message import safe_message
from utility.text.britishify import strong_british_accent
from utility.text.uwufy import owofy
from utility.web.safe_aiohttp import aiohttp_get
from views.fun_views import *


class FunSlash(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot
        self.bot.log.debug(f"Loaded {self.__cog_name__} cog")

    @slash_command(name="owo")
    async def owofy(self, ctx: commands.Context, *, text: str) -> None:
        """
        Haiiii owoowoowoo
        """
        msg = safe_message(text)

        owofied = owofy(msg)
        is_guild = True
        if not isinstance(ctx.channel, discord.TextChannel):
            is_guild = False
        if not ctx.channel.permissions_for(ctx.me).manage_webhooks or not is_guild:
            embed = discord.Embed(
                title="OwO", description=owofied, color=self.bot.theme_colour["default"]
            )
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar.url
            )
            embed.set_thumbnail(
                url="https://www.kindpng.com/picc/m/236-2362818_anime-sempai-animegirl-heart-kawaii-cute-anime-girl.png"
            )
            embed.set_footer(
                text="💡 Tip: Use the `owofy` command in a server where I have the Manage Webhooks permission and see the magic!"
            )
            await ctx.send(embed=embed)
            await ctx.respond("Successfully sent the Owofied text!", ephemeral=True)

        webhook = None
        for hook in await ctx.channel.webhooks():
            if hook.name == ctx.guild.me.name:
                webhook = hook
        if webhook is None:
            webhook = await ctx.channel.create_webhook(name=ctx.guild.me.name)

        avatar = ctx.author.avatar.url.format(format="png")

        await webhook.send(owofied, username=ctx.author.display_name, avatar_url=avatar)
        await ctx.respond("Successfully sent the Owofied text!", ephemeral=True)

    @slash_command(name="britishify")
    async def britishify(self, ctx: commands.Context, *, text: str) -> None:
        """
        Britishify the provided text. Are you bri'ish enough?
        """
        msg = safe_message(text)

        britishified = strong_british_accent(msg)

        is_guild = True

        if not isinstance(ctx.channel, discord.TextChannel):
            is_guild = False

        if not ctx.channel.permissions_for(ctx.me).manage_webhooks or not is_guild:
            embed = discord.Embed(
                title="Hey there Mate!",
                description=britishified,
                color=self.bot.theme_colour["default"],
            )
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar.url
            )
            embed.set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Flag_of_Great_Britain_%281707–1800%29.svg/188px-Flag_of_Great_Britain_%281707–1800%29.svg.png"
            )
            embed.set_footer(
                text="💡 Tip: Use the `brit` command in a server where I have the Manage Webhooks permission and see the magic!"
            )
            await ctx.send(embed=embed)
            return await ctx.respond(
                "Successfully sent the britishified text!", ephemeral=True
            )

        webhook = None
        for hook in await ctx.channel.webhooks():
            if hook.name == ctx.guild.me.name:
                webhook = hook
        if webhook is None:
            webhook = await ctx.channel.create_webhook(name=ctx.guild.me.name)

        avatar = ctx.author.avatar.url.format(format="png")

        await webhook.send(
            britishified, username=ctx.author.display_name, avatar_url=avatar
        )
        return await ctx.respond(
            "Successfully sent the britishified text!", ephemeral=True
        )

    @slash_command(name="roast")
    async def roast(self, ctx: commands.Context, user: discord.Member = None) -> None:
        """
        Roast yourself or a friend!
        """
        user = user or ctx.author
        response = await aiohttp_get(
            "https://evilinsult.com/generate_insult.php?lang=en", _type="text"
        )
        if response is None:
            return await ctx.send("Failed to get insult")
        embed = discord.Embed(
            title=response,
            description="OOOOOOOOOOOOOOO",
            color=self.bot.theme_colour["default"],
        )
        embed.set_author(
            name=f"{ctx.author.display_name} Roasted {user.display_name}!",
            icon_url=ctx.author.avatar.url,
        )
        embed.set_thumbnail(url="https://c.tenor.com/f8YmpuCCXJcAAAAC/roasted-oh.gif")
        embed.set_footer(
            text="Roast is sourced through evilinsult.com.\nWe are not responsible for the content."
        )
        view = RoastAgainButton(user, ctx.author, ctx, self.bot)
        await ctx.respond(
            user.mention if not user == ctx.author else None, embed=embed, view=view
        )

    joke = SlashCommandGroup("joke", "Joke commands")

    @joke.command(name="dark")
    async def dark(self, ctx: commands.Context) -> None:
        """Returns a random dark joke"""
        response = await aiohttp_get(
            "https://v2.jokeapi.dev/joke/Dark?blacklistFlags=nsfw,religious&format=txt",
            _type="text",
        )
        if response is None:
            return await ctx.send("Failed to get joke")
        embed = discord.Embed(
            title="Dark Joke",
            description=response,
            color=self.bot.theme_colour["default"],
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(
            url="https://purepng.com/public/uploads/large/purepng.com-skullskullvertebratesfacehuman-skull-1421526968219gpljr.png"
        )
        embed.set_footer(
            text="NOTE: Dark Joke is sourced from jokeapi.dev. We are not responsible for the content."
        )
        view = DarkJokeAgainButton(ctx)
        await ctx.respond(embed=embed, view=view)

    @joke.command(name="dad")
    async def dadjoke(self, ctx: commands.Context) -> None:
        """Gets a Dad joke"""
        joke = await aiohttp_get(
            "https://icanhazdadjoke.com/",
            _type="text",
            headers={"Accept": "text/plain"},
        )
        if joke is None:
            return await ctx.send("Failed to get joke")
        embed = discord.Embed(
            title="Dad Joke", description=joke, color=self.bot.theme_colour["default"]
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(
            url="https://us-east-1.tixte.net/uploads/i.dhravya.me/dad_joke_spacebot.png"
        )
        embed.set_footer(
            text="Dad Joke is sourced from icanhazdadjoke.com. We are not responsible for the content."
        )
        view = DadJokeAgainButton(ctx)
        await ctx.respond(embed=embed, view=view)

    @slash_command(name="8ball")
    async def eightball(self, ctx: commands.Context, *, question: str) -> None:
        """Ask the magic 8 ✨"""
        responses = {
            "It is certain.": 0x2ECC71,
            "It is decidedly so.": 0x2ECC71,
            "Without a doubt.": 0x2ECC71,
            "Yes - definitely.": 0x2ECC71,
            "You may rely on it.": 0x2ECC71,
            "As I see it, yes.": 0x2ECC71,
            "Most likely.": 0x2ECC71,
            "Outlook good.": 0x2ECC71,
            "Yes.": 0x2ECC71,
            "Signs point to yes.": 0x2ECC71,
            "send hazy, try again.": 0xE67E22,
            "Ask again later.": 0xE74C3C,
            "Better not tell you now.": 0xE74C3C,
            "Cannot predict now.": 0xE74C3C,
            "Concentrate and ask again.": 0xE74C3C,
            "Don't count on it.": 0xE74C3C,
            "My send is no.": 0xE74C3C,
            "My sources say no.": 0xE74C3C,
            "Outlook not so good.": 0xE74C3C,
            "Very doubtful.": 0xE67E22,
            "Maybe.": 0xE67E22,
        }

        answer = random.choice(list(responses.keys()))
        color = responses[answer]

        embed = discord.Embed(
            title=f"8 ball",
            description=f"**```Question: {question}```\n```Answer: {answer}```**",
            color=color,
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)

    @slash_command(name="truth")
    async def truth(self, ctx: commands.Context) -> None:
        """Gets a random truth"""
        truth = await aiohttp_get(
            "https://api.dhravya.me/truth?simple=true", _type="text"
        )
        if truth is None:
            return await ctx.send("Failed to get truth")
        embed = discord.Embed(
            title="Say the Truth!!",
            description=truth,
            color=self.bot.theme_colour["default"],
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)

    @slash_command(name="dare")
    async def dare(self, ctx: commands.Context) -> None:
        """Gets a random dare"""
        dare = await aiohttp_get(
            "https://api.dhravya.me/dare?simple=true", _type="text"
        )
        if dare is None:
            return await ctx.send("Failed to get dare")
        embed = discord.Embed(
            title="Say the dare!!",
            description=dare,
            color=self.bot.theme_colour["default"],
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)

    @slash_command(name="comic")
    async def comic(self, ctx: commands.Context, number) -> None:
        """Gets a random comic from xkcd.com"""
        mes = await ctx.send("Fetching comic...")
        if number is None:
            json_ = await aiohttp_get("https://xkcd.com/info.0.json", _type="json")
            current_comic = json_["num"]
            comic_number = random.randint(1, current_comic)
        else:
            comic_number = number
        comic_json = await aiohttp_get(
            f"https://xkcd.com/{comic_number}/info.0.json", _type="json"
        )
        if comic_json is None:
            logging.warning(f"Failed to get comic {comic_number}")
            return await ctx.send("Failed to get comic")

        embed = discord.Embed(
            title=f"xkcd #{comic_number}",
            description=comic_json["alt"],
            color=self.bot.theme_colour["default"],
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_image(url=comic_json["img"])
        embed.set_footer(text=f"xkcd.com - {comic_json['year']}")
        view = GetComicAgainButton(ctx, comic_json["img"])
        await mes.edit("", embed=embed, view=view)

    @slash_command(name="topic")
    async def topic(self, ctx: commands.Context) -> None:
        """Gets a random topic"""
        topic = await aiohttp_get(
            "https://api.dhravya.me/topic?simple=true", _type="text"
        )
        is_guild = True
        if topic is None:
            return await ctx.send("Failed to get topic")

        if isinstance(ctx.channel, discord.DMChannel):
            is_guild = False

        if not ctx.channel.permissions_for(ctx.me).manage_webhooks or not is_guild:

            embed = discord.Embed(
                title="Topic for chat",
                description=topic,
                color=self.bot.theme_colour["default"],
            )
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar.url
            )
            await ctx.send(embed=embed)

        await ctx.respond("trying to send a webhook...", ephemeral=True, delete_after=5)

        webhook = None
        for hook in await ctx.channel.webhooks():
            if hook.name == ctx.guild.me.name:
                webhook = hook
        if webhook is None:
            webhook = await ctx.channel.create_webhook(name=ctx.guild.me.name)

        avatar = ctx.author.avatar.url.format(format="png")
        embed = discord.Embed(
            description=safe_message(topic), colour=self.bot.theme_colour["default"]
        )
        embed.set_footer(text="Use the topic command to get more")
        await webhook.send(
            embed=embed, username=ctx.author.display_name, avatar_url=avatar
        )

    @slash_command(name="beer")
    async def beer(
        self,
        ctx: commands.Context,
        user: Option(discord.Member, "Whom would you like to have a beer with?"),
        reason: Option(str, "Reason for beer"),
    ) -> None:
        """Give a beer to your friend!!"""
        if user.id == self.bot.user.id:
            return await ctx.respond("*drinks beer with you* 🍻")

        if user.bot:
            return await ctx.respond(
                f"I would love to give beer to the bot **{user.name}**, but I don't think it will respond to you :/"
            )

        if user == ctx.author:
            return await ctx.respond(
                "You can't give beer to yourself! ;-; \n (*PS* if you feel lonely, you can have a party with me or SpaceDoggo :wink:)"
            )

        beer_offer = f"**{user.name}**, you got a 🍺 offer from **{ctx.author.name}**"
        beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer

        view = BeerOfferView(ctx=ctx, user=user)

        embed = discord.Embed(
            title="Cheers! 🎉",
            description=beer_offer,
            color=self.bot.theme_colour["default"],
        )
        await ctx.respond(user.mention, embed=embed, view=view)

    @slash_command(name="coinflip")
    async def coinflip(self, ctx: commands.Context) -> None:
        """Flip a coin to end that debate!"""
        coin = random.choice(["heads", "tails"])
        url = f"https://us-east-1.tixte.net/uploads/i.dhravya.me/coin_{coin}.gif"
        embed = discord.Embed(
            title="Coin Flip!",
            description=f"Flipping the coin...",
            colour=self.bot.theme_colour["default"],
        )
        embed.set_image(url=url)
        interaction = await ctx.respond(embed=embed)
        await asyncio.sleep(3)
        embed.description = "The coin landed on **{}**".format(coin)
        view = CoinFlipAgainView(ctx=ctx)
        await interaction.edit_original_message(embed=embed, view=view)

    @slash_command(
        name="beerparty",
        description="Have a beer party with some friends 🍻!",
        guild_ids=[905904010760966164],
    )
    async def beerparty_(self, ctx: commands.Context):
        interaction: discord.Interaction = ctx.interaction
        embed = discord.Embed(
            title="Beer Party 🍻",
            description=f"{ctx.author.mention} had invited everyone to join up this beer party :beers:!",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_message()
        await message.edit(embed=embed, view=BeerPartyView(message, ctx))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(FunSlash(bot))
