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
ongoing_duel=[]

class EconomyHandler:
	def __init__(self):
		self.client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
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
		drop = random.choice(list(self.load_shop().keys()))
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

	@commands.command()
	async def pick(self, ctx):
		await ctx.message.delete()
		pass

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
				embed = discord.Embed()
				embed.title = f"{name}'s Inventory"
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
				embed.set_footer(text=f"Page {i}/{len(chunks)}")
				embeds.append(embed)
			paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
			await paginator.run(embeds)
		else:
			embed = discord.Embed()
			embed.title = f"{name}'s Inventory"
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
			embed = discord.Embed(color=discord.Color.dark_orange())
			embed.title = "The Waifu Shop"
			for item in chunk:
				embed.add_field(
					name=item,
					value=f"{shop[item]['name']} {shop[item]['emoji']} | Costs `{shop[item]['price']['quantity']} {shop[item]['price']['item']}`",
					inline=False
				)
			embed.set_footer(text=f"Page {i}/{len(chunks)}")
			embeds.append(embed)
		paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
		await paginator.run(embeds)

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
							return await ctx.send(f'You are on a cooldown, try again in {codes[code]["cooldown"]-evaluated}s')
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
						return await ctx.send(f"You got `{quantity} {award}` for claiming the code")

				else:
					return await ctx.send("You've already used this code the max no of times")
			else:
				return await ctx.send("Code is currently inactive")
		else:
			return await ctx.send("Code Not found")

	@commands.command()
	async def craft(self, ctx, item, quantity: int = 1):
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
					return await ctx.send(f"You just crafted `{quantity} {item}`")
				else:
					return await ctx.send(f'You do not possess enough `{shop[item]["price"]["item"]}` to buy this item')
			else:
				return await ctx.send(f'You do not possess any `{shop[item]["price"]["item"]}` to buy this item')
		else:
			return await ctx.send("That item is not available in the shop")

	@commands.command()
	async def send(self, ctx, user: discord.Member, quantity: int, item: str):
		if user.bot:
			return await ctx.send(f"{ctx.message.author.mention}, Items cannot be given to bots.")
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
				return await ctx.send(f"You sent `{user.name}` {quantity} {item}")
			else:
				return await ctx.send(f"You don't have `{quantity} {item}` to give to the user")
		else:
			return await ctx.send("You do not have the item to send them")

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
			if quantity >= 10000:
				rr = 2
			luck = random.randint(1, 2)
			if luck == 2:
				user["erin"] -= quantity
				user["erin"] += int(quantity*rr)
				await self.eh.update_user(uid, user)
				return await ctx.send(f"You landed a heads! :coin: , your investment matured with a return of `{int(quantity*rr)} erins`")
			else:
				user["erin"] -= int(quantity*(abs(1-rr)))
				if user["erin"] < 0:
					user["erin"] = 0
				await self.eh.update_user(uid, user)
				return await ctx.send(f"lol sadphroge, you landed tails :pensive: and made a loss of `{int(quantity*(abs(1-rr)))} erins`")
		else:
			return await ctx.send("You don't have `{quantity} erin` to gamble")

	@commands.command()
	@commands.cooldown(5, 180, commands.BucketType.user)
	async def duel(self, ctx, member: discord.Member = None, amount=1, item="kanna"):
		global ongoing_duel
		if ctx.author.id in ongoing_duel:
			return await ctx.send("You cannot start another duel while being in one")
		ongoing_duel.append(ctx.author.id)
		if not member:
			ongoing_duel.remove(ctx.author.id)
			return await ctx.send("pls mention a user")

		else:
			uid = ctx.author.id
			mid = member.id
			u1 = await self.eh.find_user(uid)
			u2 = await self.eh.find_user(mid)
			if not item in u1:
				u1[item] = 0
			if not item in u2:
				u2[item] = 0
			if amount > u1[item]:
				return await ctx.send("You can't duel for more than what you have")
				ongoing_duel.remove(ctx.author.id)
			if amount > u2[item]:
				return await ctx.send("The person you are attempting to duel doesn't have enough currency")
				ongoing_duel.remove(ctx.author.id)
			if member.id in ongoing_duel:
				return await ctx.send("The person you are attempting to duel is already in a duel")
			msg = await ctx.send(f"{member.mention} has been dueled by `{ctx.author.name}#{ctx.author.discriminator}`, the reward is `{amount} {item}`. Accept? (y/n)")

			def check(m):
				condition = False
				if m.content.lower() == "y" or m.content.lower() == "yes" or m.content.lower() == "n" or m.content.lower() == "no":
					condition = True
				return m.author.id == member.id and m.channel.id == ctx.channel.id and condition

			try:
				m = await self.bot.wait_for('message', timeout=60, check=check)
			except asyncio.TimeoutError:
				await msg.edit(content=f"`{member.name}#{member.discriminator}` did not accept the duel within the time period")
				ongoing_duel.remove(ctx.author.id)
			else:
				if m.content.lower() == "n" or m.content.lower() == "no":
					return await msg.edit(content="person declined your dueling request")
				ongoing_duel.append(member.id)
				await msg.edit(content=f"`{member.name}#{member.discriminator}` has accepted the duel :crossed_swords: ")
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


def setup(bot):
	bot.add_cog(economy(bot))