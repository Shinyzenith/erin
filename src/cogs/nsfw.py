import discord
import requests
import datetime
from discord.ext.commands import cooldown, BucketType
from discord.ext.commands import (CommandOnCooldown)
from discord.ext import commands

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || NSFW COG || 
"""

class NSFW(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    @commands.is_nsfw()
    async def hentai(self, ctx):
        response = requests.get("https://shiro.gg/api/images/nsfw/hentai")
        realResponse = response.json()
        embed = discord.Embed(
            title = "Juicy henti for you!",
            color = 0xFFC0CB
        )
        embed.set_image(url = realResponse['url'])
        await ctx.message.reply(embed = embed)
            
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    @commands.is_nsfw()
    async def cum(self, ctx):
        response = requests.get("https://nekos.life/api/v2/img/cum")
        realResponse = response.json()
        embed = discord.Embed(
            title = "sticky white stuff!",
            color = 0xFFC0CB
        )
        embed.set_image(url = realResponse['url'])
        await ctx.message.reply(embed = embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    @commands.is_nsfw()
    async def thighs(self, ctx):
        response = requests.get("https://shiro.gg/api/images/nsfw/thighs")
        realResponse = response.json()
        embed = discord.Embed(
            title = "Thic thighs!",
            color = 0xFFC0CB
        )
        embed.set_image(url = realResponse['url'])
        await ctx.message.reply(embed = embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="nekogif",aliases=['neko'])
    @commands.is_nsfw()
    async def nekogif(self, ctx):
        response = requests.get("https://nekos.life/api/v2/img/nsfw_neko_gif")
        realResponse = response.json()
        embed = discord.Embed(
            title = "Gifs!",
            color = 0xFFC0CB
        )
        embed.set_image(url = realResponse['url'])
        await ctx.message.reply(embed = embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    @commands.is_nsfw()
    async def boobs(self, ctx):
        response = requests.get("https://nekos.life/api/v2/img/boobs")

        realResponse = response.json()

        embed = discord.Embed(
            title = "boooooobs!",
            color = 0xFFC0CB
        )
        embed.set_image(url = realResponse['url'])

        await ctx.message.reply(embed = embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    @commands.is_nsfw()
    async def blowjob(self, ctx):
        response = requests.get("https://nekos.life/api/v2/img/blowjob")

        realResponse = response.json()

        embed = discord.Embed(
            title = "Yummy!",
            color = 0xFFC0CB
        )
        embed.set_image(url = realResponse['url'])

        await ctx.message.reply(embed = embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    @commands.is_nsfw()
    async def pussy(self, ctx):
        response = requests.get("https://nekos.life/api/v2/img/pussy")

        realResponse = response.json()

        embed = discord.Embed(
            title = "Yummy!",
            color = 0xFFC0CB
        )
        embed.set_image(url = realResponse['url'])

        await ctx.message.reply(embed = embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    @commands.is_nsfw()
    async def spank(self, ctx, user: commands.Greedy[discord.Member] = None):
        if user == None:
            await ctx.message.reply("Who do you want to spank?.")
            return
        response = requests.get("https://nekos.life/api/v2/img/spank").json()
        spanked_users="".join([f"{users.mention} " for users in user])
        embed = discord.Embed(
            title = "Damn!",
            description = f"{spanked_users} got spanked by {ctx.author.mention}",
            color = 0xFFC0CB
        )
        embed.set_image(url = response['url'])
        await ctx.message.reply(embed = embed)

def setup(client):
    client.add_cog(NSFW(client))