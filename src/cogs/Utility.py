import discord
import asyncio
import os
import aiosqlite
import aiohttp
import motor.motor_asyncio
import sys
import time
import psutil
import datetime
import humanize
import traceback
from discord.ext import commands, tasks
from discord.enums import ActivityType, Status
from typing import Union
from aiohttp import ClientResponseError
from discord.ext import commands, tasks
from discord.ext.commands.view import StringView
from pathlib import path

async def webhook_send(url, message, username="Erin uptime Logs",avatar="https://media.discordapp.net/attachments/769824167188889600/820197487238184960/Erin.jpeg"):
	async with aiohttp.ClientSession() as session:
		webhook = discord.Webhook.from_url(url, adapter=discord.AsyncWebhookAdapter(session))
		if isinstance(message, discord.Embed):
			await webhook.send(embed=message, username=username,avatar_url=avatar)
		else:
			await webhook.send(message, username=username,avatar_url=avatar)

allowed_ords = list(range(65, 91)) + list(range(97, 123)) + \
	[32, 33, 35, 36, 37, 38, 42, 43, 45, 46, 47] + list(range(48, 65)) + list(range(90, 97))

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
		self.client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
		self.db = self.client.guilds
		self.col = self.db["prefix"]

	async def register_guild(self, g, recheck=True):
		if recheck:
			guild = await self.col.find_one({"gid": g.id})
			if not guild:
				guild={"gid": g.id, "prefixes": ["-"]}
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


