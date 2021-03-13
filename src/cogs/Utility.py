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
				reply_message="".join([f"\n`{prefix}`" for prefix in prefix_list])
				await message.reply(f"My prefixes in this server are:{reply_message}")
		except:
			pass
		# await self.bot.process_commands(message) 

	@commands.command(name="addprefix")
	@commands.has_permissions(administrator=True)
	async def addprefix(self,ctx,prefix:str=None):
		prefix_list=[]
		embed=discord.Embed(color=ctx.message.author.color,timestamp=ctx.message.created_at)
		embed.set_footer(text=ctx.message.author.display_name,icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
		db = await aiosqlite.connect('./db/prefix.db')
		cursor= await db.execute('SELECT prefix FROM prefix WHERE guild_id=?',(ctx.message.guild.id,))
		prefixes = await cursor.fetchall()
		await cursor.close()
		await db.commit()
		for item in prefixes:
			for p in item:
				prefix_list.append(str(p))
		if not prefix:
			embed.title="Current prefix list"
			prefixNames="".join([f"`{prefix}`\n" for prefix in prefix_list])
			embed.description=prefixNames
			embed.set_thumbnail(url=ctx.message.author.avatar_url)
			await db.close()
			return await ctx.message.reply("Please mention a valid prefix to be set.", embed=embed)
		for character in prefix:
			if ord(character)>127:
				return await ctx.message.reply("Unicode characters are not allowed as custom guild prefix.")
		if len(prefix_list)>=3:
			await db.close()
			return await ctx.message.reply(f"Unable to add `{prefix}` as a custom prefix. Guild has reached the max amount (3) of custom prefixes.\nRun `{ctx.prefix}removeprefix` to free up a slot")
		if prefix in prefix_list:
			await db.close()
			return await ctx.message.reply(f"Prefix `{prefix}` already exists.")
		if len(prefix)>2:
			await db.close()
			return await ctx.message.reply("Please enter a valid 2 character prefix.")
		if '"' in prefix or "'" in prefix:
			await db.close()
			return await ctx.message.reply("Please avoid using \' or \" during prefix setup ");
		sql="INSERT INTO prefix(guild_id, prefix) VALUES (?,?)"
		val = (ctx.message.guild.id,prefix,)
		cursor = await db.execute(sql,val)
		await cursor.close()
		await db.commit()
		await db.close()
		embed.title="Prefix added"
		embed.description=f"`{prefix}` added to guild prefix list"
		return await ctx.message.reply(embed=embed)

	@commands.command(aliases=["presence"])
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