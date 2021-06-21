import os
import time
import json
import random
import asyncio
from typing import OrderedDict
from operator import getitem
import discord
import logging
import humanize
import coloredlogs
import DiscordUtils
import motor.motor_asyncio

import numpy as np
import datetime as dt

from datetime import datetime
from discord.ext import commands

log = logging.getLogger("Economy cog")
coloredlogs.install(logger=log)
global ongoing_duel
ongoing_duel = []


class PrefixManager:
	def __init__(self):
		self.client = motor.motor_asyncio.AsyncIOMotorClient(
			os.getenv("CONNECTIONURI"))
		self.db = self.client.erin
		self.col = self.db["config"]

	async def register_guild(self, g):
		await self.col.insert_one({"gid": g.id, "prefixes": ["-"]})

	async def get_prefix(self, message):
		prefixes = []
		guild = await self.col.find_one({"gid": message.guild.id})
		if not guild:
			await self.register_guild(message.guild)
			prefixes = ["-"]
		else:
			prefixes = guild["prefixes"]
		return prefixes


def GLE(
		title=None, description=None, author=None, footer=None, thumbnail=None
):  # Good Looking Error
	embed = discord.Embed(
		title=title, description=description, colour=discord.Color.red()
	)
	embed.set_footer(text=footer, icon_url=author)
	return embed


def SFR(
		title=None, description=None, author=None, footer=None, thumbnail=None
):  # SatisFactory Response
	embed = discord.Embed(
		title=title, description=description, colour=discord.Color.green()
	)
	embed.set_footer(text=footer, icon_url=author)
	return embed


class EconomyHandler:
	def __init__(self):
		self.client = motor.motor_asyncio.AsyncIOMotorClient(
			os.getenv("CONNECTIONURI"))
		self.db = self.client.erin
		self.col = self.db["economy"]
		self.claims=self.db["claims"]
	async def all_users(self):
		users = self.col.find({})
		return await users.to_list(length=100)

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

	async def fetch_claims(self, c, code):
		claims=await self.claims.find_one({"uid":c,"code":code})
		if not claims:
			claims = {"uid": c, "code": code, "uses":0, "last_used":0}
			await self.claims.insert_one(claims)		
		return claims
	async def save_claims(self, c, code, data):
		claims=await self.claims.find_one({"uid":c,"code":code})
		if not claims:
			await self.claims.insert_one(data)		
		else:
			await self.claims.replace_one({"uid":c,"code":code}, data)
			
def mean_difference(times):
	times = np.diff(times)
	times = np.mean(times)
	return times


