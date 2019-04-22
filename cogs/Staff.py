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
    async def say(self, ctx, channel: discord.TextChannel = None, *, textToSay):
        if channel is None:
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

    @commands.command(brief=helpInfo['tempban']['brief'], usage=helpInfo['tempban']['usage'])
    @commands.has_role(config['staff_Role'])
    async def tempban(self, ctx, user: discord.Member, banHours=24):
        guild = self.bot.get_guild(config['server_ID'])
        staffRole = guild.get_role(config['staff_Role'])
        if staffRole not in user.roles:
            try:
                timeToUnban = int(banHours) * 3600 + int(time.time())
            except ValueError:
                await ctx.send("Please use integers")
            try:
                banInsert = f"INSERT INTO TempBans (User, UnbanTime) VALUES ({user.id}, {timeToUnban})"
                DB.execute(banInsert)
                DBConn.commit()
                await user.send(f"You have been temporaily banned for `{banHours} hours`")
                await user.ban(reason="Temporary Ban")
                await ctx.send("User has been banned temporarily")
            except Exception as e:
                await ctx.send("Unable to ban user")
                print(e)
        else:
            await ctx.send("You cannot ban another staff member!")

    @commands.command(brief=helpInfo['warn']['brief'], usage=helpInfo['warn']['usage'])
    @commands.has_role(config['staff_Role'])
    async def warn(self, ctx, user: discord.Member, *, reason):
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

        embedWarn = discord.Embed(colour=0x753543)
        embedWarn.set_author(name=user.name, icon_url=user.avatar_url)
        if warns is None:
            embedWarn.add_field(name="User has no warns", inline=True)
            embedWarn.set_footer(text="# of warns: 0")
        else:
            warnCount = len(warns)
            embedWarn.set_footer(text=f"# of warns: {warnCount}")
            for x in range(0, warnCount):
                date = datetime.utcfromtimestamp(warns[x][1]).strftime(
                    "%m/%d/%Y, %H:%M:%S") + " GMT"
                embedWarn.add_field(
                    name=f"{x+1}. {warns[x][0]}", value=date, inline=False)
        await ctx.send(embed=embedWarn)

    @commands.command(brief=helpInfo['userinfo']['brief'], usage=helpInfo['userinfo']['usage'])
    @commands.has_role(config['staff_Role'])
    async def userinfo(self, ctx, user: discord.Member):
        selectWarn = f"SELECT count(date) FROM Warnings WHERE User={user.id}"
        selectDailies = f"SELECT DailyUses FROM Dailies WHERE User={user.id}"
        DB.execute(selectWarn)
        warns = DB.fetchone()
        if warns is not None:
            warns = warns[0]
        else:
            warns = 0
        DB.execute(selectDailies)
        dailyUses = DB.fetchone()[0]
        warnCount = warns
        joinDate = user.joined_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        createdDate = user.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        userRoles = user.roles
        rolestr = ""
        for role in userRoles:
            if role.id not in [config['server_ID'], 555583424728137728]:
                rolestr += f"{role.mention}, "
        rolestr = rolestr[:len(rolestr) - 2]
        embedInfo = discord.Embed(colour=0x753543)
        embedInfo.set_author(name=user.name, icon_url=user.avatar_url)
        embedInfo.add_field(name="User ID", value=user.id, inline=False)
        embedInfo.add_field(name="Last Join Date", value=joinDate, inline=False)
        embedInfo.add_field(name="Account Creation Date", value=createdDate, inline=False)
        embedInfo.add_field(name="# of warns", value=warnCount, inline=False)
        embedInfo.add_field(name="Daily Uses", value=dailyUses, inline=False)
        embedInfo.add_field(name="roles", value=rolestr, inline=False)

        await ctx.send(embed=embedInfo)

    @commands.command(brief=helpInfo['roleinfo']['brief'], usage=helpInfo['roleinfo']['usage'])
    @commands.has_role(config['staff_Role'])
    async def roleinfo(self, ctx, role: discord.Role):
        usersWithRole = 0
        for user in ctx.message.channel.guild.members:
            if role in user.roles:
                usersWithRole += 1
        createdDate = role.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        embedRole = discord.Embed(colour=0x753543)
        embedRole.set_author(name=role.name)
        embedRole.add_field(name="Role ID", value=role.id, inline=False)
        embedRole.add_field(name="Role Color", value=f"{role.mention} - {hex(role.color.value)}", inline=False)
        embedRole.add_field(name="Hoisted?", value=role.hoist, inline=False)
        embedRole.add_field(name="Mentionable?", value=role.mentionable, inline=False)
        embedRole.add_field(name="Role Created:", value=createdDate, inline=False)
        embedRole.add_field(name="Users with role", value=usersWithRole, inline=False)

        await ctx.send(embed=embedRole)

    @commands.command(brief=helpInfo['resetstatus']['brief'], usage=helpInfo['resetstatus']['usage'])
    @commands.has_role(config['staff_Role'])
    async def resetstatus(self, ctx):
        guild = ctx.message.channel.guild
        await ctx.send("Resetting status")
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"with {guild.member_count} members"))


def setup(bot):
    bot.add_cog(Staff(bot))


def teardown(bot):
    DB.close()
