import os
import json
import discord
import asyncpg
import aiohttp
import logging
import datetime
import coloredlogs
import motor.motor_asyncio

from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from discord.ext import commands

#dotenv config
load_dotenv()
load_dotenv(verbose=True)
env_path = Path('./../') / '.env'
load_dotenv(dotenv_path=env_path)

#logger config
log = logging.getLogger("ErinBot")
coloredlogs.install(logger=log)
logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")

#webhook function
async def webhook_send(url, message, username="Erin uptime Logs",avatar="https://media.discordapp.net/attachments/769824167188889600/820197487238184960/Erin.jpeg"):
	async with aiohttp.ClientSession() as session:
		webhook = discord.Webhook.from_url(url, adapter=discord.AsyncWebhookAdapter(session))
		if isinstance(message, discord.Embed):
			await webhook.send(embed=message, username=username,avatar_url=avatar)
		else:
			await webhook.send(message, username=username,avatar_url=avatar)


#prefix manager class
class PrefixManager:
	def __init__(self):
		self.client = MongoClient(os.getenv('CONNECTIONURI'))
		self.db=self.client.erin
		self.col=self.db["config"]

	def register_guild(self, g):
		self.col.insert_one({"gid":g.id,"prefixes":["-"]})

	def get_prefix(self, client, message):
		prefixes=[]
		guild=self.col.find_one({"gid":message.guild.id})
		if not guild:
			self.register_guild(message.guild)
			prefixes=["-"]
		else:
			prefixes=guild["prefixes"]
		return prefixes


#bot instance class
class ErinBot(commands.Bot):
	def __init__(self):
		
		#intent and bot instance declaration
		intents=discord.Intents.all()
		super().__init__(command_prefix=PrefixManager().get_prefix, intents=intents,guild_subscriptions=True,case_insensitive=True)
		
		#saving startup time and creating process loop (removing the default help command cuz it's ass)
		self.remove_command('help')
		self.startup_time = datetime.datetime.utcnow()
		self.loop.create_task(self.prepare_bot())


	#Prepares the bot and connects to the database
	async def prepare_bot(self):
		log.info("Creating aiohttp session")
		self.session = aiohttp.ClientSession()
		self.cached_words=[]
		log.info("Connecting to database")
		async def init(conn):
			await conn.set_type_codec("jsonb", schema="pg_catalog", encoder=json.dumps, decoder=json.loads, format="text")
		self.db = await asyncpg.create_pool(os.getenv("DATABASEURI"), init=init)
		self.mongo = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("CONNECTIONURI"))

	#runs the instance of the bot class.
	def run(self):
		if not os.getenv("TOKEN") or os.getenv("TOKEN")=="":
			return log.error("No .env file setup with proper token paramter.")
		super().run(os.getenv("TOKEN"))


#creating an erin bot object
bot = ErinBot()

#send message on startup
@bot.event
async def on_ready():
	await webhook_send(os.getenv("UPTIMELOG"),"Erin started up \N{Thumbs Up Sign}")
	log.info(f"Logged in as {bot.user.name} - {bot.user.id}")


#creating bot class instance and loading extensions
log.info("Loading extensions")
cwd = Path(__file__).parents[0]
cwd = str(cwd)
for file in os.listdir(cwd + "/cogs"):
	if file.endswith(".py") and not file.startswith("_"):
		bot.load_extension(f"cogs.{file[:-3]}")
#running the bot
bot.run()
