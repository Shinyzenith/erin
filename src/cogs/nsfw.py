import discord
import requests
import datetime
from discord.ext.commands import cooldown, BucketType
from discord.ext.commands import (CommandOnCooldown)
from discord.ext import commands

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || 
"""

class NSFW(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def hentai(self, ctx):
		if ctx.channel.is_nsfw():
			response = requests.get("https://shiro.gg/api/images/nsfw/hentai")
			realResponse = response.json()
			embed = discord.Embed(
				title = "Juicy henti for you!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)

			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)

			embed.set_image(url = realResponse['url'])
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
			
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def cum(self, ctx):
		if ctx.channel.is_nsfw():
			response = requests.get("https://nekos.life/api/v2/img/cum")
			realResponse = response.json()
			embed = discord.Embed(
				title = "***Sticky white stuff!***",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = realResponse['url'])
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def thighs(self, ctx):
		if ctx.channel.is_nsfw():
			response = requests.get("https://shiro.gg/api/images/nsfw/thighs")
			realResponse = response.json()
			embed = discord.Embed(
				title = "Thic thighs!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = realResponse['url'])
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="nekofuck",aliases=['nekosex','nekogif'])
	async def nekofuck(self, ctx):
		if ctx.channel.is_nsfw():
			response = requests.get("https://nekos.life/api/v2/img/nsfw_neko_gif")
			realResponse = response.json()
			embed = discord.Embed(
				title = "Catgirls!!!!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = realResponse['url'])
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def boobs(self, ctx):
		if ctx.channel.is_nsfw():
			response = requests.get("https://nekos.life/api/v2/img/boobs")

			realResponse = response.json()

			embed = discord.Embed(
				title = "**Tiddies**!!!!!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = realResponse['url'])

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def blowjob(self, ctx):
		if ctx.channel.is_nsfw():
			response = requests.get("https://nekos.life/api/v2/img/blowjob")

			realResponse = response.json()

			embed = discord.Embed(
				title = "Oh shit!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = realResponse['url'])

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def pussy(self, ctx):
		if ctx.channel.is_nsfw():
			response = requests.get("https://nekos.life/api/v2/img/pussy")

			realResponse = response.json()

			embed = discord.Embed(
				title = "Dang!",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = realResponse['url'])

			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def spank(self, ctx, user: commands.Greedy[discord.Member] = None):
		if ctx.channel.is_nsfw():
			if user == None:
				await ctx.message.reply("Who do you want to spank?")
				return
			response = requests.get("https://nekos.life/api/v2/img/spank").json()
			spanked_users="".join([f"{users.mention} " for users in user])
			embed = discord.Embed(
				title = "Oooof!",
				description = f"{spanked_users} got spanked by {ctx.author.mention}",
				color = ctx.message.author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
			embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
			embed.set_image(url = response['url'])
			await ctx.message.reply(embed = embed)
		else:
			await ctx.message.reply("This command can only be used in a NSFW channel.")
def setup(bot):
	bot.add_cog(NSFW(bot))