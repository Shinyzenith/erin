import os
import sys
import time
import typing
import asyncio
import aiohttp
import discord
import logging
import humanize
import datetime
import traceback
import coloredlogs
import DiscordUtils
import motor.motor_asyncio
from pytz import timezone
from datetime import date
from datetime import datetime
from discord.ext import commands

# Initializing the logger
log = logging.getLogger("Moderation cog")
coloredlogs.install(logger=log)

#mute handler class

############ WORK IN PROGRESS #############################3
class muteHandler:
	def __init__(self):
		self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("CONNECTIONURI"))
		self.db = self.client.erin
		self.col = self.db['mute']

	async def add_mute(self,uid:int,gid:int,data):
		await self.col.replace_one({"uid":uid},data)


################# WORK IN PROGRESS ################################



# Database Handler class
class dbHandler:
	def __init__(self):
		self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("CONNECTIONURI"))
		self.db = self.client.erin
		self.col = self.db["warns"]

	async def find_user(self, uid: int, gid: int):
		user = await self.col.find_one({"uid": uid})
		if not user:
			user = await self.register_user(uid, gid)
		try:
			user[f"{gid}"]
		except KeyError:
			user[f"{gid}"] = []
		finally:
			return user

	async def register_user(self, uid: int, gid: int):
		data = {"uid": uid, f"{str(gid)}": []}
		await self.col.insert_one(data)
		return data

	async def update_user_warn(self, uid: int, data):
		await self.col.replace_one({"uid": uid}, data)


