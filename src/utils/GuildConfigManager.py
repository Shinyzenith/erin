import os
import motor.motor_asyncio

class GuildConfigManager:
    """
    Guild config util class for erin
    """

    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("CONNECTIONURI"))
        self.db = self.client.erin
        self.col = self.db["config"]

    async def register_guild(self, g, recheck=True):
        if recheck:
            guild = await self.col.find_one({"gid": g.id})
            if not guild:
                guild = {"gid": g.id, "prefixes": ["-"]}
                await self.col.insert_one(guild)
        else:
            guild = {"gid": g.id, "prefixes": ["-"]}
            await self.col.insert_one(guild)
        return guild

    async def unregister_guild(self, g, recheck=True):
        if recheck:
            guild = await self.col.find_one({"gid": g.id})
            if guild:
                await self.col.delete_one({"gid": g.id})
        else:
            await self.col.delete_one({"gid": g.id})

    async def update_guild(self, g, document):
        guild = await self.register_guild(g)
        await self.col.replace_one({"gid": g.id}, document)
        return guild

    async def get_prefix(self, g):
        prefixes = []
        guild = await self.register_guild(g)
        prefixes = guild["prefixes"]
        return prefixes

    async def add_prefix(self, g, prefix):
        guild = await self.register_guild(g)
        if prefix in guild["prefixes"]:
            return False
        else:
            guild["prefixes"].append(prefix)
            await self.update_guild(g, guild)
            return True

    async def remove_prefix(self, g, prefix):
        guild = await self.register_guild(g)
        if not prefix in guild["prefixes"]:
            return False
        else:
            guild["prefixes"].remove(prefix)
            await self.update_guild(g, guild)
            return True

    async def add_ban_appeal(self, g, ban_appeal: str):
        guild = await self.register_guild(g)
        guild["ban_appeal"] = ban_appeal
        await self.update_guild(g, guild)
        return True

    async def remove_ban_appeal(self, g):
        guild = await self.register_guild(g)
        guild.pop("ban_appeal")
        await self.update_guild(g, guild)
        return True

    async def get_ban_appeal(self, g):
        guild = await self.register_guild(g)
        link = guild["ban_appeal"]
        return link

    async def add_muted_role(self, g, muted_role: int):
        guild = await self.register_guild(g)
        guild["muted_role"] = muted_role
        await self.update_guild(g, guild)
        return True

    async def remove_muted_role(self, g):
        guild = await self.register_guild(g)
        guild.pop("muted_role")
        await self.update_guild(g, guild)

    async def get_muted_role(self, g):
        guild = await self.register_guild(g)
        muted_role = guild["muted_role"]
        return muted_role

    async def update_currency_channel(self, g, channelID: int):
        guild = await self.register_guild(g)
        guild["channel"] = channelID
        await self.update_guild(g, guild)
        return True

    async def remove_currency_channel(self, g):
        guild = await self.register_guild(g)
        guild.pop("channel")
        await self.update_guild(g, guild)

    async def get_currency_channel(self, g):
        guild = await self.register_guild(g)
        currencyChannnel = guild["channel"]
        return currencyChannnel

