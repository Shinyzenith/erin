import asyncio
import logging
import math
import os
import threading
import uuid
import coloredlogs
import numpy

from discord.ext import commands
import discord

from PIL import Image as PILImage
from io import BytesIO
from PIL import ImageFont, ImageEnhance, ImageDraw, ImageOps

log = logging.getLogger("image cog")
coloredlogs.install(logger=log)


# Finds the most recent image in the channel, maximum of 100 images.
async def get_image_async(ctx):
    async for message in ctx.channel.history(limit=100):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type != "image/jpeg" and attachment.content_type != "image/png":  # it must be an image
                    pass
                return PILImage.open(BytesIO(await attachment.read()))
    return None;

def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = numpy.matrix(matrix, dtype=numpy.float)
    B = numpy.array(pb).reshape(8)

    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)

# Asynchronous function is called by a synchronous function running in a thread.
def async_handler(func, ctx, args):
    asyncio.create_task(func(ctx, args))


async def bottomtext(ctx, args):
    # keep these the same for all functions\
    text = args[0]
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    tempString = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        draw = ImageDraw.Draw(image)
        font_size = math.ceil(image.width / 10)

        font = ImageFont.truetype("../assets/impact.ttf", font_size, encoding='unic')
        w, h = font.getsize(text)
        while w > (0.9 * width):
            font_size -= 1;
            font = ImageFont.truetype("../assets/impact.ttf", font_size, encoding='unic')
            w, h = font.getsize(text)
        border = math.floor(font_size / 15);

        x = (width - w) / 2
        y = height - (1.25 * font_size)

        # draw a border
        draw.text((x - border, y - border), text, font=font, fill="black")
        draw.text((x + border, y - border), text, font=font, fill="black")
        draw.text((x - border, y + border), text, font=font, fill="black")
        draw.text((x + border, y + border), text, font=font, fill="black")
        # draw the inside
        draw.text((x, y), text, font=font, fill="white")
        # this stuff should stay the same
        image.save(tempString)
        await ctx.message.reply(file=discord.File(tempString))
    except:
        return await ctx.send("An error occurred processing this image. ")
    finally:
        os.remove(tempString)
async def toptext(ctx, args):
    # keep these the same for all functions\
    text = args[0]
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    tempString = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        draw = ImageDraw.Draw(image)
        font_size = math.ceil(image.width / 10)

        font = ImageFont.truetype("../assets/impact.ttf", font_size, encoding='unic')
        w, h = font.getsize(text)
        while w > (0.9 * width):
            font_size -= 1;
            font = ImageFont.truetype("../assets/impact.ttf", font_size, encoding='unic')
            w, h = font.getsize(text)
        border = math.floor(font_size / 15);

        x = (width - w) / 2
        y = (0.25 * font_size)

        # draw a border
        draw.text((x - border, y - border), text, font=font, fill="black")
        draw.text((x + border, y - border), text, font=font, fill="black")
        draw.text((x - border, y + border), text, font=font, fill="black")
        draw.text((x + border, y + border), text, font=font, fill="black")
        # draw the inside
        draw.text((x, y), text, font=font, fill="white")
        # this stuff should stay the same
        image.save(tempString)
        await ctx.message.reply(file=discord.File(tempString))
    except:
        return await ctx.send("An error occurred processing this image. ")
    finally:
        os.remove(tempString)
async def rotate(ctx, args):
    degrees = args[0]
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    tempString = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        image = image.rotate(int(degrees), expand=1)
        image.save(tempString)
        await ctx.message.reply(file=discord.File(tempString))
    except:
        return await ctx.send("An error occurred processing this image. ")
    finally:
        os.remove(tempString)
async def scott(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    tempString = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        coeffs = find_coeffs(
            [(448, 631), (1800, 618), (1798, 1630), (461, 1445)],
            [(0, 0), (width, 0), (width, height), (0, height)]
           )
        image = image.transform((3000, 1583), PILImage.PERSPECTIVE, coeffs,
                      PILImage.BICUBIC)
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../assets/scott.png"
        abs_file_path = os.path.join(script_dir, rel_path)
        scottimage = PILImage.open(abs_file_path)
        scottimage.paste(image, (0,0), image)

        scottimage.save(tempString)
        await ctx.message.reply(file=discord.File(tempString))
    except Exception:
        return await ctx.send("An error occurred processing this image. ")
    finally:
        os.remove(tempString)
async def biden(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    tempString = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        coeffs = find_coeffs(
            [(790, 859), (2427, 849), (2453, 1505), (789, 1513)],
            [(0, 0), (width, 0), (width, height), (0, height)]
           )
        image.putalpha(245)
        image = image.transform((2500, 1517), PILImage.PERSPECTIVE, coeffs,
                      PILImage.BICUBIC)

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../assets/biden.jpg"
        abs_file_path = os.path.join(script_dir, rel_path)
        bidenimage = PILImage.open(abs_file_path)
        bidenimage.paste(image, (0,0), image)

        bidenimage.save(tempString)
        await ctx.message.reply(file=discord.File(tempString))
    except Exception:
        return await ctx.send("An error occurred processing this image. ")
    finally:
        os.remove(tempString)

async def deepfry(ctx, args):
    colours = ((254, 0, 2), (255, 255, 15))
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    tempString = uuid.uuid4().__str__() + ".png"

    try:

        # Crush image to hell and back
        image = image.convert('RGB')
        width, height = image.width, image.height
        image = image.resize((int(width ** .75), int(height ** .75)), resample=PILImage.LANCZOS)
        image = image.resize((int(width ** .88), int(height ** .88)), resample=PILImage.BILINEAR)
        image = image.resize((int(width ** .9), int(height ** .9)), resample=PILImage.BICUBIC)
        image = image.resize((width, height), resample=PILImage.BICUBIC)
        image = ImageOps.posterize(image, 4)

        # Generate colour overlay
        r = image.split()[0]
        r = ImageEnhance.Contrast(r).enhance(2.0)
        r = ImageEnhance.Brightness(r).enhance(1.5)

        r = ImageOps.colorize(r, colours[0], colours[1])

        # Overlay red and yellow onto main image and sharpen the hell out of it
        image = PILImage.blend(image, r, 0.75)
        image = ImageEnhance.Sharpness(image).enhance(100.0)

        image.save(tempString)
        await ctx.message.reply(file=discord.File(tempString))
    except Exception:
        return await ctx.send("An error occurred processing this image. ")
    finally:
        os.remove(tempString)

class Image(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(aliases=["meme"], name="bottomtext", description="add bottom meme text to an image")
    async def bottomtext(self, ctx, *, text: str):
        th = threading.Thread(target=async_handler(bottomtext, ctx, [text]))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="toptext", description="add top meme text to an image")
    async def toptext(self, ctx, *, text: str):
        th = threading.Thread(target=async_handler(toptext, ctx, [text]))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="rotate", description="rotate an image")
    async def rotate(self, ctx, *, degrees):
        th = threading.Thread(target=async_handler(rotate, ctx, [degrees]))
        th.start()
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="scott", description="scott the woz will show your image on his tv")
    async def scott(self, ctx):
        th = threading.Thread(target=async_handler(scott, ctx, []))
        th.start()
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="biden", description="biden gives a rally about your image")
    async def biden(self, ctx):
        th = threading.Thread(target=async_handler(biden, ctx, []))
        th.start()
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="deepfry", description="deep fries an image")
    async def deepfry(self, ctx):
        th = threading.Thread(target=async_handler(deepfry, ctx, []))
        th.start()
# setup function so this can be loaded as an extension
def setup(bot: commands.Bot):
    bot.add_cog(Image(bot))
