import discord
import asyncio
import os
import aiosqlite

from discord.ext import commands,tasks
from discord.enums import ActivityType, Status
from typing import Union
from aiohttp import ClientResponseError
from discord.ext import commands, tasks
from discord.ext.commands.view import StringView

class Utility(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} Cog has been loaded\n-----")
	# on guild add , add a default prefix
	@commands.Cog.listener()
	async def on_guild_join(self,guild):
		db = await aiosqlite.connect('./db/prefix.db')
		sql = "INSERT INTO prefix(guild_id, prefix) VALUES (?,?);"
		val = (guild.id, '-',)
		cursor = await db.execute(sql,val)
		await cursor.close()
		await db.commit()
		await db.close()
	#on guild remove, remove all the prefixes from the database
	@commands.Cog.listener()
	async def on_guild_remove(self,guild):
		db = await aiosqlite.connect("./db/prefix.db")
		sql = f"DELETE FROM prefix WHERE guild_id={guild.id}"
		cursor = await db.execute(sql)
		await cursor.close()
		await db.commit()
		await db.close()
	#print guild prefixes on pinging the bot
	@commands.Cog.listener()
	async def on_message(self,message):
		try:
			if message.mentions[0] == self.bot.user:
				prefix_list=[]
				db = await aiosqlite.connect('./db/prefix.db')
				cursor= await db.execute('SELECT prefix FROM prefix WHERE guild_id=?',(message.guild.id,))
				prefixes = await cursor.fetchall()
				await cursor.close()
				await db.commit()
				for item in prefixes:
					for p in item:
						prefix_list.append(str(p))
				if len(prefix_list)==0:
					cursor= await db.execute('INSERT INTO prefix(guild_id, prefix) VALUES(?,?)',(message.guild.id,'-'))
					await cursor.close()
					await db.commit()
					prefix_list.append('-')
				await db.close()
				reply_message="".join([f"\n`{prefix}`" for prefix in prefix_list])
				await message.reply(f"My prefixes in this server are:{reply_message}")
		except:
			pass
	#helper functions for all prefix commands
	async def get_prefix_list(self,ctx):
		guild_id=ctx.message.guild.id
		prefix_list=[]
		db = await aiosqlite.connect('./db/prefix.db')
		cursor= await db.execute('SELECT prefix FROM prefix WHERE guild_id=?',(ctx.message.guild.id,))
		prefixes = await cursor.fetchall()
		await cursor.close()
		await db.commit()
		for item in prefixes:
			for p in item:
				prefix_list.append(str(p))
		await db.close()
		return prefix_list

	#prefix manager sub command
	@commands.group(name="prefix",aliases=['setprefix'],case_insensitive=True)
	@commands.cooldown(10, 120, commands.BucketType.guild)
	@commands.has_permissions(manage_guild=True)
	async def prefix(self,ctx):
		if ctx.invoked_subcommand is None:
			await ctx.message.reply("please mention a proper argument such as `add` or `remove`")
	@prefix.command()
	@commands.has_permissions(manage_guild=True)
	async def add(self,ctx,*,prefix:str=None):
		prefix_list = await self.get_prefix_list(ctx)
		embed=discord.Embed(color=ctx.message.author.color,timestamp=ctx.message.created_at)
		embed.set_footer(text=ctx.message.author.display_name,icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

		if not prefix:
			embed.title="Current prefix list"
			prefixNames="".join([f"`{prefix}`\n" for prefix in prefix_list])
			embed.description=prefixNames
			embed.set_thumbnail(url=ctx.message.author.avatar_url)
			return await ctx.message.reply("Please mention a valid prefix to be set.", embed=embed)
		for character in prefix:
			if ord(character)>127:
				return await ctx.message.reply("Unicode characters are not allowed as custom guild prefix.")
		if len(prefix_list)>=3:
			return await ctx.message.reply(f"Unable to add `{prefix}` as a custom prefix. Guild has reached the max amount (3) of custom prefixes.\nRun `{ctx.prefix}removeprefix` to free up a slot")
		if prefix in prefix_list:
			return await ctx.message.reply(f"Prefix `{prefix}` already exists.")
		if len(prefix)>2:
			return await ctx.message.reply("Please enter a valid 2 character prefix.")
		if '"' in prefix or "'" in prefix:
			return await ctx.message.reply("Please avoid using \' or \" during prefix setup ");

		db = await aiosqlite.connect("./db/prefix.db")
		sql="INSERT INTO prefix(guild_id, prefix) VALUES (?,?)"
		val = (ctx.message.guild.id,prefix,)
		cursor = await db.execute(sql,val)
		await cursor.close()
		await db.commit()
		await db.close()

		embed.title="Prefix added"
		embed.description=f"`{prefix}` added to guild prefix list"

		return await ctx.message.reply(embed=embed)
	@prefix.command()
	@commands.has_permissions(manage_guild=True)
	async def remove(self,ctx,*,prefix:str=None):
		prefix_list=await self.get_prefix_list(ctx)
		embed=discord.Embed(color=ctx.message.author.color,timestamp=ctx.message.created_at)
		embed.set_footer(text=ctx.message.author.display_name,icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

		if len(prefix_list)<2:
			return await ctx.message.reply("Guild must have atleast 1 prefix, add another one before removing any.")
		if len(prefix)>2:
			return await ctx.message.reply("Please provide a valid prefix to remove.")
		if not (prefix in prefix_list):
			return await ctx.message.reply(f"`{prefix}` is not a custom prefix in `{ctx.message.guild.name}`")
		
		db=await aiosqlite.connect("./db/prefix.db")
		cursor = await db.execute("DELETE FROM prefix WHERE guild_id=? AND prefix=?",(ctx.message.guild.id,prefix))
		await cursor.close()
		await db.commit()
		await db.close()
		embed.title="Prefix removed"
		embed.description=f"`{prefix}` removed from guild prefix list"
		return await ctx.message.reply(embed=embed)

	#bot owner only, sets the bot activity
	@commands.command(aliases=["presence"])
	@commands.is_owner()
	async def activity(self, ctx, activity_type: str.lower,status_type:str.lower,*, message: str):
		if activity_type == "clear":
			await self.set_presence()
			embed = discord.Embed(title="Activity Removed", color=ctx.message.author.color)
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

		embed = discord.Embed(title="Activity Changed", description=msg, color=ctx.message.author.color)
		return await ctx.send(embed=embed)
	#helper function for activity command
	async def set_presence(self, *, status=None, activity_type=None, activity_message=None):
		if status=="idle":
			status=discord.Status.idle
		elif status=="online":
			status=discord.Status.online
		elif status=="offline":
			status=discord.Status.invisible
		elif status=="dnd":
			status=discord.Status.do_not_disturb
			
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
			url = "https://www.twitch.tv/pokimane" # cuz i'm a simp
			pass

		if activity_type is not None:
			activity = discord.Activity(type=activity_type, name=activity_message, url=url)
		else:
			activity = None
		await self.bot.change_presence(activity=activity, status=status)
		return activity, status
def setup(bot):
	bot.add_cog(Utility(bot))