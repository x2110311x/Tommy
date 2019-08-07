import yaml
from discord.ext import commands
from random import randint
from include import txtutils
from include import utilities
from os.path import abspath

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
    async def avater(self, ctx, *, user: discord.Member):
        embedAvatar = discord.Embed(title=f"{user.name}'s avatar",colour=0x753543)
        embedAvatar.set_image(url=user.avatar_url)
        await ctx.send(embed=embedAvatar)

    @commands.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None


def setup(bot):
    bot.add_cog(Fun(bot))
