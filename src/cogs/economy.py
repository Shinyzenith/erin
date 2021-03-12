from discord.ext import commands
from datetime import datetime
import discord
import json
import random
import os

class economy(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # @commands.command(self,ctx):


def setup(bot):
    bot.add_cog(economy(bot))