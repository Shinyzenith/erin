import discord
import requests
import datetime
import asyncio
import aiohttp
import json

from discord.ext.commands import cooldown, BucketType
from discord.ext.commands import (CommandOnCooldown)
from discord.ext import commands

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || 
"""
async def api_call(call_uri):
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{call_uri}") as response:
			response=await response.read()
			response=response.decode("utf-8")
			response=json.loads(response)
			return response['url']
			
class NSFW(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def hentai(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "Juicy henti for you!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = await api_call("https://shiro.gg/api/images/nsfw/hentai"))
			await ctx.send(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
			
	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def cum(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "***Sticky white stuff!***",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://shiro.gg/api/images/nsfw/cum"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name='thighs',aliases=['thigh','animethigh'])
	async def thighs(self, ctx):
		if ctx.channel.is_nsfw():
			realResponse = response.json()
			embed = discord.Embed(
				title = "Thic thighs!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://shiro.gg/api/images/nsfw/thighs"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="nekofuck",aliases=['nekosex','nekogif'])
	async def nekofuck(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "Catgirls!!!!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://shiro.gg/api/images/nsfw/nsfw_neko_gif"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def boobs(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "**Tiddies**!!!!!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://shiro.gg/api/images/nsfw/boobs"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def blowjob(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "Oh shit!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://shiro.gg/api/images/nsfw/blowjob"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def pussy(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "Dang!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://shiro.gg/api/images/nsfw/pussy"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def spank(self, ctx, user: commands.Greedy[discord.Member] = None):
		if ctx.channel.is_nsfw():
			if user == None:
				await ctx.message.reply("Who do you want to spank?")
				return
			spanked_users="".join([f"{users.mention} " for users in user])
			embed = discord.Embed(
				title = "Oooof!",
				description = f"{spanked_users} got spanked by {ctx.author.mention}",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://shiro.gg/api/images/nsfw/spank"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
def setup(bot):
	bot.add_cog(NSFW(bot))