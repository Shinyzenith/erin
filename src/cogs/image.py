# boilerplate dependencies
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
                image = PILImage.open(BytesIO(await attachment.read()))
                return image.convert("RGBA")  # this is important for working with transparency and stuff.
    return None


# idk what it does, just pass the destination coordinates and source coordinates and use it to skew transform
def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])

    A = numpy.matrix(matrix, dtype=numpy.float)
    B = numpy.array(pb).reshape(8)

    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)


# Asynchronous function is called by a synchronous function running in a thread.
def async_handler(func, ctx, args):
    asyncio.create_task(func(ctx, args))


# text
async def bottomtext(ctx, args):
    # keep these the same for all functions\
    text = args[0]
    image = await get_image_async(ctx)
    if image is None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        draw = ImageDraw.Draw(image)
        font_size = math.ceil(image.width / 10)

        font = ImageFont.truetype("../assets/impact.ttf", font_size, encoding='unic')
        w, h = font.getsize(text)
        while w > (0.9 * width):
            font_size -= 1
            font = ImageFont.truetype("../assets/impact.ttf", font_size, encoding='unic')
            w, h = font.getsize(text)
        border = math.floor(font_size / 15)

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
        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def toptext(ctx, args):
    # keep these the same for all functions\
    text = args[0]
    image = await get_image_async(ctx)
    if image is None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        draw = ImageDraw.Draw(image)
        font_size = math.ceil(image.width / 10)

        font = ImageFont.truetype("../assets/impact.ttf", font_size, encoding='unic')
        w, h = font.getsize(text)
        while w > (0.9 * width):
            font_size -= 1
            font = ImageFont.truetype("../assets/impact.ttf", font_size, encoding='unic')
            w, h = font.getsize(text)
        border = math.floor(font_size / 15)

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
        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def motivational(ctx, args):
    # keep these the same for all functions
    text = args[0]
    image = await get_image_async(ctx)
    if image is None:
        return await ctx.send("Can't find any images in this channel. ")

    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        imwidth, imheight = image.size
        margin = int(imheight * 0.10)
        padding = int(margin * 0.3)
        background = PILImage.new("RGB", (imwidth + margin * 2, imheight + 4 * margin), (0, 0, 0))
        width, height = background.size
        draw = ImageDraw.Draw(background)

        font_size = math.ceil(width / 10)
        font = ImageFont.truetype("../assets/times.ttf", font_size, encoding='unic')
        w, h = font.getsize(text)
        while w > (0.9 * width):
            font_size -= 1
            font = ImageFont.truetype("../assets/times.ttf", font_size, encoding='unic')
            w, h = font.getsize(text)

        x = (width - w) / 2
        y = height - margin * 3 + padding * 2

        draw.rectangle((margin - padding, margin - padding, width - margin + padding, height + padding - margin * 3),
                       fill=None, outline="white", width=int(imwidth / 200))
        background.paste(image, (margin, margin))
        # draw the inside
        draw.text((x, y), text, font=font, fill="white")
        background.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        os.remove(temp_string)
