from discord.ext import commands
from datetime import datetime
import discord
import json
import random
import os

from dotenv import load_dotenv
from pathlib import Path
#TODO make all owner commands owner only in utility.py file
#TODO implement logger 

load_dotenv()
load_dotenv(verbose=True)
env_path = Path('./../') / '.env'
load_dotenv(dotenv_path=env_path)

client = commands.Bot(command_prefix="-")

cwd = Path(__file__).parents[0]
cwd = str(cwd)
for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
                client.load_extension(f"cogs.{file[:-3]}")
client.run(os.getenv("TOKEN"))
