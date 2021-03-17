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
			response= await response.json()
			return response['url']
			
class NSFW1(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} Cog has been loaded\n-----")
			
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

			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/Random_hentai_gif"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def erok(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "Erok Kitsune !!!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/erok"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def eroneko(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "***ERO*** NEKO!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/erokemo"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="feet",aliases=['feetgif','foot'])
	async def feet(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "***Feet***",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/feetg"))
			await ctx.message.reply(embed = embed)
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
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/cum"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name='hthighs',aliases=['hthigh','animethigh'])
	async def hthighs(self, ctx):
		if ctx.channel.is_nsfw():
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
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/nsfw_neko_gif"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="futanari")
	async def futanari(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/futanari"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")


	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name='boobs',aliases=['boob'])
	async def boobs(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "**Tiddies**!!!!!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/boobs"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name='blowjob',aliases=['bj'])
	async def blowjob(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "Oh shit!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/blowjob"))

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
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/pussy"))

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
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/spank"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
	

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def lesbian(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/les"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def trap(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/trap"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def hololewd(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/hololewd"))
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def neko(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "Neko!!!!!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/ngif"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def foxgirl(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/fox_girl"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
	
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="lewdkitsune",aliases=['lewdk'])
	async def lewdkitsune(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/lewdk"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def kuni(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/kuni"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")


	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def femdom(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/femdom"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
	
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def erofeet(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/erofeet"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def solo(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/solog"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="gasm",aliases=['orgasm','orgy'])
	async def gasm(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/gasm"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def yuri(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/yuri"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def anal(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title = "",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = await api_call("https://nekos.life/api/v2/img/anal"))

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
	@commands.cooldown(3, 7, commands.BucketType.user)
	@commands.command(name="wallpaper",aliases=['wl'])
	async def wallpaper(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				color = 0xFFC0CB
				)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/wallpaper"))

			await ctx.send(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
def setup(bot):
	bot.add_cog(NSFW1(bot))