# colors and rotation/reflection
async def reflectR(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        image2 = image.crop((int(width / 2), 0, width, height))
        image2 = image2.transpose(PILImage.FLIP_LEFT_RIGHT)
        image.paste(image2, (0, 0))
        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def reflectL(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different

        image2 = image.crop((0, 0, int(width / 2), height))
        image2 = image2.transpose(PILImage.FLIP_LEFT_RIGHT)
        image.paste(image2, (int(width / 2), 0))
        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def colors(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        image = image.convert(mode='P', colors=int(args[0]))
        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def mirror(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        image = image.transpose(PILImage.FLIP_LEFT_RIGHT)
        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def rotate(ctx, args):
    degrees = args[0]
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        image = image.rotate(int(degrees), expand=1)
        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def deepfry(ctx, args):
    colours = ((254, 0, 2), (255, 255, 15))
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

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

        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def bluefry(ctx, args):
    colours = ((2, 0, 255), (0, 255, 255))
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

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

        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def bits(ctx, args):
    bits = args[0]
    # keep these the same for all functions
    image = await get_image_async(ctx)
    if image == None:
        return await ctx.send("Can't find any images in this channel. ")
    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:

        # Resize smoothly down to bits
        imgSmall = image.resize((int(bits), int(bits)), resample=PILImage.BILINEAR)

        # Scale back up using NEAREST to original size
        image = imgSmall.resize(image.size, PILImage.NEAREST)

        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass


# photoshop-type stuff
async def scott(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)

    if image == None:
        return await ctx.send("Can't find any images in this channel. ")

    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

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
        scottimage.convert("RGBA")
        scottimage.paste(image, (0, 0), image)

        scottimage.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def nintendodirect(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)

    if image == None:
        return await ctx.send("Can't find any images in this channel. ")

    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        coeffs = find_coeffs(
            [(228, 121), (1122, 121), (1024, 596), (133, 596)],
            [(0, 0), (width, 0), (width, height), (0, height)]
        )
        image = image.transform((1280, 720), PILImage.PERSPECTIVE, coeffs,
                                PILImage.BICUBIC)
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../assets/nintendodirect.jpg"
        abs_file_path = os.path.join(script_dir, rel_path)
        ninimage = PILImage.open(abs_file_path)
        ninimage.convert("RGBA")
        ninimage.paste(image, (0, 0), image)

        ninimage.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def linustechtips(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)

    if image == None:
        return await ctx.send("Can't find any images in this channel. ")

    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:
        # this stuff can be different
        coeffs = find_coeffs(
            [(495, 177), (1752, 183), (1760, 842), (522, 909)],
            [(0, 0), (width, 0), (width, height), (0, height)]
        )
        image = image.transform((2400, 1800), PILImage.PERSPECTIVE, coeffs,
                                PILImage.BICUBIC)
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../assets/linus.jpg"
        abs_file_path = os.path.join(script_dir, rel_path)
        linusimage = PILImage.open(abs_file_path)
        linusimage.convert("RGBA")
        linusimage.paste(image, (0, 0), image)

        linusimage.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def mattiasgrief(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)

    if image == None:
        return await ctx.send("Can't find any images in this channel. ")

    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../assets/mattiasgrief.png"
        abs_file_path = os.path.join(script_dir, rel_path)
        matimage = PILImage.open(abs_file_path)
        width_b, height_b = matimage.size
        new_width = int(width_b * (height / height_b))
        matimage = matimage.resize((new_width, height), PILImage.BILINEAR)
        width_b, height_b = matimage.size
        matimage.convert("RGBA")
        image.paste(matimage, (width - width_b, 0), matimage)

        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def daviegun(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)

    if image == None:
        return await ctx.send("Can't find any images in this channel. ")

    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../assets/daviegun.png"
        abs_file_path = os.path.join(script_dir, rel_path)
        davie = PILImage.open(abs_file_path)
        width_b, height_b = davie.size
        new_width = int(width_b * (height / height_b))
        davie = davie.resize((new_width, height), PILImage.BILINEAR)
        width_b, height_b = davie.size
        davie.convert("RGBA")
        image.paste(davie, (0, 0), davie)

        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
async def daviesad(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)

    if image == None:
        return await ctx.send("Can't find any images in this channel. ")

    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../assets/daviesad.png"
        abs_file_path = os.path.join(script_dir, rel_path)
        davie = PILImage.open(abs_file_path)
        width_b, height_b = davie.size
        new_width = int(width_b * (height / height_b))
        davie = davie.resize((new_width, height), PILImage.BILINEAR)
        width_b, height_b = davie.size
        davie.convert("RGBA")
        image.paste(davie, (0, 0), davie)

        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass

async def daviesad(ctx, args):
    # keep these the same for all functions
    image = await get_image_async(ctx)

    if image == None:
        return await ctx.send("Can't find any images in this channel. ")

    width, height = image.size
    temp_string = uuid.uuid4().__str__() + ".png"

    try:

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../assets/emil.png"
        abs_file_path = os.path.join(script_dir, rel_path)
        davie = PILImage.open(abs_file_path)
        width_b, height_b = davie.size
        new_width = int(width_b * (height / height_b))
        davie = davie.resize((new_width, height), PILImage.BILINEAR)
        width_b, height_b = davie.size
        davie.convert("RGBA")
        image.paste(davie, (0, 0), davie)

        image.save(temp_string)
        await ctx.message.reply(file=discord.File(temp_string))
    except Exception:
        await ctx.send("An error occurred processing this image. ")
    finally:
        try:
            os.remove(temp_string)
        except:
            pass
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
    @commands.command(name="motivational", description="Makes a motivational type meme of an image")
    async def motivational(self, ctx, *, text: str):
        th = threading.Thread(target=async_handler(motivational, ctx, [text]))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="colors", description="reduces the number of colors in an image. options are: 16, 256")
    async def colors(self, ctx, *, num_colors: str):
        th = threading.Thread(target=async_handler(colors, ctx, [num_colors]))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="rotate", description="rotate an image")
    async def rotate(self, ctx, *, degrees):
        th = threading.Thread(target=async_handler(rotate, ctx, [degrees]))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="rmirror",
                      description="replaces the left half of the image with a mirror image of the right half")
    async def rflip(self, ctx):
        th = threading.Thread(target=async_handler(reflectR, ctx, []))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="lmirror",
                      description="replaces the right half of the image with a mirror image of the left half")
    async def lflip(self, ctx):
        th = threading.Thread(target=async_handler(reflectL, ctx, []))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="flip", description="flips the image horizontally")
    async def flip(self, ctx):
        th = threading.Thread(target=async_handler(mirror, ctx, []))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="deepfry", description="deep-fries an image")
    async def deepfry(self, ctx):
        th = threading.Thread(target=async_handler(deepfry, ctx, []))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="bluefry", description="deep-fries an image, but it's blue")
    async def bluefry(self, ctx):
        th = threading.Thread(target=async_handler(bluefry, ctx, []))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="bits", description="reduces the bits of an image")
    async def bits(self, ctx, num_bits):
        th = threading.Thread(target=async_handler(bits, ctx, [num_bits]))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="scott", description="Scott the Woz leans on a tv with your image")
    async def scott(self, ctx):
        th = threading.Thread(target=async_handler(scott, ctx, []))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="nintendo", description="Nintendo Direct features your image")
    async def nintendo(self, ctx):
        th = threading.Thread(target=async_handler(nintendodirect, ctx, []))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="linus", description="Linus Tech Tips looks at your image")
    async def linus(self, ctx):
        th = threading.Thread(target=async_handler(linustechtips, ctx, []))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="daviegun", description="Davie504 is very friendly with your image in the background")
    async def daviegun(self, ctx):
        th = threading.Thread(target=async_handler(daviegun, ctx, []))
        th.start()

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.command(name="daviesad", description="Davie504 is sad.")
    async def daviesad(self, ctx):
        th = threading.Thread(target=async_handler(daviesad, ctx, []))
        th.start()

# setup function so this
# setup function so this can be loaded as an extension
def setup(bot: commands.Bot):
    bot.add_cog(Image(bot))
