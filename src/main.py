from discord.ext import commands
from datetime import datetime
import discord
import json
import random
import os

from dotenv import load_dotenv
from pathlib import Path


load_dotenv()
load_dotenv(verbose=True)
env_path = Path('./../') / '.env'
load_dotenv(dotenv_path=env_path)


client = commands.Bot(command_prefix="-")
global cache
cache = json.load(
    open("./json/eco.json")
)


def load_cache():
    global cache
    cache = json.load(
        open("./json/eco.json")
    )


def save_cache():
    global cache
    json.dump(
        cache,
        open("./json/eco.json", "w"),
        indent=4
    )


def load_codes():
    codes = json.load(
        open("./json/promo.json", "r")
    )
    return codes


def load_shop():
    shop = json.load(
        open("./json/shop.json", "r")
    )
    return shop


def update_code(code, update):
    codes = json.load(
        open("./json/promo.json", "r")
    )
    codes[code] = update
    json.dump(
        codes,
        open("./json/promo.json", "w"),
        indent=4
    )


def fetch_claims(c):
    claims = json.load(
        open("./json/claims.json", "r")
    )
    if not c in claims:
        claims[c] = {"claimed": {}}
    return claims[c]


def save_claims(c, claim):
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


def utc_time():
    return int(datetime.now().timestamp())


@client.command()
async def inv(ctx):
    global cache
    gid = str(ctx.guild.id)
    c = str(ctx.author.id)
    shop = load_shop()
    if not gid in cache:
        cache[gid] = {}
    if not c in cache[gid]:
        cache[gid][c] = {"string": 0}
        save_cache()
    embed = discord.Embed()
    embed.title = f"{ctx.author.name}'s Inventory"
    for key, value in cache[gid][c].items():
        name = (shop[key]['name'] if key in shop else key)
        embed.add_field(
            name=name.capitalize(),
            value=f"{value}",
            inline=False
        )
    return await ctx.send(embed=embed)


@client.command()
async def shop(ctx):
    shop = load_shop()
    embed = discord.Embed(color=discord.Color.dark_orange())
    embed.title = "The Bass Shop"
    for item in shop:
        embed.add_field(
            name=item,
            value=f"{shop[item]['name']} | Costs `{shop[item]['price']['quantity']} {shop[item]['price']['item']}`",
            inline=False
        )
    return await ctx.send(embed=embed)


@client.command()
async def claim(ctx, code):
    global cache
    gid = str(ctx.guild.id)
    c = str(ctx.author.id)
    claims = fetch_claims(c)["claimed"]
    codes = load_codes()
    if code in codes:
        if codes[code]["active"]:
            if code not in claims:
                claims[code] = {
                    "uses": 0,
                    "last_used": 0
                }
            if claims[code]["uses"] < codes[code]["per_person"]:
                if codes[code]["cooldown"]:
                    evaluated = utc_time()-claims[code]["last_used"]
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
                        cache[gid][c] = {"string": 0}
                    award = codes[code]["award"]["item"]
                    quantity = codes[code]["award"]["quantity"]
                    if not award in cache[gid][c]:
                        cache[gid][c][award] = 0
                    cache[gid][c][award] += quantity
                    codes[code]["uses"] += 1
                    claims[code]["uses"] += 1
                    claims[code]["last_used"] = utc_time()
                    save_cache()
                    save_claims(c, claims)
                    update_code(code, codes[code])
                    return await ctx.send("code claimed")

            else:
                return await ctx.send("You've already used this code the max no of times")
        else:
            return await ctx.send("Code is currently inactive")
    else:
        return await ctx.send("Code Not found")


@client.command()
async def craft(ctx, item, quantity: int = 1):
    global cache
    uid = str(ctx.author.id)
    gid = str(ctx.guild.id)
    if not gid in cache:
        cache[gid] = {}
        save_cache()
    if not uid in cache[gid]:
        cache[gid][uid] = {"string": 0}
        save_cache()
    shop = load_shop()
    if item in shop:
        if shop[item]["price"]["item"] in cache[gid][uid]:
            if cache[gid][uid][shop[item]["price"]["item"]] >= shop[item]["price"]["quantity"]*quantity:
                cache[gid][uid][shop[item]["price"]["item"]
                                ] -= shop[item]["price"]["quantity"]*quantity
                if not item in cache[gid][uid]:
                    cache[gid][uid][item] = 0
                cache[gid][uid][item] += quantity
                save_cache()
                return await ctx.send(f"You just crafted `{quantity} {item}`")
            else:
                return await ctx.send(f'You do not possess enough `{shop[item]["price"]["item"]}` to buy this item')
        else:
            return await ctx.send(f'You do not possess any `{shop[item]["price"]["item"]}` to buy this item')
    else:
        return await ctx.send("That item is not available in the shop")


@client.command()
async def send(ctx, user: discord.Member, item: str, quantity: int):
    global cache
    uid = str(ctx.author.id)
    gid = str(ctx.guild.id)
    tid = str(user.id)
    if not gid in cache:
        cache[gid] = {}
        save_cache()
    if not uid in cache[gid]:
        cache[gid][uid] = {"string": 0}
        save_cache()
    if not tid in cache[gid]:
        cache[gid][tid] = {"string": 0}
    if item in cache[gid][uid]:
        if quantity <= cache[gid][uid][item]:
            cache[gid][uid][item] -= quantity
            if not item in cache[gid][tid]:
                cache[gid][tid][item] = 0
            cache[gid][tid][item] += quantity
            save_cache()
            return await ctx.send(f"You sent `{user.name}` {quantity} {item}")
        else:
            return await ctx.send(f"You don't have `{quantity} {item}` to give to the user")
    else:
        return await ctx.send("You do not have the item to send them")


@client.command()
@commands.cooldown(5, 300, commands.BucketType.user)
async def gamble(ctx, quantity: int = 10):
    global cache
    uid = str(ctx.author.id)
    gid = str(ctx.guild.id)
    if not gid in cache:
        cache[gid] = {}
        save_cache()
    if not uid in cache[gid]:
        cache[gid][uid] = {"string": 0}
        save_cache()
    if quantity <= cache[gid][uid]["string"]:
        if quantity <= 5000:
            rr = 1.25
        if quantity <= 8000:
            rr = 1.5
        if quantity >= 10000:
            rr = 2
        luck = random.randint(1, 2)
        if luck == 2:
            cache[gid][uid]["string"] -= quantity
            cache[gid][uid]["string"] += int(quantity*rr)
            save_cache()
            return await ctx.send(f"You landed a heads! :coin: , your investment matured with a return of `{int(quantity*rr)} strings`")
        else:
            cache[gid][uid]["string"] -= int(quantity*(abs(1-rr)))
            if cache[gid][uid]["string"] < 0:
                cache[gid][uid]["string"] = 0
            save_cache()
            return await ctx.send(f"lol sadphroge, you landed tails :pensive: and made a loss of `{int(quantity*(abs(1-rr)))} strings`")
    else:
        return await ctx.send("You don't have `{quantity} string` to gamble")
@gamble.error
async def gamble_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Slow it down bro!",color=discord.Colour.red())
        em.description=f"Try again in {error.retry_after:.2f}s."
        await ctx.send(embed=em)
client.run(os.getenv("TOKEN"))
