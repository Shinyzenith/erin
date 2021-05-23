import os
import ast
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
from discord.ext import commands, tasks
from aiohttp import ClientResponseError
from discord.ext import commands, tasks
from discord.enums import ActivityType, Status
from discord.ext.commands.view import StringView
from collections import OrderedDict, deque, Counter


async def webhook_send(
        url,
        message,
        username="Erin uptime Logs",
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


log = logging.getLogger("Owner cog")
coloredlogs.install(logger=log)


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.warn(f"{self.__class__.__name__} Cog has been loaded")

    @commands.command(
        name="reloadone", aliases=["r1", "rone"], description="Reload an extension", hidden=True
    )
    @commands.is_owner()
    async def reloadone(self, ctx, extension):
        try:
            self.bot.reload_extension(extension)
            await ctx.send(f"**:repeat: Reloaded** `{extension}`")
            log.warning(
                f"[+] {extension} reloaded by {ctx.message.author.display_name}#{ctx.message.author.discriminator}  -  {ctx.message.author.id}"
            )
        except Exception as e:
            full = "".join(traceback.format_exception(
                type(e), e, e.__traceback__, 1))
            await ctx.send(
                f"**:warning: Extension `{extension}` not reloaded.**\n```py\n{full}```"
            )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx):
        log.info("")
        cwd = Path(__file__).parents[0]
        cwd = str(cwd)
        msg = "```"
        for file in os.listdir(cwd):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    self.bot.unload_extension(f"cogs.{file[:-3]}")
                except:
                    pass
                self.bot.load_extension(f"cogs.{file[:-3]}")
                msg += f"\n[+] Loaded cogs.{file[:-3]}"
                log.warning(
                    f"[+] Reloaded cogs.{file[:-3]} by {ctx.message.author.display_name}#{ctx.message.author.discriminator}  -  {ctx.message.author.id}"
                )
        msg += "```"
        log.info("")
        return await ctx.message.reply(msg)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension):
        try:
            self.bot.unload_extension(extension)
            await ctx.send(f"**:x: Unloaded** `{extension}`")
            log.warning(
                f"[+] {extension} Unloaded by {ctx.message.author.display_name}#{ctx.message.author.discriminator}  -  {ctx.message.author.id}"
            )
        except Exception as e:
            full = "".join(traceback.format_exception(
                type(e), e, e.__traceback__, 1))
            await ctx.send(
                f"**:warning: Extension `{extension}` not unloaded.**\n```py\n{full}```"
            )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension):
        try:
            self.bot.load_extension(extension)
            await ctx.send(f"**:white_check_mark: loaded** `{extension}`")
            log.warning(
                f"[+] {extension} Loaded by {ctx.message.author.display_name}#{ctx.message.author.discriminator}  -  {ctx.message.author.id}"
            )
        except Exception as e:
            full = "".join(traceback.format_exception(
                type(e), e, e.__traceback__, 1))
            await ctx.send(
                f"**:warning: Extension `{extension}` not loaded.**\n```py\n{full}```"
            )
        # bot owner only, sets the bot activity

    @commands.command(aliases=["presence"], hidden=True)
    @commands.is_owner()
    async def activity(
            self, ctx, activity_type: str.lower, status_type: str.lower, *, message: str
    ):
        if activity_type == "clear":
            await self.set_presence()
            embed = discord.Embed(
                title="Activity Removed", color=ctx.message.author.color
            )
            return await ctx.send(embed=embed)

        try:
            activity_type = ActivityType[activity_type]
        except KeyError:
            return await ctx.send(
                f"{ctx.message.author.mention}, mention a proper activity object."
            )

        try:
            status_type = Status[status_type]
        except KeyError:
            return await ctx.send(
                f"{ctx.message.author.mention}, mention a proper status object."
            )

        activity, _ = await self.set_presence(
            activity_type=activity_type, activity_message=message, status=status_type
        )
        msg = f"Activity set to: {activity.type.name.capitalize()} "
        if activity.type == ActivityType.listening:
            msg += f"to {activity.name}."
        elif activity.type == ActivityType.competing:
            msg += f"in {activity.name}."
        else:
            msg += f"{activity.name}."

        embed = discord.Embed(
            title="Activity Changed", description=msg, color=ctx.message.author.color
        )
        log.warn(
            f"Bot activity command issued by {ctx.message.author.display_name}#{ctx.message.author.discriminator}  -  {ctx.message.author.id}\nCommand ran: {ctx.message.content}"
        )
        return await ctx.send(embed=embed)

    # helper function for activity command

    async def set_presence(
            self, *, status=None, activity_type=None, activity_message=None
    ):
        if status == "idle":
            status = discord.Status.idle
        elif status == "online":
            status = discord.Status.online
        elif status == "offline":
            status = discord.Status.invisible
        elif status == "dnd":
            status = discord.Status.do_not_disturb

        if activity_type is None:
            activity_type = discord.Game
        url = None
        if activity_type is not None and not activity_message:
            activity_message = "Erin-bot"

        if activity_type == ActivityType.listening:
            if activity_message.lower().startswith("to "):
                activity_message = activity_message[3:].strip()
        elif activity_type == ActivityType.competing:
            if activity_message.lower().startswith("in "):
                activity_message = activity_message[3:].strip()
        elif activity_type == ActivityType.streaming:
            url = "https://www.twitch.tv/pokimane"  # cuz i'm a simp
            pass

        if activity_type is not None:
            activity = discord.Activity(
                type=activity_type, name=activity_message, url=url
            )
        else:
            activity = None
        await self.bot.change_presence(activity=activity, status=status)
        return activity, status

    @commands.command(aliases=["reboot"], hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        await webhook_send(
            os.getenv("UPTIMELOG"),
            f"Bot restart command issued by {ctx.message.author.mention}",
        )
        log.warn(
            f"Bot restart command issued by {ctx.message.author.display_name}#{ctx.message.author.discriminator}  -  {ctx.message.author.id}"
        )
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @commands.command(name="logout", description="Logout the bot", hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        await webhook_send(
            os.getenv("UPTIMELOG"),
            f"Bot logout command issued by {ctx.message.author.mention}",
        )
        log.warn(
            f"Bot logout command issued by {ctx.message.author.display_name}#{ctx.message.author.discriminator}  -  {ctx.message.author.id}"
        )
        await self.bot.close()

    @commands.command(aliases=['run', 'eval'], hidden=True)
    @commands.is_owner()
    async def eval_fn(self, ctx, *, cmd):
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        self.insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }

        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))

        await ctx.send(f"{result}")

    def insert_returns(self, body):
        # insert return stmt if the last expression is a expression statement
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        # for if statements, we insert returns into the body and the orelse
        if isinstance(body[-1], ast.If):
            insert_returns(body[-1].body)
            insert_returns(body[-1].orelse)

        # for with blocks, again we insert returns into the body
        if isinstance(body[-1], ast.With):
            insert_returns(body[-1].body)


def setup(bot):
    bot.add_cog(Owner(bot))
