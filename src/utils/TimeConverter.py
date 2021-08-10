import re
from discord.ext import commands
time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        if round(time) == 0:
            raise commands.BadArgument(
                f"Please enter a valid time format, eg: {ctx.prefix}mute @user 1d2h3m4s ---> denoting mute @user for 1 day, 2 hour, 3 minutes and 4 seconds."
            )
        else:
            return round(time)

