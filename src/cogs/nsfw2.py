import discord
import asyncio
import os
import discord
import requests
import datetime
import asyncio
import aiohttp
import json
import logging, coloredlogs

from discord.ext.commands import cooldown, BucketType
from discord.ext.commands import (CommandOnCooldown)
from discord.ext import commands

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || 
"""
log = logging.getLogger("NSFW(2) cog")
coloredlogs.install(logger=log)
async def api_call(call_uri):
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{call_uri}") as response:
			response= await response.json()
			return response

class NSFW2(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")
	
	@commands.cooldown(3,7,commands.BucketType.user)
	@commands.command(name="ass",aliases=['hentaiass','hass'])
	async def ass(self,ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=hass")
			embed = discord.Embed(
				title = "",
				color = response['color'],
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = response['message'] )
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
	
	@commands.cooldown(3,7,commands.BucketType.user)
	@commands.command(name="porn",aliases=['pgif'])
	async def porn(self,ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=pgif")
			embed = discord.Embed(
				title = "",
				color = response['color'],
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = response['message'] )
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(3,7,commands.BucketType.user)
	@commands.command(name="4k")
	async def fourk(self,ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=4k")
			embed = discord.Embed(
				title = "",
				color = response['color'],
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = response['message'] )
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(3,7,commands.BucketType.user)
	@commands.command(name="yaoi")
	async def yaoi(self,ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=yaoi")
			embed = discord.Embed(
				title = "",
				color = response['color'],
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = response['message'] )
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(3,7,commands.BucketType.user)
	@commands.command(name="thigh",aliases=['thighs'])
	async def thigh(self,ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=thigh")
			embed = discord.Embed(
				title = "",
				color = response['color'],
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = response['message'] )
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

def setup(bot):
	bot.add_cog(NSFW2(bot))