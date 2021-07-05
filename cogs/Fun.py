import yaml
import re
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

class SaidNoError(Exception):
    pass

def commands_check():
    async def predicate(ctx):
        return ctx.message.channel.id == 555581400414289935 or ctx.message.author.id == 207129652345438211
    return commands.check(predicate)

class Fun(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['spooky']['brief'], usage=helpInfo['spooky']['usage'])
    @commands_check()
    async def spooky(self, ctx):
        user = ctx.message.author
        nickname = user.display_name
        newNick = f"👻🎃{nickname}🎃👻"
        if len(newNick) > 32:
            spookyEm = discord.Embed(title="That's a long name you got there....",
                                      description = "Your nickname is too long! Discord won't let me make you spooky.\nChange your nickname and try again",
                                    colour=0xeb6123)  
            spookyEm.set_footer(text="Tommy © 2020 x2110311x", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=spookyEm)
        else:
            if nickname.find("👻") != -1 and nickname.find("🎃") != -1:
                def check(m):
                    if m.author == user and m.channel == ctx.message.channel:
                        if m.content.lower() == "no":
                            raise SaidNoError()
                        elif m.content.lower() == "yes":
                            return True
                        else:
                            return False
                    else:
                        return False
                spookyEm = discord.Embed(title="Aaah! You already look pretty spooky.",
                                        description = "Are you sure you want to become spookier?", colour=0xeb6123)  
                spookyEm.set_footer(text="Tommy © 2020 x2110311x", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=spookyEm)
                try:
                    await self.bot.wait_for('message', check=check, timeout=30)
                    try:
                        await user.edit(nick=newNick,reason="IT'S SPOOKY TIME")
                        spookyEm = discord.Embed(title="Boo!",
                                            description = f"You're lookin' pretty spooky there, {nickname}", colour=0xeb6123)  
                        spookyEm.set_footer(text="Tommy © 2020 x2110311x", icon_url=self.bot.user.avatar_url)
                        spookyEm.set_author(name=newNick, icon_url=user.avatar_url)
                        await ctx.send(embed=spookyEm)
                    except Exception as e:
                        spookyEm = discord.Embed(title="Uh oh!",
                                            description = "I wasn't able to update your nickname!\nCopy the nickname above and set it manually", colour=0xeb6123)  
                        spookyEm.set_footer(text="Tommy © 2020 x2110311x", icon_url=self.bot.user.avatar_url)
                        spookyEm.set_author(name=newNick, icon_url=user.avatar_url)
                        await ctx.send(embed=spookyEm)
                        chanTest = self.bot.get_channel(config['testing_Channel'])
                        await chanTest.send(f"Error spookifing {user.mention}\n{e}")
                except SaidNoError:
                    spookyEm = discord.Embed(title="That's fine.",
                                        description = "You can always do it later by running the command again", colour=0xeb6123)  
                    spookyEm.set_footer(text="Tommy © 2020 x2110311x", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=spookyEm)
                except asyncio.TimeoutError:
                    spookyEm = discord.Embed(title="Did I scare you away?",
                                        description = "I didn't get a valid answer from you.\nYou can always do it later by running the command again",
                                        colour=0xeb6123)  
                    spookyEm.set_footer(text="Tommy © 2020 x2110311x", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=spookyEm)
            else:
                try:
                    await user.edit(nick=newNick,reason="IT'S SPOOKY TIME")
                    spookyEm = discord.Embed(title="Boo!",
                                        description = f"You're lookin' pretty spooky there, {nickname}", colour=0xeb6123)  
                    spookyEm.set_footer(text="Tommy © 2020 x2110311x", icon_url=self.bot.user.avatar_url)
                    spookyEm.set_author(name=newNick, icon_url=user.avatar_url)
                    await ctx.send(embed=spookyEm)
                except Exception as e:
                    spookyEm = discord.Embed(title="Uh oh!",
                                        description = "I wasn't able to update your nickname!\nCopy the nickname above and set it manually", colour=0xeb6123)  
                    spookyEm.set_footer(text="Tommy © 2020 x2110311x", icon_url=self.bot.user.avatar_url)
                    spookyEm.set_author(name=newNick, icon_url=user.avatar_url)
                    await ctx.send(embed=spookyEm)
                    chanTest = self.bot.get_channel(config['testing_Channel'])
                    await chanTest.send(f"Error spookifing {user.mention}\n{e}")

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
    async def avatar(self, ctx, *, user: discord.User = None):
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 858508465151672350:
            if len(message.attachments) > 0:
                guild = message.channel.guild
                emote = await guild.fetch_emoji(794636237973487666)
                await message.add_reaction(emote)

    @commands.check
    async def globally_block_dms(self, ctx):
        return ctx.guild is not None


def setup(bot):
    bot.add_cog(Fun(bot))
