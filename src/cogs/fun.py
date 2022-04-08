from typing import Union
import random
import logging
import asyncio

import discord
from discord.ext import commands

from utility.text.britishify import strong_british_accent
from utility.text.uwufy import owofy
from utility.text.zalgoify import zalgo
from utility.text.safe_message import safe_message
from utility.web.safe_aiohttp import aiohttp_get

from views.fun_views import *
from utility.text.subscript_superscript import *


class Fun(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot
        self.bot.log.debug(f"Loaded {self.__cog_name__} cog")
        self.help_doc = "Fun commands to have some fun!"
        self.beer_emojis = []

    @commands.command("owofy", aliases=["uwufy", "owo"])
    async def owofy(self, ctx: commands.Context, *, text: str) -> None:
        """
        Oh... UwU Hai thewe ·///· Owofies the pwovided text uwu
        """
        msg = safe_message(text)

        owofied = owofy(msg)
        # If the channel isnt a guild
        is_guild = True
        # if ctx.channel isnt in a guild,
        # then it isnt a guild channel
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
            return await ctx.send(embed=embed)

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            await ctx.message.delete()

        webhook = None
        for hook in await ctx.channel.webhooks():
            if hook.name == ctx.guild.me.name:
                webhook = hook
        if webhook is None:
            webhook = await ctx.channel.create_webhook(name=ctx.guild.me.name)

        avatar = ctx.author.avatar.url.format(format="png")

        await webhook.send(owofied, username=ctx.author.display_name, avatar_url=avatar)

    @commands.command("britishify", aliases=["britainify", "brit", "british"])
    async def britishify(self, ctx: commands.Context, *, text: str) -> None:
        """
        cahn you pahss me ah bottle of waht-ah
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
            return await ctx.send(embed=embed)

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            await ctx.message.delete()

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

    @commands.command("zalgoify", aliases=["corrupt"])
    async def zalgoify(self, ctx: commands.Context, *, text: str) -> None:
        """
        Zalgo-ify your message
        """
        msg = safe_message(text)
        z = zalgo()
        # mazimum zalgo

        zalgoified = z.zalgofy(text=msg)

        is_guild = True
        # if ctx.channel isnt in a guild,
        # then it isnt a guild channel
        if not isinstance(ctx.channel, discord.TextChannel):
            is_guild = False
        if not ctx.channel.permissions_for(ctx.me).manage_webhooks or not is_guild:
            embed = discord.Embed(
                title="CORRUPT",
                description=zalgoified,
                color=self.bot.theme_colour["default"],
            )
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar.url
            )
            embed.set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Zalgo_text_filter.png/300px-Zalgo_text_filter.png"
            )
            embed.set_footer(
                text="💡 Tip: Use the `corrupt` command in a server where I have the Manage Webhooks permission and see the magic!"
            )
            return await ctx.send(embed=embed)

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            await ctx.message.delete()

        webhook = None
        for hook in await ctx.channel.webhooks():
            if hook.name == ctx.guild.me.name:
                webhook = hook
        if webhook is None:
            webhook = await ctx.channel.create_webhook(name=ctx.guild.me.name)

        avatar = ctx.author.avatar.url.format(format="png")

        await webhook.send(
            zalgoified, username=ctx.author.display_name, avatar_url=avatar
        )

    @commands.command("decancer", aliases=["deconfuse"])
    async def decancer(self, ctx: commands.Context, *, text: str) -> None:
        pass

    @commands.command(name="roast", aliases=["roastme"])
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
        await ctx.send(
            user.mention if not user == ctx.author else None, embed=embed, view=view
        )

    @commands.command(name="darkjoke", aliases=["dark_joke"])
    async def darkjoke(self, ctx: commands.Context) -> None:
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
        await ctx.send(embed=embed, view=view)

    @commands.command(name="dadjoke", aliases=["dad_joke"])
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
        await ctx.send(embed=embed, view=view)

    @commands.command(name="fact", aliases=["factoid"])
    async def fact(self, ctx: commands.Context) -> None:
        """Gets a random fact"""
        await ctx.send("This endpoint isnt ready yet!")

    @commands.command(name="8ball", aliases=["eightball"])
    async def eightball(self, ctx: commands.Context, *, question: str) -> None:
        """Ask the magic 🎱"""
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
            "No": 0xE74C3C,
            "Clearly no": 0xE74C3C,
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
        await ctx.send(embed=embed)

    @commands.command(name="truth")
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
        await ctx.send(embed=embed)

    @commands.command(name="dare")
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
        await ctx.send(embed=embed)

    @commands.command(name="comic", aliases=["xkcd"])
    async def comic(
        self, ctx: commands.Context, number: Union[int, str] = None
    ) -> None:
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

    @commands.command(name="topic")
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
        if ctx.channel.permissions_for(ctx.me).manage_messages:
            await ctx.message.delete()

    @commands.command(name="numberfact")
    async def numberfact(
        self, ctx: commands.Context, number: Union[int, None] = None
    ) -> None:
        """Did you know the meaning of 69?"""
        number = number or random.randint(1, 200)
        fact = await aiohttp_get(f"http://numbersapi.com/{number}", _type="text")
        if fact is None:
            return await ctx.send("Failed to get fact")
        embed = discord.Embed(
            title=f"Did you know?",
            description=fact,
            color=self.bot.theme_colour["default"],
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="asktrump", aliases=["trump", "ask_trump"])
    async def ask_trump(self, ctx: commands.Context, question: str) -> None:
        """What does trump think? 🤔"""
        message = await ctx.send("Asking Trump...")
        trump = await aiohttp_get(
            f"https://api.whatdoestrumpthink.com/api/v1/quotes/personalized?q={question}"
        )
        quote = trump["message"]
        embed = discord.Embed(
            title="Trump says...",
            description=quote,
            color=self.bot.theme_colour["default"],
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await message.edit("", embed=embed)

    @commands.command(name="beer", aliases=["cheers"])
    async def beer(
        self, ctx: commands.Context, user: discord.Member, *, reason: str = None
    ) -> None:
        """Cheers to your friend!"""
        if user.id == self.bot.user.id:
            return await ctx.send("*drinks beer with you* 🍻")

        if user.bot:
            return await ctx.send(
                f"I would love to give beer to the bot **{ctx.author.name}**, but I don't think it will respond to you :/"
            )

        if user == ctx.author:
            return await ctx.send(
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
        await ctx.send(user.mention, embed=embed, view=view)

    @commands.command(name="coinflip")
    async def coinflip(
        self, ctx: commands.Context, message: discord.Message = None
    ) -> None:
        """Flip a coin to end that debate!"""
        if message:
            if not message.author.id == self.bot.user.id:
                return
        coin = random.choice(["heads", "tails"])
        url = f"https://us-east-1.tixte.net/uploads/i.dhravya.me/coin_{coin}.gif"
        embed = discord.Embed(
            title="Coin Flip!",
            description=f"Flipping the coin...",
            colour=self.bot.theme_colour["default"],
        )
        embed.set_image(url=url)
        message_ = (
            await ctx.send(embed=embed)
            if not message
            else await message.edit(embed=embed)
        )
        await asyncio.sleep(3)
        embed.description = "The coin landed on **{}**".format(coin)
        view = CoinFlipAgainView(ctx=ctx)
        await message_.edit(embed=embed, view=view)

    @commands.command(name="beerparty")
    async def beerparty_(self, ctx: commands.Context):
        """Have a beerparty in the server. Invite your friends!"""
        embed = discord.Embed(
            title="Beer Party 🍻",
            description=f"{ctx.author.mention} had invited everyone to join up this beer party :beers:!",
            color=discord.Color.green(),
        )
        message = await ctx.send(embed=embed)
        await message.edit(embed=embed, view=BeerPartyView(message, ctx))


def setup(bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
    bot.add_cog(Fun(bot))
