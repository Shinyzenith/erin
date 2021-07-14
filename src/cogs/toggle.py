# Meta

CANNOT_BE_TOGGLED=[
    "config",
    "errorhandler",
    "help",
    "toggle",
    "owner"
]

import discord
from discord.ext import commands
from main import ubc

class Toggle(commands.Cog):
    def __init__(self, client):
        self.bot=client

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx, *, cog: str="module_name"): 
        cogs=[c.lower() for c in list(self.bot.cogs.keys())]
        cog=cog.lower()
        if cog in CANNOT_BE_TOGGLED:
            return await ctx.send(embed=discord.Embed(
                color=ctx.author.color,
                description="<:crossmark:864857891675308042> This module cannot be toggled"
            ))
        if cog not in cogs:
            return await ctx.send(embed=discord.Embed(
                color=discord.Color.red(),
                description="<:crossmark:864857891675308042> Specified module is not a valid module"
            ))
        status=await ubc.toggle_cog(ctx.guild, cog)
        return await ctx.send(embed=discord.Embed(
            color=ctx.author.color,
            description=f":white_check_mark: Module `{cog}` was {status}"
        ))
    

def setup(client):
    client.add_cog(Toggle(client))

