import os
import discord
import aiohttp
import logging
import datetime
import coloredlogs
import time
from discord.ext.commands.cog import Cog
import humanize
import motor.motor_asyncio
import datetime as dt

from pathlib import Path
from dotenv import load_dotenv
from database import ErinDatabase
from discord.ext import commands

# dotenv config
load_dotenv()
load_dotenv(verbose=True)
env_path = Path('./../') / '.env'
load_dotenv(dotenv_path=env_path)

# logger config
log = logging.getLogger("ErinBot")
coloredlogs.install(logger=log)
logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s",
                    datefmt="%m/%d/%y - %H:%M:%S %Z")

# loading softbans vars

global ubc
global notsoftbanned
global isoncooldown

# Cooldown Error


class CooldownError(commands.CheckFailure):
    pass


class BotBan(commands.CheckFailure):
    pass
# webhook function


async def webhook_send(url, message, username="Erin uptime Logs", avatar="https://raw.githubusercontent.com/AakashSharma7269/erin/main/erin.png?token=AOP54YUJCVK5WQY5LQ6AK5TAWOXYK"):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(
            url, adapter=discord.AsyncWebhookAdapter(session))
        if isinstance(message, discord.Embed):
            await webhook.send(embed=message, username=username, avatar_url=avatar)
        else:
            await webhook.send(message, username=username, avatar_url=avatar)


# prefix manager class
class PrefixManager:
    def __init__(self, bot):
        self.client = ErinDatabase(bot, os.getenv('CONNECTIONURI'))
        self.prefixes = {}

    def get_prefix(self, client, message):
        prefixes = self.client.get_prefix(guild=message.guild, message=message)
        self.prefixes[str(message.guild.id)] = prefixes
        return prefixes

# bot banning class


class UserBanClient:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("CONNECTIONURI"))
        self.db = self.client.erin
        self.col = self.db["softbans"]
        self.col2 = self.db["cooldowns"]
        self.users = []

    async def fetch_user_bans(self, user):
        if str(user.id) in self.users:
            log.warn(f"{user.id} is banned from using this bot")
            raise BotBan("You are banned from using this bot")
            return False

        ban = await self.col.find_one({"uid": str(user.id)})
        if ban:
            log.warn(f"{user.id} is banned from using this bot")
            raise BotBan("You are banned from using this bot")
            self.users.append(str(user.id))
        return (False if ban else True)

    async def softban_user(self, userid: int):
        if str(userid) in self.users:
            return True
        ban = await self.col.find_one({"uid": str(userid)})
        if ban:
            self.users.append(str(userid))
            return True
        else:
            self.users.append(str(userid))
            await self.col.insert_one({"uid": str(userid)})
            return True

    async def remove_softban(self, userid: int):
        if str(userid) in self.users:
            self.users.remove(str(userid))
        ban = await self.col.find_one({"uid": str(userid)})
        if ban:
            self.col.delete_one({"uid": str(userid)})
            return True
        else:
            return True

    async def check_cooldowns(self, ctx):
        cooldown = await self.col2.find_one({"uid": ctx.author.id, "cmd": ctx.command.name})
        if not cooldown:
            return True
        else:
            if int(float(cooldown["time"])) > time.time():
                if cooldown["uses"] >= cooldown["permitted_uses"]:
                    period = humanize.naturaldelta(dt.timedelta(
                        seconds=int(float(cooldown["time"]))-time.time()))
                    raise CooldownError(f'Try again in {period}')
                else:
                    return True
            else:
                await self.col2.delete_one({"uid": ctx.author.id, "cmd": ctx.command.name})
                return True

    async def create_cooldown(self, ctx, uses: int, period: int):
        cooldown = await self.col2.find_one({"uid": ctx.author.id, "cmd": ctx.command.name})
        if cooldown:
            if cooldown["uses"] < uses:
                if time.time() > int(float(cooldown["time"])):
                    await self.col2.delete_one({"uid": ctx.author.id, "cmd": ctx.command.name})
                    return
                else:
                    del cooldown["_id"]
                    cooldown["uses"] += 1
                    await self.col2.replace_one({"uid": ctx.author.id, "cmd": ctx.command.name}, cooldown)
                    return
            else:
                if time.time() > int(float(cooldown["time"])):
                    await self.col2.delete_one({"uid": ctx.author.id, "cmd": ctx.command.name})
                    return
        else:
            await self.col2.insert_one({"uid": ctx.author.id, "cmd": ctx.command.name, "time": str(time.time()+period), "uses": 1, "permitted_uses": uses})

    async def predicate(self, ctx):
        return await self.fetch_user_bans(ctx.author)

    async def cooldown_checker(self, ctx):
        return await self.check_cooldowns(ctx)
# bot instance class


class ErinBot(commands.Bot):
    def __init__(self):

        # intent and bot instance declaration
        intents = discord.Intents.all()
        super().__init__(command_prefix=PrefixManager(self).get_prefix,
                         intents=intents, guild_subscriptions=True, case_insensitive=True)

        # saving startup time and creating process loop (removing the default help command cuz it's ass)
        self.remove_command('help')
        self.startup_time = datetime.datetime.utcnow()
        self.loop.create_task(self.prepare_bot())

    # Prepares the bot and connects to the database

    async def prepare_bot(self):
        log.info("Creating aiohttp session")
        self.session = aiohttp.ClientSession()
        log.info("Connecting to database")
        self.mongo = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("CONNECTIONURI"))

    # runs the instance of the bot class.
    def run(self):
        if not os.getenv("TOKEN") or os.getenv("TOKEN") == "":
            return log.error("No .env file setup with proper token paramter.")
        super().run(os.getenv("TOKEN"))


# creating an erin bot object
bot = ErinBot()

# initalizing clients
ubc = UserBanClient()
isoncooldown = commands.check(ubc.cooldown_checker)

# send message on startup
@bot.event
async def on_ready():
    await webhook_send(os.getenv("UPTIMELOG"), "Erin started up \N{Thumbs Up Sign}")
    log.info(f"Logged in as {bot.user.name} - {bot.user.id}")

# loading extensions
log.info("Loading extensions")
cwd = Path(__file__).parents[0]
cwd = str(cwd)
for file in os.listdir(cwd + "/cogs"):
    if file.endswith(".py") and not file.startswith("_"):
        bot.load_extension(f"cogs.{file[:-3]}")

# binding checks
bot.add_check(ubc.predicate)

# running the bot
bot.run()
