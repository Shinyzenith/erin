import os
import re
import json
import typing
import asyncio
import discord
import asyncpg
import logging
import humanize
import datetime
import dateparser
import coloredlogs

from discord.ext import commands, tasks


class DiscordConverter(commands.Converter):
    def mention_or_id(self, arg):
        match = re.match(r"([0-9]{15,21})$", arg) or re.match(r"<@!?([0-9]+)>$", arg)
        return match

    async def wait_for_ratelimit(self, ctx):
        async with ctx.typing():
            while ctx.bot.is_ws_ratelimited():
                await asyncio.sleep(5)


class MemberConverter(DiscordConverter):
    async def convert(self, ctx, arg):
        match = self.mention_or_id(arg)

        # ID or mention
        if match:
            int_arg = int(match.group(1))

            try:
                member = await ctx.guild.fetch_member(int_arg)
                return member
            except discord.HTTPException:
                pass

        # Split username and discriminator
        if len(arg) > 5 and arg[-5] == "#":
            discriminator = arg[-4:]
            username = arg[:-5]
        else:
            username = arg
            discriminator = None

        if ctx.bot.is_ws_ratelimited():
            await self.wait_for_ratelimit(ctx)

        # Query members by username
        members = await ctx.guild.query_members(query=username, limit=100, cache=False)
        for member in members:
            if member.name == username and (
                not discriminator or member.discriminator == discriminator
            ):
                return member

        # Query members by nickname
        members = await ctx.guild.query_members(query=arg, limit=100, cache=False)
        for member in members:
            if member.nick == arg:
                return member

        raise commands.BadArgument(f"Member `{arg}` not found")


class UserConverter(DiscordConverter):
    async def convert(self, ctx, arg):
        match = self.mention_or_id(arg)

        # ID or mention
        if match:
            int_arg = int(match.group(1))

            try:
                member = await ctx.bot.fetch_user(int_arg)
                return member
            except discord.HTTPException:
                pass

        # Split username and discriminator
        if len(arg) > 5 and arg[-5] == "#":
            discriminator = arg[-4:]
            username = arg[:-5]
        else:
            username = arg
            discriminator = None

        if ctx.bot.is_ws_ratelimited():
            await self.wait_for_ratelimit(ctx)

        # Query members by username
        members = await ctx.guild.query_members(query=username, limit=100, cache=False)
        for member in members:
            if member.name == username and (
                not discriminator or member.discriminator == discriminator
            ):
                return member

        raise commands.BadArgument(f"User `{arg}` not found")


class TimeConverter(commands.Converter):
    async def convert(self, ctx, arg):
        try:
            if not arg.startswith("in") and not arg.startswith("at"):
                arg = f"in {arg}"
            time = dateparser.parse(arg, settings={"TIMEZONE": "UTC"})
        except:
            raise commands.BadArgument("Failed to parse time")
        if not time:
            raise commands.BadArgument("Failed to parse time")
        return time


log = logging.getLogger("Highlight cog")
coloredlogs.install(logger=log)


