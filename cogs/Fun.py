import yaml
import discord
import io
from discord.ext import commands
from random import randint
from include import txtutils
from include import utilities
from os.path import abspath
from PIL import Image
from colory.color import Color as xColor


with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['Fun']


class Fun(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['rate']['brief'], usage=helpInfo['rate']['usage'])
    async def rate(self, ctx, *, object):
        await ctx.send(f"I would rate {object} **{randint(0,10)} out of 10**")

    @commands.command(brief=helpInfo['magic8ball']['brief'], usage=helpInfo['magic8ball']['usage'])
    async def magic8ball(self, ctx):
        await ctx.send(txtutils.magic8ball())

    @commands.command(brief=helpInfo['yt']['brief'], usage=helpInfo['yt']['usage'])
    async def yt(self, ctx, *, query):
        msgSearch = await ctx.send(F"Searching for `{query}` ")
        await msgSearch.edit(content=utilities.ytsearch(query))

    @commands.command(brief=helpInfo['avatar']['brief'], usage=helpInfo['avatar']['usage'])
    async def avatar(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        embedAvatar = discord.Embed(title=f"{user.name}'s avatar", colour=0x753543)
        embedAvatar.set_image(url=user.avatar_url)
        await ctx.send(embed=embedAvatar)
        
    @commands.command(brief=helpInfo['color']['brief'], usage=helpInfo['color']['usage'], aliases=["colour"])
    async def color(self, ctx, hexcode):
        try:
            if hexcode[0] == "#":
                hexint = int(hexcode[1:], 16)
            else:
                hexint = int(hexcode, 16)
        except ValueError:
            await ctx.send("That's not a valid color code!")
            return
        if hexcode[0] != "#":
            hexcode = f"#{hexcode}"
        if len(hexcode) != 7:
            await ctx.send("That's not a valid color code!")
            return
        colorObj = xColor(hexcode,'wiki')
        colorName = colorObj.name
        colorImage = Image.new("RGB", (100,100), hexcode)
        imgByteArr = io.BytesIO()
        colorImage.save(imgByteArr, format="PNG")
        imgByteArr.seek(0)
        imgFile = discord.File(fp=imgByteArr, filename="color.png")
        colorEm = discord.Embed(title=hexcode, colour=hexint)
        colorEm.set_image(url="attachment://color.png")
        colorEm.set_author(name=colorName)
        await ctx.send(file=imgFile, embed=colorEm)

    @commands.check
    async def globally_block_dms(self, ctx):
        return ctx.guild is not None


def setup(bot):
    bot.add_cog(Fun(bot))
