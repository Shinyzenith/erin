import discord
import datetime
import random
import aiohttp
import requests
import json
import asyncio
import logging,coloredlogs
import os
from discord.ext import commands

log = logging.getLogger("fun cog")
coloredlogs.install(logger=log)
async def api_call(call_uri):
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{call_uri}") as response:
			response= await response.json()
			return response['url']

class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")
		
	@commands.cooldown(5,7,commands.BucketType.user)
	@commands.command(name="furrify",aliases=['owo','uwu'])
	async def furrify(self, ctx, *, msg):
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://nekos.life/api/v2/owoify?text={msg}") as response:
				response=await response.read()
				response=response.decode("utf-8")
				response=json.loads(response)
				return await ctx.message.reply(response['owo'])
	
	@commands.cooldown(5,10,commands.BucketType.user)
	@commands.command(name="8ball")
	async def ball(self,ctx,question:str):
		response=""
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://nekos.life/api/v2/8ball") as response:
				response=await response.json()
		embed = discord.Embed(
			title = "8ball",
			color = ctx.message.author.color,
			timestamp=ctx.message.created_at,
			description=response['response']
		)
		embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
		embed.set_image(url =response['url'])
		await ctx.message.reply(embed = embed)

	@commands.cooldown(1 ,3,commands.BucketType.user)
	@commands.command()
	async def coffee(self,ctx):
		response = requests.get("https://coffee.alexflipnote.dev/random.json")
		realResponse = response.json()
		embed = discord.Embed(
			title = "*Coffee!*",
			color = ctx.message.author.color,
			timestamp=ctx.message.created_at
		)
		embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
		embed.set_image(url = realResponse['file'])

		await ctx.message.reply(embed = embed)       

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases = ['random_name'])
	async def randomname(self, ctx):
		await ctx.message.reply(requests.get("https://nekos.life/api/v2/name").json()['name'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def quote(self, ctx):
		results = requests.get('https://type.fit/api/quotes').json()
		num = random.randint(1, 1500)
		content = results[num]['text']
		await ctx.message.reply(content)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases=['meow', 'simba', 'cats'])
	async def cat(self, ctx):
		async with aiohttp.ClientSession() as cs:
			async with cs.get("http://aws.random.cat/meow") as r:
				data = await r.json()

				embed = discord.Embed(title = "Cute catto! <a:ConfusedCat:820562537971449886>", color = ctx.message.author.color,timestamp=ctx.message.created_at)
				embed.set_image(url = data['file'])
				embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
				embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
				await ctx.message.reply(embed=embed)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def advice(self, ctx):
		url = "https://api.adviceslip.com/advice"
		response = requests.get(url)
		advice = response.json()
		real_advice = advice['slip']['advice']
		await ctx.message.reply(real_advice)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def mock(self, ctx, *,text=None):

		if text == None:
			await ctx.message.reply("Please enter some text!")
		else:

			filter = ['@here', '@everyone', '<@&', '<@!']

			for word in filter:
				if text.count(word) > 0:
					await ctx.message.reply(f"Don't even try to ping with me.")
					return

			res = ""
			for c in text:
				chance = random.randint(0,1)
				if chance:
					res += c.upper()
				else:
					res += c.lower()
			await ctx.message.reply(res)
	@commands.cooldown(3,5,commands.BucketType.user)
	@commands.command()
	async def fact(self,ctx):
		reponse=""
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://nekos.life/api/v2/fact") as response:
				response=await response.json()

		return await ctx.message.reply(response['fact'])

	@commands.cooldown(5, 7, commands.BucketType.user)
	@commands.command(name="goose")
	async def goose(self, ctx):
		embed = discord.Embed(
			title = "",
			color = ctx.message.author.color,
			timestamp=ctx.message.created_at
		)
		embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
		embed.set_image(url = await api_call("https://nekos.life/api/v2/img/goose"))
		await ctx.message.reply(embed = embed)

	@commands.cooldown(3, 7, commands.BucketType.user)
	@commands.command(name="waifu")
	async def waifu(self, ctx):
		embed = discord.Embed(
			title = "",
			color = ctx.message.author.color,
			timestamp=ctx.message.created_at
		)
		embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
		embed.set_image(url = await api_call("https://nekos.life/api/v2/img/waifu"))

		await ctx.send(embed = embed)
		
def setup(bot):
	bot.add_cog(Fun(bot))