class Highlight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._highlight_batch = []
        self._batch_lock = asyncio.Lock(loop=bot.loop)

        self.bulk_insert_loop.add_exception_type(asyncpg.PostgresConnectionError)
        self.bulk_insert_loop.start()

    @commands.Cog.listener()
    async def on_ready(self):

        log.info("Initiating database")

        query = """CREATE TABLE IF NOT EXISTS words (
				   user_id BIGINT,
				   guild_id BIGINT,
				   word TEXT
				   );

				   CREATE TABLE IF NOT EXISTS settings (
				   user_id BIGINT PRIMARY KEY,
				   disabled BOOL,
				   timezone INT,
				   blocked_users BIGINT ARRAY,
				   blocked_channels BIGINT ARRAY
				   );

				   CREATE TABLE IF NOT EXISTS timers (
				   id SERIAL PRIMARY KEY,
				   user_id BIGINT,
				   event TEXT,
				   time TIMESTAMP,
				   extra jsonb DEFAULT ('{}'::jsonb),
				   created_at TIMESTAMP DEFAULT (now() at time zone 'utc')
				   );

				   CREATE TABLE IF NOT EXISTS highlights (
				   guild_id BIGINT,
				   channel_id BIGINT,
				   message_id BIGINT,
				   author_id BIGINT,
				   user_id BIGINT,
				   word TEXT,
				   invoked_at TEXT
				   );

				   CREATE UNIQUE INDEX IF NOT EXISTS unique_words_index ON words (user_id, guild_id, word);
				"""
        await self.bot.db.execute(query)
        log.info("Preparing words cache")
        for row in await self.bot.db.fetch("SELECT word FROM words"):
            if row["word"] not in self.bot.cached_words:
                self.bot.cached_words.append(row["word"])
        log.warn(f"{self.__class__.__name__} Cog has been loaded")

    def cog_unload(self):
        self.bulk_insert_loop.stop()

    def cog_check(self, ctx):
        return ctx.guild

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if message.author.bot:
            return

        notifications = []
        for cached_word in self.bot.cached_words:
            if self.word_in_message(cached_word, message.content.lower()):
                query = """SELECT *
						   FROM words
						   WHERE words.guild_id=$1 AND words.word=$2;
						"""
                words = await self.bot.db.fetch(query, message.guild.id, cached_word)

                for word in words:
                    if word["user_id"] not in [
                        notification["user_id"] for notification in notifications
                    ]:
                        notifications.append(word)

        tasks = [
            self.send_highlight(message, notification) for notification in notifications
        ]
        await asyncio.gather(*tasks)

    async def send_highlight(self, message, word):
        try:
            member = await message.guild.fetch_member(word["user_id"])
        except discord.NotFound:
            log.info(
                "Received a highlight for user ID %s (guild ID %s) but member could not be fetched",
                word["user_id"],
                word["guild_id"],
            )

        query = """SELECT *
				   FROM settings
				   WHERE settings.user_id=$1;
				"""
        settings = await self.bot.db.fetchrow(query, member.id)
        if not settings:
            settings = {
                "user_id": member.id,
                "disabled": False,
                "timezone": 0,
                "blocked_users": [],
                "blocked_channels": [],
            }
        timezone = settings["timezone"]

        if member.id == message.author.id or settings["disabled"]:
            return
        if not message.channel.permissions_for(member).read_messages:
            return
        if (
            message.channel.id in settings["blocked_channels"]
            or message.author.id in settings["blocked_users"]
        ):
            return

        utc = ""
        if timezone == 0:
            utc = " UTC"

        description = f"In {message.channel.mention} for `{discord.utils.escape_markdown(message.guild.name)}` you were highlighted with the word **{discord.utils.escape_markdown(word['word'])}**\n\n"
        em = discord.Embed(
            description=description,
            timestamp=message.created_at,
            color=discord.Color.blurple(),
        )
        em.set_author(
            name=message.author.display_name, icon_url=message.author.avatar_url
        )
        em.add_field(name="Jump", value=f"[Jump!]({message.jump_url})")
        em.set_footer(text="Triggered")

        try:
            history = await message.channel.history(limit=3, before=message).flatten()
            messages = []
            for ms in reversed(history):
                content = f"{ms.content[:50]}{'...' if len(ms.content) > 50 else ''}"
                time = (ms.created_at + datetime.timedelta(hours=timezone)).strftime(
                    "%H:%M:%S"
                )
                messages.append(
                    f"`{time}{utc}` {discord.utils.escape_markdown(str(ms.author))}: {discord.utils.escape_markdown(content)}"
                )
            em.description += "\n".join(messages)
        except discord.HTTPException:
            pass

        span = re.search(word["word"], message.content.lower()).span()
        content = discord.utils.escape_markdown(message.content[: span[0]])
        content += f"**{discord.utils.escape_markdown(word['word'])}**"
        content += discord.utils.escape_markdown(message.content[span[1] :])

        content = f"{content[:50]}{'...' if len(content) > 50 else ''}"
        time = (message.created_at + datetime.timedelta(hours=timezone)).strftime(
            "%H:%M:%S"
        )
        em.description += f"\n> `{time}{utc}` {discord.utils.escape_markdown(str(message.author))}: {content}"

        # Check for anything new to add
        try:
            ms = await self.bot.wait_for(
                "message", check=lambda ms: ms.channel == message.channel, timeout=10
            )
            if ms.author.id == member.id:
                return

            content = f"{ms.content[:50]}{'...' if len(ms.content) > 50 else ''}"
            time = (ms.created_at + datetime.timedelta(hours=timezone)).strftime(
                "%H:%M:%S"
            )
            em.description += f"\n`{time}{utc}` {discord.utils.escape_markdown(str(ms.author))}: {discord.utils.escape_markdown(content)}"
        except asyncio.TimeoutError:
            pass

        self._highlight_batch.append(
            {
                "guild_id": message.guild.id,
                "channel_id": message.channel.id,
                "message_id": message.id,
                "author_id": message.author.id,
                "user_id": word["user_id"],
                "word": word["word"],
                "invoked_at": message.created_at.isoformat(),
            }
        )

        try:
            await member.send(embed=em)
        except discord.Forbidden:
            log.warning("Forbidden to send highlight message to user ID %s", member.id)

    def word_in_message(self, word, message):
        # Get the word in the message
        match = re.search(word, message)

        # Word isn't the message so, reurn False
        if not match:
            return False

        span = match.span()

        start = span[0] - 1
        end = span[1]

        if start >= 0:
            # If the charecter before the word is not a space, then the word techincally isn't in the message
            if message[start] != " ":
                return False

        return True

    async def can_dm(self, user):
        # Attempt to check if the user can be be sen DMs by sending an empy message
        try:
            await user.send()
        except discord.HTTPException as exc:
            if exc.code == 50006:
                return True
            elif exc.code == 50007:
                return False
            else:
                raise

    @commands.command(name="add", description="Add a word to your highlight list")
    async def add(self, ctx, *, word):
        word = word.lower()
        can_dm = await self.can_dm(ctx.author)
        if not can_dm:
            await ctx.send(":x: You need to enable DMs")
        elif f"<@!{self.bot.user.id}>" in word:
            await ctx.send(":x: Your highlight word can't mention me")
        elif len(word) < 2:
            await ctx.send(":x: Your word must be at least 2 characters")
        elif len(word) > 20:
            await ctx.send(":x: Your word cannot be bigger than 20 characters")
        else:
            try:
                query = f"""SELECT * FROM words WHERE user_id ={ctx.author.id} AND guild_id={ctx.guild.id} """
                result = await self.bot.db.fetch(query)
                if len(result) >= 20:
                    return await ctx.message.reply(
                        f"You have reached the guild limit of 20 highlights, please remove one highlight with `{ctx.prefix}remove` to free up a slot"
                    )
            except:
                pass
            try:
                query = """INSERT INTO words (user_id, guild_id, word)
						VALUES ($1, $2, $3);
						"""
                await self.bot.db.execute(query, ctx.author.id, ctx.guild.id, word)

                if word not in self.bot.cached_words:
                    self.bot.cached_words.append(word)
                await ctx.send(
                    f":white_check_mark: Added `{word}` to your highlight list"
                )
            except asyncpg.UniqueViolationError:
                await ctx.send(":x: You already have this word")

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(
        name="remove", description="Remove a word from your highlight list"
    )
    async def remove(self, ctx, *, word):
        query = """DELETE FROM words
				   WHERE words.user_id=$1 AND words.guild_id=$2 AND words.word=$3;
				"""
        result = await self.bot.db.execute(query, ctx.author.id, ctx.guild.id, word)

        if result == "DELETE 0":
            await ctx.send(":x: This word is not registered")
        else:
            await ctx.send(
                f":white_check_mark: Removed `{word}` from your highlight list"
            )

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name="clear", description="Clear your highlight list")
    async def clear(self, ctx):
        query = """DELETE FROM words
					WHERE words.user_id=$1 AND words.guild_id=$2;
				"""
        result = await self.bot.db.execute(query, ctx.author.id, ctx.guild.id)

        await ctx.send(f":white_check_mark: Your highlight list has been cleared")

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(
        name="import",
        description="Import words from another server",
        usage="<server id>",
        aliases=["transfer"],
    )
    async def transfer(self, ctx, guild_id: int):
        query = """SELECT *
				   FROM words
				   WHERE words.user_id=$1 AND (words.guild_id=$2 OR words.guild_id=$3);
				"""
        words = await self.bot.db.fetch(query, ctx.author.id, guild_id, ctx.guild.id)
        words = [dict(word) for word in words]

        to_transfer = []
        for word in words:
            if word["guild_id"] == guild_id and word["word"] not in [
                word["word"] for word in words if word["guild_id"] == ctx.guild.id
            ]:
                word["guild_id"] = ctx.guild.id
                to_transfer.append(word)

        if to_transfer:
            query = """INSERT INTO words (user_id, guild_id, word)
					   SELECT x.user_id, x.guild_id, x.word
					   FROM jsonb_to_recordset($1::jsonb) AS
					   x(user_id BIGINT, guild_id BIGINT, word TEXT);
					"""

            await self.bot.db.execute(query, to_transfer)
            await ctx.send(":white_check_mark: Your highlight list has been imported")
        else:
            await ctx.send(":x: You have no words to transfer from this server")

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(
        name="show", description="View your highlight list", aliases=["words", "list"]
    )
    async def show(self, ctx):
        query = """SELECT * FROM words
				   WHERE words.user_id=$1 AND words.guild_id=$2;
				"""
        rows = await self.bot.db.fetch(query, ctx.author.id, ctx.guild.id)

        query = """SELECT *
				FROM settings
				WHERE settings.user_id=$1;
				"""
        settings = await self.bot.db.fetchrow(query, ctx.author.id)

        if not rows:
            await ctx.send("You have no words for this server")
        else:
            em = discord.Embed(color=discord.Color.blurple())
            em.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            word = ""
            for row in rows:
                word += f"\n{row['word']}"
            em.add_field(name="Highlighted words:", inline=False, value=word)

            if not settings or (
                not settings["blocked_channels"] and not settings["blocked_users"]
            ):
                em.add_field(
                    name="Blocked users and channels:",
                    inline=False,
                    value="No blocked user(s) or channel(s)",
                )
                return await ctx.send(embed=em)
            else:
                users = []
                for user_id in settings["blocked_users"]:
                    user = await self.bot.fetch_user(user_id)
                    if user:
                        users.append(user.mention)
                if users:
                    em.add_field(
                        name="Blocked Users", value="\n".join(users), inline=True
                    )
                channels = []
                for channel_id in settings["blocked_channels"]:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        channels.append(channel.mention)

                if channels:
                    em.add_field(
                        name="Blocked Channels", value="\n".join(channels), inline=True
                    )

                await ctx.send(embed=em)
            try:
                await ctx.message.delete()
            except discord.HTTPException:
                pass

    @commands.command(
        name="block",
        description="Block a user or channel",
        usage="<user or channel>",
        aliases=["ignore"],
    )
    async def block(
        self, ctx, *, user: typing.Union[UserConverter, discord.TextChannel]
    ):
        query = """SELECT *
				   FROM settings
				   WHERE settings.user_id=$1;
				"""
        settings = await self.bot.db.fetchrow(query, ctx.author.id)

        if isinstance(user, discord.User) or isinstance(user, discord.Member):
            if settings:
                if user.id in settings["blocked_users"]:
                    await ctx.send(":x: This user is already blocked")
                else:
                    settings["blocked_users"].append(user.id)
                    query = """UPDATE settings
							   SET blocked_users=$1
							   WHERE settings.user_id=$2;
							"""
                    await self.bot.db.execute(
                        query, settings["blocked_users"], ctx.author.id
                    )
                    await ctx.send(f":no_entry_sign: Blocked `{user.display_name}`")
            else:
                query = """INSERT INTO settings (user_id, disabled, timezone, blocked_users, blocked_channels)
						   VALUES ($1, $2, $3, $4, $5);
						"""
                await self.bot.db.execute(query, ctx.author.id, False, 0, [user.id], [])
        else:
            if settings:
                if user.id in settings["blocked_channels"]:
                    await ctx.send(":x: This channel is already blocked")
                else:
                    settings["blocked_channels"].append(user.id)
                    query = """UPDATE settings
							   SET blocked_channels=$1
							   WHERE settings.user_id=$2;
							"""
                    await self.bot.db.execute(
                        query, settings["blocked_channels"], ctx.author.id
                    )
                    await ctx.send(f":no_entry_sign: Blocked {user.mention}")
            else:
                query = """INSERT INTO settings (user_id, disabled, timezone, blocked_users, blocked_channels)
						   VALUES ($1, $2, $3, $4, $5);
						"""
                await self.bot.db.execute(query, ctx.author.id, False, 0, [], [user.id])

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(
        name="unblock",
        description="Unblock a user or channel",
        usage="<user or channel>",
    )
    async def unblock(
        self, ctx, *, user: typing.Union[UserConverter, discord.TextChannel]
    ):
        query = """SELECT *
				   FROM settings
				   WHERE settings.user_id=$1;
				"""
        settings = await self.bot.db.fetchrow(query, ctx.author.id)

        if isinstance(user, discord.User) or isinstance(user, discord.Member):

            if settings:
                if user.id not in settings["blocked_users"]:
                    await ctx.send(":x: This user is not blocked")
                else:
                    settings["blocked_users"].remove(user.id)
                    query = """UPDATE settings
							   SET blocked_users=$1
							   WHERE settings.user_id=$2;
							"""
                    await self.bot.db.execute(
                        query, settings["blocked_users"], ctx.author.id
                    )
                    await ctx.send(
                        f":white_check_mark: Unblocked `{user.display_name}`"
                    )
            else:
                await ctx.send(":x: This user is not blocked")

        else:

            if settings:
                if user.id not in settings["blocked_channels"]:
                    await ctx.send(":x: This channel is not blocked")
                else:
                    settings["blocked_channels"].remove(user.id)
                    query = """UPDATE settings
							   SET blocked_channels=$1
							   WHERE settings.user_id=$2;
							"""
                    await self.bot.db.execute(
                        query, settings["blocked_channels"], ctx.author.id
                    )
                    await ctx.send(f":white_check_mark: Unblocked {user.mention}")
            else:
                await ctx.send(":x: This channel is not blocked")

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.group(
        name="blocked",
        description="View your blocked list",
        invoke_without_command=True,
    )
    async def blocked(self, ctx):
        query = """SELECT *
				   FROM settings
				   WHERE settings.user_id=$1;
				"""
        settings = await self.bot.db.fetchrow(query, ctx.author.id)

        if not settings or (
            not settings["blocked_channels"] and not settings["blocked_users"]
        ):
            await ctx.send(":x: You have no channnels or users blocked")
        else:
            em = discord.Embed(color=discord.Color.blurple())
            em.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

            users = []
            for user_id in settings["blocked_users"]:
                user = await self.bot.fetch_user(user_id)
                if user:
                    users.append(user.mention)

            if users:
                em.add_field(name="Blocked Users", value="\n".join(users))

            channels = []
            for channel_id in settings["blocked_channels"]:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    channels.append(channel.mention)

            if channels:
                em.add_field(name="Blocked Channels", value="\n".join(channels))

            await ctx.send(embed=em)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @blocked.command(name="clear", description="Clear your blocked list")
    async def blocked_clear(self, ctx):
        query = """UPDATE settings
				   SET blocked_users=$1, blocked_channels=$2
				   WHERE settings.user_id=$3;
				"""
        await self.bot.db.execute(query, [], [], ctx.author.id)

        await ctx.send(f":white_check_mark: Your blocked list has been cleared")

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name="enable", description="Enable highlight")
    async def enable(self, ctx):
        await self.bot.get_cog("Timers").cancel_timer(ctx.author.id, "disable")

        query = """INSERT INTO settings (user_id, disabled, timezone, blocked_users, blocked_channels)
				   VALUES ($1, $2, $3, $4, $5)
				   ON CONFLICT (user_id)
				   DO UPDATE SET disabled=$2;
				"""
        await self.bot.db.execute(query, ctx.author.id, False, 0, [], [])

        await ctx.send(":white_check_mark: Highlight has been enabled")

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name="disable", description="Disable highlight", aliases=["dnd"])
    async def disable(self, ctx, *, time: TimeConverter = None):
        await self.bot.get_cog("Timers").cancel_timer(ctx.author.id, "disable")

        query = """INSERT INTO settings (user_id, disabled, timezone, blocked_users, blocked_channels)
				   VALUES ($1, $2, $3, $4, $5)
				   ON CONFLICT (user_id)
				   DO UPDATE SET disabled=$2;
				"""
        await self.bot.db.execute(query, ctx.author.id, True, 0, [], [])

        if time:
            await self.bot.get_cog("Timers").create_timer(
                ctx.author.id, "disabled", time, {}
            )

        await ctx.send(
            f":white_check_mark: Highlight has been disabled {f'`for {humanize.naturaldelta(time-datetime.datetime.utcnow())}`' if time else ''}"
        )

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name="timezone", description="Set your timezone")
    async def timezone(self, ctx, timezone: int = None):
        if timezone:
            query = """INSERT INTO settings (user_id, disabled, timezone, blocked_users, blocked_channels)
					   VALUES ($1, $2, $3, $4, $5)
					   ON CONFLICT (user_id)
					   DO UPDATE SET timezone=$3;
					"""

            await self.bot.db.execute(query, ctx.author.id, False, timezone, [], [])
            await ctx.send(f":white_check_mark: Timezone set to `{timezone}`")

        else:
            query = """SELECT *
					   FROM settings
					   WHERE settings.user_id=$1;
					"""
            settings = await self.bot.db.fetchrow(query, ctx.author.id)
            if settings:
                await ctx.send(f"Your current timezone is `{settings['timezone']}`")
            else:
                await ctx.send(f"Your current timezone is `{0}`")

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_disabled_complete(self, timer):
        query = """INSERT INTO settings (user_id, disabled, timezone)
				   VALUES ($1, $2, $3)
				   ON CONFLICT (user_id)
				   DO UPDATE SET disabled=$2;
				"""
        await self.bot.db.execute(query, timer["user_id"], False, 0)

    async def bulk_insert(self):
        query = """INSERT INTO highlights (guild_id, channel_id, message_id, author_id, user_id, word, invoked_at)
				   SELECT x.guild_id, x.channel_id, x.message_id, x.author_id, x.user_id, x.word, x.invoked_at
				   FROM jsonb_to_recordset($1::jsonb) AS
				   x(guild_id BIGINT, channel_id BIGINT, message_id BIGINT, author_id BIGINT, user_id BIGINT, word TEXT, invoked_at TEXT)
				"""
        if self._highlight_batch:
            await self.bot.db.execute(query, self._highlight_batch)
            total = len(self._highlight_batch)
            self._highlight_batch.clear()

    @tasks.loop(seconds=20)
    async def bulk_insert_loop(self):
        async with self._batch_lock:
            await self.bulk_insert()

    @bulk_insert_loop.before_loop
    async def before_bulk_insert_loop(self):
        log.info("Waiting to start bulk insert loop")
        await self.bot.wait_until_ready()
        log.info("Starting bulk insert loop")


def setup(bot):
    bot.add_cog(Highlight(bot))
