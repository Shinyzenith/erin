import discord
import logging
import coloredlogs
import DiscordUtils

from discord import Embed
from discord.ext import commands
from discord.errors import Forbidden

log = logging.getLogger("help cog")
coloredlogs.install(logger=log)
async def send_embed(ctx, embed):
	try:
		await ctx.message.reply(embed=embed)
	except Forbidden:
		try:
			await ctx.author.send(
				f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
				f"May you inform the server team about this issue? :slight_smile: ", embed=embed)
		except:
			ctx.send("It seems i don't have perms to send embeds in this channel.")

class Help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.Cog.listener()
	async def on_ready(self):
		log.warn(f"{self.__class__.__name__} Cog has been loaded")
	@commands.command()
	async def help(self, ctx, *,input:str=None):
		if not input:
			emb = discord.Embed(title='Commands and modules', color=ctx.message.author.color,description=f'Use `{ctx.prefix}help <module>` to gain more information about that module <:Kanna:822144873170731018>\n')
			emb.set_footer(text=f"Requested by {ctx.message.author}",icon_url=self.bot.user.avatar_url)
			emb.set_thumbnail(url=ctx.message.author.avatar_url)
			emb.set_author(name=ctx.message.author.display_name,icon_url=ctx.message.guild.icon_url)

			cogs_desc = ''
			for cog in self.bot.cogs:
				if len(self.bot.get_cog(cog).get_commands())==0:
					continue
				cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

			emb.add_field(name='Modules', value=cogs_desc, inline=False)

			commands_desc = ''
			for command in self.bot.walk_commands():
				if not command.cog_name and not command.hidden:
					commands_desc += f'{command.name} - {command.help}\n'
			if commands_desc:
				emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)
			return await send_embed(ctx, emb)

		else:
			pages=[]
			def make_embed():
				embed=Embed(color=ctx.message.author.color,timestamp=ctx.message.created_at)
				embed.set_footer(text=f"Requested by {ctx.message.author}",icon_url=self.bot.user.avatar_url)
				embed.set_thumbnail(url=ctx.message.author.avatar_url)
				embed.set_author(name=ctx.message.author.display_name,icon_url=ctx.message.guild.icon_url)
				return embed

			for cog in self.bot.cogs:
				if cog.lower() == input.lower():
					threshold=10
					commands=self.bot.get_cog(cog).get_commands()
					command_chunk=[commands[i:i + threshold] for i in range(0, len(commands), threshold)]
					i=0
					embeds=[]
					command_list=""
					for chunk in command_chunk:
						embed = make_embed()
						for command in chunk:
							embed.title=f"{command.cog_name} - Commands"
							embed.description=self.bot.cogs[cog].__doc__
							embed.set_footer(text='<> Denotes required argument. [] Denotes optional argument')
							if command.hidden:
								continue
							i = i + 1
							aliases=""
							description=""
							if len(command.aliases)!=0:
								aliases=", ".join([alias for alias in command.aliases])
							else: aliases="None"
							description=command.description or "None"

							command_list = command_list + f'{i}) ``{ctx.prefix}{command.name}``\n'
							embed.add_field(inline=False,name=f"`{ctx.prefix}{command.name}`",value=f"Aliases: **{aliases}**\nDescription: **{description}**\nUsage: **{ctx.prefix+command.name} {command.signature}**")
						embeds.append(embed)
						embed=None
						command_list=""
					if len(embeds)==1:
						return await send_embed(ctx,embed=embeds[0])
					elif len(embeds)==0:
						emb = discord.Embed(title="lol, sadphroge \N{PENSIVE FACE}\N{PENSIVE FACE}\N{PENSIVE FACE}",
									description=f"ERROR 404 couldn't find `{input}` module",
									color=ctx.message.author.color)
						return await send_embed(ctx, emb)
					else:
						paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
						paginator.add_reaction('\N{Black Left-Pointing Double Triangle with Vertical Bar}', "first")
						paginator.add_reaction('\N{Black Left-Pointing Double Triangle}', "back")
						paginator.add_reaction('\N{CROSS MARK}', "lock")
						paginator.add_reaction('\N{Black Right-Pointing Double Triangle}', "next")
						paginator.add_reaction('\N{Black Right-Pointing Double Triangle with Vertical Bar}', "last")
						return await paginator.run(embeds)
					break

			else:
				emb = discord.Embed(title="lol, sadphroge \N{PENSIVE FACE}\N{PENSIVE FACE}\N{PENSIVE FACE}",
									description=f"ERROR 404 couldn't find `{input}` module",
									color=ctx.message.author.color)
				return await send_embed(ctx, emb)

def setup(bot):
	bot.add_cog(Help(bot))