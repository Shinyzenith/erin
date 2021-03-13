from discord.ext import commands
from datetime import datetime
import discord
import json
import random
import os
import sqlite3

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
load_dotenv(verbose=True)
env_path = Path('./../') / '.env'
load_dotenv(dotenv_path=env_path)

intents=discord.Intents.all()
def get_prefix(client,message):
	prefix_list=[]
	db = sqlite3.connect('./db/prefix.db').cursor()
	prefix= db.execute('SELECT prefix FROM prefix WHERE guild_id=?',(message.guild.id,))
	prefix = prefix.fetchall()
	db.close()
	for item in prefix:
		for p in item:
			prefix_list.append(str(p))
	print(prefix_list)
	return prefix_list
client=commands.Bot(command_prefix=get_prefix,case_insensitive=True,intents=intents,guild_subscriptions=True)
cwd = Path(__file__).parents[0]
cwd = str(cwd)
for file in os.listdir(cwd + "/cogs"):
	if file.endswith(".py") and not file.startswith("_"):
		client.load_extension(f"cogs.{file[:-3]}")


#demo change
	
client.run(os.getenv("TOKEN"))
