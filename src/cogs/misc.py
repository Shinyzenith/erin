import os
import sys
import time
import psutil
import asyncio
import aiohttp
import discord
import logging
import humanize
import datetime
import aiosqlite
import traceback
import coloredlogs
import motor.motor_asyncio

from typing import Union
from pathlib import Path
from discord.ext import commands, tasks
from aiohttp import ClientResponseError
from discord.ext import commands, tasks
from discord.enums import ActivityType, Status
from discord.ext.commands.view import StringView
from collections import OrderedDict, deque, Counter


log = logging.getLogger("Utility cog")
coloredlogs.install(logger=log)
allowed_ords = (
    list(range(65, 91))
    + list(range(97, 123))
    + [32, 33, 35, 36, 37, 38, 42, 43, 45, 46, 47]
    + list(range(48, 65))
    + list(range(90, 97))
)


class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        if self.value == 1:
            return f"{self.value} {format_spec}"
        else:
            return f"{self.value} {format_spec}s"


class PrefixManager:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("CONNECTIONURI"))
        self.db = self.client.erin
        self.col = self.db["prefix"]

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


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pm = PrefixManager()

    @commands.Cog.listener()
    async def on_ready(self):
        log.warn(f"{self.__class__.__name__} Cog has been loaded")

    # on guild add , add a default prefix

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.pm.register_guild(guild)

    # on guild remove, remove all the prefixes from the database

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.pm.unregister_guild(guild)

    # print guild prefixes on pinging the bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return
        prefixes = await self.pm.get_prefix(message.guild)
        if len(message.mentions) > 0:
            if message.mentions[0] == self.bot.user:
                reply_message = "".join([f"\n`{prefix}`" for prefix in prefixes])
                await message.reply(f"My prefixes in this server are:{reply_message}")

    # prefix manager sub command
    @commands.group(name="prefix", aliases=["setprefix"], case_insensitive=True)
    @commands.cooldown(10, 120, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.message.reply(
                "please mention a proper argument such as `add` or `remove`"
            )

    @prefix.command()
    @commands.has_permissions(manage_guild=True)
    async def add(self, ctx, *, prefix: str = None):
        prefixes = await self.pm.get_prefix(ctx.guild)
        embed = discord.Embed(
            color=ctx.message.author.color, timestamp=ctx.message.created_at
        )
        embed.set_footer(
            text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
        )
        embed.set_author(
            name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
        )

        if not prefix:
            embed.title = "Current prefix list"
            prefixNames = "".join([f"`{prefix}`\n" for prefix in prefixes])
            embed.description = prefixNames
            embed.set_thumbnail(url=ctx.message.author.avatar_url)
            return await ctx.message.reply(
                "Please mention a valid prefix to be set.", embed=embed
            )
        for character in prefix:
            if ord(character) not in allowed_ords:
                return await ctx.message.reply(
                    f"The character `{character}` in this prefix is not permitted"
                )
        if len(prefixes) >= 3:
            return await ctx.message.reply(
                f"Unable to add `{prefix}` as a custom prefix. Guild has reached the max amount (3) of custom prefixes.\nRun `{ctx.prefix}prefix remove <prefix to be removed>` to free up a slot"
            )
        if prefix in prefixes:
            return await ctx.message.reply(f"Prefix `{prefix}` already exists.")
        if len(prefix) > 2:
            return await ctx.message.reply("Please enter a valid 2 character prefix.")
        for item in prefixes:
            if prefix in item or item in prefix:
                return await ctx.message.reply(
                    f"`{prefix}` is technically present in `{item}`. Remove `{item}` before proceeding to add `{prefix}`"
                )
        added = await self.pm.add_prefix(ctx.guild, prefix)
        if added:
            embed.title = "Prefix added"
            embed.description = f"`{prefix}` added to guild prefix list"
        else:
            embed.title = "Prefix not added"
            embed.description = f"`{prefix}` was alerady in the prefix list"
        return await ctx.message.reply(embed=embed)

    @prefix.command()
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx, *, prefix: str = None):
        prefixes = await self.pm.get_prefix(ctx.guild)

        embed = discord.Embed(
            color=ctx.message.author.color, timestamp=ctx.message.created_at
        )

        embed.set_footer(
            text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
        )

        embed.set_author(
            name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
        )

        if len(prefixes) < 2:
            return await ctx.message.reply(
                "Guild must have atleast 1 prefix, add another one before removing any."
            )
        if len(prefix) > 2:
            return await ctx.message.reply("Please provide a valid prefix to remove.")
        if not (prefix in prefixes):
            return await ctx.message.reply(
                f"`{prefix}` is not a custom prefix in `{ctx.message.guild.name}`"
            )
        removed = await self.pm.remove_prefix(ctx.guild, prefix)
        if removed:
            embed.title = "Prefix removed"
            embed.description = f"`{prefix}` removed from guild prefix list"
        else:
            embed.title = "Prefix not removed"
            embed.description = f"`{prefix}` was already in the guild prefix list"
        return await ctx.message.reply(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def ping(self, ctx):
        time_now = time.time()
        msg = await ctx.message.reply(
            embed=discord.Embed(title="Pinging...", color=0x00FFFF)
        )
        embed = discord.Embed(
            title="Pong! :ping_pong:",
            description=f"API Latency: **{round(self.bot.latency * 1000)}ms**\nBot Latency: **{round((time.time() - time_now) * 1000)}ms**",
            color=0x00FFFF,
        )
        embed.set_footer(
            text=f"{ctx.message.author.display_name}#{ctx.message.author.discriminator}",
            icon_url=ctx.message.author.avatar_url,
        )
        embed.set_author(
            name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
        )
        await msg.edit(embed=embed)

    @commands.command(name="stats", aliases=["status"], description="View system stats")
    async def stats(self, ctx):
        channel_types = Counter(
            isinstance(c, discord.TextChannel) for c in self.bot.get_all_channels()
        )
        text = channel_types[True]

        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        em = discord.Embed(title="Bot Stats", color=discord.Color.blurple())
        em.add_field(
            name="General info:",
            inline=False,
            value=f"Total Guilds: **{len(list(self.bot.guilds))}**\nTotal Users: **{len(list(self.bot.users))}**\nTotal Channels: **{text}**",
        )
        em.add_field(
            name="Developers:",
            inline=False,
            value="<@633967275090771971> (Shinyzenith#6969)\n<@488688724948025357>(DankCoder#9983)",
        )
        em.add_field(
            name="Server info:",
            value=f"Discord.py Version: **{discord.__version__}**\nPython verion: **{sys.version}**\nVerion info: **{sys.version_info}**\n\nCPU: **{psutil.cpu_percent()}% used with {plural(psutil.cpu_count()):CPU}**\nMemory: **{humanize.naturalsize(mem.used)}/{humanize.naturalsize(mem.total)} ({mem.percent}% used)**\nDisk Space: **{humanize.naturalsize(disk.used)}/{humanize.naturalsize(disk.total)} ({disk.percent}% used)**",
        )
        em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        em.set_thumbnail(url=ctx.message.author.avatar_url)
        em.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=em)

    @commands.command(name="uptime", description="Check my uptime")
    async def uptime(self, ctx):
        delta = datetime.datetime.utcnow() - self.bot.startup_time
        await ctx.send(f"I started up {humanize.naturaldelta(delta)} ago")

    @commands.command(
        name="invite", description="Get a invite link to add me to your server"
    )
    async def invite(self, ctx):
        perms = discord.Permissions.all()
        await ctx.send(
            f"<{discord.utils.oauth_url(self.bot.user.id, permissions=perms)}>"
        )


def setup(bot):
    bot.add_cog(Misc(bot))
