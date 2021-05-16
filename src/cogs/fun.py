import os
import json
import random
import asyncio
import discord
import aiohttp
import logging
import datetime
import coloredlogs

from discord.ext import commands

log = logging.getLogger("fun cog")
coloredlogs.install(logger=log)
async def api_call(call_uri,state=True):
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{call_uri}") as response:
			response= await response.json()
			if state:
				return response['url']
			if state ==False:
				return response

class Fun(commands.Cog):
	"""
	Random fun commands <:LMAO:843365384064204801>
	"""
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")
		
	@commands.cooldown(5,7,commands.BucketType.user)
	@commands.command(name="furrify",aliases=['owo','uwu'])
	async def furrify(self, ctx, *, msg):
		try:
			await ctx.message.delete()
		except discord.HTTPException:
			pass
		response=await api_call(f"https://nekos.life/api/v2/owoify?text={msg}",False)
		return await ctx.send(response['owo'])
	
	@commands.cooldown(5,10,commands.BucketType.user)
	@commands.command(name="8ball")
	async def ball(self,ctx,question:str):
		response=await api_call(f"https://nekos.life/api/v2/8ball",False)
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
		response = await api_call("https://coffee.alexflipnote.dev/random.json",False)
		embed = discord.Embed(
			title = "*Coffee!*",
			color = ctx.message.author.color,
			timestamp=ctx.message.created_at
		)
		embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
		embed.set_image(url = response['file'])

		await ctx.message.reply(embed = embed)       

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases = ['random_name'])
	async def randomname(self, ctx):
		response = await api_call("https://nekos.life/api/v2/name",False)
		await ctx.message.reply(response['name'])
		
	@commands.cooldown(3, 5, commands.BucketType.user)
	@commands.command()
	async def quote(self, ctx):
		results = ""
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://type.fit/api/quotes") as response:
				response= await response.read()
				response=json.loads(response)
				results = response
		num = random.randint(1, 1500)
		content = results[num]['text']
		author=results[num]['author']
		await ctx.message.reply(f"\"{content}\" - {author}")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases=['meow', 'simba', 'cats'])
	async def cat(self, ctx):
		response = await api_call("http://aws.random.cat/meow",False)
		embed = discord.Embed(title = "Cute catto! <a:ConfusedCat:820562537971449886>", color = ctx.message.author.color,timestamp=ctx.message.created_at)
		embed.set_image(url = response['file'])
		embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
		await ctx.message.reply(embed=embed)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def advice(self, ctx):
		response = ""
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://api.adviceslip.com/advice") as response:
				response= await response.read()
				response=json.loads(response)
		advice = response['slip']['advice']
		await ctx.message.reply(advice)

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
		response=await api_call("https://nekos.life/api/v2/fact",False)
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
		
	@commands.command(aliases=['e'])
	@commands.cooldown(3, 7, commands.BucketType.user)
	@commands.has_guild_permissions(manage_messages=True)
	async def modecho(self,ctx,member: discord.Member,*,content):
		await ctx.message.delete()
		current_webhooks = await ctx.message.channel.webhooks()
		new_webhook=''
		webhook_count=[]
		for webhook in current_webhooks:
			if webhook.name=="Davie bot webhook":
				webhook_count.append(webhook)
		if(len(webhook_count)>1):
			new_webhook = await ctx.message.channel.create_webhook(name='Davie bot webhook',reason="Bot webhook")
			for webhook in webhook_count:
				await webhook.delete()
		elif len(webhook_count)==0:
			new_webhook=await ctx.message.channel.create_webhook(name='Davie bot webhook',reason="Bot webhook")
		elif len(webhook_count)==1:
			for webhook in webhook_count:
				new_webhook=webhook
		await webhook.send(content=content,username=member.display_name,avatar_url=member.avatar_url)
def setup(bot):
	bot.add_cog(Fun(bot))