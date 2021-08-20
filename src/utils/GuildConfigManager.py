import os
import discord
import motor.motor_asyncio
from lru import LRU
from utils.singleton import Singleton

PREFIX_CACHE_SIZE = 1000


class GuildConfigManager(metaclass=Singleton):
    """
    Guild config util class for erin
    """

    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("CONNECTIONURI"))
        self.db = self.client.erin
        self.col = self.db["config"]
        self.prefix_lru = LRU(PREFIX_CACHE_SIZE)

    async def register_guild(self, guild_object:discord.Guild, recheck=True):
        if recheck:
            guild = await self.col.find_one({"gid": guild_object.id})
            if not guild:
                guild = {"gid": guild_object.id, "prefixes": ["-"]}
                await self.col.insert_one(guild)
        else:
            guild = {"gid": guild_object.id, "prefixes": ["-"]}
            await self.col.insert_one(guild)
        return guild

    async def unregister_guild(self, guild_object:discord.Guild, recheck=True):
        if recheck:
            guild = await self.col.find_one({"gid": guild_object.id})
            if guild:
                await self.col.delete_one({"gid": guild_object.id})
        else:
            await self.col.delete_one({"gid": guild_object.id})

    async def update_guild(self, guild_object:discord.Guild, document):
        guild = await self.register_guild(guild_object)
        await self.col.replace_one({"gid": guild_object.id}, document)
        return guild

    async def get_prefix(self, guild_object:discord.Guild):
        if guild_object.id in self.prefix_lru:
            prefixes = self.prefix_lru[guild_object.id]
        else:
            guild = await self.register_guild(guild_object)
            prefixes = guild["prefixes"]
            self.prefix_lru[guild_object.id] = prefixes
        return prefixes

    async def add_prefix(self, guild_object:discord.Guild, prefix):
        guild = await self.register_guild(guild_object)
        if prefix in guild["prefixes"]:
            return False
        else:
            guild["prefixes"].append(prefix)
            await self.update_guild(guild_object, guild)
            del self.prefix_lru[guild_object.id]
            return True

    async def remove_prefix(self, guild_object:discord.Guild, prefix):
        guild = await self.register_guild(guild_object)
        if not prefix in guild["prefixes"]:
            return False
        else:
            guild["prefixes"].remove(prefix)
            await self.update_guild(guild_object, guild)
            del self.prefix_lru[guild_object.id]
            return True

    async def add_ban_appeal(self, guild_object:discord.Guild, ban_appeal: str):
        guild = await self.register_guild(guild_object)
        guild["ban_appeal"] = ban_appeal
        await self.update_guild(guild_object, guild)
        return True

    async def remove_ban_appeal(self, guild_object:discord.Guild):
        guild = await self.register_guild(guild_object)
        guild.pop("ban_appeal")
        await self.update_guild(guild_object, guild)
        return True

    async def get_ban_appeal(self, guild_object:discord.Guild):
        guild = await self.register_guild(guild_object)
        link = guild["ban_appeal"]
        return link

    async def add_muted_role(self, guild_object:discord.Guild, muted_role: int):
        guild = await self.register_guild(guild_object)
        guild["muted_role"] = muted_role
        await self.update_guild(guild_object, guild)
        return True

    async def remove_muted_role(self, guild_object:discord.Guild):
        guild = await self.register_guild(guild_object)
        guild.pop("muted_role")
        await self.update_guild(guild_object, guild)

    async def get_muted_role(self, guild_object:discord.Guild):
        guild = await self.register_guild(guild_object)
        muted_role = guild["muted_role"]
        return muted_role

    async def update_currency_channel(self, guild_object:discord.Guild, channelID: int):
        guild = await self.register_guild(guild_object)
        guild["channel"] = channelID
        await self.update_guild(guild_object, guild)
        return True

    async def remove_currency_channel(self, guild_object:discord.Guild):
        guild = await self.register_guild(guild_object)
        guild.pop("channel")
        await self.update_guild(guild_object, guild)

    async def get_currency_channel(self, guild_object:discord.Guild):
        guild = await self.register_guild(guild_object)
        currencyChannnel = guild["channel"]
        return currencyChannnel

    async def set_default_mutetime(self,guild_object:discord.Guild,default:int=None):
        guild = await self.register_guild(guild_object)
        current_mute_time=None # the current config
        try:
            current_mute_time=guild["default_mute_duration"]
        except KeyError:
            pass
        if  current_mute_time==None and default==None:
            guild['default_mute_duration'] = 3600 # default mute time will be 1 hour if config var has not been set
            return await self.update_guild(guild_object,guild)
        elif default !=None:
            guild['default_mute_duration'] = default
            return await self.update_guild(guild_object,guild)

    async def get_default_mutetime(self,guild_object:discord.Guild):
        guild = await self.register_guild(guild_object)
        try:
            current_mute_time=guild['default_mute_duration']
        except KeyError:
            await self.set_default_mutetime(guild_object)
            current_mute_time = await self.register_guild(guild_object)
            current_mute_time=current_mute_time['default_mute_duration']
        return current_mute_time
