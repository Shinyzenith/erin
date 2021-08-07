import os
import typing
import asyncio
import discord
import logging
import humanize
import datetime
import coloredlogs
import DiscordUtils
from time import time
import motor.motor_asyncio
from datetime import datetime
from main import ubc, isoncooldown
from discord.ext import commands, tasks
from utils.TimeConverter import TimeConverter
from utils.GuildConfigManager import GuildConfigManager
# Initializing the logger
log = logging.getLogger("Moderation cog")
coloredlogs.install(logger=log)

class muteHandler:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("CONNECTIONURI"))
        self.db = self.client.erin
        self.gch = GuildConfigManager()
        self.col = self.db["mute"]

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

# Database Handler class
class dbHandler:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("CONNECTIONURI"))
        self.db = self.client.erin
        self.col = self.db["warns"]

    async def find_user(self, uid: str, gid: int):
        user = await self.col.find_one({"uid": uid})
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
        await self.col.insert_one(data)
        return data

    async def update_user_warn(self, uid: str, data):
        await self.col.replace_one({"uid": f"{uid}"}, data)


class Moderation(commands.Cog):
    """
    Basic moderation commands (automod coming soon!)
    """

    def __init__(self, bot):
        self.bot = bot
        self._autounmute.start()
        self.muteHandler = muteHandler()
        self.dbHandler = dbHandler()
        self.TimeConverter = TimeConverter()
        self.GuildConfigManager = GuildConfigManager()

    @tasks.loop(seconds=2)
    async def _autounmute(self):
        await self.bot.wait_until_ready()
        await self.muteHandler.unmute_loaded_mutes(self.bot)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        userMutes = await self.muteHandler.fetch_user_mutes(member.id, guild.id)
        if len(userMutes) == 0:
            return
        try:
            muteRoleID = await self.GuildConfigManager.get_muted_role(guild)
        except:
            return
        mutedRole = guild.get_role(muteRoleID)
        if not mutedRole:
            return
        try:
            await member.add_roles(
                mutedRole,
                reason=f"{self.bot.user.name} auto unmute function triggered.",
            )
        except:
            pass

        entryData = {
            "type": "mute",
            "reason": "User left and rejoined guild while muted.",
            "time": datetime.utcnow().strftime("%a, %#d %B %Y, %I:%M %p UTC"),
            "mod": f"{self.bot.user.id}",
        }
        userData = await self.dbHandler.find_user(str(member.id), guild.id)
        userData["gid"][f"{guild.id}"].append(entryData)
        await self.dbHandler.update_user_warn(str(member.id), userData)

    @commands.Cog.listener()
    async def on_ready(self):
        log.warn(f"{self.__class__.__name__} Cog has been loaded")

    @commands.command(name="warn", aliases=["strike"], description="Warn a user")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def warn(self, ctx, user: discord.Member, *, reason: str = "No reason given."):
        # sanitizing input
        if user.bot:
            return await ctx.message.reply("Don't even **try** to warn my kind :)")

        if len(reason) > 150:
            return await ctx.message.reply(
                "Reason parameter exceeded 150 characters. Please write a shorter reason to continue"
            )
        if (
            user.top_role.position > ctx.message.author.top_role.position
            or user.top_role.position == ctx.message.author.top_role.position
        ):
            return await ctx.message.reply(
                "You can't use me to warn someone above or at the same role level as you :)"
            )

        if (
            user.top_role.position > ctx.message.author.top_role.position
            or user.top_role.position == ctx.message.author.top_role.position
        ):
            return await ctx.message.reply(
                f"Cannot warn {user.mention} as their highest role is the same as or above your highest role."
            )

        # editing the user object to hold the user data
        entryData = {
            "type": "strike",
            "reason": reason,
            "time": ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
            "mod": f"{ctx.message.author.id}",
        }
        userData = await self.dbHandler.find_user(str(user.id), ctx.message.guild.id)
        userData["gid"][f"{ctx.message.author.guild.id}"].append(entryData)

        # updating user entries
        await self.dbHandler.update_user_warn(str(user.id), userData)

        # building the embed
        channel = discord.Embed(
            description=f"Punishment(s) for {user.name}#{user.discriminator} submitted successfully.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )
        channel.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        channel.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )

        dmEmbed = discord.Embed(
            title="Erin Moderation",
            description=f"Your punishments have been updated in {ctx.message.guild.name}.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )

        dmEmbed.add_field(name="Action", value="Strike/Warn", inline=True)

        dmEmbed.add_field(name="Reason", value=f"{reason}", inline=True)

        dmEmbed.add_field(name="Moderator",
                          value=f"<@{entryData['mod']}>", inline=True)

        dmEmbed.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        dmEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        await ctx.message.reply(embed=channel)
        try:
            await user.send(embed=dmEmbed)
        except:
            pass
        # editing the reason of a warn that was entered prior

    @commands.command(name="reason", aslias=["rs"], description="Changes a warn/strike reason")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def reason(self, ctx, searchUser: discord.User, warnID: int, *, reason: str = None):
        if not reason:
            return await ctx.send("Please mention the new reason!")
        if len(reason) > 150:
            return await ctx.send("Hey! the maximum word limit for a warn reason is 150.")
        # gathering the user warns in a user dictionary
        user = await self.dbHandler.find_user(str(searchUser.id), ctx.message.guild.id)
        # checking if the warn exists in the database !!
        if len(user["gid"][f"{ctx.guild.id}"]) < warnID:
            return await ctx.send(f"WarnID {warnID} doesn't exist!")
        # if the user isn't the origianl person who issued the perm then they are denied from changing the reason unless they're and admin
        if user["gid"][f"{ctx.guild.id}"][warnID - 1]["mod"] != str(ctx.message.author.id) and ctx.author.guild_permissions.administrator == False:
            return await ctx.send("Hey, you cannot change the reason of a warn that was issued by someone else!\nOnly an admin can change the reason which was added by someone else")
        # Setting the new reason dictionary
        oldReason = user['gid'][f'{ctx.guild.id}'].pop(warnID - 1)
        newReason = oldReason
        newReason["reason"] = reason
        # inserting new reason dictionary into warns array
        user['gid'][f'{ctx.guild.id}'].insert(warnID-1, newReason)
        await self.dbHandler.update_user_warn(str(searchUser.id), user)
        channelEmbed = discord.Embed(
            description=f"Set reason for punishment with ID `{warnID}` to `{reason}`",
            color=11661816,
            timestamp=ctx.message.created_at,
        )
        channelEmbed.set_footer(
            text=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
        )
        channelEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        dmEmbed = discord.Embed(
            title="Erin Moderation",
            description=f"Your punishments have been updated in {ctx.message.guild.name}.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )

        dmEmbed.add_field(name="Action", value="Reason update", inline=True)

        dmEmbed.add_field(name="Reason ID", value=f"{warnID}", inline=False)

        dmEmbed.add_field(name="Old Reason",
                          value=f"{oldReason['reason']}", inline=False)

        dmEmbed.add_field(name="New Reason",
                          value=f"{newReason['reason']}", inline=False)

        dmEmbed.add_field(name="Moderator",
                          value=f"{ctx.message.author.mention}", inline=False)
        try:
            await searchUser.send(embed=dmEmbed)
        except:
            pass
        return await ctx.send(embed=channelEmbed)

    @ commands.command(name="search", aliases=["warns"], description="Shows a users punishments")
    @ commands.guild_only()
    async def search(self, ctx, searchUser: discord.User):
        user = await self.dbHandler.find_user(str(searchUser.id), ctx.message.guild.id)
        threshold = 5
        reason_chunk = [
            user["gid"][f"{ctx.message.guild.id}"][i: i + threshold]
            for i in range(0, len(user["gid"][f"{ctx.message.guild.id}"]), threshold)
        ]

        i = 0
        embeds = []
        for chunk in reason_chunk:
            embed = discord.Embed(
                title=f"All punishments for {searchUser.name}#{searchUser.discriminator}",
                color=11661816,
                timestamp=ctx.message.created_at,
            )
            embed.set_footer(
                text=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
            )
            embed.set_author(name=self.bot.user.name,
                             icon_url=self.bot.user.avatar_url)

            for reason in chunk:
                i = i + 1

                embed.add_field(
                    inline=False,
                    name=f"{i}) {reason['type']}",
                    value=f"Reason: **{reason['reason']}**\nTime: **{reason['time']}**\nResponsible moderator: **<@{reason['mod']}>**",
                )

            embeds.append(embed)
            embed = None

        if len(embeds) == 1:
            return await ctx.message.reply(embed=embeds[0])

        elif len(embeds) == 0:
            emb = discord.Embed(
                description=f"{searchUser.mention} has a clean state",
                color=11661816,
                timestamp=ctx.message.created_at,
            )
            emb.set_footer(
                text=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
            )
            emb.set_author(
                name=self.bot.user.name, icon_url=self.bot.user.avatar_url
            )
            return await ctx.message.reply(embed=emb)

        else:
            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(
                ctx, remove_reactions=True
            )
            paginator.add_reaction(
                "\N{Black Left-Pointing Double Triangle with Vertical Bar}", "first"
            )
            paginator.add_reaction(
                "\N{Black Left-Pointing Double Triangle}", "back")
            paginator.add_reaction("\N{CROSS MARK}", "lock")
            paginator.add_reaction(
                "\N{Black Right-Pointing Double Triangle}", "next")
            paginator.add_reaction(
                "\N{Black Right-Pointing Double Triangle with Vertical Bar}", "last"
            )
            return await paginator.run(embeds)

    @commands.command(name="delpunishments", description="Deletes __**ALL**__ punishments")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def delpunishments(self, ctx, user: discord.User):
        delUser = await self.dbHandler.find_user(str(user.id), ctx.message.guild.id)
        request = await ctx.message.reply(
            f"**This will delete ALL punishments that the {user.mention} has.** Type \"yes\" to continue, \"no\" to cancel. "
        )
        try:
            message = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel.id == ctx.channel.id and ("yes" in m.content.lower() or "no" in m.content.lower()))
        except asyncio.TimeoutError:
            return await ctx.message.channel.send(
                "Woops, you didn't reply within 30 seconds... request cancelled. "
            )

        if "yes" in message.content.lower():
            delUser["gid"].pop(f"{ctx.message.guild.id}")
            await self.dbHandler.update_user_warn(str(user.id), delUser)

            await request.delete()
            try:
                await message.delete()
            except:
                pass
            return await ctx.message.reply(
                f"All records of {user.mention} have been deleted."
            )
        else:
            return await ctx.message.reply(
                "Request cancelled."
            )

    @commands.command(name="ban" , description="Bans a user")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        user: typing.Union[discord.Member, discord.User],
        *,
        reason: str = "No reason given. "
    ):
        try:
            await ctx.guild.fetch_ban(user)
            channelEmbed = discord.Embed(
                description=f"{user.name}#{user.discriminator} is already banned from the server!",
                color=16724787,
                timestamp=ctx.message.created_at,
            )
            channelEmbed.set_footer(
                text=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
            )
            channelEmbed.set_author(
                name=self.bot.user.name, icon_url=self.bot.user.avatar_url
            )
            return await ctx.send(embed=channelEmbed)
        except discord.NotFound:
            pass
        if len(reason) > 150:
            return await ctx.message.reply(
                "Reason parameter exceeded 150 characters. Please write a shorter reason to continue."
            )
        entryData = {
            "type": "Ban",
            "reason": reason,
            "time": ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
            "mod": f"{ctx.message.author.id}",
        }

        channelEmbed = discord.Embed(
            description=f"{user.mention} has been banned from {ctx.guild.name}",
            color=11661816,
            timestamp=ctx.message.created_at,
        )
        channelEmbed.set_footer(
            text=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
        )
        channelEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        dmEmbed = discord.Embed(
            title="Erin Moderation",
            description=f"Your punishments have been updated in {ctx.message.guild.name}.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )

        dmEmbed.add_field(name="Action", value="Ban", inline=True)

        dmEmbed.add_field(name="Reason", value=f"{reason}", inline=True)

        dmEmbed.add_field(name="Moderator",
                          value=f"<@{entryData['mod']}>", inline=True)

        try:
            ban_appeal = await self.GuildConfigManager.get_ban_appeal(ctx.guild)
            dmEmbed.add_field(name="Ban Appeal link:",
                              value=ban_appeal, inline=False)
        except KeyError:
            pass

        dmEmbed.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        dmEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        if isinstance(user, discord.User):
            await ctx.message.guild.ban(user, reason=reason)
            try:
                await user.send(embed=dmEmbed)
            except:
                pass
        if isinstance(user, discord.Member):
            bot = ctx.guild.get_member(self.bot.user.id)
            if (
                user.top_role.position > bot.top_role.position
                or user.top_role.position == bot.top_role.position
            ):
                return await ctx.message.reply(
                    f"Cannot ban {user.mention} as their highest role is the same as or above me."
                )
            if (
                user.top_role.position > ctx.message.author.top_role.position
                or user.top_role.position == ctx.message.author.top_role.position
            ):
                return await ctx.message.reply(
                    "You can't use me to ban someone above or at the same role level as you :)"
                )

            try:
                await user.send(embed=dmEmbed)
            except:
                pass
            try:
                await ctx.message.guild.ban(user, reason=reason, delete_message_days=0)
            except discord.errors.Forbidden:
                return await ctx.message.reply(
                    f"Unable to ban {user.mention}. Make sure i have `Ban members` permission enabled."
                )
        userData = await self.dbHandler.find_user(str(user.id), ctx.message.guild.id)
        userData["gid"][f"{ctx.message.author.guild.id}"].append(entryData)
        await self.dbHandler.update_user_warn(str(user.id), userData)
        return await ctx.message.reply(embed=channelEmbed)

    @commands.command(name="softban" , description="Softbans a user which bans them and quickly unbans them to purge thier messages")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def softban(
        self,
        ctx,
        user: typing.Union[discord.Member, discord.User],
        *,
        reason: str = "No reason given. "
    ):
        try:
            await ctx.guild.fetch_ban(user)
            channelEmbed = discord.Embed(
                description=f"{user.name}#{user.discriminator} is already banned from the server!",
                color=16724787,
                timestamp=ctx.message.created_at,
            )
            channelEmbed.set_footer(
                text=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
            )
            channelEmbed.set_author(
                name=self.bot.user.name, icon_url=self.bot.user.avatar_url
            )
            return await ctx.send(embed=channelEmbed)
        except discord.NotFound:
            pass
        if len(reason) > 150:
            return await ctx.message.reply(
                "Reason parameter exceeded 150 characters. Please write a shorter reason to continue."
            )
        entryData = {
            "type": "Softban",
            "reason": reason,
            "time": ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
            "mod": f"{ctx.message.author.id}",
        }

        channelEmbed = discord.Embed(
            description=f"{user.mention} has been soft-banned from {ctx.guild.name}",
            color=11661816,
            timestamp=ctx.message.created_at,
        )
        channelEmbed.set_footer(
            text=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
        )
        channelEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        dmEmbed = discord.Embed(
            title="Erin Moderation",
            description=f"Your punishments have been updated in {ctx.message.guild.name}.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )

        dmEmbed.add_field(name="Action", value="Softban", inline=True)

        dmEmbed.add_field(name="Reason", value=f"{reason}", inline=True)

        dmEmbed.add_field(name="Moderator",
                          value=f"<@{entryData['mod']}>", inline=True)

        dmEmbed.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        dmEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        if isinstance(user, discord.User):
            await ctx.message.guild.ban(user, reason=reason, delete_message_days=7)
            await ctx.message.guild.unban(user, reason="softban")
            try:
                await user.send(embed=dmEmbed)
            except:
                pass
        if isinstance(user, discord.Member):
            bot = ctx.guild.get_member(self.bot.user.id)
            if (
                user.top_role.position > bot.top_role.position
                or user.top_role.position == bot.top_role.position
            ):
                return await ctx.message.reply(
                    f"Cannot ban {user.mention} as their highest role is the same as or above me."
                )
            if (
                user.top_role.position > ctx.message.author.top_role.position
                or user.top_role.position == ctx.message.author.top_role.position
            ):
                return await ctx.message.reply(
                    "You can't use me to soft-ban someone above or at the same role level as you :)"
                )

            try:
                await user.send(embed=dmEmbed)
            except:
                pass
            try:
                await ctx.message.guild.ban(user, reason=reason, delete_message_days=7)
                await ctx.message.guild.unban(user, reason="softban")
            except discord.errors.Forbidden:
                return await ctx.message.reply(
                    f"Unable to soft ban {user.mention}. Make sure i have `Ban Members` permission enabled."
                )
        userData = await self.dbHandler.find_user(str(user.id), ctx.message.guild.id)
        userData["gid"][f"{ctx.message.author.guild.id}"].append(entryData)
        # uodating user entries
        await self.dbHandler.update_user_warn(str(user.id), userData)
        return await ctx.message.reply(embed=channelEmbed)

    @commands.command(name="unban", description="Unbans a user")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        ctx,
        user: discord.User,
        *,
        reason: str = "No reason given. "
    ):
        try:
            await ctx.guild.fetch_ban(user)
            if len(reason) > 150:
                return await ctx.message.reply(
                    "Reason parameter exceeded 150 characters. Please write a shorter reason to continue."
                )
            entryData = {
                "type": "Unban",
                "reason": reason,
                "time": ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
                "mod": f"{ctx.message.author.id}",
            }

            channelEmbed = discord.Embed(
                description=f"{user.mention} has been unbanned from {ctx.guild.name}",
                color=11661816,
                timestamp=ctx.message.created_at,
            )
            channelEmbed.set_footer(
                text=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
            )
            channelEmbed.set_author(
                name=self.bot.user.name, icon_url=self.bot.user.avatar_url
            )
            dmEmbed = discord.Embed(
                title="Erin Moderation",
                description=f"Your punishments have been updated in {ctx.message.guild.name}.",
                color=11661816,
                timestamp=ctx.message.created_at,
            )

            dmEmbed.add_field(name="Action", value="Unban", inline=True)

            dmEmbed.add_field(name="Reason", value=f"{reason}", inline=True)

            dmEmbed.add_field(
                name="Moderator", value=f"<@{entryData['mod']}>", inline=True
            )

            dmEmbed.set_footer(
                text=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
            )
            dmEmbed.set_author(
                name=self.bot.user.name, icon_url=self.bot.user.avatar_url
            )
            try:
                await ctx.message.guild.unban(user, reason=reason)
            except discord.errors.Forbidden:
                return await ctx.message.reply(
                    f"Unable to unban {user.mention}. Make sure i have `Ban Members` permission enabled."
                )
            try:
                await user.send(embed=dmEmbed)
            except:
                pass

            userData = await self.dbHandler.find_user(
                str(user.id), ctx.message.guild.id
            )
            userData["gid"][f"{ctx.message.author.guild.id}"].append(entryData)
            # uodating user entries
            await self.dbHandler.update_user_warn(str(user.id), userData)
            return await ctx.message.reply(embed=channelEmbed)

        except discord.NotFound:
            channelEmbed = discord.Embed(
                description=f"{user.name}#{user.discriminator} is not banned from the server!",
                color=16724787,
                timestamp=ctx.message.created_at,
            )
            channelEmbed.set_footer(
                text=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
            )
            channelEmbed.set_author(
                name=self.bot.user.name, icon_url=self.bot.user.avatar_url
            )
            return await ctx.send(embed=channelEmbed)

    @commands.command(name="rmpunish", description="Removes a punishment")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def rmpunish(self, ctx, user: discord.User, warn: int = None):
        rmUser = await self.dbHandler.find_user(str(user.id), ctx.message.guild.id)
        if not warn:
            return await ctx.send(
                f"Please mention the warn id of the reason that you want to delete from {user.mention}'s logs."
            )
        if warn > len(rmUser["gid"][f"{ctx.guild.id}"]):
            return await ctx.send(f"Invalid warn id for {user.mention}")
        removedWarn = rmUser["gid"][f"{ctx.guild.id}"].pop(warn - 1)
        await self.dbHandler.update_user_warn(str(user.id), rmUser)

        embed = discord.Embed(
            title="Erin Moderation",
            description=f"Warn removed for {user.mention}. Deleted warn details are:",
            color=11661816,
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Action", value=removedWarn["type"], inline=True)

        embed.add_field(
            name="Reason", value=removedWarn["reason"], inline=True)

        embed.add_field(name="Moderator",
                        value=f"<@{removedWarn['mod']}>", inline=True)

        embed.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        embed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        try:
            await user.send(embed=embed)
        except:
            pass
        await ctx.reply(embed=embed)

    @commands.command(name="mute", description="Mutes a user")
    @commands.has_guild_permissions(mute_members=True)
    async def mute(self, ctx, member: discord.Member, mute_period: str=None, *, reason: str = "No reason given. "):
        try:
            muted_role = await self.GuildConfigManager.get_muted_role(ctx.guild)
        except KeyError:
            return await ctx.message.reply(
                "No muted role has been setup for the server. Make a muted role before running the mute command."
            )
        if len(reason) > 150:
            return await ctx.message.reply(
                "Reason parameter exceeded 150 characters. Please write a shorter reason to continue."
            )

        try:
            mutedExpireTimeRaw = await self.TimeConverter.convert(ctx,mute_period)
        except:
            mutedExpireTimeRaw = await self.GuildConfigManager.get_default_mutetime(ctx.guild)

        mutedAt = time()
        mutedExpireTime = mutedExpireTimeRaw + mutedAt
        mutedRole = ctx.message.guild.get_role(muted_role)
        if mutedRole in member.roles:
            return await ctx.message.reply(f"{member.mention} is already muted :((")
        if not mutedRole:
            return await ctx.message.reply(
                "Muted role not found. Please ask an admin to reset the muted role for the server."
            )
        bot = ctx.guild.get_member(self.bot.user.id)
        if (
            member.top_role.position > ctx.message.author.top_role.position
            or member.top_role.position == ctx.message.author.top_role.position
        ):
            return await ctx.message.reply(
                "You can't use me to mute someone above or at the same role level as you :)"
            )
        if (
            member.top_role.position > bot.top_role.position
            or member.top_role.position == bot.top_role.position
        ):
            return await ctx.message.reply(
                f"Cannot mute {member.mention} as their highest role is the same as or above me."
            )
        try:
            await member.add_roles(
                mutedRole,
                reason=f"{self.bot.user.name} mute function triggered.",
            )
        except discord.errors.Forbidden:
            return await ctx.message.reply(
                f"Unable to mute {member.mention} make sure i have `manage roles` permission enabled."
            )

        entryData = {
            "type": "mute",
            "reason": reason,
            "time": ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
            "mod": f"{ctx.message.author.id}",
        }
        userData = await self.dbHandler.find_user(str(member.id), ctx.message.guild.id)
        userData["gid"][f"{ctx.message.author.guild.id}"].append(entryData)
        await self.dbHandler.update_user_warn(str(member.id), userData)
        channel = discord.Embed(
            description=f"Punishment(s) for {member.name}#{member.discriminator} submitted successfully.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )
        channel.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        channel.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )

        dmEmbed = discord.Embed(
            title="Erin Moderation",
            description=f"Your punishments have been updated in {ctx.message.guild.name}.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )

        dmEmbed.add_field(
            name="Action", value=f"{entryData['type']}", inline=True)

        dmEmbed.add_field(
            name="Reason", value=f"{entryData['reason']}", inline=True)

        dmEmbed.add_field(name="Moderator",
                          value=f"<@{entryData['mod']}>", inline=True)

        dmEmbed.add_field(
            name="Expiration",
            value=f"{humanize.precisedelta(mutedExpireTimeRaw)}",
            inline=False,
        )

        dmEmbed.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        dmEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        await ctx.message.reply(embed=channel)
        try:
            await member.send(embed=dmEmbed)
        except:
            pass
        await self.muteHandler.register_mute(
            str(member.id), mutedExpireTime, mutedAt, ctx.message.guild.id, reason
        )

    @commands.command(name="unmute", description="Unmutes a user")
    @commands.has_guild_permissions(mute_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason given. "):
        if len(reason) > 150:
            return await ctx.message.reply(
                "Reason parameter exceeded 150 characters. Please write a shorter reason to continue."
            )

        try:
            mutedRoleID = await self.GuildConfigManager.get_muted_role(ctx.guild)
        except:
            return await ctx.message.reply(
                f"Unable to unmute {member.mention} as the guild muted role has not been setup in my config >:(("
            )
        mutedRole = ctx.message.guild.get_role(mutedRoleID)

        mutes = await self.muteHandler.fetch_user_mutes(member.id, ctx.message.guild.id)
        if len(mutes) == 0:
            try:
                if mutedRole in member.roles:
                    await member.remove_roles(
                        mutedRole,
                        reason=f"{self.bot.user.name} was manually unmuted",
                    )
                    entryData = {
                        "type": "mute",
                        "reason": "Unknown reason.",
                        "time": ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
                        "mod": f"{self.bot.user.id}",
                    }
                    userData = await self.dbHandler.find_user(str(member.id), ctx.message.guild.id)
                    userData["gid"][f"{ctx.message.author.guild.id}"].append(entryData)
                    await self.dbHandler.update_user_warn(str(member.id), userData)
                    return await ctx.message.reply(
                        f"*uhhhhhhh awkward moment* {member.mention} is muted, but I have no record of it. Mute role has been removed automatically, and the mute has been logged."
                    )

                return await ctx.message.reply(
                    f"*uhhhhhhh awkward moment* {member.mention} is not muted"
                )
            except:
                return ctx.message.reply(
                    f"Unable to unmute {member.mention} make sure i have `manage roles` permission and their highest role is not above my highest role"
                )

        for mute in mutes:
            await self.muteHandler.delete_mute_entry(mute)

        if not mutedRole:
            return await ctx.message.reply(
                f"Unable to unmute {member.mention} as the guild muted role was not found."
            )
        try:
            await member.remove_roles(
                mutedRole,
                reason=f"{self.bot.user.name} unmute function triggered",
            )
        except discord.errors.Forbidden:
            return ctx.message.reply(
                f"Unable to unmute {member.mention} make sure i have `manage roles` permission and their highest role is not above my highest role"
            )
        entryData = {
            "type": "unmute",
            "reason": reason,
            "time": ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
            "mod": f"{ctx.message.author.id}",
        }
        userData = await self.dbHandler.find_user(str(member.id), ctx.message.guild.id)
        userData["gid"][f"{ctx.message.author.guild.id}"].append(entryData)
        await self.dbHandler.update_user_warn(str(member.id), userData)
        channel = discord.Embed(
            description=f"{member.name}#{member.discriminator} unmuted successfully.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )
        channel.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        channel.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )

        dmEmbed = discord.Embed(
            title="Erin Moderation",
            description=f"Your punishments have been updated in {ctx.message.guild.name}.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )

        dmEmbed.add_field(
            name="Action", value=f"{entryData['type']}", inline=True)

        dmEmbed.add_field(
            name="Reason", value=f"{entryData['reason']}", inline=True)

        dmEmbed.add_field(name="Moderator",
                          value=f"<@{entryData['mod']}>", inline=True)

        dmEmbed.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        dmEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        await ctx.message.reply(embed=channel)
        try:
            await member.send(embed=dmEmbed)
        except:
            pass

    @commands.command(name="kick", description="Kicks a user")
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        user: discord.Member,
        *,
        reason: str = "No reason given. "
    ):
        if len(reason) > 150:
            return await ctx.message.reply(
                "Reason parameter exceeded 150 characters. Please write a shorter reason to continue."
            )

        bot = ctx.guild.get_member(self.bot.user.id)
        if (
            user.top_role.position > bot.top_role.position
            or user.top_role.position == bot.top_role.position
        ):
            return await ctx.message.reply(
                f"Cannot kick {user.mention} as their highest role is the same as or above me."
            )
        if (
            user.top_role.position > ctx.message.author.top_role.position
            or user.top_role.position == ctx.message.author.top_role.position
        ):
            return await ctx.message.reply(
                "You can't use me to kick someone above or at the same role level as you :)"
            )
        entryData = {
            "type": "kick",
            "reason": reason,
            "time": ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
            "mod": f"{ctx.message.author.id}",
        }

        channelEmbed = discord.Embed(
            description=f"{user.mention} has been kicked from {ctx.guild.name}",
            color=11661816,
            timestamp=ctx.message.created_at,
        )
        channelEmbed.set_footer(
            text=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
        )
        channelEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )
        dmEmbed = discord.Embed(
            title="Erin Moderation",
            description=f"Your punishments have been updated in {ctx.message.guild.name}.",
            color=11661816,
            timestamp=ctx.message.created_at,
        )

        dmEmbed.add_field(
            name="Action", value=f"{entryData['type']}", inline=True)

        dmEmbed.add_field(name="Reason", value=f"{reason}", inline=True)

        dmEmbed.add_field(name="Moderator",
                          value=f"<@{entryData['mod']}>", inline=True)

        dmEmbed.set_footer(
            text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url
        )
        dmEmbed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.avatar_url
        )

        try:
            await user.send(embed=dmEmbed)
        except:
            pass

        try:
            await ctx.message.guild.kick(user, reason=reason)
        except discord.errors.Forbidden:
            return await ctx.message.reply(
                f"Unable to kick {user.mention}. Make sure i have `Kick members` permission enabled."
            )
        userData = await self.dbHandler.find_user(str(user.id), ctx.message.guild.id)
        userData["gid"][f"{ctx.message.author.guild.id}"].append(entryData)
        await self.dbHandler.update_user_warn(str(user.id), userData)
        return await ctx.message.reply(embed=channelEmbed)

    @commands.command(name="isbanned", description="Shows if a user is banned or not")
    @commands.guild_only()
    async def isbanned(self, ctx, user: discord.User):
        try:
            ban = await ctx.guild.fetch_ban(user)
            reason = ("No reason given. " if not ban.reason else ban.reason)
            return await ctx.message.reply(
                f"{user.mention} is banned from {ctx.message.guild.name} with reason: `{reason}`"
            )
        except discord.NotFound:
            return await ctx.message.reply(
                f"{user.mention} is not banned from {ctx.message.guild.name}"
            )

    @commands.command(name="fakeban", aliases=['fban'], description="Fake bans")
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def fakeban(self, ctx, member: discord.Member = None, *, reason: str = "No reason given. "):
        await ctx.message.delete()
        if not member:
            return await ctx.send("Mention a user to ban :))")
        embed = discord.Embed(title="Ban", description=f"Notified via direct messages.",
                              color=ctx.message.author.color, timestamp=ctx.message.created_at)
        embed.set_author(
            name=f"{ctx.message.author.name}", icon_url=ctx.message.author.avatar_url
        )
        embed.set_footer(
            text=f"{member.name}#{member.discriminator} has been banned", icon_url=member.avatar_url
        )
        embed.add_field(name="Responsible Moderator:",
                        value=f"{ctx.message.author.mention}", inline=False)
        embed.add_field(name="Reason:", value=reason, inline=False)
        embed.add_field(
            name="Banned:", value=f"{member.mention} - {member.id}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, description="Shows useful information about a user")
    @commands.guild_only()
    async def whois(self, ctx, *, member: discord.Member = None):
        if not member:
            member = ctx.message.author
        roles = [role for role in member.roles]
        roles = roles[1:]
        if len(roles) != 0:
            user_roles = ", ".join([role.mention for role in roles])
        else:
            user_roles = "User has no roles"

        hoisted_role = None
        for role in roles:
            if role.hoist == True:
                hoisted_role = role.mention

        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at,
                              title=f"User Info - {member}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}")

        permissions = ", ".join(
            [perm[0] for perm in member.guild_permissions if perm[1]])
        permissions = permissions.replace("_", " ")
        permissions = permissions.split(",")
        permissions_formatted = []
        word = ""
        for p in permissions:
            for p in p.split():
                word += " "+p[0].upper()+p[1:]
            permissions_formatted.append(word)
            word = ""
        permissions_formatted = ",  ".join(
            [permissions for permissions in permissions_formatted])
        is_user_bot = "Yes" if member.bot == True else "No"
        user_created = int(member.created_at.timestamp())
        user_joined = int(member.joined_at.timestamp())
        user_boosting = None
        user_boosting_days = None
        if member.premium_since != None:
            user_boosting = f"<t:{int(member.premium_since.timestamp())}:F>"
            user_boosting_days = f"<t:{int(member.premium_since.timestamp())}:R>"

        user_highest_role = member.top_role.mention
        embed.add_field(name="User identity:", value=f"User id: **{member.id}**\nBot user? **{is_user_bot}**\n\nBoosting since: **{user_boosting}**\nBoosting days: **{user_boosting_days}**", inline=False)
        embed.add_field(
                name="Dates:", value=f"Account created at: **<t:{user_created}:F>**\nUser account was created: **<t:{user_created}:R> **\n\nJoined server at: **<t:{user_joined}:F>**\nUser joined the server: **<t:{user_joined}:R> **", inline=False)
        embed.add_field(name="User Permissions: ",
                        value=f"\n{permissions_formatted}", inline=False)

        if not (len(member.roles)-1 >= 25):
            embed.add_field(
                name=f"Roles[{len(member.roles)-1}]:", value=user_roles, inline=False)
        else:
            embed.add_field(name=f"Roles[{len(member.roles)-1}]:",
                            value=f'{member.mention} has too many roles, hence they wont be printed.')
        embed.add_field(name="Highest Role:",
                        value=user_highest_role, inline=False)
        embed.add_field(name="Hoisted Role:", value=hoisted_role, inline=False)
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, description="Shows a users avatar")
    async def avatar(self, ctx, *, member: discord.User = None):
        if not member:
            member = ctx.author
        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at,
                              title=f"{member} account avatar", description=f"[User avatar link]({member.avatar_url})")
        embed.set_image(url=member.avatar_url)
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.message.channel.send(embed=embed)

    @commands.command(description="Shows how many people have a role", aliases=["rolemembers"])
    @commands.guild_only()
    async def inrole(self, ctx, *, role: discord.Role):
        members = []
        for user in ctx.guild.members:
            if role in user.roles:
                members.append(user)
        if len(members) == 0:
            return await ctx.send(f"No members have {role.mention} role")
        concat = ""
        embeds = []
        threshold = 10
        position_count = 1
        members = [members[i:i + threshold]
                   for i in range(0, len(members), threshold)]
        for chunk in members:
            for item in chunk:
                concat = concat+f"{position_count}) {item.mention}\n"
                position_count += 1
            embed = discord.Embed(
                title=f"Rolemembers for {role.name}", timestamp=ctx.message.created_at, color=role.color)
            embed.set_author(name=ctx.message.guild.name,
                             icon_url=ctx.message.guild.icon_url)
            embed.set_thumbnail(url=ctx.message.author.avatar_url)
            embed.set_footer(text=self.bot.user.name,
                             icon_url=self.bot.user.avatar_url)
            embed.add_field(name=f"⠀", value=concat)
            embeds.append(embed)
            embed = None
            concat = ""
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(
            ctx, remove_reactions=True)
        paginator.add_reaction(
            '\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', "first")
        paginator.add_reaction('\N{LEFTWARDS BLACK ARROW}', "back")
        paginator.add_reaction('\N{BLACK RIGHTWARDS ARROW}', "next")
        paginator.add_reaction(
            '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', "last")
        await paginator.run(embeds)

    @commands.command(name='roleinfo', aliases=['ri'], description=('Shows info about a role'))
    async def roleinfo_command(self, ctx, *, role: discord.Role = None):
        if not role:
            return await ctx.send("Mention a role / enter role id / type out a role name (case sensitive).")
        permissions = ", ".join([perm[0].replace('_', ' ').capitalize()
                                 for perm in role.permissions if perm[1]])
        if "Administrator" in permissions:
            permissions = "Role has administrator enabled. All permissions are granted."
        elif len(permissions) == 0:
            permissions = "Role has no permissions enabled!"
        role_created_days = (datetime.now()-role.created_at).days
        embed = discord.Embed(
            title="Role info", timestamp=ctx.message.created_at, color=role.color)
        embed.set_author(name=ctx.message.author.name,
                         icon_url=ctx.message.guild.icon_url)
        embed.set_footer(text=self.bot.user.name,
                         icon_url=self.bot.user.avatar_url)
        embed.add_field(inline=False, name="General Information:",
                        value=f'Role name: **{role.mention}**\nRole ID: `{role.id}`\nRole Position: **{role.position}**\nRole Color Hex: `{role.color}`\n\nIs role mentioned separately from online members? **{role.hoist}**\nIs role mentionable? **{role.mentionable}**\nIs role managed by integration? **{role.managed}**')
        embed.add_field(inline=False, name="Dates:",
                        value=f'Role was created at **{role.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}**\nRole was created **{role_created_days} **')
        embed.add_field(inline=False, name="Permission info:",
                        value=f'Role Permission Integer: `{role.permissions.value}`\n\nPermissions: **{permissions}**')
        await ctx.send(embed=embed)

    @commands.command(name='prune', description="Deletes messages")
    @isoncooldown
    async def prune(self, ctx, amount: int = 50):
        try:
            await ctx.message.delete()
        except:
            pass
        user = self.bot.user
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.author.id == user.id:
                counter += 1
                return True
            else:
                return False
        try:
            deleted = await ctx.channel.purge(limit=amount, check=check)
            await ubc.create_cooldown(ctx, 2,180)
        except:
            pass
# TODO ability to add a mod log channel and write an async handler to webhook the data to the channel.
# TODO: 2) TEMPBAN 5) invite lookup
# TODO add logging features such as member log, vc log, ban log, unban log, kick log, and so on and so forth


def setup(bot):
    bot.add_cog(Moderation(bot))
