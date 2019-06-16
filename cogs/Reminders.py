import asyncio
import time
import yaml

from datetime import datetime
from discord.ext import commands
from include import DB, utilities
from os.path import abspath

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['Reminders']

# Database connections #
DBConn = None


class SaidNoError(Exception):
    pass


async def processreminds(bot, DBConnect):
    while bot.is_ready():
        # Wait 15 seconds to run again #
        await asyncio.sleep(15)
        curTime = int(time.time())
        # Reminders #
        remindSelect = f"SELECT User, Reminder FROM Reminders WHERE date <= {curTime}"
        reminds = await DB.select_all(remindSelect, DBConnect)
        if len(reminds) > 0:
            for remind in reminds:
                try:
                    user = bot.get_user(remind[0])
                    reason = remind[1]
                    await user.send(f"You are being reminded for `{reason}`")
                    deleteReminder = f"DELETE FROM Reminders WHERE User = {user.id} AND Reminder = '{reason}' AND Date < {curTime}"
                    await DB.execute(deleteReminder, DBConnect)
                except AttributeError:
                    chanTest = bot.get_channel(config['testing_Channel'])
                    print(f"Unable to remind user: {remind[0]}")
                    await chanTest.send(f"Unable to remind user: {remind[0]}")


class Reminders(commands.Cog, name="Reminder Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['remind']['brief'], usage=helpInfo['remind']['usage'])
    async def remind(self, ctx, *, remindReason):
        try:
            if remindReason.find(",") == -1:
                await ctx.send("You forgot the comma!")
            else:
                remindTimeStr = remindReason[remindReason.find(","):]
                remindReason = remindReason[:remindReason.find(",")]
                remindTime = 0
                if remindTimeStr.find("w") != -1:
                    weeks = int(remindTimeStr[remindTimeStr.find(" "):remindTimeStr.find("w")])
                    remindTime += weeks * 10080
                    remindTimeStr = remindTimeStr[remindTimeStr.find("w"):]

                if remindTimeStr.find("d") != -1:
                    days = int(remindTimeStr[remindTimeStr.find(" "):remindTimeStr.find("d")])
                    remindTime += days * 1440
                    remindTimeStr = remindTimeStr[remindTimeStr.find("d"):]

                if remindTimeStr.find("h") != -1:
                    hours = int(remindTimeStr[remindTimeStr.find(" "):remindTimeStr.find("h")])
                    remindTime += hours * 60
                    remindTimeStr = remindTimeStr[remindTimeStr.find("h"):]

                if remindTimeStr.find("m") != -1:
                    minutes = int(remindTimeStr[remindTimeStr.find(" "):remindTimeStr.find("m")])
                    remindTime += minutes
                    remindTimeStr = remindTimeStr[remindTimeStr.find("m"):]

                remindEpoch = int(time.time()) + (int(remindTime) * 60)
                if remindTimeStr.find("s") != -1:
                    seconds = int(remindTimeStr[remindTimeStr.find(" "):remindTimeStr.find("s")])
                    remindEpoch += seconds

                if remindEpoch == 0:
                    await ctx.send("You didn't specify a unit of time!")
                else:
                    author = ctx.message.author
                    remindInsert = f"INSERT INTO Reminders (User, Reminder, Date) VALUES ({author.id},'{remindReason}',{remindEpoch})"
                    await DB.execute(remindInsert, DBConn)
                    timeToRemind = utilities.seconds_to_units(int(remindEpoch - time.time()) + 1)
                    await ctx.send(f"You will be reminded in {timeToRemind} for `{remindReason}`")
        except ValueError:
            await ctx.send("An error occured. You may have used decimals. Don't")

    @commands.command(brief=helpInfo['myreminders']['brief'], usage=helpInfo['myreminders']['usage'], alias="myreminds")
    async def myreminders(self, ctx):
        author = ctx.message.author
        remindSelect = f"SELECT Reminder, Date FROM Reminders WHERE User = {author.id}"
        reminds = await DB.select_all(remindSelect, DBConn)
        if len(reminds) > 0:
            remindString = "Your reminders: \n```\n"
            for remind in reminds:
                reason = remind[0]
                date = datetime.utcfromtimestamp(remind[1]).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                remindString += f"{reason}  at {date} \n"
            remindString += "```"
            await ctx.send(remindString)
        else:
            await ctx.send("You have no reminders")

    @commands.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None

    @commands.Cog.listener()
    async def on_ready(self):
        global DBConn
        DBConn = await DB.connect()
        await processreminds(self.bot, DBConn)


def setup(bot):
    bot.add_cog(Reminders(bot))


def teardown(bot):
    DB.close()
