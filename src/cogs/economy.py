from discord.ext import commands
from datetime import datetime
import discord
import json
import random
import os
import numpy as np
import time
import asyncio
global cache
cache = json.load(
    open("./json/eco.json")
)


def mean_difference(times):
    times = np.diff(times)
    times = np.mean(times)
    return times


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

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message(self, message):
        gid = str(message.guild.id)
        if gid in cache:
            if self.activity.update(gid, message):
                await self.drop(message)

    async def drop(self, msg):
        global cache
        gid = str(msg.guild.id)
        embed = discord.Embed()
        quantity = random.randint(5, 60)
        embed.title = f"Use -pick to get {quantity} kanna"
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
            tid = str(winner.id)
            if not gid in cache:
                cache[gid] = {}
            if not tid in cache[gid]:
                cache[gid][tid] = {"erin": 0}
                self.save_cache()
            if not "kanna" in cache[gid][tid]:
                cache[gid][tid]["kanna"] = 0
            cache[gid][tid]["kanna"] += quantity
            self.save_cache()
            embed.title = ""
            embed.description = f"`{winner.name}` got the drop"
            await award.edit(embed=embed)

    @commands.command()
    async def pick(self, ctx):
        pass

    def load_cache(self):
        global cache
        cache = json.load(
            open("./json/eco.json")
        )

    def save_cache(self):
        global cache
        json.dump(
            cache,
            open("./json/eco.json", "w"),
            indent=4
        )

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
        global cache
        gid = str(ctx.guild.id)
        if not member:
            member = ctx.message.author
        name = member.name
        member = str(member.id)
        shop = self.load_shop()
        if not gid in cache:
            cache[gid] = {}
        if not member in cache[gid]:
            cache[gid][member] = {"erin": 0}
            self.save_cache()
        embed = discord.Embed()
        embed.title = f"{name}'s Inventory"
        for key, value in cache[gid][member].items():
            name = (shop[key]['name'] if key in shop else key)
            embed.add_field(
                name=name.capitalize(),
                value=f"{value}",
                inline=False
            )
        return await ctx.send(embed=embed)

    @commands.command()
    async def shop(self, ctx):
        shop = self.load_shop()
        embed = discord.Embed(color=discord.Color.dark_orange())
        embed.title = "The Waifu Shop"
        for item in shop:
            embed.add_field(
                name=item,
                value=f"{shop[item]['name']} | Costs `{shop[item]['price']['quantity']} {shop[item]['price']['item']}`",
                inline=False
            )
        return await ctx.send(embed=embed)

    @commands.command()
    async def claim(self, ctx, code):
        global cache
        gid = str(ctx.guild.id)
        c = str(ctx.author.id)
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
                        if not gid in cache:
                            cache[gid] = {}
                        if not c in cache[gid]:
                            cache[gid][c] = {"erin": 0}
                        award = codes[code]["award"]["item"]
                        quantity = codes[code]["award"]["quantity"]
                        if not award in cache[gid][c]:
                            cache[gid][c][award] = 0
                        cache[gid][c][award] += quantity
                        codes[code]["uses"] += 1
                        claims[code]["uses"] += 1
                        claims[code]["last_used"] = self.utc_time()
                        self.save_cache()
                        self.save_claims(c, claims)
                        self.update_code(code, codes[code])
                        return await ctx.send("code claimed")

                else:
                    return await ctx.send("You've already used this code the max no of times")
            else:
                return await ctx.send("Code is currently inactive")
        else:
            return await ctx.send("Code Not found")

    @commands.command()
    async def craft(self, ctx, item, quantity: int = 1):
        global cache
        uid = str(ctx.author.id)
        gid = str(ctx.guild.id)
        if not gid in cache:
            cache[gid] = {}
            self.save_cache()
        if not uid in cache[gid]:
            cache[gid][uid] = {"erin": 0}
            self.save_cache()
        shop = self.load_shop()
        if item in shop:
            if shop[item]["price"]["item"] in cache[gid][uid]:
                if cache[gid][uid][shop[item]["price"]["item"]] >= shop[item]["price"]["quantity"]*quantity:
                    cache[gid][uid][shop[item]["price"]["item"]
                                    ] -= shop[item]["price"]["quantity"]*quantity
                    if not item in cache[gid][uid]:
                        cache[gid][uid][item] = 0
                    cache[gid][uid][item] += quantity
                    self.save_cache()
                    return await ctx.send(f"You just crafted `{quantity} {item}`")
                else:
                    return await ctx.send(f'You do not possess enough `{shop[item]["price"]["item"]}` to buy this item')
            else:
                return await ctx.send(f'You do not possess any `{shop[item]["price"]["item"]}` to buy this item')
        else:
            return await ctx.send("That item is not available in the shop")

    @commands.command()
    async def send(self, ctx, user: discord.Member, item: str, quantity: int):
        if user.bot:
            return await ctx.send(f"{ctx.message.author.mention}, Items cannot be given to bots.")
        global cache
        uid = str(ctx.author.id)
        gid = str(ctx.guild.id)
        tid = str(user.id)
        if not gid in cache:
            cache[gid] = {}
            self.save_cache()
        if not uid in cache[gid]:
            cache[gid][uid] = {"erin": 0}
            self.save_cache()
        if not tid in cache[gid]:
            cache[gid][tid] = {"erin": 0}
        if item in cache[gid][uid]:
            if quantity <= cache[gid][uid][item]:
                cache[gid][uid][item] -= quantity
                if not item in cache[gid][tid]:
                    cache[gid][tid][item] = 0
                cache[gid][tid][item] += quantity
                self.save_cache()
                return await ctx.send(f"You sent `{user.name}` {quantity} {item}")
            else:
                return await ctx.send(f"You don't have `{quantity} {item}` to give to the user")
        else:
            return await ctx.send("You do not have the item to send them")

    @commands.command()
    @commands.cooldown(5, 300, commands.BucketType.user)
    async def gamble(self, ctx, quantity: int = 10):
        global cache
        uid = str(ctx.author.id)
        gid = str(ctx.guild.id)
        if not gid in cache:
            cache[gid] = {}
            self.save_cache()
        if not uid in cache[gid]:
            cache[gid][uid] = {"erin": 0}
            self.save_cache()
        if quantity <= cache[gid][uid]["erin"]:
            if quantity <= 5000:
                rr = 1.25
            if quantity <= 8000:
                rr = 1.5
            if quantity >= 10000:
                rr = 2
            luck = random.randint(1, 2)
            if luck == 2:
                cache[gid][uid]["erin"] -= quantity
                cache[gid][uid]["erin"] += int(quantity*rr)
                self.save_cache()
                return await ctx.send(f"You landed a heads! :coin: , your investment matured with a return of `{int(quantity*rr)} erins`")
            else:
                cache[gid][uid]["erin"] -= int(quantity*(abs(1-rr)))
                if cache[gid][uid]["erin"] < 0:
                    cache[gid][uid]["erin"] = 0
                self.save_cache()
                return await ctx.send(f"lol sadphroge, you landed tails :pensive: and made a loss of `{int(quantity*(abs(1-rr)))} erins`")
        else:
            return await ctx.send("You don't have `{quantity} erin` to gamble")

  
  
def setup(bot):
    bot.add_cog(economy(bot))
