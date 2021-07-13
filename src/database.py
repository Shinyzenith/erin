import logging

import coloredlogs
import discord
from discord.ext import commands
from pymongo import MongoClient

log = logging.getLogger("Database wrapper")
coloredlogs.install(logger=log)


class ErinDatabase(MongoClient):
    def __init__(self, bot: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = self.erin
        self.col = self.db["config"]
        self.bot = bot

    def register_guild(self, guild: discord.guild.Guild):
        self.col.insert_one({"gid": guild.id, "prefixes": ["-"]})

    def get_prefix(self, guild: discord.guild.Guild,
                   message: discord.message.Message) -> list[str]:
        result = self.col.find_one({"gid": guild.id})
        if not result:
            self.register_guild(message.guild)
            prefixes = ["-"]
        else:
            prefixes = result["prefixes"]
        # May or may not have copied code from:
        # https://stackoverflow.com/a/64434732/10291933
        prefixes = commands.when_mentioned_or(*prefixes)(self.bot, message)
        return prefixes

    def __repr__(self):
        return f"ErinDatabase(bot={repr(self.bot)})"

    def __hash__(self):
        return hash(repr(self))