def divide_chunks(l, n):
	return [l[i * n: (i + 1) * n] for i in range((len(l) + n - 1) // n)]


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
				roll = random.randint(1, 12)
				if roll == 6:
					response = True
			self.activity[gid] = []
		return response


class IsThisSupposedToWorkHere:
	def __init__(self):
		self.client = motor.motor_asyncio.AsyncIOMotorClient(
			os.getenv("CONNECTIONURI"))
		self.db = self.client.erin
		self.col = self.db["config"]

	async def get_currency_channel(self, g):
		guild = await self.col.find_one({"gid": g})
		currencyChannnel = guild["channel"]
		return currencyChannnel

	async def is_it_thonk(self, channel):
		gid = channel.guild.id
		cid = channel.id
		try:
			currencyGenChannel = await self.get_currency_channel(gid)
		except:
			return False
		if cid == currencyGenChannel:
			return True
		else:
			return False


class Economy(commands.Cog):
	"""
	Economy commands (In development)
	"""
	def __init__(self, bot):
		self.activity = ActivityRecorder()
		self.bot = bot
		self.eh = EconomyHandler()
		self.pm = PrefixManager()
		self.itstwh = IsThisSupposedToWorkHere()

	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")

	@commands.Cog.listener()
	async def on_message(self, message):
		if not message.guild:
			return
		gid = str(message.guild.id)
		if not message.author.bot:
			if await self.itstwh.is_it_thonk(message.channel):
				if self.activity.update(gid, message):
					try:
						await self.drop(message)
					except:
						pass

	async def drop(self, msg):
		prefix = (await self.pm.get_prefix(msg))[0]
		drop = "erin"
		embed = discord.Embed()
		quantity = random.randint(5, 60)
		embed.title = f"Use `{prefix}pick {quantity}`  to get `{quantity} {drop}`"
		embed.set_image(url="https://cdn.discordapp.com/emojis/820473033700671569.png?v=1")
		award = await msg.channel.send(embed=embed)

		def check(m):
			return (
				m.content.lower() == f"{prefix}pick {quantity}".lower()
				and m.channel.id == msg.channel.id
			)

		try:
			m = await self.bot.wait_for("message", timeout=15.0, check=check)
		except asyncio.TimeoutError:
			embed.title = ""
			embed.description = f"nobody picked the juicy drop :("
			embed.set_image(url="https://cdn.discordapp.com/emojis/856411166845567006.png?v=1")
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
			embed.set_image(url="https://cdn.discordapp.com/emojis/856411166765744168.png?v=1")
			await award.edit(embed=embed)

	def load_codes(self):
		codes = json.load(open("./json/promo.json", "r"))
		return codes

	def load_shop(self):
		shop = json.load(open("./json/shop.json", "r"))
		return shop
	def load_jobs(self):
		jobs = json.load(open("./json/work.json", "r", encoding='utf-8' ))
		return jobs
	def update_code(self, code, update):
		codes = json.load(open("./json/promo.json", "r"))
		codes[code] = update
		json.dump(codes, open("./json/promo.json", "w"), indent=4)

	def fetch_claims(self, c):
		claims = json.load(open("./json/claims.json", "r"))
		if not str(c) in claims:
			claims[str(c)] = {"claimed": {}}
		return claims[str(c)]

	def save_claims(self, c, claim):
		claims = json.load(open("./json/claims.json", "r"))
		if not str(c) in claims:
			claims[str(c)] = {"claimed": {}}
		claims[str(c)]["claimed"] = claim
		json.dump(claims, open("./json/claims.json", "w"), indent=4)

	def utc_time(self):
		return int(datetime.now().timestamp())

	@commands.command(name="inv" , description="Shows your inventory")
	async def inv(self, ctx, member: discord.Member = None):
		if not member:
			member = ctx.message.author
		name = member.name
		shop = self.load_shop()
		user = await self.eh.find_user(member.id)
		values = list(user.items())
		for v in values.copy():
			if v[1]==0 and v[0]!="erin":
				values.remove(v)
			if v[0]!="erin" and v[0] not in shop:
				values.remove(v)
		
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
					name = (
						shop[key]["emoji"] + " " + shop[key]["name"]
						if key in shop
						else "<:erin:820473033700671569> " + key
					)
					embed.add_field(
						name=name.capitalize(), value=f"{value}", inline=False
					)
				embed.set_footer(
					text=f"Page {i}/{len(chunks)}", icon_url=ctx.author.avatar_url
				)
				embed.set_thumbnail(url=ctx.author.avatar_url)
				embeds.append(embed)
			paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
			paginator.add_reaction(
				"\N{Black Left-Pointing Double Triangle with Vertical Bar}", "first"
			)
			paginator.add_reaction(
				"\N{Black Left-Pointing Double Triangle}", "back")
			paginator.add_reaction("\N{CROSS MARK}", "lock")
			paginator.add_reaction(
				"\N{Black Right-Pointing Double Triangle}", "next")
			paginator.add_reaction(
				"\N{Black Right-Pointing Double Triangle with Vertical Bar}", "last"
			)
			await paginator.run(embeds)
		else:
			embed = discord.Embed(color=ctx.author.color)
			embed.title = f"{name}'s Inventory"
			embed.set_thumbnail(url=ctx.author.avatar_url)
			for key, value in chunks[0]:
				if key == "_id" or key == "uid":
					continue
				if value == 0 and key != "erin":
					continue
				name = (
					shop[key]["emoji"] + " " + shop[key]["name"]
					if key in shop
					else "<:erin:820473033700671569> " + key
				)
				embed.add_field(name=name.capitalize(),
								value=f"{value}", inline=False)
			return await ctx.send(embed=embed)

	@commands.command(name="shop" , description="Shows the shop")
	async def shop(self, ctx):
		shop = self.load_shop()
		embeds = []
		shop=OrderedDict(
			sorted(shop.items(), key=lambda x: getitem(x[1], "raw_price"))
		)
		chunks = divide_chunks(list(shop.keys()), 5)
		i = 0
		for chunk in list(chunks):
			i += 1
			embed = discord.Embed(color=discord.Color.teal())
			embed.title = "The Waifu Shop"
			for item in chunk:
				v= (f" / `{shop[item]['raw_price']} erin`" if shop[item]['price']['item']!="erin" else "")
				embed.add_field(
					name=item,
					value=f"{shop[item]['name']} {shop[item]['emoji']} | Costs `{shop[item]['price']['quantity']} {shop[item]['price']['item']}`" + v,
					inline=False,
				)
			embed.set_footer(
				text=f"Page {i}/{len(chunks)}", icon_url=ctx.author.avatar_url
			)
			embeds.append(embed)
		paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
		paginator.add_reaction(
			"\N{Black Left-Pointing Double Triangle with Vertical Bar}", "first"
		)
		paginator.add_reaction(
			"\N{Black Left-Pointing Double Triangle}", "back")
		paginator.add_reaction("\N{CROSS MARK}", "lock")
		paginator.add_reaction(
			"\N{Black Right-Pointing Double Triangle}", "next")
		paginator.add_reaction(
			"\N{Black Right-Pointing Double Triangle with Vertical Bar}", "last"
		)
		await paginator.run(embeds)

	@commands.command(name="claim" , description="Claim an item :flushed:")
	async def claim(self, ctx, code):
		c = ctx.author.id
		codes = self.load_codes()
		if code in codes:
			claims = await self.eh.fetch_claims(c, code)
			if codes[code]["active"]:
				if claims["uses"] < codes[code]["per_person"]:
					if codes[code]["cooldown"]:
						evaluated = self.utc_time() - claims["last_used"]
						if evaluated >= codes[code]["cooldown"]:
							allowed = True
						else:
							allowed = False
							t = humanize.naturaldelta(
								dt.timedelta(
									seconds=codes[code]["cooldown"] - evaluated
								)
							)
							return await ctx.send(
								embed=GLE(
									None,
									f"You are on a cooldown, try again in {t}",
									ctx.author.avatar_url,
									footer=f"{ctx.author.name}#{ctx.author.discriminator}",
								)
							)
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
						claims["uses"] += 1
						claims["last_used"] = self.utc_time()
						await self.eh.update_user(c, user)
						await self.eh.save_claims(c, code, claims)
						self.update_code(code, codes[code])
						return await ctx.send(
							embed=SFR(
								None,
								f"You got `{quantity} {award}` \N{White Heavy Check Mark}",
								ctx.author.avatar_url,
								footer=f"{ctx.author.name}#{ctx.author.discriminator}",
							)
						)

				else:
					return await ctx.send(
						embed=GLE(
							None,
							"Promo code used max number of times",
							ctx.author.avatar_url,
							footer=f"{ctx.author.name}#{ctx.author.discriminator}",
						)
					)
			else:
				return await ctx.send(
					embed=GLE(
						None,
						"Code is inactive",
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					)
				)
		else:
			return await ctx.send(
				embed=GLE(
					None,
					"Code not found",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)

	@commands.command(aliases=["buy"], description="Buy an item from the shop :flushed:")
	async def craft(self, ctx, quantity: int = 1, item="kanna"):
		if quantity <= 0:
			return await ctx.send(
				embed=GLE(
					None,
					"You cannot craft negative amounts",
					author=ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		uid = ctx.author.id
		user = await self.eh.find_user(uid)
		shop = self.load_shop()
		if item in shop:
			if shop[item]["price"]["item"] in user:
				if (
						user[shop[item]["price"]["item"]]
						>= shop[item]["price"]["quantity"] * quantity
				):
					user[shop[item]["price"]["item"]] -= (
						shop[item]["price"]["quantity"] * quantity
					)
					if not item in user:
						user[item] = 0
					user[item] += quantity
					await self.eh.update_user(uid, user)
					return await ctx.send(
						embed=SFR(
							None,
							f"You just crafted `{quantity} {item}` \N{White Heavy Check Mark}",
							ctx.author.avatar_url,
							footer=f"{ctx.author.name}#{ctx.author.discriminator}",
						)
					)
				else:
					return await ctx.send(
						embed=GLE(
							None,
							f'You do not possess enough {shop[item]["price"]["item"]}',
							ctx.author.avatar_url,
							footer=f"{ctx.author.name}#{ctx.author.discriminator}",
						)
					)
			else:
				return await ctx.send(
					embed=GLE(
						None,
						f'You do not posses any {shop[item]["price"]["item"]}',
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					)
				)
		else:
			return await ctx.send(
				embed=GLE(
					None,
					"The item is not in the shop",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)

	@commands.command(aliases=["destroy", "sell", "uncraft"],  description="Destroys an item :pensive:")
	async def disintegrate(self, ctx, amount: int = 5, item="kanna"):
		if amount <= 0:
			return await ctx.send(
				embed=GLE(
					None,
					"You cannot disintegrate negative amounts",
					author=ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		shop = self.load_shop()
		user = await self.eh.find_user(ctx.author.id)
		if item in user and item in shop:
			if user[item] >= amount:
				user["erin"] += shop[item]["raw_price"] * amount
				user[item] -= amount
				embed = discord.Embed(color=ctx.author.color)
				embed.title = "Item converted"
				embed.description = f"{shop[item]['emoji']} {amount} {item} ➜ <:erin:820473033700671569> {shop[item]['raw_price']*amount} erin"
				await self.eh.update_user(ctx.author.id, user)
				return await ctx.send(embed=embed)
			else:
				return await ctx.send(
					embed=GLE(
						None,
						"Please specify a valid amount to disintegrate",
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					)
				)
		else:
			return await ctx.send(
				embed=GLE(
					None,
					"The item is either not in your inventory or the shop",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)

	@commands.command(description=":flushed: sends money/items")
	async def send(self, ctx, user: discord.Member, quantity: int, item: str):
		if quantity <= 0:
			return await ctx.send(
				embed=GLE(
					None,
					"You cannot send negative amounts",
					author=ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		if user.bot:
			return await ctx.send(
				embed=GLE(
					None,
					"Item's cannot be sent to bots",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
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
				try:
					await user.send(embed=SFR(
						None,
						description=f"`{ctx.author.name}#{ctx.author.discriminator}` sent you {quantity} {item}",
						footer=f"{ctx.author.name}#{ctx.author.discriminator}"
					))
				except:
					pass
				return await ctx.send(
					embed=SFR(
						None,
						f"You sent `{user.name}#{user.discriminator}` {quantity} {item} \N{White Heavy Check Mark}",
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					)
				)
			else:
				return await ctx.send(
					embed=GLE(
						None,
						f"You do not have `{quantity} {item}` to send the user",
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					)
				)
		else:
			return await ctx.send(
				embed=GLE(
					None,
					"You do not have the item to send them",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)

	@commands.command(description="Makes a drop in chat for others to get!")
	async def plant(self, ctx, amount: int, item):
		if amount <= 0:
			return await ctx.send(
				embed=GLE(
					None,
					"You cannot plant negative amounts",
					author=ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		shop = self.load_shop()
		if not item in shop:
			return await ctx.send(
				embed=GLE(
					None,
					"That is not a droppable item",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		user = await self.eh.find_user(ctx.author.id)
		if not item in user:
			user[item] = 0
		if amount > user[item]:
			return await ctx.send(
				embed=GLE(
					None,
					"You can't plant more than what you have",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		embed = discord.Embed()
		embed.title = (
			f"{ctx.author.name}#{ctx.author.discriminator} dropped `{amount} {item}`"
		)
		embed.set_footer(text=f"Pick it up using {ctx.prefix}pick")
		award = await ctx.channel.send(embed=embed)

		def check(m):
			x=(
				m.content.lower() == f"{ctx.prefix}pick".lower()
				and m.channel.id == ctx.channel.id
				and m.author.id != ctx.author.id
			)
			return x

		try:
			m = await self.bot.wait_for("message", timeout=120.0, check=check)
		except asyncio.TimeoutError:
			embed.title = ""
			embed.description = f"nobody picked the juicy drop :("
			embed.set_footer(text="")
			try:
				await award.edit(embed=embed)
			except: 
				pass
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
			embed.set_footer(text="")
			try:
				await award.edit(embed=embed)
			except:
				pass
	@commands.command(hidden=True)
	@commands.is_owner()
	async def yeet_exploiter(self, ctx):
		data=self.eh.col.find({})
		data= await data.to_list(length=10000)
		shop=self.load_shop()
		for user in data:
			initial=user.copy()
			for item in initial:
				if item=="uid" or item=="_id":
					continue
				if item not in shop and item!="erin":
					del user[item]
					continue
				if user[item]>10000000:
					user[item]=1000000
			if initial!=user:
				await self.eh.col.replace_one({"uid":user["uid"]}, user)
		await ctx.send("hello")
	@commands.command(hidden=True)
	@commands.is_owner()
	async def getself(self, ctx, quantity: int=5, item: str="kanna"):
		if quantity <= 0:
			return await ctx.send(
				embed=GLE(
					None,
					"You cannot get negative amounts",
					author=ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		shop=self.load_shop()
		if item!="erin":
			if item not in shop:
				return await ctx.send("this item is not in the shop")
		user=await self.eh.find_user(ctx.author.id)
		if item not in user:
			user[item]=0
		user[item]+=quantity
		await self.eh.update_user(ctx.author.id, user)
		return await ctx.send("added item")
	@commands.command(hidden=True)
	@commands.is_owner()
	async def takeitems(self, ctx, uid: int, quantity: int=5, item: str="kanna"):
		if quantity <= 0:
			return await ctx.send(
				embed=GLE(
					None,
					"You cannot take negative amounts",
					author=ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		shop=self.load_shop()
		if item!="erin":
			if item not in shop:
				return await ctx.send("this item is not in the shop")
		user=await self.eh.find_user(uid)
		if item not in user:
			user[item]=0
		if quantity>user[item]:
			user[item]=0
		else:
			user[item]-=quantity
		await self.eh.update_user(uid, user)
		return await ctx.send("removed item")

	@commands.command(description="Shows the crafting recipe of items ~~minecraft moment~~")
	async def recipe(self, ctx, item, quantity: int = 1):
		item=item.lower()
		if quantity <= 0:
			return await ctx.send(
				embed=GLE(
					None,
					"You cannot check recipe's for negative amouts",
					author=ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		shop = self.load_shop()
		if not item in shop:
			return await ctx.send(
				embed=GLE(
					None,
					"The specified item is not craftable",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)

		def determine_price(item, amount):
			if item in shop:
				yield item, amount
				yield from determine_price(
					shop[item]["price"]["item"],
					shop[item]["price"]["quantity"] * amount,
				)
			else:
				yield item, amount

		order = list(reversed(list(determine_price(item, quantity))))
		embed = SFR(
			title=f"Price for {quantity} {item}",
			description="```",
			author=ctx.author.avatar_url,
			footer=f"{ctx.author.name}#{ctx.author.discriminator}",
		)
		i = 0
		for it in order:
			i += 1
			embed.description += "\n"
			embed.description += (
				"  " * i
				+ f"\N{Downwards Arrow with Tip Rightwards} {humanize.intcomma(it[1])} {it[0]}"
			)
		embed.description += "```"
		return await ctx.send(embed=embed)
	@commands.command(hidden=True)
	@commands.is_owner()
	async def jobs(self,ctx):
		jobs=self.load_jobs()
		values = list(jobs.items())
		chunks = divide_chunks(values, 5)
		if len(chunks) > 1:
			embeds = []
			i = 0
			for chunk in chunks:
				i += 1
				embed = discord.Embed(color=ctx.author.color)
				embed.title = f"Available Jobs"
				for key, value in chunk:
					name = (
						value["name"]
					)
					embed.add_field(
						name=name.capitalize(), value=f"`ID: {value['id']}` | Pays `{value['pay']['quantity']} {value['pay']['item']}`", inline=False
					)
				embed.set_footer(
					text=f"Page {i}/{len(chunks)}", icon_url=ctx.author.avatar_url
				)
				embed.set_thumbnail(url=ctx.author.avatar_url)
				embeds.append(embed)
			paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
			paginator.add_reaction(
				"\N{Black Left-Pointing Double Triangle with Vertical Bar}", "first"
			)
			paginator.add_reaction(
				"\N{Black Left-Pointing Double Triangle}", "back")
			paginator.add_reaction("\N{CROSS MARK}", "lock")
			paginator.add_reaction(
				"\N{Black Right-Pointing Double Triangle}", "next")
			paginator.add_reaction(
				"\N{Black Right-Pointing Double Triangle with Vertical Bar}", "last"
			)
			await paginator.run(embeds)
		else:
			embed = discord.Embed(color=ctx.author.color)
			embed.title = f"Available Jobs"
			embed.set_thumbnail(url=ctx.author.avatar_url)
			for key, value in chunks[0]:
					name = (
						value["name"]
					)
					embed.add_field(
						name=name.capitalize(), value=f"`ID: {value['id']}` | Pays `{value['pay']['quantity']} {value['pay']['item']}1", inline=False
					)
			return await ctx.send(embed=embed)
	@commands.command(description="Resets all your items big F")
	async def reset(self, ctx):
		embed = discord.Embed(color=ctx.author.color)
		embed.title = f"Are you sure that you wish to reset your progress? (y/n)"
		embed.description = (
			"Once it resets, your progress will cannot be reverted back. "
		)
		embed.set_thumbnail(url=ctx.author.avatar_url)
		embed.set_footer(
			text="This message will auto-cancel in 15 seconds",
			icon_url=ctx.author.avatar_url,
		)
		msg = await ctx.send(embed=embed)

		def check(m):
			condition = False
			if (
					m.content.lower() == "y"
					or m.content.lower() == "yes"
					or m.content.lower() == "n"
					or m.content.lower() == "no"
			):
				condition = True
			return (
				m.author.id == ctx.author.id
				and m.channel.id == ctx.channel.id
				and condition
			)

		try:
			m = await self.bot.wait_for("message", timeout=15, check=check)
		except asyncio.TimeoutError:
			await msg.edit(
				embed=GLE(
					None,
					f"Your progress hasn't been resetted",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)
		else:
			if m.content.lower() == "n" or m.content.lower() == "no":
				return await msg.edit(
					embed=GLE(
						None,
						f"Your progress hasn't been resetted",
						ctx.author.avatar_url,
						footer=f"{ctx.author.name}#{ctx.author.discriminator}",
					)
				)
			user = await self.eh.find_user(ctx.author.id)
			user2 = {"_id": user["_id"], "uid": ctx.author.id, "erin": 0}
			await self.eh.update_user(ctx.author.id, user2)
			await msg.edit(
				embed=SFR(
					None,
					f"Your progess has been removed ",
					ctx.author.avatar_url,
					footer=f"{ctx.author.name}#{ctx.author.discriminator}",
				)
			)


def setup(bot):
	bot.add_cog(Economy(bot))
