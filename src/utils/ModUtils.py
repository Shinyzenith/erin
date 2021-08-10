import os
from time import time
import motor.motor_asyncio
from utils.GuildConfigManager import GuildConfigManager

class ModUtils:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("CONNECTIONURI"))
        self.db = self.client.erin
        self.gch = GuildConfigManager()
        self.col = self.db["mute"]
        self.col1 = self.db["warns"]

    async def fetch_user_mutes(self, uid: int, gid: int):
        current_time = time()
        cursor = self.col.find(
            {
                "uid": str(uid),
                "me": {"$gte": current_time},
                "gid": gid,
            }
        )
        MemberMutes = await cursor.to_list(
            length=99999999999999999999999999999999999999999999
        )
        return MemberMutes

    async def register_mute(
        self, uid: str, muteExpiration: int, muteAssignedAt: int, gid: int, reason: str
    ):
        data = {
            "uid": uid,
            "me": muteExpiration,
            "gid": gid,
            "details": {"ma": muteAssignedAt, "reason": reason},
        }
        await self.col.insert_one(data)
        return data

    async def load_mutes(self):
        current_time = round(time())
        cursor = self.col.find({"me": {"$lte": current_time}})
        return await cursor.to_list(
            length=99999999999999999999999999999999999999999999
        )  # lol

    async def delete_mute_entry(self, mute):
        data = {"uid": mute["uid"], "me": mute["me"], "gid": mute["gid"]}
        await self.col.delete_one(data)

    async def unmute_loaded_mutes(self, bot):
        mute_list = await self.load_mutes()
        for mute in mute_list:
            guild = bot.get_guild(mute["gid"])
            if not guild:
                return await self.delete_mute_entry(mute)
            else:
                try:
                    muteRoleID = await self.gch.get_muted_role(guild)
                    mutedMember = guild.get_member(int(mute["uid"]))

                except:
                    return await self.delete_mute_entry(mute)
                mutedRole = guild.get_role(muteRoleID)
                if not mutedRole:
                    return await self.delete_mute_entry(mute)
                try:
                    await mutedMember.remove_roles(
                        mutedRole,
                        reason=f"{bot.user.name} auto unmute function triggered.",
                    )
                except:
                    pass
                return await self.delete_mute_entry(mute)

    async def find_user(self, uid: str, gid: int):
        user = await self.col1.find_one({"uid": uid})
        if not user:
            user = await self.register_user(uid, gid)
        try:
            user["gid"][f"{gid}"]
        except KeyError:
            user["gid"][f"{gid}"] = []
        finally:
            return user

    async def register_user(self, uid: str, gid: int):
        data = {"uid": f"{uid}", "gid": {f"{str(gid)}": []}}
        await self.col1.insert_one(data)
        return data

    async def update_user_warn(self, uid: str, data):
        await self.col1.replace_one({"uid": f"{uid}"}, data)
