import discord
from discord.ext import commands

import traceback
import sys
import datetime
import humanize

class HighlightHelpCommand(commands.HelpCommand):
    bottom_text = "\n\nKey: `<required> [optional]`. **Remove <> and [] when using the command**. \nFor more help join the [support server]({0})."

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        em = discord.Embed(title=f"{bot.user.name} Help", description=f"{bot.description}. If you need more help you can join the [support server]({bot.support_server_link}).\n\n", color=discord.Color.blurple())
        em.set_thumbnail(url=bot.user.avatar_url)

        commands = await self.filter_commands(bot.commands)
        for command in commands:
            em.description += f"`{self.get_command_signature(command)}` {f'- {command.description}' if command.description else ''}\n"

        em.description += "\n\nKey: `<required> [optional]`. **Remove <> and [] when using the command**."

        await ctx.send(embed=em)

    async def send_cog_help(self, cog):
        ctx = self.context
        bot = ctx.bot

        em = discord.Embed(title=f"{bot.user.name} Help", description=f"{bot.description}. Join our support sever for any questions or related issues [support server]({bot.support_server_link}).\n\n", color=discord.Color.blurple())
        em.set_thumbnail(url=bot.user.avatar_url)

        commands = await self.filter_commands(cog.get_commands())
        for command in commands:
            em.description += f"`{self.get_command_signature(command)}` {f'- {command.description}' if command.description else ''}\n"

        em.description += "\n\nKey: `<required> [optional]`. **Remove <> and [] when using the command**."

        await ctx.send(embed=em)

    async def send_command_help(self, command):
        ctx = self.context
        bot = ctx.bot

        em = discord.Embed(title=command.name, description=command.description or "", color=discord.Color.blurple())
        em.set_thumbnail(url=bot.user.avatar_url)

        if command.aliases:
            em.description += f"\nAliases: {', '.join(command.aliases)}"

        em.description += self.bottom_text.format(bot.support_server_link)

        await ctx.send(embed=em)

    async def send_group_help(self, group):
        ctx = self.context
        bot = ctx.bot

        em = discord.Embed(title=group.name, description=group.description or "", color=discord.Color.blurple())
        em.set_thumbnail(url=bot.user.avatar_url)

        if group.aliases:
            em.description += f"\nAliases: {', '.join(group.aliases)}\n"

        commands = await self.filter_commands(group.commands)
        for command in commands:
            em.description += f"`{self.get_command_signature(command)}` {f'- {command.description}' if command.description else ''}\n"

        em.description += self.bottom_text.format(bot.support_server_link)

        await ctx.send(embed=em)

class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self._original_help_command = bot.help_command
        bot.help_command = HighlightHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

def setup(bot):
    bot.add_cog(Meta(bot))
