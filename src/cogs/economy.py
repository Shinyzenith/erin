from discord.ext import commands
from datetime import datetime
import discord
import json
import random
import os
import numpy as np
import time
import asyncio
import DiscordUtils
import motor.motor_asyncio
import coloredlogs,logging


log = logging.getLogger("economy cog")
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
		self.client = motor.motor_asyncio.AsyncIOMotorClient(
			'localhost', 27017)
		self.db = self.client.users
		self.col = self.db["economy"]

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


def mean_difference(times):
	times = np.diff(times)
	times = np.mean(times)
	return times


def divide_chunks(l, n):
	return [l[i * n:(i + 1) * n] for i in range((len(l) + n - 1) // n)]


class ActivityRecorder:
	def __init__(self):
		self.activity = {}

	def update(self, gid, msg):
		response = False
		if not gid in self.activity:
			self.activity[gid] = []

		self.activity[gid].append([msg, time.time()])
		if len(self.activity[gid]) > 5:
			active = self.activity[gid][-5:]
			times = [a[1] for a in active]
			times = mean_difference(times)
			if times < 7:
				roll = random.randint(1, 6)
				if roll == 6:
					response = True
			self.activity[gid] = []
		return response


class economy(commands.Cog):
	def __init__(self, bot):
		self.activity = ActivityRecorder()
		self.bot = bot
		self.eh = EconomyHandler()

	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")

	@commands.Cog.listener()
	async def on_message(self, message):
		gid = str(message.guild.id)
		if self.activity.update(gid, message):
			await self.drop(message)

	async def drop(self, msg):
		drop = random.choice(list(self.load_shop().keys()) +
							 ["erin" for i in range(len(self.load_shop())//2)])
		embed = discord.Embed()
		quantity = random.randint(5, 60)
		embed.title = f"Use -pick to get `{quantity} {drop}`"
		award = await msg.channel.send(embed=embed)

		def check(m):
			return m.content == "-pick" and m.channel.id == msg.channel.id

		try:
			m = await self.bot.wait_for('message', timeout=15.0, check=check)
		except asyncio.TimeoutError:
			embed.title = ""
			embed.description = f"nobody picked the juicy drop :("
			await award.edit(embed=embed)
			pass
		else:
			winner = m.author
			udata = await self.eh.find_user(winner.id)
			if not drop in udata:
				udata[drop] = 0
			udata[drop] += quantity
			await self.eh.update_user(winner.id, udata)
			embed.title = ""
			embed.description = f"`{winner.name}` got the drop"
			await award.edit(embed=embed)

	# @commands.command()
	# async def pick(self, ctx):
	#     await ctx.message.delete()
	#     pass

	def load_codes(self):
		codes = json.load(
			open("./json/promo.json", "r")
		)
		return codes

	def load_shop(self):
		shop = json.load(
			open("./json/shop.json", "r")
		)
		return shop

	def update_code(self, code, update):
		codes = json.load(
			open("./json/promo.json", "r")
		)
		codes[code] = update
		json.dump(
			codes,
			open("./json/promo.json", "w"),
			indent=4
		)

	def fetch_claims(self, c):
		claims = json.load(
			open("./json/claims.json", "r")
		)
		if not c in claims:
			claims[c] = {"claimed": {}}
		return claims[c]

	def save_claims(self, c, claim):
		claims = json.load(
			open("./json/claims.json", "r")
		)
		if not c in claims:
			claims[c] = {"claimed": {}}
		claims[c]["claimed"] = claim
		json.dump(
			claims,
			open("./json/claims.json", "w"),
			indent=4
		)

	def utc_time(self):
		return int(datetime.now().timestamp())

	@commands.command()
	async def inv(self, ctx, member: discord.Member = None):
		if not member:
			member = ctx.message.author
		name = member.name
		shop = self.load_shop()
		user = await self.eh.find_user(member.id)
		values = list(user.items())

		chunks = divide_chunks(values, 5)
		if len(chunks) > 1:
			embeds = []
			i = 0
			for chunk in chunks:
				i += 1
				embed = discord.Embed(color=ctx.author.color)
				embed.title = f"{member.name}'s Inventory"
				for key, value in chunk:
					if key == "_id" or key == "uid":
						continue
					name = (shop[key]['emoji']+" "+shop[key]['name']
							if key in shop else "<:erin:820473033700671569> "+key)
					embed.add_field(
						name=name.capitalize(),
						value=f"{value}",
						inline=False
					)
				embed.set_footer(
					text=f"Page {i}/{len(chunks)}", icon_url=ctx.author.avatar_url)
				embed.set_thumbnail(url=ctx.author.avatar_url)
				embeds.append(embed)
			paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
			paginator.add_reaction('\N{Black Left-Pointing Double Triangle with Vertical Bar}', "first")
			paginator.add_reaction('\N{Black Left-Pointing Double Triangle}', "back")
			paginator.add_reaction('\N{CROSS MARK}', "lock")
			paginator.add_reaction('\N{Black Right-Pointing Double Triangle}', "next")
			paginator.add_reaction('\N{Black Right-Pointing Double Triangle with Vertical Bar}', "last")
			await paginator.run(embeds)
		else:
			embed = discord.Embed(color=ctx.author.color)
			embed.title = f"{name}'s Inventory"
			embed.set_thumbnail(url=ctx.author.avatar_url)
			for key, value in chunks[0]:
				if key == "_id" or key == "uid":
					continue
				name = (shop[key]['emoji']+" "+shop[key]['name']
						if key in shop else "<:erin:820473033700671569> "+key)
				embed.add_field(
					name=name.capitalize(),
					value=f"{value}",
					inline=False
				)
			return await ctx.send(embed=embed)

	@commands.command()
	async def shop(self, ctx):
		shop = self.load_shop()
		embeds = []
		chunks = divide_chunks(list(shop.keys()), 5)
		i = 0
		for chunk in list(chunks):
			i += 1
			embed = discord.Embed(color=discord.Color.teal())
			embed.title = "The Waifu Shop"
			for item in chunk:
				embed.add_field(
					name=item,
					value=f"{shop[item]['name']} {shop[item]['emoji']} | Costs `{shop[item]['price']['quantity']} {shop[item]['price']['item']}`",
					inline=False
				)
			embed.set_footer(
				text=f"Page {i}/{len(chunks)}", icon_url=ctx.author.avatar_url)
			embeds.append(embed)
			paginator.add_reaction('\N{Black Left-Pointing Double Triangle with Vertical Bar}', "first")
			paginator.add_reaction('\N{Black Left-Pointing Double Triangle}', "back")
			paginator.add_reaction('\N{CROSS MARK}', "lock")
			paginator.add_reaction('\N{Black Right-Pointing Double Triangle}', "next")
			paginator.add_reaction('\N{Black Right-Pointing Double Triangle with Vertical Bar}', "last")
		await paginator.run(embeds)

	@commands.command()
	async def recipe(self, ctx, item):
		shop = self.load_shop()
		if not item in shop:
			return await ctx.send(GLE(
				None,
				"The specified item is not craftable",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))

	@commands.command()
	async def claim(self, ctx, code):
		c = ctx.author.id
		claims = self.fetch_claims(c)["claimed"]
		codes = self.load_codes()
		if code in codes:
			if codes[code]["active"]:
				if code not in claims:
					claims[code] = {
						"uses": 0,
						"last_used": 0
					}
				if claims[code]["uses"] < codes[code]["per_person"]:
					if codes[code]["cooldown"]:
						evaluated = self.utc_time()-claims[code]["last_used"]
						if evaluated >= codes[code]["cooldown"]:
							allowed = True
						else:
							allowed = False
							return await ctx.send(embed=GLE(
								None,
								f'You are on a cooldown, try again in {codes[code]["cooldown"]-evaluated}s',
								ctx.author.avatar_url,
								footer=f"{ctx.author.name}#{ctx.author.discriminator}"
							))
					else:
						allowed = True
					if allowed:
						user = await self.eh.find_user(c)
						award = codes[code]["award"]["item"]
						quantity = codes[code]["award"]["quantity"]
						if not award in user:
							user[award] = 0
						user[award] += quantity
						codes[code]["uses"] += 1
						claims[code]["uses"] += 1
						claims[code]["last_used"] = self.utc_time()
						await self.eh.update_user(c, user)
						self.save_claims(c, claims)
						self.update_code(code, codes[code])
						return await ctx.send(embed=SFR(
							None,
							f"You got `{quantity} {award}` ✅",
							ctx.author.avatar_url,
							footer=f"{ctx.author.name}#{ctx.author.discriminator}",
						))

				else:
					return await ctx.send(embed=GLE(
						None,
						"Promo code used max number of times",
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					))
			else:
				return await ctx.send(embed=GLE(
					None,
					"Code is inactive",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
		else:
			return await ctx.send(embed=GLE(
				None,
				"Code not found",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))

	@commands.command(aliases=["buy"])
	async def craft(self, ctx, quantity: int = 1, item="kanna"):
		uid = ctx.author.id
		user = await self.eh.find_user(uid)
		shop = self.load_shop()
		if item in shop:
			if shop[item]["price"]["item"] in user:
				if user[shop[item]["price"]["item"]] >= shop[item]["price"]["quantity"]*quantity:
					user[shop[item]["price"]["item"]
						 ] -= shop[item]["price"]["quantity"]*quantity
					if not item in user:
						user[item] = 0
					user[item] += quantity
					await self.eh.update_user(uid, user)
					return await ctx.send(embed=SFR(
						None,
						f'You just crafted `{quantity} {item}` ✅',
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					))
				else:
					return await ctx.send(embed=GLE(
						None,
						f'You do not possess enough {shop[item]["price"]["item"]}',
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					))
			else:
				return await ctx.send(embed=GLE(
					None,
					f'You do not posses any {shop[item]["price"]["item"]}',
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
		else:
			return await ctx.send(embed=GLE(
				None,
				"The item is not in the shop",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))

	@commands.command(aliases=['destroy', "sell", "uncraft"])
	async def disintegrate(self, ctx, amount: int = 5, item="kanna"):
		shop = self.load_shop()
		user = await self.eh.find_user(ctx.author.id)
		if item in user and item in shop:
			if user[item] >= amount:
				user["erin"] += shop[item]["raw_price"]*amount
				embed = discord.Embed(color=ctx.author.color)
				embed.title = "Item converted"
				embed.description = f"{shop[item]['emoji']} {amount} {item} ➜ <:erin:820473033700671569> {shop[item]['raw_price']*amount} erin"
				await self.eh.update_user(ctx.author.id, user)
				return await ctx.send(embed=embed)
			else:
				return await ctx.send(embed=GLE(
					None,
					"Please specify a valid amount to disintegrate",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
		else:
			return await ctx.send(embed=GLE(
				None,
				"The item is either not in your inventory or the shop",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))

	@commands.command()
	async def send(self, ctx, user: discord.Member, quantity: int, item: str):
		if user.bot:
			return await ctx.send(embed=GLE(
				None,
				"Item's cannot be sent to bots",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))
		uid = ctx.author.id
		tid = user.id
		u1 = await self.eh.find_user(uid)
		u2 = await self.eh.find_user(tid)
		if item in u1:
			if quantity <= u1[item]:
				u1[item] -= quantity
				if not item in u2:
					u2[item] = 0
				u2[item] += quantity
				await self.eh.update_user(uid, u1)
				await self.eh.update_user(tid, u2)
				return await ctx.send(embed=SFR(
					None,
					f"You sent `{user.name}#{user.discriminator}` {quantity} {item} ✅",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
			else:
				return await ctx.send(embed=GLE(
					None,
					f"You do not have `{quantity} {item}` to send the user",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				))
		else:
			return await ctx.send(embed=GLE(
				None,
				"You do not have the item to send them",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))

	@commands.command()
	async def plant(self, ctx, amount: int = 4, item="kanna"):
		shop = self.load_shop()
		if not item in shop:
			return await ctx.send(embed=GLE(
				None,
				"That is not a droppable item",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))
		user = await self.eh.find_user(ctx.author.id)
		if not item in user:
			user[item] = 0
		if amount > user[item]:
			return await ctx.send(embed=GLE(
				None,
				"You can't plant more than what you have",
				ctx.author.avatar_url,
				footer=f"{ctx.author.name}#{ctx.author.discriminator}",
			))
		embed = discord.Embed()
		embed.title = f"{ctx.author.name}#{ctx.author.discriminator} dropped `{amount} {item}`"
		award = await ctx.channel.send(embed=embed)

		def check(m):
			return m.content == "-pick" and m.channel.id == ctx.channel.id and m.author.id != ctx.author.id

		try:
			m = await self.bot.wait_for('message', timeout=15.0, check=check)
		except asyncio.TimeoutError:
			embed.title = ""
			embed.description = f"nobody picked the juicy drop :("
			await award.edit(embed=embed)
			pass
		else:
			winner = m.author
			udata = await self.eh.find_user(winner.id)
			if not item in udata:
				udata[item] = 0
			udata[item] += amount
			user[item] -= amount
			await self.eh.update_user(winner.id, udata)
			await self.eh.update_user(ctx.author.id, user)
			embed.title = ""
			embed.description = f"`{winner.name}` got the drop"
			await award.edit(embed=embed)


def setup(bot):
	bot.add_cog(economy(bot))