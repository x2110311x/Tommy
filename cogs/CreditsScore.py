import asyncio
import discord
import io
import requests
import sqlite3
import time
import yaml

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from discord.ext import commands
from include.utilities import seconds_to_units
from math import ceil
from math import floor
from math import sqrt
from os.path import abspath

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)


with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['CreditsScore']

# Database connections #
DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()


async def is_owner(ctx):
    return ctx.author.id == 207129652345438211


class SaidNoError(Exception):
    pass


class CreditsScore(commands.Cog, name="Credits, Score and Rank Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['daily']['brief'], usage=helpInfo['daily']['usage'])
    async def daily(self, ctx):
        author = ctx.message.author
        dailyCheck = f"SELECT LastDaily FROM Dailies WHERE user == {author.id}"
        DB.execute(dailyCheck)
        dailyDate = DB.fetchone()
        if dailyDate is not None:
            dailyDate = int(dailyDate[0]) + 86400
            if dailyDate <= int(time.time()):
                dailyImage = Image.open(abspath("./include/images/daily.png"))
                avatarURL = requests.get(author.avatar_url)
                avatarImage = Image.open(io.BytesIO(avatarURL.content))

                avatarImage.thumbnail((118, 118), Image.ANTIALIAS)
                dailyImage.paste(avatarImage, (28, 22))

                unameFnt = ImageFont.truetype(abspath("./include/fonts/calibri.ttf"), 60)
                unameDraw = ImageDraw.Draw(dailyImage)
                unameDraw.text((176, 18), f"{author.name}", font=unameFnt, fill=(255, 255, 255))
                unameDraw.text((176, 94), "Got 200 Credits", font=unameFnt, fill=(0, 0, 0))

                imgByteArr = io.BytesIO()
                dailyImage.save(imgByteArr, format='PNG')
                imgByteArr.seek(0)
                sendFile = discord.File(fp=imgByteArr, filename="daily.png")

                dailyUpdate = f"UPDATE Dailies SET DailyUses = DailyUses + 1, LastDaily={int(time.time())} WHERE User = {author.id}"
                creditUpdate = f"UPDATE Credits SET Credits = Credits + 200 WHERE User = {author.id}"
                DB.execute(dailyUpdate)
                DB.execute(creditUpdate)
                DBConn.commit()
                await ctx.send(file=sendFile)
            else:
                timeToDaily = seconds_to_units(dailyDate - int(time.time()))
                await ctx.send(f"You have `{timeToDaily}` until you can use !daily")

    @commands.command(brief=helpInfo['score']['brief'], usage=helpInfo['score']['usage'])
    async def score(self, ctx):
        if len(ctx.message.mentions) == 1:
            userToScore = ctx.message.mentions[0]
        else:
            userToScore = ctx.message.author

        levelSelect = f"SELECT Level, Points FROM Levels WHERE User ={userToScore.id}"
        DB.execute(levelSelect)
        levelsResult = DB.fetchone()
        if levelsResult is not None:
            levels = levelsResult[0]
            points = levelsResult[1]
            pointsToNext = ceil(4.0268 * (levels + 1)**2 + 4.01338 * (levels + 1) + 1) - points
        else:
            levels = 0
            pointsToNext = 0

        creditsSelect = f"SELECT Credits FROM Credits WHERE User = {userToScore.id}"
        DB.execute(creditsSelect)
        creditsResult = DB.fetchone()
        if creditsResult is not None:
            credits = creditsResult[0]
        else:
            credits = 0

        rankSelect = "SELECT User FROM Levels ORDER BY Points Desc"
        DB.execute(rankSelect)
        rankSelect = DB.fetchall()
        if rankSelect is not None:
            rank = rankSelect.index((userToScore.id,)) + 1
        else:
            rank = 0

        goldSelect = f"SELECT COUNT(TimeGiven) FROM Golds WHERE User = {userToScore.id}"
        DB.execute(goldSelect)
        goldResult = DB.fetchall()
        if goldResult is not None:
            try:
                golds = goldResult[0][0]
            except TypeError:
                golds = 0
        else:
            golds = 0

        scoreImage = Image.open(abspath("./include/images/score.png"))
        avatarURL = requests.get(userToScore.avatar_url)
        avatarImage = Image.open(io.BytesIO(avatarURL.content))

        avatarImage.thumbnail((121, 121), Image.ANTIALIAS)
        scoreImage.paste(avatarImage, (13, 72))

        unameFnt = ImageFont.truetype(abspath("./include/fonts/calibrib.ttf"), 40)
        levelFnt = ImageFont.truetype(abspath("./include/fonts/calibrib.ttf"), 65)
        rankFnt = ImageFont.truetype(abspath("./include/fonts/calibrib.ttf"), 50)

        unameDraw = ImageDraw.Draw(scoreImage)
        levelDraw = ImageDraw.Draw(scoreImage)
        rankDraw = ImageDraw.Draw(scoreImage)

        unameDraw.text((144, 18), userToScore.name, font=unameFnt, fill=(255, 255, 255))
        unameDraw.text((16, 261), str(credits), font=unameFnt, fill=(255, 255, 255))
        unameDraw.text((16, 342), str(pointsToNext), font=unameFnt, fill=(255, 255, 255))
        unameDraw.text((16, 428), str(golds), font=unameFnt, fill=(255, 255, 255))
        levelDraw.text((144, 131), str(levels), font=levelFnt, fill=(255, 255, 255))
        rankDraw.text((407, 109), str(rank), font=rankFnt, fill=(255, 255, 255))

        imgByteArr = io.BytesIO()
        scoreImage.save(imgByteArr, format='PNG')
        imgByteArr.seek(0)
        sendFile = discord.File(fp=imgByteArr, filename="score.png")

        await ctx.send(file=sendFile)

    @commands.command(brief=helpInfo['donate']['brief'], usage=helpInfo['donate']['usage'])
    async def donate(self, ctx, user: discord.Member, amount):
        if int(amount) <= 1000:
            author = ctx.message.author
            creditCheck = f"SELECT Credits FROM Credits WHERE User = {author.id}"
            DB.execute(creditCheck)
            credits = DB.fetchone()
            if credits is not None:
                if credits[0] >= int(amount):
                    def check(m):
                        if m.author == author and m.channel == ctx.message.channel:
                            if m.content.lower() == 'yes':
                                return True
                            elif m.content.lower() == 'no':
                                raise SaidNoError
                            else:
                                return False
                        else:
                            return False
                    await ctx.send(f"Are you sure you want to donate `{amount} credits` to {user.mention}?")
                    try:
                        await self.bot.wait_for('message', check=check, timeout=30)
                        updateDonator = f"UPDATE Credits SET Credits = Credits - {int(amount)} WHERE User = {author.id}"
                        updateDonatee = f"UPDATE Credits SET Credits = Credits +{int(amount)} WHERE User = {user.id}"
                        DB.execute(updateDonator)
                        DB.execute(updateDonatee)
                        await ctx.send(f"You donated {amount} credits to {user.mention}")
                        DBConn.commit()
                    except asyncio.TimeoutError:
                        await ctx.send("Timeout reached. Donation cancelled!")
                    except SaidNoError:
                        await ctx.send("Donation cancelled")
                else:
                    await ctx.send("You do not have enough credits!")
        else:
            await ctx.send("You can only donate 1000 credits at once")

    @commands.command(brief=helpInfo['alltop']['brief'], usage=helpInfo['alltop']['usage'])
    async def alltop(self, ctx, page=1):
        rankEnd = (10 * page)
        rankStart = rankEnd - 10
        rankSelect = "SELECT User, Points, Level FROM Levels ORDER BY Points Desc"
        DB.execute(rankSelect)
        rankSelect = DB.fetchall()
        users = []
        if rankSelect is not None:
            if rankEnd < len(rankSelect):
                rankSelect = rankSelect[rankStart:rankEnd]
                for user in rankSelect:
                    users.append(self.bot.get_user(user[0]))
                rankImage = Image.open(abspath("./include/images/rank.png"))
                unameRankFnt = ImageFont.truetype(abspath("./include/fonts/calibri.ttf"), 30)
                levelPointFnt = ImageFont.truetype(abspath("./include/fonts/calibril.ttf"), 18)
                for x in range(0, 10):
                    avatarURL = requests.get(users[x].avatar_url)
                    avatarImage = Image.open(io.BytesIO(avatarURL.content))

                    avatarImage.thumbnail((42, 42), Image.ANTIALIAS)
                    rankImage.paste(avatarImage, (80, (64 + x * 53)))

                    textDraw = ImageDraw.Draw(rankImage)
                    textDraw.text((139, (64 + x * 53)), str(users[x].name), font=unameRankFnt, fill=(255, 255, 255))
                    textDraw.text((36, (70 + x * 53)), str(rankStart + x + 1), font=unameRankFnt, fill=(255, 255, 255))

                    textDraw.text((166, (92 + x * 53)), f"Points:  {rankSelect[x][1]}", font=levelPointFnt, fill=(255, 255, 255))
                    textDraw.text((305, (92 + x * 53)), f"Level:  {rankSelect[x][2]}", font=levelPointFnt, fill=(255, 255, 255))

                imgByteArr = io.BytesIO()
                rankImage.save(imgByteArr, format='PNG')
                imgByteArr.seek(0)
                sendFile = discord.File(fp=imgByteArr, filename="leaderboard.png")

                await ctx.send(file=sendFile)
            else:
                await ctx.send("There aren't that many pages!")
        else:
            await ctx.send("Couldn't get ranks. Try again later")

    @commands.command(brief=helpInfo['top']['brief'], usage=helpInfo['top']['usage'])
    async def top(self, ctx, page=1):
        rankEnd = (10 * page)
        rankStart = rankEnd - 10
        rankSelect = "SELECT User, MonthPoints, MonthLevel FROM Levels ORDER BY MonthPoints Desc"
        DB.execute(rankSelect)
        rankSelect = DB.fetchall()
        users = []
        if rankSelect is not None:
            if rankEnd < len(rankSelect):
                rankSelect = rankSelect[rankStart:rankEnd]
                for user in rankSelect:
                    users.append(self.bot.get_user(user[0]))
                rankImage = Image.open(abspath("./include/images/rank.png"))
                unameRankFnt = ImageFont.truetype(abspath("./include/fonts/calibri.ttf"), 30)
                levelPointFnt = ImageFont.truetype(abspath("./include/fonts/calibril.ttf"), 18)
                for x in range(0, 10):
                    avatarURL = requests.get(users[x].avatar_url)
                    avatarImage = Image.open(io.BytesIO(avatarURL.content))

                    avatarImage.thumbnail((42, 42), Image.ANTIALIAS)
                    rankImage.paste(avatarImage, (80, (64 + x * 53)))

                    textDraw = ImageDraw.Draw(rankImage)
                    textDraw.text((139, (64 + x * 53)), str(users[x].name), font=unameRankFnt, fill=(255, 255, 255))
                    textDraw.text((36, (70 + x * 53)), str(rankStart + x + 1), font=unameRankFnt, fill=(255, 255, 255))

                    textDraw.text((166, (92 + x * 53)), f"Points:  {rankSelect[x][1]}", font=levelPointFnt, fill=(255, 255, 255))
                    textDraw.text((305, (92 + x * 53)), f"Level:  {rankSelect[x][2]}", font=levelPointFnt, fill=(255, 255, 255))

                imgByteArr = io.BytesIO()
                rankImage.save(imgByteArr, format='PNG')
                imgByteArr.seek(0)
                sendFile = discord.File(fp=imgByteArr, filename="leaderboard.png")

                await ctx.send(file=sendFile)
            else:
                await ctx.send("There aren't that many pages!")
        else:
            await ctx.send("Couldn't get ranks. Try again later")

    @commands.command(brief=helpInfo['monthlyreset']['brief'], usage=helpInfo['monthlyreset']['usage'])
    @commands.check(is_owner)
    async def monthlyreset(self, ctx):
        await ctx.send("Resetting monthly scores")
        updateMonthly = "UPDATE Levels SET MonthPoints = 0, MonthLevel = 0"
        DB.execute(updateMonthly)
        DBConn.commit()
        await ctx.send("Done!")

    @commands.Cog.listener()
    async def on_message(self, message):
        user = message.author
        timeSelect = f"SELECT NextPoint FROM Levels WHERE User ={user.id}"
        DB.execute(timeSelect)
        nextPoint = DB.fetchone()
        if nextPoint is not None:
            nextPoint = nextPoint[0]
            if nextPoint <= int(time.time()):
                newNext = int(time.time() + 30)
                updatePoints = f"UPDATE Levels SET Points = Points + 1, MonthPoints = MonthPoints +1, NextPoint = {newNext} WHERE User = {user.id}"
                DB.execute(updatePoints)
                selectPoints = f"SELECT Level, Points, MonthLevel, MonthPoints FROM Levels WHERE User = {user.id}"
                DB.execute(selectPoints)
                points = DB.fetchone()

                if points is not None:
                    allLevel = points[0]
                    allPoints = points[1]
                    monthLevel = points[2]
                    monthPoints = points[3]

                    if floor((59.8 * sqrt(allPoints) - 59.8) / 120) > allLevel:
                        level = floor((59.8 * sqrt(allPoints) - 59.8) / 120)
                        updateLevel = f"UPDATE Levels SET Level = {level} WHERE User = {user.id}"
                        DB.execute(updateLevel)
                        await message.channel.send(f"<@{user.id}> Level Up! You are at level {level}.")

                    if floor((59.8 * sqrt(monthPoints) - 59.8) / 120) > monthLevel:
                        level = floor((59.8 * sqrt(monthPoints) - 59.8) / 120)
                        updateLevel = f"UPDATE Levels SET MonthLevel = {level} WHERE User = {user.id}"
                        DB.execute(updateLevel)
        DBConn.commit()


def setup(bot):
    bot.add_cog(CreditsScore(bot))


def teardown(bot):
    DB.close()