class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.dbHandler = dbHandler()

	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")

	@commands.command(name="warn", aliases=["strike"])
	@commands.has_permissions(manage_messages=True)
	@commands.guild_only()
	async def warn(self, ctx, user: discord.Member, *, reason: str):
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
				f"Cannot warn {user.mention} as their highest role is the same as or above your highest role."
			)

		# editing the user object to hold the user data
		entryData = {
			"type": "strike",
			"reason": reason,
			"time": ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
			"mod": f"{ctx.message.author.id}",
		}
		userData = await self.dbHandler.find_user(user.id, ctx.message.guild.id)
		userData[f"{ctx.message.author.guild.id}"].append(entryData)

		# uodating user entries
		await self.dbHandler.update_user_warn(user.id, userData)

		# building the embed
		channel = discord.Embed(
			description=f"Punishment(s) for {user.display_name}#{user.discriminator} submitted successfully.",
			color=11661816,
			timestamp=ctx.message.created_at,
		)
		channel.set_footer(
			text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
		)
		channel.set_author(
			name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
		)

		dmEmbed = discord.Embed(
			title="Erin Moderation",
			description=f"Your punishments have been updated in {ctx.message.guild.name}.",
			color=11661816,
			timestamp=ctx.message.created_at,
		)

		dmEmbed.add_field(name="Action", value="Strike/Warn", inline=True)

		dmEmbed.add_field(name="Reason", value=f"{reason}", inline=True)

		dmEmbed.add_field(name="Moderator", value=f"<@{entryData['mod']}>", inline=True)

		dmEmbed.set_footer(
			text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
		)
		dmEmbed.set_author(
			name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
		)
		await ctx.message.reply(embed=channel)
		try:
			await user.send(embed=dmEmbed)
		except:
			pass

	@commands.command(name="search", aliases=["warns"])
	@commands.guild_only()
	async def search(self, ctx, searchUser: discord.User):
		user = await self.dbHandler.find_user(searchUser.id, ctx.message.guild.id)
		threshold = 5
		reason_chunk = [
			user[f"{ctx.message.guild.id}"][i : i + threshold]
			for i in range(0, len(user[f"{ctx.message.guild.id}"]), threshold)
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
				text=ctx.message.author.display_name,
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

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
				text=ctx.message.author.display_name,
				icon_url=ctx.message.author.avatar_url,
			)
			emb.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			return await ctx.message.reply(embed=emb)

		else:
			paginator = DiscordUtils.Pagination.CustomEmbedPaginator(
				ctx, remove_reactions=True
			)
			paginator.add_reaction(
				"\N{Black Left-Pointing Double Triangle with Vertical Bar}", "first"
			)
			paginator.add_reaction("\N{Black Left-Pointing Double Triangle}", "back")
			paginator.add_reaction("\N{CROSS MARK}", "lock")
			paginator.add_reaction("\N{Black Right-Pointing Double Triangle}", "next")
			paginator.add_reaction(
				"\N{Black Right-Pointing Double Triangle with Vertical Bar}", "last"
			)
			return await paginator.run(embeds)

	@commands.command()
	@commands.guild_only()
	@commands.has_permissions(administrator=True)
	async def delpunishments(self, ctx, user: discord.User):
		delUser = await self.dbHandler.find_user(user.id, ctx.message.guild.id)
		request = await ctx.message.reply(
			f"**This will delete ALL punishments that the {user.mention} has.** Do you want to continue?"
		)
		await request.add_reaction("\N{WHITE HEAVY CHECK MARK}")
		await request.add_reaction("\N{CROSS MARK}")

		def check(reaction, user):
			state = (
				user == ctx.message.author
				and str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}"
				or str(reaction.emoji) == "\N{CROSS MARK}"
				and reaction.message.id == request.id
				and user.bot == False
			)
			return state

		try:
			reaction, author = await self.bot.wait_for(
				"reaction_add", timeout=30.0, check=check
			)
		except asyncio.TimeoutError:
			return await ctx.message.channel.send(
				"Woops you didnt react within 30 seconds...."
			)

		if str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}":
			try:
				await request.clear_reaction("\N{WHITE HEAVY CHECK MARK}")
				await request.clear_reaction("\N{CROSS MARK}")
			except:
				pass
			delUser.pop(f"{ctx.message.guild.id}")
			await self.dbHandler.update_user_warn(user.id, delUser)
			try:
				return await request.edit(
					content=f"All records of {user.mention} have been deleted"
				)
			except:
				return await ctx.message.reply(
					f"All records of {user.mention} have been deleted"
				)
		elif str(reaction.emoji) == "\N{CROSS MARK}":
			try:
				await request.clear_reaction("\N{WHITE HEAVY CHECK MARK}")
				await request.clear_reaction("\N{CROSS MARK}")
			except:
				pass

			try:
				return await request.edit(
					content=f"\N{CROSS MARK} reaction recieved ...cancelling process"
				)
			except:
				return await ctx.message.reply(
					f"\N{CROSS MARK} reaction recieved ...cancelling process"
				)

	@commands.command()
	@commands.guild_only()
	@commands.has_permissions(ban_members=True)
	async def ban(
		self,
		ctx,
		user: typing.Union[discord.Member, discord.User],
		*,
		reason: str,
	):
		try:
			await ctx.guild.fetch_ban(user)
			channelEmbed = discord.Embed(
			description=f"{user.display_name}#{user.discriminator} is already banned from the server!",
			color=16724787,
			timestamp=ctx.message.created_at,
			)
			channelEmbed.set_footer(
				text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
			)
			channelEmbed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
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
			text=ctx.message.author.display_name,
			icon_url=ctx.message.author.avatar_url,
		)
		channelEmbed.set_author(
			name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
		)
		dmEmbed = discord.Embed(
			title="Erin Moderation",
			description=f"Your punishments have been updated in {ctx.message.guild.name}.",
			color=11661816,
			timestamp=ctx.message.created_at,
		)

		dmEmbed.add_field(name="Action", value="Ban", inline=True)

		dmEmbed.add_field(name="Reason", value=f"{reason}", inline=True)

		dmEmbed.add_field(name="Moderator", value=f"<@{entryData['mod']}>", inline=True)

		dmEmbed.set_footer(
			text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
		)
		dmEmbed.set_author(
			name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
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
					"You can't use me to ban someone below or at the same role level as you :)"
				)

			try:
				await user.send(embed=dmEmbed)
			except:
				pass
			await ctx.message.guild.ban(user, reason=reason)

		userData = await self.dbHandler.find_user(user.id, ctx.message.guild.id)
		userData[f"{ctx.message.author.guild.id}"].append(entryData)
		# uodating user entries
		await self.dbHandler.update_user_warn(user.id, userData)
		return await ctx.message.reply(embed=channelEmbed)

	@commands.command()
	@commands.guild_only()
	@commands.has_permissions(ban_members=True)
	async def softban(
		self,
		ctx,
		user: typing.Union[discord.Member, discord.User],
		*,
		reason: str,
	):
		try:
			await ctx.guild.fetch_ban(user)
			channelEmbed = discord.Embed(
			description=f"{user.display_name}#{user.discriminator} is already banned from the server!",
			color=16724787,
			timestamp=ctx.message.created_at,
			)
			channelEmbed.set_footer(
				text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
			)
			channelEmbed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
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
			text=ctx.message.author.display_name,
			icon_url=ctx.message.author.avatar_url,
		)
		channelEmbed.set_author(
			name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
		)
		dmEmbed = discord.Embed(
			title="Erin Moderation",
			description=f"Your punishments have been updated in {ctx.message.guild.name}.",
			color=11661816,
			timestamp=ctx.message.created_at,
		)

		dmEmbed.add_field(name="Action", value="Softban", inline=True)

		dmEmbed.add_field(name="Reason", value=f"{reason}", inline=True)

		dmEmbed.add_field(name="Moderator", value=f"<@{entryData['mod']}>", inline=True)

		dmEmbed.set_footer(
			text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
		)
		dmEmbed.set_author(
			name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
		)
		if isinstance(user, discord.User):
			await ctx.message.guild.ban(user, reason=reason,delete_message_days=7)
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
					"You can't use me to ban someone below or at the same role level as you :)"
				)

			try:
				await user.send(embed=dmEmbed)
			except:
				pass
			await ctx.message.guild.ban(user, reason=reason,delete_message_days=7)
			await ctx.message.guild.unban(user, reason="softban")								
		userData = await self.dbHandler.find_user(user.id, ctx.message.guild.id)
		userData[f"{ctx.message.author.guild.id}"].append(entryData)
		# uodating user entries
		await self.dbHandler.update_user_warn(user.id, userData)
		return await ctx.message.reply(embed=channelEmbed)

	@commands.command()
	@commands.guild_only()
	@commands.has_permissions(ban_members=True)
	async def unban(
		self,
		ctx,
		user: discord.User,
		*,
		reason: str,
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
				text=ctx.message.author.display_name,
				icon_url=ctx.message.author.avatar_url,
			)
			channelEmbed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			dmEmbed = discord.Embed(
				title="Erin Moderation",
				description=f"Your punishments have been updated in {ctx.message.guild.name}.",
				color=11661816,
				timestamp=ctx.message.created_at,
			)

			dmEmbed.add_field(name="Action", value="Unban", inline=True)

			dmEmbed.add_field(name="Reason", value=f"{reason}", inline=True)

			dmEmbed.add_field(name="Moderator", value=f"<@{entryData['mod']}>", inline=True)

			dmEmbed.set_footer(
				text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
			)
			dmEmbed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			await ctx.message.guild.unban(user, reason=reason)
			try:
				await user.send(embed=dmEmbed)
			except:
				pass

			userData = await self.dbHandler.find_user(user.id, ctx.message.guild.id)
			userData[f"{ctx.message.author.guild.id}"].append(entryData)
			# uodating user entries
			await self.dbHandler.update_user_warn(user.id, userData)
			return await ctx.message.reply(embed=channelEmbed)

		except discord.NotFound:
			channelEmbed = discord.Embed(
			description=f"{user.display_name}#{user.discriminator} is not banned from the server!",
			color=16724787,
			timestamp=ctx.message.created_at,
			)
			channelEmbed.set_footer(
				text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
			)
			channelEmbed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			return await ctx.send(embed=channelEmbed)

	@commands.command()
	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	async def rmpunish(self, ctx, user: discord.User, warn: int = None):
		rmUser = await self.dbHandler.find_user(user.id, ctx.message.guild.id)
		if not warn:
			return await ctx.send(
				f"Please mention the warn id of the reason that you want to delete from {user.mention}'s logs."
			)
		if warn > len(rmUser[f"{ctx.guild.id}"]):
			return await ctx.send(f"Invalid warn id for {user.mention}")
		removedWarn = rmUser[f"{ctx.guild.id}"].pop(warn - 1)
		await self.dbHandler.update_user_warn(user.id, rmUser)

		embed = discord.Embed(
			title="Erin Moderation",
			description=f"Warn removed for {user.mention}. Deleted warn details are:",
			color=11661816,
			timestamp=ctx.message.created_at,
		)

		embed.add_field(name="Action", value=removedWarn["type"], inline=True)

		embed.add_field(name="Reason", value=removedWarn["reason"], inline=True)

		embed.add_field(name="Moderator", value=f"<@{removedWarn['mod']}>", inline=True)

		embed.set_footer(
			text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url
		)
		embed.set_author(
			name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
		)
		try:
			await user.send(embed=embed)
		except:
			pass
		await ctx.reply(embed=embed)


#TODO complete the mute handler class

# TODO: 2) TEMPBAN 3) MUTE COMMAND 4) ADD EXPIRATION FIELD TO THE JSON OBJECT 5) invite lookup
# TODO 6) unmute 7) MUTE HANDLER CLASS 8) tempban time regex
# @TODO ON ADD TO GUILD IT SHOULD BE LOGGED WITH MEMBER COUNT AND OWNER ID
# @ TODO ON GUILD LEAVE SHOULD BE LOGGED
def setup(bot):
	bot.add_cog(Moderation(bot))
