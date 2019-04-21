import discord
import sqlite3
import time
import yaml

from datetime import datetime
from discord.ext import commands
from os.path import abspath

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['Staff']

# Database connections #
DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()


class Staff(commands.Cog, name="Staff Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['say']['brief'], usage=helpInfo['say']['usage'])
    @commands.has_role(config['staff_Role'])
    async def say(self, ctx, *, textToSay):
        try:
            channel = ctx.message.channel_mentions[0]
            txtindex = ctx.message.content.find('>') + 1
            textToSay = ctx.message.content[txtindex:]
        except IndexError:
            channel = ctx.channel
        await channel.send(textToSay)

    @commands.command(brief=helpInfo['kick']['brief'], usage=helpInfo['kick']['usage'])
    @commands.has_role(config['staff_Role'])
    async def kick(self, ctx, user: discord.Member):
        staffRole = self.bot.get_guild(
            config['server_ID']).get_role(config['staff_Role'])
        if staffRole not in user.roles:
            await user.kick(reason=ctx.author.name)
            await ctx.send(f"{user.mention} has been kicked!")
        else:
            await ctx.send("You cannot kick another staff member!")

    @commands.command(brief=helpInfo['ban']['brief'], usage=helpInfo['ban']['usage'])
    @commands.has_role(config['staff_Role'])
    async def ban(self, ctx, user: discord.Member):
        staffRole = self.bot.get_guild(
            config['server_ID']).get_role(config['staff_Role'])
        if staffRole not in user.roles:
            await user.ban(reason=ctx.author.name)
            await ctx.send(f"{user.mention} has been banned!")
        else:
            await ctx.send("You cannot ban another staff member!")

    @commands.command(brief=helpInfo['mute']['brief'], usage=helpInfo['mute']['usage'])
    @commands.has_role(config['staff_Role'])
    async def mute(self, ctx, user: discord.Member, mutetime=5):
        guild = self.bot.get_guild(config['server_ID'])
        muteRole = guild.get_role(config['mute_Role'])
        defaultRole = guild.get_role(config['join_Role'])
        staffRole = guild.get_role(config['staff_Role'])
        if staffRole not in user.roles:
            try:
                timeToMute = int(mutetime) * 60 + int(time.time())
            except ValueError:
                await ctx.send("Please use integers")

            try:
                muteInsert = f"INSERT INTO Mutes (User, UnmuteTime) VALUES ({user.id}, {timeToMute})"
                DB.execute(muteInsert)
                DBConn.commit()
                await user.remove_roles(defaultRole)
                await user.add_roles(muteRole)
                await user.send(f"You have been muted for `{mutetime} minutes`")
                await ctx.send("User has been muted")
            except Exception as e:
                await ctx.send("Unable to mute user")
                print(e)
        else:
            await ctx.send("You cannot mute another staff member!")

    @commands.command(brief=helpInfo['warn']['brief'], usage=helpInfo['warn']['usage'])
    @commands.has_role(config['staff_Role'])
    async def warn(ctx, user: discord.Member, *, reason):
        try:
            warnInsert = "INSERT INTO Warnings (User, Reason, Date, WarnedBy) VALUES (?,?,?,?)"
            DB.execute(warnInsert, (user.id, reason,
                                    int(time.time()), ctx.author.id))
            DBConn.commit()
            await user.send(f"You have been warned for `{reason}`")
            await ctx.send("User has been warned")
        except Exception as e:
            await ctx.send("Unable to warn user")
            print(e)

    @commands.command(brief=helpInfo['unmute']['brief'], usage=helpInfo['unmute']['usage'])
    @commands.has_role(config['staff_Role'])
    async def unmute(self, ctx, user: discord.Member = None):
        guild = self.bot.get_guild(config['server_ID'])
        muteRole = guild.get_role(config['mute_Role'])
        defaultRole = guild.get_role(config['join_Role'])
        if muteRole in user.roles:
            await user.remove_roles(muteRole)
            await user.add_roles(defaultRole)
            await user.send("You have been unmuted")
            await ctx.send("User has been unmuted")
            deleteMute = f"DELETE FROM Mutes WHERE User = {user.id}"
            DB.execute(deleteMute)
            DBConn.commit()

    @commands.command(brief=helpInfo['chkwarn']['brief'], usage=helpInfo['chkwarn']['usage'])
    @commands.has_role(config['staff_Role'])
    async def chkwarn(self, ctx, user: discord.Member):
        selectWarn = f"SELECT reason, date FROM Warnings WHERE User={user.id}"
        DB.execute(selectWarn)
        warns = DB.fetchall()
        print(warns)

        embedWarn = discord.Embed(colour=0x753543)
        embedWarn.set_author(name=user.name, icon_url=user.avatar_url)
        if warns is None:
            embedWarn.add_field(name="User has no warns", inline=True)
            embedWarn.set_footer(text="# of warns: 0")
        else:
            warnCount = len(warns)
            embedWarn.set_footer(text=f"# of warns: {warnCount}")
            for x in range(0, warnCount):
                date = datetime.fromtimestamp(warns[x][1]).strftime(
                    "%m/%d/%Y, %H:%M:%S") + " EST"
                embedWarn.add_field(
                    name=f"{x+1}. {warns[x][0]}", value=date, inline=False)
        await ctx.send(embed=embedWarn)


def setup(bot):
    bot.add_cog(Staff(bot))
