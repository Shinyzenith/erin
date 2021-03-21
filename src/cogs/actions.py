import json
import typing
import aiohttp
import asyncio
import discord
import logging
import requests
import coloredlogs

from discord.ext import commands

log = logging.getLogger("actions cog")
coloredlogs.install(logger=log)
async def api_call(call_uri,state=True):
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{call_uri}") as response:
			response= await response.json()
			if state:
				return response['url']
			if state ==False:
				return response

class Actions(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")

	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def hug(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Mention someone you wanna hug ;)")
			return
		hugged_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "aww hugs uwu",
			description = f"{ctx.author.mention} just hugged {hugged_users}",
			color = 0xFFC0CB
			)
		embed.set_image(url=await api_call("https://nekos.life/api/v2/img/hug"))

		await ctx.send(", ".join([users.mention for users in user]),embed = embed)
	
	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def laugh(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Mention someone you wanna laugh at ;)")
			return
		laughedat="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "AHAHAHAH!!",
			description = f"{ctx.author.mention} just laughed at {laughedat}",
			color = 0xFFC0CB
			)
		response=await api_call("http://api.nekos.fun:8080/api/laugh",state=False)
		embed.set_image(url=response['image'])

		await ctx.send(", ".join([users.mention for users in user]),embed = embed)
	
	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def lick(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Mention someone you wanna lick ;)")
			return
		licked_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "*Tasty*",
			description = f"{ctx.author.mention} just licked {licked_users}",
			color = 0xFFC0CB
			)
		response=await api_call("http://api.nekos.fun:8080/api/lick",state=False)
		embed.set_image(url=response['image'])

		await ctx.send(", ".join([users.mention for users in user]),embed = embed)

	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def cry(self, ctx):
		embed = discord.Embed(
			title = "<a:KannaCry:822716843440734218><a:KannaCry:822716843440734218><a:KannaCry:822716843440734218>",
			color = 0xFFC0CB
			)
		response=await api_call("http://api.nekos.fun:8080/api/cry",state=False)
		embed.set_image(url=response['image'])

		await ctx.send(embed = embed)

	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def cuddle(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Mention someone you wanna cuddle ;)")
			return
		cuddle_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "aww cuddles uwu",
			description = f"{ctx.author.mention} just cuddled {cuddle_users}",
			color = 0xFFC0CB
			)
		embed.set_image(url=await api_call("https://nekos.life/api/v2/img/cuddle"))

		await ctx.send(", ".join([users.mention for users in user]),embed = embed)

	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def kiss(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Mention someone you wanna kiss ;)")
			return

		if user == ctx.author:
			await ctx.message.reply("Imagine kissing yourself...")
			return
		kissed_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "<a:nekokissr:820991965217816607><a:nekokissl:820992009702604850>",
			description = f"{ctx.author.mention} just kissed {kissed_users}",
			color = 0xFFC0CB
			)
		embed.set_image(url=await api_call("https://nekos.life/api/v2/img/kiss"))

		await ctx.send(", ".join([users.mention for users in user]),embed=embed)

	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def pat(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Mention someone you wanna pat ;)")
			return

		if user == ctx.author:
			await ctx.message.reply("Imagine patting yourself...")
			return
		pat_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "*cute pats*",
			description = f"<:kanna:820279669131575306> {ctx.author.mention} just patted {pat_users}",
			color = 0xFFC0CB
			)
		embed.set_image(url=await api_call("https://nekos.life/api/v2/img/pat"))

		await ctx.send(", ".join([users.mention for users in user]),embed=embed)

	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def poke(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Why are you so lonely? Mention someone that you wanna poke, you can't poke yourself :(")
			return

		if user == ctx.author:
			await ctx.message.reply("Imagine patting yourself... why are you so lonely")
			return
		poke_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "***poke poke***",
			description = f"<:kanna:820279669131575306> {ctx.author.mention} just poked {poke_users}",
			color = 0xFFC0CB
			)
		embed.set_image(url=await api_call("https://nekos.life/api/v2/img/poke"))

		await ctx.send(", ".join([users.mention for users in user]),embed=embed)
	
	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def baka(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Who tf are you calling a baka?")
			return
		bakas="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "**BAKA!!**",
			description = f"{bakas}, ANTA BAKA??!?!?!?",
			color = 0xFFC0CB
			)
		embed.set_image(url=await api_call("https://nekos.life/api/v2/img/baka"))

		await ctx.send(", ".join([users.mention for users in user]),embed=embed)
	
	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def feed(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Who tf are you feeding?")
			return
		fed_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "",
			description = f"<:kanna:820279669131575306> {ctx.author.mention} fed {fed_users}",
			color = 0xFFC0CB
			)
		embed.set_image(url=await api_call("https://nekos.life/api/v2/img/feed"))

		await ctx.send(", ".join([users.mention for users in user]),embed=embed)

	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def smug(self, ctx):
		
		embed = discord.Embed(
			title=f"{ctx.author.name} smugged",
			color = 0xFFC0CB
			)
		embed.set_image(url=await api_call("https://nekos.life/api/v2/img/smug"))

		await ctx.send(embed=embed)

	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def slap(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Mention someone you wanna slap ;)")
			return

		if user == ctx.author:
			await ctx.message.reply("Imagine slapping yourself...")
			return
		slapped_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "**Damn son!**",
			description = f"{slapped_users} just got slapped by {ctx.author.mention}.",
			color = 0xFFC0CB
		)
		embed.set_image(url =await api_call("https://nekos.life/api/v2/img/slap"))

		await ctx.send(", ".join([users.mention for users in user]),embed=embed)

	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def tickle(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Mention someone you wanna tickle ;)")
			return

		if user == ctx.author:
			await ctx.message.reply("Imagine tickling yourself...")
			return
		tickled_users="".join([f"{users.mention} " for users in user])
		embed = discord.Embed(
			title = "Tickle, tickle!",
			description = f"{tickled_users} just got tickled by {ctx.author.mention}.",
			color = 0xFFC0CB
		)
		embed.set_image(url = await api_call("https://nekos.life/api/v2/img/tickle"))

		await ctx.send(", ".join([users.mention for users in user]),embed=embed)

def setup(client):
	client.add_cog(Actions(client))