# !!!! NOT FINISHED YET!!! I'M STILL WORKING ON THE CONFIG MANAGER FOR THIS!!!!
from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
#from guildconfigmanager import GCM
import discord
import aiohttp

# Exporters


async def export_message(webhook, message):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(
            webhook, adapter=AsyncWebhookAdapter(session))
        await webhook.send(embed=message, username='Logger', avatar_url="https://cdn4.iconfinder.com/data/icons/small-n-flat/24/notepad-512.png")


async def export_reaction(reaction, user, webhook, status="added"):
    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Reaction {status.capitalize()}"
    embed.description = f"""
    **Reaction Data:**
    Reaction: {reaction.emoji}
    {f'Reaction Name: `{reaction.emoji.name}`' if reaction.custom_emoji else ""}
    {f'Reaction ID: `{reaction.emoji.id}`' if reaction.custom_emoji else ""}
    **Message Data:**
    Message: [Jump]({reaction.message.jump_url})
    Author: `{user.name}#{user.discriminator}` | AuthorID: `{user.id}`
    Channel: {reaction.message.channel.mention} | ID: `{reaction.message.channel.id}`
    """
    await export_message(webhook, embed)


async def export_reaction_clear(reaction, webhook):

    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Reaction Cleared"
    embed.description = f"""
    **Reaction Data:**
    Reaction: {reaction.emoji}
    {f'Reaction Name: `{reaction.emoji.name}`' if reaction.custom_emoji else ""}
    {f'Reaction ID: `{reaction.emoji.id}`' if reaction.custom_emoji else ""}
    **Message Data:**
    Message: [Jump]({reaction.message.jump_url})
    Channel: {reaction.message.channel.mention} | ID: `{reaction.message.channel.id}`
    """
    await export_message(webhook, embed)


async def export_message_delete(msg, webhook):

    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Message Deleted"
    embed.description = f"""
    **Message Data:**
    MessageContent: ```{msg.content}```
    Author: `{msg.author.name}#{msg.author.discriminator}` | AuthorID: `{msg.author.id}`
    Channel: {msg.channel.mention} | ID: `{msg.channel.id}`
    """
    await export_message(webhook, embed)


async def export_message_delete_several(msgs, webhook):
    data = [
        f"[{m.author.name}#{m.author.discriminator}]: {m.content}" for m in msgs]
    data = data.join("\n")
    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Messages Purged"
    embed.description = data[0:1500] + "..."
    embed.set_footer(
        text=f"{len(msgs)} msgs were purged that were known to cache")
    await export_message(webhook, embed)


async def export_message_edit(before, after, webhook):
    if before.content == after.content:
        return
    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Message Edited"
    embed.description = f"""
    **Before:**
    {before.content}

    **After:**
    {after.content}
    """
    embed.set_author(
        name=f"{before.author.name}#{before.author.discriminator}", icon_url=before.author.avatar_url)
    await export_message(webhook, embed)


async def export_channel_event(channel, webhook, status="created"):

    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Channel {status.capitalize()}"
    embed.description = f"""
    **Channel Data:**
    Channel Name: ```{channel.name}```
    Channel ID: `{channel.id}`
    """
    await export_message(webhook, embed)


async def export_channel_update(before, after, webhook):

    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Channel Updated"
    embed.description = f"""
    **Before**
    Channel Name: ```{before.name}```
    Channel ID: `{before.id}`
    Channel Topic: `{before.topic}`

    **After**
    Channel Name: ```{after.name}```
    Channel ID: `{after.id}`
    Channel Topic: `{after.topic}`
    """
    await export_message(webhook, embed)


async def export_channel_pin(channel, pin, webhook):

    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Message Pinned"
    embed.description = f"""
    A new message was pinned/unpinned on {pin.strftime('%m/%d/%Y, %H:%M:%S') if pin else "DUMMY_DATE"}

    **Channel**
    Channel Name: ```{channel.name}```
    Channel ID: `{channel.id}`
    """
    await export_message(webhook, embed)


async def export_member(member, webhook, status="joined"):

    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Member {status.capitalized()}"
    embed.description = f"""
    **Member Data:**
    Member: `{member.name}#{member.discriminator}`
    MemberID: `{member.id}`
    """
    await export_message(webhook, embed)


