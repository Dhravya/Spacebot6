# CONTRIBUTORS:
# Dhravya Shah https://github.com/dhravya - Fun, Logging, Mod, and a lot more
# 27Saumya https://github.com/27Saumya - Ticket system
# nexxeln https://github.com/nexxeln - Button roles, modals
# Infernum1 https://github.com/Infernum1 - Logging

import os
from os import environ as env
import dotenv
import logging
import asyncio
import sys

from discord.ext import commands
import discord
from pycord.ext import ipc
import asyncmy
import topgg

from utility.disc.command_hinter import CommandHinter, CommandGenerator
from utility.disc.get_prefix import get_prefix
from utility.db.database import Database

from views.button_roles_views import RoleButton
from views.ticket_views import *


try:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s\t\t %(asctime)s",
        filename=os.path.join(os.path.dirname(__file__), "logs", "main.log"),
    )
except Exception as e:
    print(e)

dotenv.load_dotenv()
logging.info("Starting bot, loaded env variables")


# Getting the cog file
cog_files = [
    os.path.join(os.path.dirname(__file__), "cogs"),
    os.path.join(os.path.dirname(__file__), "slash_cogs"),
    os.path.join(os.path.dirname(__file__), "background_cogs"),
]
logging.info(f"Using cog file: {cog_files}")

# Specifying the intents
intents = discord.Intents.default()
intents.messages = True
intents.members = True


class SpaceBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.persistent_views_added = False
        self.ipc = ipc.Server(
            self, secret_key=env.get("IPC_SECRET_KEY"), host="0.0.0.0"
        )

    async def is_owner(self, user: discord.User) -> bool:
        if user.id in [881861601756577832, 512885190251642891]:
            return True
        return await super().is_owner(user)

    async def on_ready(self):
        print(f"{bot.user.name} has connected to Discord!")
        bot.log.info(f"Logged in as {bot.user}")
        if not self.persistent_views_added:
            self.add_view(TicketPanelView(self))
            self.add_view(TicketControlsView(self))
            self.add_view(TicketCloseTop(self))
            self.persistent_views_added = True
        await bot.change_presence(
            activity=discord.Game(name="Spacebot rewrite in progress")
        )
        bot.log.info("Bot ready, waiting for threads to load")
        await asyncio.sleep(15)
        db = Database(bot)

        bot.log.info("Setting prefix cache")
        await db._prefix_cache_set()
        bot.prefix_cache = db.prefix_cache

        bot.log.info("Setting automod cache")
        await db._automod_cache_set()

        print("Loading persistent buttons")
        view = discord.ui.View(timeout=None)
        # Sleeping for a second to allow the bot to connect to the database
        await self.cursor.execute("SELECT * FROM roles")
        # make a list of guilds and roles of that guild
        roles = await self.cursor.fetchall()
        for guild_id, role_id in roles:
            guild = self.get_guild(guild_id)
            role = guild.get_role(role_id)
            if role:
                self.log.info(f"Adding role button for {role}")
                view.add_item(RoleButton(role))
        # add the view to the bot so it will watch for button interactions
        self.add_view(view)
        print("Persistent buttons loaded. Bot is ready!")

    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)


bot = SpaceBot(
    command_prefix=get_prefix,
    intents=intents,
    case_insensitive=True,
    strip_after_prefix=True,
)
bot.connected = False

bot.log = logging

CommandHinter(bot, CommandGenerator())


async def connect_to_db(bot) -> None:
    bot.conn = await asyncmy.connect(
        user=env.get("DB_USER"),
        password=env.get("DB_PASS"),
        host=env.get("DB_HOST"),
        database=env.get("DB_NAME"),
        port=int(env.get("DB_PORT")),
    )
    bot.cursor = bot.conn.cursor()
    bot.log.info("Connected to DB")
    print("Connected to DB")
    bot.connected = True


loop = asyncio.get_event_loop()
loop.run_until_complete(connect_to_db(bot))
bot.connect_to_db = connect_to_db

bot.dev_mode = True

if not bot.dev_mode:
    bot.topggpy = topgg.DBLClient(
        bot,
        os.getenv("TOPGG_TOKEN"),
        autopost=True,
        post_shard_count=True,
    )
    bot.log.info("Loaded top.gg module")

bot.theme_colour = {"default": 0x2F3136, "error": 0x57F287, "success": 0x57F287}

bot.load_extension("jishaku")
for cog_file in cog_files:
    filename = os.path.basename(cog_file)
    for cog in os.listdir(cog_file):
        if cog.endswith(".py"):
            try:
                bot.load_extension(f"{filename}.{cog[:-3]}")
                bot.log.info(f"Loaded cog {cog}")
            except Exception as e:
                bot.log.error(f"Error loading cog {cog}: {e}", exc_info=True)


async def mobile(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": sys.platform,
                "$browser": "Discord iOS",
                "$device": "pycord",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
            "v": 3,
        },
    }
    if self.shard_id is not None and self.shard_count is not None:
        payload["d"]["shard"] = [self.shard_id, self.shard_count]
    state = self._connection
    if state._activity is not None or state._status is not None:
        payload["d"]["presence"] = {
            "status": state._status,
            "game": state._activity,
            "since": 0,
            "afk": False,
        }
    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value
    await self.call_hooks(
        "before_identify", self.shard_id, initial=self._initial_identify
    )
    await self.send_as_json(payload)


discord.gateway.DiscordWebSocket.identify = mobile

if __name__ == "__main__":
    bot.ipc.start()
    if bot.dev_mode == True:
        bot.run(env.get("DEV_TOKEN"))
    else:
        bot.run(env.get("BOT_TOKEN"))
