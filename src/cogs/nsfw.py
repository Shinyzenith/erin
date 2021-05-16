import json
import discord
import asyncio
import aiohttp
import logging
import requests
import datetime
import coloredlogs

from discord.ext import commands
from discord.ext.commands import cooldown, BucketType

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || 
"""
log = logging.getLogger("NSFW cog")
coloredlogs.install(logger=log)


async def api_call(call_uri, returnObj=False):
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{call_uri}") as response:
			response = await response.json()
			if returnObj == False:
				return response["url"]
			elif returnObj == True:
				return response


class NSFW(commands.Cog):
	"""
	Meme commands <a:awkwardkid:843361776619618304> ~~There's a slight possibility that they aren't memes~~
	"""

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def hentai(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="Juicy henti for you!",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)

			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)

			embed.set_image(
				url=await api_call("https://nekos.life/api/v2/img/Random_hentai_gif")
			)
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def erok(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="Erok Kitsune !!!",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)

			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)

			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/erok"))
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def eroneko(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="***ERO*** NEKO!",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)

			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)

			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/erokemo"))
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="feet", aliases=["feetgif", "foot"])
	async def feet(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="***Feet***",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)

			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)

			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/feetg"))
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def cum(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="***Sticky white stuff!***",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/cum"))
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="hthighs", aliases=["hthigh", "animethigh"])
	async def hthighs(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="Thic thighs!",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(
				url=await api_call("https://shiro.gg/api/images/nsfw/thighs")
			)
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="nekofuck", aliases=["nekosex", "nekogif"])
	async def nekofuck(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="Catgirls!!!!",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(
				url=await api_call("https://nekos.life/api/v2/img/nsfw_neko_gif")
			)
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="futanari")
	async def futanari(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(
				url=await api_call("https://nekos.life/api/v2/img/futanari")
			)
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="boobs", aliases=["boob"])
	async def boobs(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="**Tiddies**!!!!!",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/boobs"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="blowjob", aliases=["bj"])
	async def blowjob(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="Oh shit!",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/blowjob"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def pussy(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="Dang!",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/pussy"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def spank(self, ctx, user: commands.Greedy[discord.Member] = None):
		if ctx.channel.is_nsfw():
			if user == None:
				await ctx.message.reply("Who do you want to spank?")
				return
			spanked_users = "".join([f"{users.mention} " for users in user])
			embed = discord.Embed(
				title="Oooof!",
				description=f"{spanked_users} got spanked by {ctx.author.mention}",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/spank"))
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def lesbian(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				color=ctx.message.author.color, timestamp=ctx.message.created_at
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/les"))
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def trap(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				color=ctx.message.author.color, timestamp=ctx.message.created_at
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/trap"))
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command()
	async def hololewd(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				color=ctx.message.author.color, timestamp=ctx.message.created_at
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(
				url=await api_call("https://nekos.life/api/v2/img/hololewd")
			)
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def neko(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="Neko!!!!!",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/ngif"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def foxgirl(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(
				url=await api_call("https://nekos.life/api/v2/img/fox_girl")
			)

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="lewdkitsune", aliases=["lewdk"])
	async def lewdkitsune(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/lewdk"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def kuni(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/kuni"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def femdom(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/femdom"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def erofeet(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/erofeet"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def solo(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/solog"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="gasm", aliases=["orgasm", "orgy"])
	async def gasm(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/gasm"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def yuri(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/yuri"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def anal(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(
				title="",
				color=ctx.message.author.color,
				timestamp=ctx.message.created_at,
			)
			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)
			embed.set_image(url=await api_call("https://nekos.life/api/v2/img/anal"))

			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(3, 7, commands.BucketType.user)
	@commands.command(name="wallpaper", aliases=["wl"])
	async def wallpaper(self, ctx):
		if ctx.channel.is_nsfw():
			embed = discord.Embed(color=0xFFC0CB)
			embed.set_image(
				url=await api_call("https://nekos.life/api/v2/img/wallpaper")
			)

			await ctx.send(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(3, 7, commands.BucketType.user)
	@commands.command(name="ass", aliases=["hentaiass", "hass"])
	async def ass(self, ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=hass", True)
			embed = discord.Embed(
				title="", color=response["color"], timestamp=ctx.message.created_at
			)

			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)

			embed.set_image(url=response["message"])
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(3, 7, commands.BucketType.user)
	@commands.command(name="porn", aliases=["pgif"])
	async def porn(self, ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=pgif", True)
			embed = discord.Embed(
				title="", color=response["color"], timestamp=ctx.message.created_at
			)

			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)

			embed.set_image(url=response["message"])
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(3, 7, commands.BucketType.user)
	@commands.command(name="4k")
	async def fourk(self, ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=4k", True)
			embed = discord.Embed(
				title="", color=response["color"], timestamp=ctx.message.created_at
			)

			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)

			embed.set_image(url=response["message"])
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(3, 7, commands.BucketType.user)
	@commands.command(name="yaoi")
	async def yaoi(self, ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=yaoi", True)
			embed = discord.Embed(
				title="", color=response["color"], timestamp=ctx.message.created_at
			)

			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)

			embed.set_image(url=response["message"])
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(3, 7, commands.BucketType.user)
	@commands.command(name="thigh", aliases=["thighs"])
	async def thigh(self, ctx):
		if ctx.channel.is_nsfw():
			response = await api_call("https://nekobot.xyz/api/image?type=thigh", True)
			embed = discord.Embed(
				title="", color=response["color"], timestamp=ctx.message.created_at
			)

			embed.set_footer(
				text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",
				icon_url=ctx.message.author.avatar_url,
			)
			embed.set_author(
				name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url
			)

			embed.set_image(url=response["message"])
			await ctx.message.reply(embed=embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")


def setup(bot):
	bot.add_cog(NSFW(bot))
