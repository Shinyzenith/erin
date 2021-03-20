from discord.ext import commands
import discord
import json
import random
import os
import time
import asyncio
import logging,coloredlogs
import motor.motor_asyncio

log = logging.getLogger("gambling cog")
coloredlogs.install(logger=log)
global ongoing_duel
ongoing_duel = []


def GLE(title=None, description=None, author=None, footer=None, thumbnail=None):  # Good Looking Error
	embed = discord.Embed(
		title=title,
		description=description,
		colour=discord.Color.red()
	)
	embed.set_footer(
		text=footer,
		icon_url=author
	)
	return embed


def SFR(title=None, description=None, author=None, footer=None, thumbnail=None):  # SatisFactory Response
	embed = discord.Embed(
		title=title,
		description=description,
		colour=discord.Color.green()
	)
	embed.set_footer(
		text=footer,
		icon_url=author
	)
	return embed


class EconomyHandler:
	def __init__(self):
		self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("CONNECTIONURI"))
		self.db = self.client.erin
		self.col = self.db["economy"]
		self.crates = self.db["crates"]

	async def find_user(self, uid: int):
		user = await self.col.find_one({"uid": uid})
		if not user:
			user = await self.register_user(uid)
		return user

	async def register_user(self, uid: int):
		data = {"uid": uid, "erin": 0}
		await self.col.insert_one(data)
		return data

	async def update_user(self, uid: int, data):
		await self.col.replace_one({"uid": uid}, data)

	async def fetch_crates(self, uid: int):
		user = await self.crates.find_one({'uid': uid})
		if not user:
			user = {"uid": uid, "basic": 0, "advanced": 0, "ultra": 0}
			await self.crates.insert_one(user)
		return user

	async def update_crates(self, uid: int, data):
		await self.crates.replace_one({"uid": uid}, data)


