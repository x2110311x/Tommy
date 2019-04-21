import yaml
from discord.ext import commands
from random import randint
from include import txtutils
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


def setup(bot):
    bot.add_cog(Fun(bot))