async def export_user_update(before, after, webhook):
    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Member Edited"
    embed.description = f"""
    **Before:**
    Username: {before.name}
    UID: {before.id}
    Avatar: [Avatar]({before.avatar_url})
    Discrim: {before.discrimnator}

    **After:**
    Username: {after.name}
    UID: {after.id}
    Avatar: [Avatar]({after.avatar_url})
    Discrim: {after.discrimnator}
    """
    embed.set_author(
        name=f"{before.author.name}#{before.author.discriminator}", icon_url=before.author.avatar_url)
    await export_message(webhook, embed)


async def export_guild_integration_update(guild, webhook):

    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Guild Integrations Update"
    integrations = await guild.integrations()
    msg = ""
    for i in integrations:
        msg += f"{i.name}: " + \
            (":green_circle:" if i.enabled else ":red_circle:") + "\n"
    embed.description = f"""
    **Current Integrations:**
    {msg}
    """
    await export_message(webhook, embed)


async def export_guild_webhook_update(channel, webhook):

    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Channel Webhook Update"
    webhooks = await channel.webhooks()
    msg = ""
    for i in webhooks:
        msg += f"{i.name if i.name else 'WEBHOOK_NAME'}: {i.id}\n"
    embed.description = f"""
    **Current Webhooks:**
    {msg}
    """
    embed.set_footer(text=f"Channel: {channel.name} | {channel.id}")
    await export_message(webhook, embed)


async def export_guild_update(before, after, webhook):
    embed = discord.Embed(color=discord.Color.green())
    embed.title = f"Guild Update"
    embed.description = f"""
    **Before:**
    Guild Name: {before.name}
    GuildID: {before.id}
    Icon: [Avatar]({before.icon_url})
    Region: {before.region}

    **After:**
    Guild Name: {after.name}
    GuildID: {after.id}
    Icon: [Avatar]({after.icon_url})
    Region: {after.region}
    """
    await export_message(webhook, embed)


async def export_guild_role_event(role, webhook, status="created"):
    embed = discord.Embed(color=discord.Color.red())
    embed.title = f"Role {status.capitalize()}"
    embed.description = f"""
    **Role Data:**
    RoleName: {role.name}
    RoleID: `{role.id}`
    RolePosition: `#{role.position}`
    RoleMentionable?: `{role.mentionable}`
    """
    await export_message(webhook, embed)


class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # await GCM.fetch_webhook(user.guild.id)
        self.webhook = "https://discord.com/api/webhooks/845869820066136074/P1jkQFIl54bzjADncrIRnaXkJI3oQYptHC_Ysc_WJ6t80QSQ4m-6TRPizcJdFQNfnSAi"

    """
    Reaction Events
    """

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await export_reaction(reaction, user, self.webhook)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        await export_reaction(reaction, user, self.webhook, "removed")

    @commands.Cog.listener()
    async def on_reaction_clear(self, reaction):
        await export_reaction_clear(reaction, self.webhook)

    @commands.Cog.listener()
    async def on_reaction_clear_emoji(self, reaction):
        await export_reaction_clear(reaction, self.webhook)

    """
    Message Events
    """

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        await export_message_delete(message, self.webhook)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        print("delete triggered")
        await export_message_delete_several(payload.cached_messages, self.webhook)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await export_message_edit(before, after, self.webhook)

    """
    Channel Events
    """

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await export_channel_event(channel, self.webhook)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await export_channel_event(channel, self.webhook, "deleted")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        await export_channel_update(before, after, self.webhook)

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        await export_channel_pin(channel, last_pin, self.webhook)

    """
    Member Events
    """

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await export_member(member, self.webhook)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await export_member(member, self.webhook, "left")

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        await export_user_update(before, after, self.webhook)

    """
    Guild Events
    """
    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild):
        await export_guild_integration_update(guild, self.webhook)

    @commands.Cog.listener()
    async def on_webhook_update(self, channel):
        print("webhook called")
        await export_guild_webhook_update(channel, self.webhook)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        await export_guild_update(before, after, self.webhook)

    @commands.Cog.listener()
    async def on_role_create(self, role):
        await export_guild_role_event(role, self.webhook)

    @commands.Cog.listener()
    async def on_role_delete(self, role):
        await export_guild_role_event(role, self.webhook, "deleted")


def setup(bot):
    bot.add_cog(Logger(bot))