class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.pm = PrefixManager()

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} Cog has been loaded\n-----")
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
		prefixes = await self.pm.get_prefix(message.guild)
		if len(message.mentions) > 0:
			if message.mentions[0] == self.bot.user:
				reply_message = "".join([f"\n`{prefix}`" for prefix in prefixes])
				await message.reply(f"My prefixes in this server are:{reply_message}")

	# prefix manager sub command
	@commands.group(name="prefix", aliases=['setprefix'], case_insensitive=True)
	@commands.cooldown(10, 120, commands.BucketType.guild)
	@commands.has_permissions(manage_guild=True)
	async def prefix(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.message.reply("please mention a proper argument such as `add` or `remove`")

	@prefix.command()
	@commands.has_permissions(manage_guild=True)
	async def add(self, ctx, *, prefix: str = None):
		prefixes = await self.pm.get_prefix(ctx.guild)
		embed = discord.Embed(color=ctx.message.author.color,
							  timestamp=ctx.message.created_at)
		embed.set_footer(text=ctx.message.author.display_name,
						 icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,
						 icon_url=self.bot.user.avatar_url)

		if not prefix:
			embed.title = "Current prefix list"
			prefixNames = "".join([f"`{prefix}`\n" for prefix in prefixes])
			embed.description = prefixNames
			embed.set_thumbnail(url=ctx.message.author.avatar_url)
			return await ctx.message.reply("Please mention a valid prefix to be set.", embed=embed)
		for character in prefix:
			if ord(character) not in allowed_ords:
				return await ctx.message.reply(f"The character `{character}` in this prefix is not permitted")
		if len(prefixes) >= 3:
			return await ctx.message.reply(f"Unable to add `{prefix}` as a custom prefix. Guild has reached the max amount (3) of custom prefixes.\nRun `{ctx.prefix}prefix remove <prefix to be removed>` to free up a slot")
		if prefix in prefixes:
			return await ctx.message.reply(f"Prefix `{prefix}` already exists.")
		if len(prefix) > 2:
			return await ctx.message.reply("Please enter a valid 2 character prefix.")
		for item in prefixes:
			if prefix in item or item in prefix:
				return await ctx.message.reply(f"`{prefix}` is technically present in `{item}`. Remove `{item}` before proceeding to add `{prefix}`")
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

		embed = discord.Embed(color=ctx.message.author.color,
							  timestamp=ctx.message.created_at)

		embed.set_footer(text=ctx.message.author.display_name,
						 icon_url=ctx.message.author.avatar_url)

		embed.set_author(name=self.bot.user.display_name,
						 icon_url=self.bot.user.avatar_url)

		if len(prefixes) < 2:
			return await ctx.message.reply("Guild must have atleast 1 prefix, add another one before removing any.")
		if len(prefix) > 2:
			return await ctx.message.reply("Please provide a valid prefix to remove.")
		if not (prefix in prefixes):
			return await ctx.message.reply(f"`{prefix}` is not a custom prefix in `{ctx.message.guild.name}`")
		removed = await self.pm.remove_prefix(ctx.guild, prefix)
		if removed:
			embed.title = "Prefix removed"
			embed.description = f"`{prefix}` removed from guild prefix list"
		else:
			embed.title = "Prefix not removed"
			embed.description = f"`{prefix}` was already in the guild prefix list"
		return await ctx.message.reply(embed=embed)

	# bot owner only, sets the bot activity
	@commands.command(aliases=["presence"])
	@commands.is_owner()
	async def activity(self, ctx, activity_type: str.lower, status_type: str.lower, *, message: str):
		if activity_type == "clear":
			await self.set_presence()
			embed = discord.Embed(title="Activity Removed",
								  color=ctx.message.author.color)
			return await ctx.send(embed=embed)

		try:
			activity_type = ActivityType[activity_type]
		except KeyError:
			return await ctx.send(f"{ctx.message.author.mention}, mention a proper activity object.")

		try:
			status_type = Status[status_type]
		except KeyError:
			return await ctx.send(f"{ctx.message.author.mention}, mention a proper status object.")

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

		embed = discord.Embed(title="Activity Changed",
							  description=msg, color=ctx.message.author.color)
		return await ctx.send(embed=embed)
	# helper function for activity command

	async def set_presence(self, *, status=None, activity_type=None, activity_message=None):
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
				type=activity_type, name=activity_message, url=url)
		else:
			activity = None
		await self.bot.change_presence(activity=activity, status=status)
		return activity, status

	@commands.command(aliases=["reboot"])
	@commands.is_owner()
	async def restart(self,ctx):
		await webhook_send(os.getenv("UPTIMELOG"), f"Bot restart command issued by {ctx.message.author.mention}")
		os.execv(sys.executable, [sys.executable] + sys.argv)
	@commands.command(name="logout", description="Logout the bot")
	@commands.is_owner()
	async def logout(self, ctx):
		await webhook_send(os.getenv("UPTIMELOG"), f"Bot logout command issued by {ctx.message.author.mention}")
		await self.bot.logout()
	
	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command()
	async def ping(self, ctx):
		time_now = time.time()
		msg = await ctx.message.reply(embed=discord.Embed(title="Pinging...", color = 0x00FFFF))
		embed = discord.Embed(title="Pong! :ping_pong:", description=f"API Latency: **{round(self.bot.latency * 1000)}ms**\nBot Latency: **{round((time.time() - time_now) * 1000)}ms**", color=0x00FFFF)
		embed.set_footer(text=f"{ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
		await msg.edit(embed=embed)

	@commands.command(name="reloadone",aliases=['r1','rone'], description="Reload an extension")
	@commands.is_owner()
	async def reloadone(self, ctx, extension):
		try:
			self.bot.reload_extension(extension)
			await ctx.send(f"**:repeat: Reloaded** `{extension}`")
		except Exception as e:
			full = "".join(traceback.format_exception(type(e), e, e.__traceback__, 1))
			await ctx.send(f"**:warning: Extension `{extension}` not reloaded.**\n```py\n{full}```")
	
	@commands.command()
	@commands.is_owner()
	async def reload(self,ctx):
		cwd = Path(__file__).parents[0]
		cwd = str(cwd)
		msg="```"
		for file in os.listdir(cwd + "/cogs"):
				if file.endswith(".py") and not file.startswith("_"):
						try: self.bot.unload_extension(f"cogs.{file[:-3]}")
						except: pass       
						self.bot.load_extension(f"cogs.{file[:-3]}")     
						msg+=f"\n[+] Loaded cogs.{file[:-3]}"
						print(f"[+] Loaded cogs.{file[:-3]}")
		msg+="```"
		return await ctx.message.reply(msg)

	@commands.command(name="stats", description="View system stats")
	async def stats(self, ctx):
		em = discord.Embed(title="Server Stats", color=discord.Color.blurple())
		em.add_field(name="CPU", value=f"{psutil.cpu_percent()}% used with {plural(psutil.cpu_count()):CPU}",inline=False)
		mem = psutil.virtual_memory()
		em.add_field(name="Memory", value=f"{humanize.naturalsize(mem.used)}/{humanize.naturalsize(mem.total)} ({mem.percent}% used)",inline=False)
		disk = psutil.disk_usage("/")
		em.add_field(name="Disk", value=f"{humanize.naturalsize(disk.used)}/{humanize.naturalsize(disk.total)} ({disk.percent}% used)",inline=False)
		await ctx.send(embed=em)

	@commands.command(name="uptime", description="Check my uptime")
	async def uptime(self, ctx):
		delta = datetime.datetime.utcnow()-self.bot.startup_time
		await ctx.send(f"I started up {humanize.naturaldelta(delta)} ago")

	@commands.command(name="invite", description="Get a invite link to add me to your server")
	async def invite(self, ctx):
		perms = discord.Permissions.all()
		await ctx.send(f"<{discord.utils.oauth_url(self.bot.user.id, permissions=perms)}>")


def setup(bot):
	bot.add_cog(Utility(bot))