class Gambling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.eh = EconomyHandler()

	def load_shop(self):
		shop = json.load(
			open("./json/shop.json", "r")
		)
		return shop

	def load_crates(self):
		crates = json.load(
			open("./json/crates.json", "r")
		)
		return crates

	@commands.command()
	async def pick(self, ctx):
		try:
			await ctx.message.delete()
		except:
			pass

	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")

	@commands.command()
	@commands.cooldown(5, 300, commands.BucketType.user)
	async def gamble(self, ctx, quantity: int = 10):
		uid = ctx.author.id
		user = await self.eh.find_user(uid)
		if quantity <= user["erin"]:
			if quantity <= 5000:
				rr = 1.25
			if quantity <= 8000:
				rr = 1.5
			if quantity > 8000:
				rr = 2
			luck = random.randint(1, 2)
			if luck == 2:
				user["erin"] -= quantity
				user["erin"] += int(quantity*rr)
				await self.eh.update_user(uid, user)
				return await ctx.send(embed=SFR(
					None,
					f"You landed a heads! :coin: , your investment matured with a return of `{int(quantity*rr)} erins` \N{White Heavy Check Mark}",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
			else:
				user["erin"] -= int(quantity*(abs(1-rr)))
				if user["erin"] < 0:
					user["erin"] = 0
				await self.eh.update_user(uid, user)
				return await ctx.send(embed=GLE(
					None,
					f"lol sadphroge <a:bonk:821245636061429772>, you landed tails :pensive: and made a loss of `{int(quantity*(abs(1-rr)))} erins` <:erin:820473033700671569>",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
		else:
			return await ctx.send(embed=GLE(
				None,
				f"You don't have `{quantity} erin` to gamble",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))

	@commands.command()
	@commands.cooldown(5, 180, commands.BucketType.user)
	async def duel(self, ctx, member: discord.Member = None, amount=1, item=None):
		global ongoing_duel
		if ctx.author.id in ongoing_duel:
			return await ctx.send(embed=GLE(
				None,
				f"You cannot start another duel while being in one",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))
		ongoing_duel.append(ctx.author.id)
		if not item:
			ongoing_duel.remove(ctx.author.id)
			return await ctx.send(embed=GLE(
				None,
				f"pls mention the bet for this battle",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))
		if not member:
			ongoing_duel.remove(ctx.author.id)
			return await ctx.send(embed=GLE(
				None,
				f"pls mention a user",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))		
		else:
			if member.id == ctx.author.id:
				ongoing_duel.remove(ctx.author.id)
				return await ctx.send(embed=GLE(
					None,
					f"you can't battle yourself dumass <:shoko:820338188228886569>",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
			uid = ctx.author.id
			mid = member.id
			u1 = await self.eh.find_user(uid)
			u2 = await self.eh.find_user(mid)
			if not item in u1:
				u1[item] = 0
			if not item in u2:
				u2[item] = 0
			if amount > u1[item]:
				ongoing_duel.remove(ctx.author.id)
				return await ctx.send(embed=GLE(
					None,
					f"You can't battle for more than what you have <:mai:820332737973059584>",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
			if amount > u2[item]:
				ongoing_duel.remove(ctx.author.id)
				return await ctx.send(embed=GLE(
					None,
					f"The person you are attempting to battle doesn't have enough currency <:mai:820332737973059584>",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
			if member.id in ongoing_duel:
				ongoing_duel.remove(ctx.author.id)
				return await ctx.send(embed=GLE(
					None,
					f"The person you are attempting to battle is already in a duel <:mai:820332737973059584>",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
			msg = await ctx.send(embed=SFR(
				None,
				f"{member.mention} has been dueled by `{ctx.author.name}#{ctx.author.discriminator}`, the reward is `{amount} {item}`. Accept? (y/n)",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))

			def check(m):
				condition = False
				if m.content.lower() == "y" or m.content.lower() == "yes" or m.content.lower() == "n" or m.content.lower() == "no":
					condition = True
				return m.author.id == member.id and m.channel.id == ctx.channel.id and condition

			try:
				m = await self.bot.wait_for('message', timeout=60, check=check)
			except asyncio.TimeoutError:
				await msg.edit(embed=GLE(
					None,
					f"`{member.name}#{member.discriminator}` did not accept the duel within the time period",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
				ongoing_duel.remove(ctx.author.id)
			else:
				if m.content.lower() == "n" or m.content.lower() == "no":
					ongoing_duel.remove(ctx.author.id)
					return await msg.edit(embed=GLE(
						None,
						f"Person declined your duel request <:hana:820288678689636363>",
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					))
				ongoing_duel.append(member.id)
				await msg.edit(embed=SFR(
					None,
					f"`{member.name}#{member.discriminator}` has accepted the duel :crossed_swords: ",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
				shop = self.load_shop()
				random_emoj = shop[random.choice(list(shop.keys()))]["emoji"]
				msg = await ctx.send("this message will change in several seconds, first to say `-pick` will win the award")
				await asyncio.sleep(random.randint(7, 12))
				await msg.edit(content=random_emoj)

				def check2(m):
					return (m.author.id == member.id or m.author.id == ctx.author.id) and m.channel.id == ctx.channel.id and m.content == "-pick"
				try:
					m = await self.bot.wait_for('message', timeout=15, check=check2)
				except asyncio.TimeoutError:
					await msg.edit(content=f"nobody won, breh")
				else:
					winner = m.author
					if u1["uid"] == winner.id:
						u1[item] += amount
						u2[item] -= amount
					else:
						u2[item] += amount
						u1[item] -= amount
					await self.eh.update_user(uid, u1)
					await self.eh.update_user(mid, u2)
					ongoing_duel.remove(ctx.author.id)
					ongoing_duel.remove(member.id)
					return await ctx.send(f"`{winner.name}#{winner.discriminator}` won UwU :>")

	@commands.command()
	async def crates(self, ctx):
		user = await self.eh.fetch_crates(ctx.author.id)
		embed = discord.Embed(color=ctx.author.color)
		embed.title = f"{ctx.author.name}'s Crates"
		crates = self.load_crates()
		del user["uid"]
		del user["_id"]
		for crate in user:
			embed.add_field(
				name=crates[crate]["name"],
				value=user[crate]
			)
		return await ctx.send(embed=embed)

	@commands.group(name="case", aliases=['lootcase', "crate"], case_insensitive=True)
	async def case(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.message.reply(embed=GLE(
				None,
				"The correct format to open a case be `-case <type(basic,advanced,ultra)>`",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))

	@case.command()
	async def basic(self, ctx):
		user = await self.eh.fetch_crates(ctx.author.id)
		u = await self.eh.find_user(ctx.author.id)
		shop = self.load_shop()
		if user["basic"] == 0:
			return await ctx.send(embed=GLE(
				None,
				"You don't have any basic crates <:kofuku:820337881074761758>",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))
		else:
			user["basic"] -= 1
		weights = random.sample(range(1, 500), 3)
		drops = self.load_crates()
		basic_crate = drops["basic"]["items"]
		embed = discord.Embed()
		embed.title = "You got:"
		embed.description = ""
		for weight in weights:
			item = random.choice(basic_crate)
			if not item in u:
				u[item] = 0
			u[item] += weight
			embed.description += f"\n {shop[item]['emoji']} {weight} {item}"
			basic_crate.remove(item)
		await self.eh.update_user(ctx.author.id, u)
		await self.eh.update_crates(ctx.author.id, user)
		return await ctx.send(embed=embed)

	@case.command()
	async def advanced(self, ctx):
		user = await self.eh.fetch_crates(ctx.author.id)
		u = await self.eh.find_user(ctx.author.id)
		shop = self.load_shop()
		if user["advanced"] == 0:
			return await ctx.send(embed=GLE(
				None,
				"You don't have any advanced crates <:kofuku:820337881074761758>",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))
		else:
			user["advanced"] -= 1
		weights = random.sample(range(1, 20), 3)
		drops = self.load_crates()
		basic_crate = drops["advanced"]["items"]
		embed = discord.Embed()
		embed.title = "You got:"
		embed.description = ""
		for weight in weights:
			item = random.choice(basic_crate)
			if not item in u:
				u[item] = 0
			u[item] += weight
			embed.description += f"\n {shop[item]['emoji']} {weight} {item}"
			basic_crate.remove(item)
		await self.eh.update_user(ctx.author.id, u)
		await self.eh.update_crates(ctx.author.id, user)
		return await ctx.send(embed=embed)

	@case.command()
	async def ultra(self, ctx):
		user = await self.eh.fetch_crates(ctx.author.id)
		u = await self.eh.find_user(ctx.author.id)
		shop = self.load_shop()
		if user["ultra"] == 0:
			return await ctx.send(embed=GLE(
				None,
				"You don't have any ultra crates <:kofuku:820337881074761758>",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))
		else:
			user["ultra"] -= 1
		weights = random.sample(range(1, 50), 3)
		drops = self.load_crates()
		basic_crate = drops["ultra"]["items"]
		embed = discord.Embed()
		embed.title = "You got:"
		embed.description = ""
		for weight in weights:
			item = random.choice(basic_crate)
			if not item in u:
				u[item] = 0
			u[item] += weight
			embed.description += f"\n {shop[item]['emoji']} {weight} {item}"
			basic_crate.remove(item)
		await self.eh.update_user(ctx.author.id, u)
		await self.eh.update_crates(ctx.author.id, user)
		return await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Gambling(bot))