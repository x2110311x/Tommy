# **************************************** #
# tommy.py
# Written by x2110311x
# Main file for running Tommy Bot
# **************************************** #

# Include Libraries #
import asyncio
import discord
import sqlite3
import time
import yaml

from difflib import SequenceMatcher
from datetime import datetime
from discord.ext import commands
from include import utilities
from os import system
from os.path import abspath


# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

intStartTime = int(time.time())  # time the bot started at
bot = commands.Bot(command_prefix="!")


# Database connections #
DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()

startup_extensions = ["cogs.JoinLeave",
                      "cogs.FM",
                      "cogs.Staff",
                      "cogs.CreditsScore",
                      "cogs.Tags",
                      "cogs.Reminders",
                      "cogs.Gold",
                      "cogs.Fun",
                      "cogs.AuditLogs",
                      "cogs.ShopandRoles"]

for extension in startup_extensions:
    bot.load_extension(extension)


with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['Utilities']


async def is_owner(ctx):
    return ctx.author.id == 207129652345438211


class Utilities(commands.Cog, name="Utility Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['epoch']['brief'], usage=helpInfo['epoch']['usage'])
    async def epoch(self, ctx):
        intCurEpoch = int(time.time())
        await ctx.send(f"The current epoch is {intCurEpoch}")

    @commands.command(brief=helpInfo['fromepoch']['brief'], usage=helpInfo['fromepoch']['usage'])
    async def fromepoch(self, ctx, epoch: int):
        dateTime = datetime.utcfromtimestamp(epoch).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        await ctx.send(f"{epoch} is {dateTime}")

    @commands.command(brief=helpInfo['reloadextensions']['brief'], usage=helpInfo['reloadextensions']['usage'])
    @commands.check(is_owner)
    async def reloadextensions(self, ctx):
        for extension in startup_extensions:
            bot.reload_extension(extension)

        await ctx.send("Extensions reloaded!")

    @commands.command(brief=helpInfo['update']['brief'], usage=helpInfo['update']['usage'])
    @commands.check(is_owner)
    async def update(self, ctx):
        await ctx.send("Updating Bot")
        system('/bot/tommy/bot/bashscripts/update.sh')
        await asyncio.sleep(30)
        await ctx.send("Restarting Bot")
        await bot.close()
        DB.close()
        system('systemctl restart tommy')

    @commands.command(brief=helpInfo['update']['brief'], usage=helpInfo['update']['usage'])
    @commands.check(is_owner)
    async def restart(self, ctx):
        await ctx.send("Restarting Bot")
        await bot.close()
        DB.close()
        system('systemctl restart tommy')

    @commands.command(brief=helpInfo['ping']['brief'], usage=helpInfo['ping']['usage'])
    async def ping(self, ctx):
        msgResp = await ctx.send("Bot is up!")
        editStamp = utilities.msdiff(ctx.message.created_at, msgResp.created_at)
        strResp = f"Pong! `{editStamp}ms`"
        await msgResp.edit(content=strResp)

    @commands.command(brief=helpInfo['uptime']['brief'], usage=helpInfo['uptime']['usage'])
    async def uptime(self, ctx):
        nowtime = time.time()
        uptime = utilities.seconds_to_units(int(nowtime - intStartTime))
        await ctx.send(f"Tommy has been online for `{uptime}`.")


bot.add_cog(Utilities(bot))


async def minutetasks():
    while bot.is_ready():
        # Wait 20 seconds to run again #
        await asyncio.sleep(20)
        # Unmutes #
        curTime = int(time.time())
        muteSelect = f"SELECT User FROM Mutes WHERE UnmuteTime <= {curTime}"
        DB.execute(muteSelect)
        unmutes = DB.fetchall()
        if len(unmutes) > 0:
            for userToUnmute in unmutes:
                try:
                    guild = bot.get_guild(config['server_ID'])
                    muteRole = guild.get_role(config['mute_Role'])
                    defaultRole = guild.get_role(config['join_Role'])
                    user = guild.get_member(userToUnmute[0])
                    await user.remove_roles(muteRole)
                    await user.add_roles(defaultRole)
                    await user.send("You have been unmuted")
                    deleteMute = f"DELETE FROM Mutes WHERE User ={user.id}"
                    DB.execute(deleteMute)
                except AttributeError:
                    print(f"Unable to unmute user: {userToUnmute[0]}")

        # unban #
        banSelect = f"SELECT User FROM TempBans WHERE UnbanTime <= {curTime}"
        DB.execute(banSelect)
        unbans = DB.fetchall()
        if len(unbans) > 0:
            for userToUnban in unbans:
                try:
                    guild = bot.get_guild(config['server_ID'])
                    user = discord.Object(id=userToUnban[0])
                    print(user)
                    print("Attempting to unban")
                    guild = bot.get_guild(config['server_ID'])
                    await guild.unban(user)
                    await user.send("You have been unbanned")
                    deleteMute = f"DELETE FROM TempBans WHERE User ={user.id}"
                    DB.execute(deleteMute)
                except AttributeError:
                    print(f"Unable to unban user: {userToUnban[0]}")

        # Reminders #
        remindSelect = f"SELECT User, Reminder FROM Reminders WHERE date <= {curTime}"
        DB.execute(remindSelect)
        reminds = DB.fetchall()
        if len(reminds) > 0:
            for remind in reminds:
                try:
                    user = bot.get_user(remind[0])
                    reason = remind[1]
                    await user.send(f"You are being reminded for `{reason}`")
                    deleteReminder = f"DELETE FROM Reminders WHERE User = {user.id} AND Reminder = '{reason}' AND Date < {curTime}"
                    DB.execute(deleteReminder)
                except AttributeError:
                    print(f"Unable to remind user: {remind[0]}")
        DBConn.commit()


@bot.listen()
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = ctx.message.content[1:]
        cmdIndex = message.find(" ")
        if cmdIndex != -1:
            usedCommand = message[:cmdIndex]
        else:
            usedCommand = message
        foundCommand = None
        highestRatio = 0.0
        for command in bot.commands:
            commandName = command.name
            comparison = SequenceMatcher(None, usedCommand, commandName)
            if comparison.ratio() > highestRatio:
                highestRatio = comparison.ratio()
                foundCommand = command
        await ctx.send(f"Hmm! You forgot to specify {error.param}\n ```Usage: !{foundCommand.name} {foundCommand.usage}```")
    elif isinstance(error, commands.ExtensionNotLoaded):
        await ctx.send(f"Uhoh! The {error.name} extension is not loaded! Please contact x2110311x")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        message = ctx.message.content[1:]
        cmdIndex = message.find(" ")
        if cmdIndex != -1:
            usedCommand = message[:cmdIndex]
        else:
            usedCommand = message
        foundCommand = None
        highestRatio = 0.0
        for command in bot.commands:
            commandName = command.name
            comparison = SequenceMatcher(None, usedCommand, commandName)
            if comparison.ratio() > highestRatio:
                highestRatio = comparison.ratio()
                foundCommand = command
        if foundCommand is not None:
            embedUnknownCommand = discord.Embed(title=f"Unknown command: !{usedCommand}", colour=0x753543)
            embedUnknownCommand.add_field(
                name=f"Did you mean to use !{foundCommand.name}?", value=foundCommand.brief, inline=False)
            if foundCommand.usage is None:
                cmdUsage = ""
            else:
                cmdUsage = foundCommand.usage
            embedUnknownCommand.add_field(
                name="Usage", value=f"!{foundCommand.name} {cmdUsage}", inline=False)
            await ctx.send(embed=embedUnknownCommand)
    else:
        await ctx.send(f"Unknown error occured. Please contact x2110311x \n{error}")


@bot.event
async def on_ready():
    print("Logged in")

    # Message Testing Channel #
    chanTest = bot.get_channel(config['testing_Channel'])
    await chanTest.send("Bot has started")

    # Update Status #
    guild = bot.get_guild(config['server_ID'])
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"with {guild.member_count} members"))
    await minutetasks()

bot.run(config['token'], bot=True, Reconnect=True)
