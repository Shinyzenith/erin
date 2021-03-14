import discord
import datetime
import random
import aiohttp
import requests
import os
from discord.ext import commands

class Fun(commands.Cog):
	def __init__(self, client):
		self.client = client
		
	@commands.command(name="furrify",aliases=['owo','uwu'])
	async def furrify(self, ctx, *, msg):

		vowels = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']

		def last_replace(s, old, new):
			li = s.rsplit(old, 1)
			return new.join(li)

		def text_to_owo(text):
			smileys = [';;w;;', '^w^', '>w<', 'UwU', '(・`ω\´・)', '(´・ω・\`)']

			text = text.replace('L', 'W').replace('l', 'w')
			text = text.replace('R', 'W').replace('r', 'w')

			text = last_replace(text, '!', '! {}'.format(random.choice(smileys)))
			text = last_replace(text, '?', '? owo')
			text = last_replace(text, '.', '. {}'.format(random.choice(smileys)))

			for v in vowels:
				if 'n{}'.format(v) in text:
					text = text.replace('n{}'.format(v), 'ny{}'.format(v))
				if 'N{}'.format(v) in text:
					text = text.replace('N{}'.format(v), 'N{}{}'.format('Y' if v.isupper() else 'y', v))

			return text

		await ctx.send(text_to_owo(msg))        
				
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def neko(self, ctx):
		response = requests.get("https://shiro.gg/api/images/neko")

		realResponse = response.json()

		embed = discord.Embed(
			title = "Neko!!!!! CATGIRL!!!",
			color = ctx.message.author.color,
			timestamp=ctx.message.created_at
		)
		embed.set_footer(text=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}",icon_url=ctx.message.author.avatar_url)
		embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.avatar_url)
		embed.set_image(url = realResponse['url'])

		await ctx.send(embed = embed)                

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

def setup(client):
	client.add_cog(Fun(client))