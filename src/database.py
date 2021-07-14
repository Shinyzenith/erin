import functools
import logging

import cachetools
import coloredlogs
import discord
from discord.ext import commands
from pymongo import MongoClient

log = logging.getLogger("Database wrapper")
coloredlogs.install(logger=log)


# Generic cache function. Modify to suit specific functions like the prefix
# cache
#
# def cache(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         cache_key = args + tuple(kwargs.items())
#         if cache_key not in wrapper.cache:
#             wrapper.cache[cache_key] = func(*args, **kwargs)
#         return wrapper.cache[cache_key]
#     wrapper.cache = cachetools.LRUCache(maxsize=1000)
#     return wrapper


def prefix_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Tries to get the "guild" parameter
        cache_key = kwargs["guild"] if "guild" in kwargs else args[1]
        if cache_key not in wrapper.cache:
            wrapper.cache[cache_key] = func(*args, **kwargs)
        print(f"Current size of cache is {wrapper.cache.currsize} items")
        return wrapper.cache[cache_key]
    wrapper.cache = cachetools.LRUCache(maxsize=1000)
    return wrapper


class ErinDatabase(MongoClient):
    def __init__(self, bot: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = self.erin
        self.col = self.db["config"]
        self.bot = bot

    def register_guild(self, guild: discord.guild.Guild):
        self.col.insert_one({"gid": guild.id, "prefixes": ["-"]})

    @prefix_cache
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
        # TODO: Clear cache when prefix on server is changed
        # print(self.get_prefix.cache)
        return prefixes

    def __repr__(self):
        return f"ErinDatabase(bot={repr(self.bot)})"

    def __hash__(self):
        return hash(repr(self))
