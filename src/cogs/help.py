import discord
from discord.ext import commands
from discord.errors import Forbidden
import DiscordUtils
from discord import Embed
import logging
import coloredlogs

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
	async def help(self, ctx, *input):
		if not input:
			emb = discord.Embed(title='Commands and modules', color=ctx.message.author.color,description=f'Use `{ctx.prefix}help <module>` to gain more information about that module :smiley:\n')

			cogs_desc = ''
			for cog in self.bot.cogs:
				cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

			emb.add_field(name='Modules', value=cogs_desc, inline=False)

			commands_desc = ''
			for command in self.bot.walk_commands():
				if not command.cog_name and not command.hidden:
					commands_desc += f'{command.name} - {command.help}\n'
			if commands_desc:
				emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

		elif len(input) == 1:
			pages=[]
			for cog in self.bot.cogs:
				if cog.lower() == input[0].lower():
					# getting commands from cog
					threshold=10
					commands=self.bot.get_cog(cog).get_commands()
					command_chunk=[commands[i:i + threshold] for i in range(0, len(commands), threshold)]
					i=0
					embeds=[]
					command_list=""
					for chunk in command_chunk:
						for command in chunk:
								if command.hidden:
									continue
								i = i + 1
								command_list = command_list + f'{i}) ``{ctx.prefix}{command.name}``\n'
						embed=Embed(title=f"{command.cog_name} - Commands", description=self.bot.cogs[cog].__doc__,color=ctx.message.author.color,timestamp=ctx.message.created_at)
						embed.set_footer(text=f"Requested by {ctx.message.author}",icon_url=self.bot.user.avatar_url)
						embed.set_thumbnail(url=ctx.message.author.avatar_url)
						embed.set_author(name=ctx.message.author.display_name,icon_url=ctx.message.guild.icon_url)
						embed.add_field(inline=False,name="Command list",value=command_list)
						embeds.append(embed)
						embed=None
						command_list=""
					paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
					paginator.add_reaction('⏮️', "first")
					paginator.add_reaction('⏪', "back")
					paginator.add_reaction('⏩', "next")
					paginator.add_reaction('⏭️', "last")
					paginator.add_reaction('🔐', "lock")
					await paginator.run(embeds)
					break

			else:
				emb = discord.Embed(title="What's that?!",
									description=f"I've never heard from a module called `{input[0]}` before :scream:",
									color=discord.Color.orange())
				return await send_embed(ctx, emb)
		elif len(input) > 1:
			emb = discord.Embed(title="That's too much.",
								description="Please request only one module at once :sweat_smile:",
								color=discord.Color.orange())
			return await send_embed(ctx, emb)


def setup(bot):
	bot.add_cog(Help(bot))