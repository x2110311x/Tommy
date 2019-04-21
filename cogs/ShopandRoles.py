import asyncio
import sqlite3
import yaml

from discord.ext import commands
from include import txtutils
from os.path import abspath

with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['ShopandRoles']

DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()


class SaidNoError(Exception):
    pass


class ShopandRoles(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['pingon']['brief'], usage=helpInfo['pingon']['usage'])
    async def pingon(self, ctx):
        user = ctx.message.author

        def check(m):
            if m.author == user and m.channel == user.dm_channel:
                if m.content.lower() == 'yes':
                    return True
                elif m.content.lower() == 'no':
                    raise SaidNoError
                else:
                    return False
            else:
                return False

        await ctx.send("Check your DMs for more info")

        roleList = []
        for role in config['pingable_Roles']:
            roleList.append(ctx.message.guild.get_role(role))

        try:
            for role in roleList:
                await user.send(f"Do you want the {role.name} role?")
                try:
                    await self.bot.wait_for('message', check=check, timeout=30)
                    await ctx.message.author.add_roles(role)
                except SaidNoError:
                    pass
            await user.send("Roles added! All done!")
        except asyncio.TimeoutError:
            await user.send("Timeout reached. Try again later!")

    @commands.command(brief=helpInfo['pingoff']['brief'], usage=helpInfo['pingoff']['usage'])
    async def pingoff(self, ctx):
        user = ctx.message.author

        def check(m):
            if m.author == user and m.channel == user.dm_channel:
                if m.content.lower() == 'yes':
                    return True
                elif m.content.lower() == 'no':
                    raise SaidNoError
                else:
                    return False
            else:
                return False

        await ctx.send("Check your DMs for more info")

        roleList = []
        for role in config['pingable_Roles']:
            roleList.append(ctx.message.guild.get_role(role))

        try:
            for role in roleList:
                await user.send(f"Do you want to remove the {role.name} role?")
                try:
                    await self.bot.wait_for('message', check=check, timeout=30)
                    await ctx.message.author.remove_roles(role)
                except SaidNoError:
                    pass
            await user.send("Roles Removed! All done!")
        except asyncio.TimeoutError:
            await user.send("Timeout reached. Try again later!")


def setup(bot):
    bot.add_cog(ShopandRoles(bot))


def teardown(bot):
    DB.close()
