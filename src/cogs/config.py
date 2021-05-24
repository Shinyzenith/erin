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
import traceback
import coloredlogs
import motor.motor_asyncio

from typing import Union
from pathlib import Path
from discord.utils import get
from discord.ext import commands, tasks
from aiohttp import ClientResponseError
from discord.ext import commands, tasks
from discord.enums import ActivityType, Status
from discord.ext.commands.view import StringView
from collections import OrderedDict, deque, Counter


async def webhook_send(
        url,
        message,
        username="Erin Logs",
        avatar="https://raw.githubusercontent.com/AakashSharma7269/erin/main/erin.png?token=AOP54YUJCVK5WQY5LQ6AK5TAWOXYK",
):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(
            url, adapter=discord.AsyncWebhookAdapter(session)
        )
        if isinstance(message, discord.Embed):
            await webhook.send(embed=message, username=username, avatar_url=avatar)
        else:
            await webhook.send(message, username=username, avatar_url=avatar)
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


class GuildConfigManager:
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


class Config(commands.Cog):
    """
    Configuration commands for the server admins!
    """

    def __init__(self, bot):
        self.bot = bot
        self.gcm = GuildConfigManager()

    @commands.Cog.listener()
    async def on_ready(self):
        log.warn(f"{self.__class__.__name__} Cog has been loaded")

    # on guild add , add a default prefix

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.gcm.register_guild(guild)
        channelEmbed = discord.Embed(
            name="Erin added!",
            description=f"Erin was added to `{guild.name}`",
            color=11661816,
        )
        channelEmbed.add_field(name="Guild ID:", value=guild.id, inline=False)
        channelEmbed.add_field(name="Guild owner id:",
                               value=guild.owner.id, inline=False)
        channelEmbed.add_field(name="Guild owner:",
                               value=f"<@{guild.owner.id}> , {guild.owner}", inline=False)
        channelEmbed.set_thumbnail(url=guild.icon_url)
        channelEmbed.set_footer(
            text=guild.name,
            icon_url=guild.icon_url,
        )
        channelEmbed.set_author(
            name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
        )
        await webhook_send(
            os.getenv("GUILDADDLOG"),
            message=channelEmbed,
            username="Erin join logs"
        )

    # on guild remove, remove all the prefixes from the database

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.gcm.unregister_guild(guild)
        print("Erin removed!")
        channelEmbed = discord.Embed(
            name="Erin removed :c",
            description=f"Erin was removed from `{guild.name}`",
            color=11661816,
        )
        channelEmbed.add_field(name="Guild ID:", value=guild.id, inline=False)
        channelEmbed.add_field(name="Guild owner id:",
                               value=guild.owner.id, inline=False)
        channelEmbed.add_field(name="Guild owner:",
                               value=f"<@{guild.owner.id}> , {guild.owner}", inline=False)
        channelEmbed.set_thumbnail(url=guild.icon_url)
        channelEmbed.set_footer(
            text=guild.name,
            icon_url=guild.icon_url,
        )
        channelEmbed.set_author(
            name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
        )
        await webhook_send(
            os.getenv("GUILDREMOVELOG"),
            message=channelEmbed,
            username="Erin leave logs"
        )
    # print guild prefixes on pinging the bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if len(message.mentions) == 1:
            if message.mentions[0] == self.bot.user:
                message_content = message.content.split()
                try:
                    if message_content[1].lower() == "prefix":
                        prefixes = await self.gcm.get_prefix(message.guild)
                        reply_message = "".join(
                            [f"\n`{prefix}`" for prefix in prefixes])
                        await message.reply(f"My prefixes in this server are:{reply_message}")
                except:
                    pass

    # prefix manager sub command
    @commands.group(name="prefix", aliases=["setprefix"], case_insensitive=True, description="Sets my prefix!")
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
        prefixes = await self.gcm.get_prefix(ctx.guild)
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
        added = await self.gcm.add_prefix(ctx.guild, prefix)
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
        prefixes = await self.gcm.get_prefix(ctx.guild)

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
        removed = await self.gcm.remove_prefix(ctx.guild, prefix)
        if removed:
            embed.title = "Prefix removed"
            embed.description = f"`{prefix}` removed from guild prefix list"
        else:
            embed.title = "Prefix not removed"
            embed.description = f"`{prefix}` was already in the guild prefix list"
        return await ctx.message.reply(embed=embed)

    @commands.group(name="muterole", case_insensitive=True, description="Sets up a `Muted` role!")
    @commands.cooldown(10, 120, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    async def muterole(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.message.reply(
                "please mention a proper argument such as `add`, `remove` or `show`"
            )

    @muterole.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def _add(self, ctx, muted_role: discord.Role):
        bot = ctx.guild.get_member(self.bot.user.id)

        # if the muted role is @everyone then throw badargument error
        if muted_role.id == ctx.guild.id:
            raise commands.errors.BadArgument(
                message='Role "@everyone" not found.')

        if muted_role.managed == True:
            raise commands.errors.BadArgument(
                message=f"{muted_role.mention} is managed by discord integration and cannot be added to anyone by me."
            )

        if muted_role.position > bot.top_role.position:
            return await ctx.send(
                "I cannot assign the role to mute members as it is above my highest role."
            )

        add = await self.gcm.add_muted_role(ctx.guild, muted_role.id)
        if add:
            return await ctx.message.reply(f"Mute role for `{ctx.guild.name}` updated.")

    @muterole.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def _remove(self, ctx):
        try:
            await self.gcm.remove_muted_role(ctx.guild)
        except KeyError:
            return await ctx.message.reply(
                f"Muted role doesn't exist for `{ctx.guild.name}`"
            )
        return await ctx.message.reply(f"Mute role for `{ctx.guild.name}` removed.")

    @muterole.command(name="show")
    async def _show(self, ctx):
        try:
            muted_role_id = await self.gcm.get_muted_role(ctx.guild)
        except KeyError:
            return await ctx.message.reply(
                f"No mute role has been setup for {ctx.guild.name}"
            )
        muted_role = get(ctx.message.guild.roles, id=muted_role_id)
        embed = discord.Embed(
            title=f"{ctx.guild.name} - muted role is:",
            description=f"{muted_role.mention}",
            timestamp=ctx.message.created_at,
            color=ctx.message.author.color,
        )
        return await ctx.message.reply(embed=embed)

    @commands.group(name="banappeal", case_insensitive=True, description="Sets the ban appeal link")
    @commands.cooldown(10, 120, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    async def banappeal(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.message.reply(
                "please mention a proper argument such as `add`, `remove` or `show`"
            )

    @banappeal.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def __add(self, ctx, *, url: str):
        ban_appeal = await self.gcm.add_ban_appeal(ctx.guild, url)
        if ban_appeal:
            return await ctx.message.reply(
                f"Ban appeal link for `{ctx.guild.name}` updated."
            )

    @banappeal.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def __remove(self, ctx):
        try:
            await self.gcm.remove_ban_appeal(ctx.guild)
        except KeyError:
            return await ctx.message.reply(
                f"Ban appeal link doesn't exist for `{ctx.guild.name}`"
            )
        return await ctx.message.reply(
            f"Ban appeal link for `{ctx.guild.name}` removed."
        )

    @banappeal.command(name="show")
    async def __show(self, ctx):
        try:
            ban_appeal = await self.gcm.get_ban_appeal(ctx.guild)
        except KeyError:
            return await ctx.message.reply(
                f"No ban appeal link has been setup for {ctx.guild.name}"
            )
        embed = discord.Embed(
            title=f"{ctx.guild.name} - Ban appeal link:",
            description=f"{ban_appeal}",
            timestamp=ctx.message.created_at,
            color=ctx.message.author.color,
        )
        return await ctx.message.reply(embed=embed)

    @commands.group(name="currencygen", case_insensitive=True, description="Sets the `drop/pick` channel")
    @commands.cooldown(10, 120, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    async def currencygen(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.message.reply(
                "please mention a proper argument such as `add`, `remove` or `show`"
            )

    @currencygen.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def ___add(self, ctx, *, channel: discord.TextChannel):
        currencyChannel = await self.gcm.update_currency_channel(ctx.guild, channel.id)
        if currencyChannel:
            return await ctx.message.reply(
                f"Currency generation channel for `{ctx.guild.name}` has been updated."
            )

    @currencygen.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def ___remove(self, ctx):
        try:
            await self.gcm.remove_currency_channel(ctx.guild)
        except KeyError:
            return await ctx.message.reply(
                f"Currency generation channel config doesn't exist for `{ctx.guild.name}`"
            )
        return await ctx.message.reply(
            f"Currency generation channel for `{ctx.guild.name}` removed."
        )

    @currencygen.command(name="show")
    async def ___show(self, ctx):
        try:
            currencyChannel = await self.gcm.get_currency_channel(ctx.guild)
        except KeyError:
            return await ctx.message.reply(
                f"No currency generation channel has been setup for {ctx.guild.name}"
            )
        if not ctx.guild.get_channel(currencyChannel):
            return await ctx.message.reply(
                f"No currency generation channel has been setup for {ctx.guild.name}"
            )
        embed = discord.Embed(
            title=f"{ctx.guild.name} - Currency generation channel:",
            description=f"{ctx.guild.get_channel(currencyChannel).mention}",
            timestamp=ctx.message.created_at,
            color=ctx.message.author.color,
        )
        return await ctx.message.reply(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)

    @commands.command()
    @commands.group(name="ping", description="Shows you my ping!")
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
        em.set_author(name=self.bot.user.name,
                      icon_url=self.bot.user.avatar_url)
        em.set_thumbnail(url=ctx.message.author.avatar_url)
        em.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=em)

    @commands.command(name="uptime", description="Check my uptime")
    async def uptime(self, ctx):
        delta = datetime.datetime.utcnow() - self.bot.startup_time
        await ctx.send(f"I started up {humanize.precisedelta(delta)} ago")

    @commands.command(
        name="invite", description="Get a invite link to add me to your server"
    )
    async def invite(self, ctx):

        perms = discord.Permissions.all()
        
        await ctx.send(
            f"<{discord.utils.oauth_url(self.bot.user.id, permissions=perms)}>"
        )
        


def setup(bot):
    bot.add_cog(Config(bot))
