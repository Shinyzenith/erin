import discord
import requests
import typing
from discord.ext import commands

class Actions(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} Cog has been loaded\n-----")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def hug(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Mention someone you wanna hug ;)")
			return
		hugged_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "aww hugs uwu",
			description = f"this is so cute >< {ctx.author.mention} just hugged {hugged_users}",
			color = 0xFFC0CB
			)
		embed.set_image(url=requests.get("https://nekos.life/api/hug").json()['url'])

		await ctx.send(embed = embed)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def kiss(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Why are you so lonely? Mention someone that you wanna kiss, you can't kiss yourself :(")
			return

		if user == ctx.author:
			await ctx.message.reply("Imagine kissing yourself... why are you so lonely")
			return
		kissed_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "<a:kissr:808235262261723156><a:kissl:808235261708337182>",
			description = f"{ctx.author.mention} just kissed {kissed_users}",
			color = 0xFFC0CB
			)
		embed.set_image(url=requests.get("https://nekos.life/api/kiss").json()['url'])

		await ctx.send(embed=embed)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def pat(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Why are you so lonely? Mention someone that you wanna pat, you can't pat yourself :(")
			return

		if user == ctx.author:
			await ctx.message.reply("Imagine patting yourself... why are you so lonely")
			return
		pat_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "*cute pats*",
			description = f"<a:uwuAYAYA:800611977247719424> {ctx.author.mention} just patted {pat_users}",
			color = 0xFFC0CB
			)
		embed.set_image(url=requests.get("https://nekos.life/api/pat").json()['url'])

		await ctx.send(embed=embed)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def slap(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Who do you want to slap idiot? Mention it next time.")
			return

		if user == ctx.author:
			await ctx.message.reply("Imagine slapping yourself... why are you so lonely")
			return
		slapped_users="".join(f'{users.mention} ' for users in user)
		embed = discord.Embed(
			title = "Damn boi!",
			description = f"{slapped_users} just got slapped by {ctx.author.mention}.",
			color = 0xFFC0CB
		)
		embed.set_image(url = requests.get("https://nekos.life/api/v2/img/slap").json()['url'])

		await ctx.send(embed=embed)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def tickle(self, ctx, user: commands.Greedy[discord.Member] = None):
		if user == None:
			await ctx.message.reply(f"Who do you want to tickle idiot? Mention it next time.")
			return

		if user == ctx.author:
			await ctx.message.reply("Imagine tickling yourself... why are you so lonely")
			return
		tickled_users="".join([f"{users.mention} " for users in user])
		embed = discord.Embed(
			title = "Tickle, tickle!",
			description = f"{tickled_users} just got tickled by {ctx.author.mention}.",
			color = 0xFFC0CB
		)
		embed.set_image(url = requests.get("https://nekos.life/api/v2/img/tickle").json()['url'])

		await ctx.send(embed=embed)

def setup(client):
	client.add_cog(Actions(client))