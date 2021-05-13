# imports
import discord
import aiosqlite
import json
import time
from discord.ext import commands
from collections import Counter
import logging
import re
import numpy as np
from datetime import datetime
import calendar
import aiohttp


def dt2ts(dt):
    """Converts a datetime object to UTC timestamp

    naive datetime will be considered UTC.

    """

    return calendar.timegm(dt.utctimetuple())


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def check_with(string, wordlist):
    if any(map(string.lower().__contains__, wordlist)):
        return True


# TODO
    # Auto slowmode - done i think
global config
config = json.load(open("config.json", "r"))


async def webhook_send(url, message, username="LoggingCog", avatar="https://assets.stickpng.com/images/580b585b2edbce24c47b245d.png"):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(
            url, adapter=discord.AsyncWebhookAdapter(session))
        if isinstance(message, discord.Embed):
            await webhook.send(embed=message, username=username, avatar_url=avatar)
        else:
            await webhook.send(message, username=username, avatar_url=avatar)

# Standards
davie = 737690513876058203
logging.getLogger("discord").propagate = False
logging.basicConfig(
    format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
urlregex = open("urlregex.txt", "r", encoding="utf-8").read().strip()

# Base Classes


class GuildManager:
    def __init__(self):
        self.gpm = GuildPenaltyManager()
        self.asf = AutoSlowdownFilter()
        self.rf = GuildAntiRaid()
        pass

    async def update(self, message):
        if config["WHITELISTED_CHANNELS"] != []:
            whitelist = message.channel.id in config["WHITELISTED_CHANNELS"]
        else:
            whitelist = True
        if whitelist:
            if config["PENALTY_FILTER"]:
                await self.gpm.update(message)
            if config["AUTOSLOWDOWN_FILTER"]:
                await self.asf.update(message)


class GuildAntiRaid:
    def __init__(self):
        self.users = []
        pass

    async def log_join(self, member):
        if len(self.users) < config["RAID_USER_LIMIT"]:
            self.users.append([member, int(time.time())])
        else:
            await self.check_if_raid()

    async def check_if_raid(self):
        logging.info(f"Raid check called")
        times = [user[1] for user in self.users]
        times = np.array(times)
        times = np.diff(times)
        if len(times) == 0:
            np.append(times, 0)
        times = np.average(times)
        JOIN_FLAGS = []
        TIME_FLAG = 0
        AVATAR_FLAGS = []
        # EMAIL_FLAGS=[]
        if times < config["RAID_AVG_JOIN_TIME"]:
            TIME_FLAG = 1
        for user in self.users:
            join_date = dt2ts(user[0].created_at)
            if int(time.time())-join_date < config["RAID_JOIN_MIN"]:
                JOIN_FLAGS.append(1)
            else:
                JOIN_FLAGS.append(0)
            avatar = str(user[0].avatar_url)
            if any(substring in avatar for substring in ["/0.", "/1.", "/2.", "/3.", "/4."]):
                AVATAR_FLAGS.append(1)
            else:
                AVATAR_FLAGS.append(0)
            # EMAIL_FLAGS.append(1)
        AVATAR_POSSIBILITY = np.average(AVATAR_FLAGS)
        # EMAIL_POSSIBILITY=np.average(AVATAR_FLAGS)
        JOIN_POSSIBILITY = np.average(JOIN_FLAGS)
        confidence = (sum([
            AVATAR_POSSIBILITY,
            TIME_FLAG,
            # EMAIL_POSSIBILITY,
            JOIN_POSSIBILITY
        ])/3)*100
        if confidence > (config["RAID_SUSPECTED_CONFIDENCE"]/3)*100:
            logging.info("Potential raid caught")
            embed = discord.Embed()
            embed.title = "Suspected Raid"
            embed.description = "\n".join(
                [f"{u[0].name}#{u[0].discriminator}" for u in self.users])
            embed.add_field(name="Confidence:",
                            value=f"{round(confidence,2)}%")
            embed.add_field(name="Average join time:",
                            value=f"Each person joined at an interval of {times}s")
            embed.add_field(
                name="User Creation:", value=f"{JOIN_FLAGS.count(1)}/{len(JOIN_FLAGS)} users were new")
            embed.add_field(
                name="Avatar flags:", value=f"{AVATAR_FLAGS.count(1)}/{len(AVATAR_FLAGS)} users had no avatar")

            await webhook_send(config["RAID_WEBHOOK_URL"], embed)
        self.users = []


class GuildPenaltyManager:
    def __init__(self):
        self.users = {}
        pass

    async def dm_user(self, user, message):
        try:
            await user.send(message)
        except:
            logging.warning(f"Couldn't message {user.name}")

    async def update(self, message):
        if not str(message.author.id) in self.users:
            self.users[str(message.author.id)] = PenaltyManager(message.author)
        penalty = await self.users[str(message.author.id)].call_penalty(
            message)  # Update Penalties for a given user
        if penalty:
            if penalty.tension_level <= len(config["ACTIONS"]):
                msg = config["ACTIONS"][penalty.tension_level-1][2]
                if config["ACTIONS"][penalty.tension_level-1][0] == "WARN":
                    if config["ACTIONS"][penalty.tension_level-1][1] == "DM":
                        await self.dm_user(message.author, msg.replace("%mention%", message.author.mention))
                    else:
                        await message.channel.send(msg.replace("%mention%", message.author.mention))
                if config["ACTIONS"][penalty.tension_level-1][0] == "KICK":
                    if config["ACTIONS"][penalty.tension_level-1][1] == "DM":
                        await self.dm_user(message.author, msg.replace("%mention%", message.author.mention))
                    else:
                        await message.channel.send(msg.replace("%mention%", message.author.mention))
                    await message.author.kick()
                if config["ACTIONS"][penalty.tension_level-1][0] == "BAN":

                    if config["ACTIONS"][penalty.tension_level-1][1] == "DM":
                        await self.dm_user(message.author, msg.replace("%mention%", message.author.mention))
                    else:
                        await message.channel.send(msg.replace("%mention%", message.author.mention))
                    await message.author.ban()


class PenaltyManager:
    def __init__(self, user):
        self.user = user
        self.penalty = 0
        self.tension_level = 0
        self.last = int(time.time())
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

    async def call_penalty(self, message):
        msg = message.content.lower()
        self.add_message(msg)
        mapped = Counter(self.messages)

        if self.__flush():  # Check if person hasn't caused a ruckus in over a minute
            logging.info(f"ID: {message.author.id} flushing penalties")
            self.__reset()

        if not config["AUTO_PROFANE_FILTER"]:
            if check_with(msg, config["LOW_LEVEL_PROFANITY_WORDS"]):
                logging.info(
                    f"ID: {message.author.id} low profanity detection")
                self.penalty += config["LOW_PENALTY"]
            if check_with(msg, config["HIGH_LEVEL_PROFANITY_WORDS"]):
                try:
                    await message.delete()
                except:
                    logging.info(
                        f"ID: {message.author.id} couldn't delete message, insufficient perms most likely")
                logging.info(
                    f"ID: {message.author.id} high profanity detection")
                self.penalty += config["HIGH_PENALTY"]
        else:
            pass
        if len(self.messages) > 3:
            repeated = max(mapped, key=lambda key: mapped[key])
            if self.messages[-1] == self.messages[-2]:
                self.penalty += 5
                logging.info(
                    f"ID: {message.author.id} message repeated, penalty: {self.penalty}")
            if mapped[repeated] > config["REPEAT_THRESHOLD"]:
                self.penalty += 15
                self.messages = []
                logging.info(
                    f"ID: {message.author.id} repeat threshold reached: {self.penalty}")

        if self.penalty > config["PENALTY_THRESHOLD"]:
            logging.info(
                f"ID: {message.author.id} penalty threshold reached: {self.penalty}")
            penalty = self.penalty
            self.__raise_tension()
            return Penalty(penalty, self.tension_level)
        self.last = int(time.time())

    def __flush(self):
        return True if (int(time.time())-self.last) > config["FLUSH_AFTER"] else False

    def __raise_tension(self):
        self.penalty = 0
        self.messages = []
        self.tension_level += 1

    def __reset(self):
        self.penalty = 0
        self.messages = []
        self.tension_level = 0


class Penalty:
    def __init__(self, score, tension_level):
        self.score = score
        self.tension_level = tension_level

# class ChainFilter:
#     def __init__(self):
#         self.messages=[]
#     def detect_alphabetic(self):
#         is_alphabetic=False
#         for message in enumerate(self.messages):
#             if len(message[1])<=2:
#                 if not is_int(message[1]):
#                     if message[1] in [chr(x) for x in range(65,91) ] + [chr(x) for x in range(97, 123)]:
#                         is_alphabetic=True
class AutoSlowdownFilter:

    def __init__(self):
        self.messages = {}  # List of messages, key: channel id and value: list of messages
        self.last = time.time()  # Time since last message

    async def update(self, message):
        if not str(message.channel.id) in self.messages:
            self.messages[str(message.channel.id)] = []

        self.messages[str(message.channel.id)].append((time.time(), message))
        if len(self.messages[str(message.channel.id)]) == config["AUTOSLOWDOWN_THRESHOLD"]:
            times = [x[0] for x in self.messages[str(message.channel.id)]]
            times = np.diff(times)
            # Check for mean difference in message sending times
            average = np.average(times)
            if average < 0.5:
                await message.channel.edit(slowmode_delay=(5 if message.channel.slowmode_delay == 0 else message.channel.slowmode_delay+1))
            else:
                if message.channel.slowmode_delay != 0:
                    await message.channel.edit(slowmode_delay=0)
            self.messages[str(message.channel.id)] = []


class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.GUILD_MANAGERS = {}

    @commands.Cog.listener()
    async def on_member_update(self, old, new):
        """
        - Auto Rename Filter
        - More Potential Filters

        """
        if old.guild.id != davie:
            return
        if new.bot:
            return

        if config["AUTORENAME_FILTER"]:
            if old.display_name != new.display_name:
                print(f"updated: {new.display_name} | {new.display_name}")
                if new.nick:
                    if check_with(new.display_name, config["HIGH_LEVEL_PROFANITY_WORDS"]):
                        logging.info(f"ID: {new.id} | Autorenamed")
                        await new.edit(nick="change your username")

    @commands.Cog.listener()
    async def on_ready(self):

        print("Ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
            - Raid Filter
            - Autokick Filter
            - Autorename Filter

        """
        if member.guild.id != davie:
            return
        if not str(member.guild.id) in self.GUILD_MANAGERS:
            self.GUILD_MANAGERS[str(member.guild.id)] = GuildManager()

        if config["RAID_FILTER"]:
            await self.GUILD_MANAGERS[str(member.guild.id)].rf.log_join(member)

        if config["AUTOKICK_FILTER"]:
            if check_with(member.name, config["HIGH_LEVEL_PROFANITY_WORDS"]):
                try:
                    await member.send(config["AUTOKICK_MESSAGE"])
                except:
                    logging.warning(
                        f"Couldn't message {member.name} about their kick")
                    pass
                await member.kick()
                logging.info(f"ID: {member.id} | Autokicked for NSFW name")

        else:
            if config["AUTORENAME_FILTER"]:
                if check_with(member.name, config["HIGH_LEVEL_PROFANITY_WORDS"]):
                    logging.info(f"ID: {member.id} | Autorenamed")
                    await member.edit(nick="change your username")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
            - Penalty Filter
            - Most of Automod Features

        """
        if message.author.bot:
            return
        if message.guild.id != davie:
            return
        if not str(message.guild.id) in self.GUILD_MANAGERS:
            self.GUILD_MANAGERS[str(message.guild.id)] = GuildManager()
        await self.GUILD_MANAGERS[str(message.guild.id)].update(message)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 10):
        deleted = await ctx.channel.purge(limit=amount)
        return await ctx.send(f"Deleted {len(deleted)} message(s)")

    @commands.group(invoke_without_command=True)
    @commands.has_guild_permissions(manage_messages=True)
    async def pp(self, ctx):
        await ctx.send("Please specify the required arguments")

    @pp.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def messages(self, ctx, amount: int = 10):
        deleted = await ctx.channel.purge(limit=amount+1)
        return await ctx.send(f"Deleted {len(deleted)-1} message(s)")

    @pp.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def links(self, ctx, amount: int = 10):
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False
            chunks = " ".join(m.content.lower().split("\n"))
            chunks = chunks.split(" ")
            for chunk in chunks:
                if (True if re.search(urlregex, chunk) else False):
                    counter += 1
                    return True
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"Deleted {len(deleted)}/{amount} message(s) which had links")

    @pp.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def startswith(self, ctx, key, amount: int = 10):
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.content.startswith(key):
                counter += 1
                return True
            else:
                return False
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"Deleted {len(deleted)}/{amount} message(s) which started with the given keyword")

    @pp.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def endswith(self, ctx, key, amount: int = 10):
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.content.endswith(key):
                counter += 1
                return True
            else:
                return False
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"Deleted {len(deleted)}/{amount} message(s) which ended with the given keyword")

    @pp.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def contains(self, ctx, key, amount: int = 10):
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if key in m.content:
                counter += 1
                return True
            else:
                return False
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"Deleted {len(deleted)}/{amount} message(s) which contained the given keyword")

    @pp.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def user(self, ctx, user: discord.Member, amount: int = 10):
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.author.id == user.id:
                counter += 1
                return True
            else:
                return False
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"Deleted {len(deleted)}/{amount} message(s) which were sent by the mentioned user")

    @pp.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def invites(self, ctx, amount: int = 10):
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if "discord.gg/" in m.content.lower():
                counter += 1
                return True
            else:
                return False
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"Deleted {len(deleted)}/{amount} message(s) which contained invites")

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def settings(self, ctx, check_type="read", key=None, *, value=None):
        if ctx.guild.id != davie:
            return
        global config
        embed = discord.Embed()
        embed.title = "Config for the server"
        if check_type == "read":
            for x in config:
                if x == "RAID_WEBHOOK_URL":
                    continue
                if not isinstance(config[x], list):
                    embed.add_field(name=x.replace(
                        "_", " ").capitalize(), value=config[x], inline=False)
            return await ctx.send(embed=embed)
        if check_type == "edit":
            if not key or not value:
                return await ctx.send("No key/value specified")
            if not key in config:
                return await ctx.send("Specified key isn't available in my config")

            if is_int(value):
                value = int(value)
            if value == "True" or value == "False":
                value = eval(value)
            prev = config[key]
            config[key] = value
            f = open("config.json", "w")
            json.dump(config, f, indent=4)
            embed = discord.Embed()
            embed.title = "Updated values"
            embed.description = f"""
            {key} was changed:

            `{prev} => {value}`
            """
            return await ctx.send(embed=embed)
        if check_type == "toggle":
            if not key:
                return await ctx.send("No key/value specified")
            if not key in config:
                return await ctx.send("Specified key isn't available in my config")
            if not isinstance(config[key], bool):
                return await ctx.send("Specified feature cannot be toggled.")
            prev = config[key]
            config[key] = (not prev)
            f = open("config.json", "w")
            json.dump(config, f, indent=4)
            embed = discord.Embed()
            embed.title = "Updated values"
            embed.description = f"""
            {key} was toggled:

            `{prev} => {(not prev)}`
            """
            return await ctx.send(embed=embed)
        return await ctx.send(f"Unrecognized parameter: `{check_type}`")

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def swear(self, ctx, check_type="add", key=None, list_level="low"):
        if ctx.guild.id != davie:
            return
        global config
        ltype = list_level.upper()+"_LEVEL_PROFANITY_WORDS"
        if not ltype in ["LOW_LEVEL_PROFANITY_WORDS", "HIGH_LEVEL_PROFANITY_WORDS"]:
            return await ctx.send("Specified swear level is not registered in my config")
        if not key:
            return await ctx.send("No word specified")

        if check_type == "add":
            if key in config[ltype]:
                return await ctx.send("Swear word is already in list ")
            config[ltype].append(key)
            f = open("config.json", "w")
            json.dump(config, f, indent=4)
            embed = discord.Embed()
            embed.title = "Updated values"
            embed.description = f"""
            {key} was added to the swear list
            """
            return await ctx.send(embed=embed)
        if check_type == "remove":
            if not key in config[ltype]:
                return await ctx.send("Swear word is not in the swear list ")
            config[ltype] = list(filter((key).__ne__, config[ltype]))
            f = open("config.json", "w")
            json.dump(config, f, indent=4)
            embed = discord.Embed()
            embed.title = "Updated values"
            embed.description = f"""
            {key} was removed from the swear list
            """
            return await ctx.send(embed=embed)
        return await ctx.send(f"Unrecognized parameter: `{check_type}`")

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def whitelist(self, ctx, key=None):
        if ctx.guild.id != davie:
            return
        global config
        if not key:
            return await ctx.send("No channel id specified")
        else:
            if not is_int(key):
                return await ctx.send("Specify a channel ID")
            else:
                key = int(key)
        removed = False
        if key in config["WHITELISTED_CHANNELS"]:
            config["WHITELISTED_CHANNELS"] = list(
                filter(lambda a: a != key, config["WHITELISTED_CHANNELS"]))
            removed = True
        else:
            config["WHITELISTED_CHANNELS"].append(key)
        f = open("config.json", "w")
        json.dump(config, f, indent=4)
        embed = discord.Embed()
        embed.title = "Updated values"
        embed.description = f"""
        {key} was {("added to" if not removed else "removed from")} the channels whitelist
        """
        return await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Automod(client))
