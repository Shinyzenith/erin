import discord
import os
import sqlite3
import logging
import json
import asyncpg
import logging
import datetime
import aiohttp

from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
load_dotenv(verbose=True)
env_path = Path('./../') / '.env'
load_dotenv(dotenv_path=env_path)

intents=discord.Intents.all()

log = logging.getLogger("ErinBot")
logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")

def get_prefix(client,message):
	prefix_list=[]
	db = sqlite3.connect('./db/prefix.db').cursor()
	prefix= db.execute('SELECT prefix FROM prefix WHERE guild_id=?',(message.guild.id,))
	prefix = prefix.fetchall()
	db.close()
	for item in prefix:
		for p in item:
			prefix_list.append(str(p))
	return prefix_list

class ErinBot(commands.Bot):
    def __init__(self):
        intents = intents=discord.Intents.all()
        super().__init__(command_prefix=get_prefix, description="No description rn lmfao", intents=intents,guild_subscriptions=True)
        self.loop.create_task(self.prepare_bot())
        log.info("Loading extensions")
        self.cogs_to_add = ["cogs.actions", "cogs.economy", "cogs.Utility", "cogs.errorhandler","cogs.fun","cogs.nsfw1","cogs.nsfw2","cogs.highlighter.admin","cogs.highlighter.highlight","cogs.highlighter.meta","cogs.highlighter.timers"]
        self.load_extension("jishaku")
        for cog in self.cogs_to_add:
            self.load_extension(cog)

        self.startup_time = datetime.datetime.utcnow()
        self.support_server_link = "https://discord.gg/davie504"

    async def prepare_bot(self):
        log.info("Creating aiohttp session")
        self.session = aiohttp.ClientSession()

        log.info("Connecting to database")

        async def init(conn):
            await conn.set_type_codec("jsonb", schema="pg_catalog", encoder=json.dumps, decoder=json.loads, format="text")
        self.db = await asyncpg.create_pool(os.getenv("DATABASEURI"), init=init)

        log.info("Initiating database")

        query = """CREATE TABLE IF NOT EXISTS words (
                   user_id BIGINT,
                   guild_id BIGINT,
                   word TEXT
                   );

                   CREATE TABLE IF NOT EXISTS settings (
                   user_id BIGINT PRIMARY KEY,
                   disabled BOOL,
                   timezone INT,
                   blocked_users BIGINT ARRAY,
                   blocked_channels BIGINT ARRAY
                   );

                   CREATE TABLE IF NOT EXISTS timers (
                   id SERIAL PRIMARY KEY,
                   user_id BIGINT,
                   event TEXT,
                   time TIMESTAMP,
                   extra jsonb DEFAULT ('{}'::jsonb),
                   created_at TIMESTAMP DEFAULT (now() at time zone 'utc')
                   );

                   CREATE TABLE IF NOT EXISTS highlights (
                   guild_id BIGINT,
                   channel_id BIGINT,
                   message_id BIGINT,
                   author_id BIGINT,
                   user_id BIGINT,
                   word TEXT,
                   invoked_at TEXT
                   );

                   CREATE UNIQUE INDEX IF NOT EXISTS unique_words_index ON words (user_id, guild_id, word);
                """
        await self.db.execute(query)

        log.info("Preparing words cache")
        self.cached_words = []
        for row in await self.db.fetch("SELECT word FROM words"):
            if row["word"] not in self.cached_words:
                self.cached_words.append(row["word"])

    async def on_ready(self):
        log.info(f"Logged in as {self.user.name} - {self.user.id}")
        self.console = self.get_channel(config.console)

    def run(self):
        super().run(os.getenv("TOKEN"))
        
bot = ErinBot()
bot.run()