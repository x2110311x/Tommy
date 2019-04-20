# **************************************** #
# tommy.py
# Written by x2110311x
# Main file for running Tommy Bot
# **************************************** #

# Include Libraries #
import asyncio
import discord
import io
import pylast
import requests
import sqlite3
import time
import yaml

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
from discord.ext import commands
from include import txtutils
from include import utilities
from math import ceil
from math import floor
from math import sqrt
from os.path import abspath
from random import randint


# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

intStartTime = int(time.time())  # time the bot started at
bot = commands.Bot(command_prefix="!")

userInsert = "INSERT INTO users (ID, Name, JoinDate, CreatedDate, PrimaryRole) VALUES (?,?,?,?,?)"
dailyInsert = "INSERT INTO Dailies (User) VALUES (?)"
levelInsert = "INSERT INTO Levels (User) VALUES (?)"
creditInsert = "INSERT INTO Credits (User) VALUES (?)"
setfmInsert = "INSERT INTO FM (User, LastFMUsername, LastUpdated) VALUES (?,?,?)"
warnInsert = "INSERT INTO Warnings (User, Reason, Date, WarnedBy) VALUES (?,?,?,?)"

password_hash = pylast.md5(config['FM_Pass'])
lastfm = pylast.LastFMNetwork(api_key=config['FM_API_Key'], api_secret=config['FM_API_Secret'],
                              username=config['FM_User'], password_hash=password_hash)


# Database connections #
DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()


class PingsEveryone(commands.CheckFailure):
    pass


class SaidNoError(Exception):
    pass


async def minutetasks():
    curTime = int(time.time())
    muteSelect = f"SELECT User FROM Mutes WHERE UnmuteTime <= {curTime}"
    DB.execute(muteSelect)
    unmutes = DB.fetchall()
    if len(unmutes) > 0:
        for user in unmutes:
            user = bot.get_user(user[0])
            guild = bot.get_guild(config['server_ID'])
            muteRole = guild.get_role(config['mute_Role'])
            defaultRole = guild.get_role(config['join_Role'])
            await user.remove_roles(muteRole)
            await user.add_roles(defaultRole)
            await user.send("You have been unmuted")
            deleteMute = f"DELETE FROM Mutes WHERE User ={user.id}"
            DB.execute(deleteMute)
    remindSelect = f"SELECT User, Reminder FROM Reminders WHERE date <= {curTime}"
    DB.execute(remindSelect)
    reminds = DB.fetchall()
    if len(reminds) > 0:
        for remind in reminds:
            user = bot.get_user(remind[0])
            reason = remind[1]
            await user.send(f"You are being reminded for `{reason}`")
            deleteReminder = f"DELETE FROM Reminders WHERE User = {user.id} AND Reminder = '{reason}' AND Date < {curTime}"
            DB.execute(deleteReminder)
    DBConn.commit()
    await asyncio.sleep(20)
    await minutetasks()


def notPingEveryone():
    async def predicate(ctx):
        if ctx.message.clean_content.find("@everyone") != -1:
            raise PingsEveryone("I'm not going to ping everyone bud")
        elif ctx.message.clean_content.find("@here") != -1:
            raise PingsEveryone("I'm not going to ping here bud")
        else:
            return True
    return commands.check(predicate)


@bot.event
async def on_member_join(member):
    # Push user to Databases #
    username = f"{member.name}#{member.discriminator}"
    JoinDate = int(member.joined_at.timestamp())
    CreatedDate = int(member.created_at.timestamp())
    # Insert if new #
    try:
        DB.execute(userInsert, member.id, username, CreatedDate,
                   JoinDate, member.top_role.id)
        DB.execute(dailyInsert, (member.id))
        DB.execute(levelInsert, (member.id))
        DB.execute(creditInsert, (member.id))
        DBConn.commit()
    # Update if previously joined #
    except sqlite3.IntegrityError:
        DB.execute(
            f"UPDATE users SET Left = 'F', JoinDate={JoinDate} WHERE ID={member.id}")

    # Update Status #
    guild = bot.get_guild(config['server_ID'])
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(
                                  f"with {guild.member_count} members"))


@bot.event
async def on_member_remove(member):
    # Remove from user table #
    DB.execute(f"UPDATE users SET Left='T' WHERE ID={member.id}")

    # Update Status #
    guild = bot.get_guild(config['server_ID'])
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(
                                  f"with {guild.member_count} members"))


@bot.command()
async def epoch(ctx):
    intCurEpoch = int(time.time())
    await ctx.send(f"The current epoch is {intCurEpoch}")


@bot.command()
async def setfm(ctx, *, username):
    try:
        DB.execute(setfmInsert, (ctx.author.id, username, int(time.time())))
        await ctx.send("Username Set!")
    except sqlite3.IntegrityError:
        DB.execute(
            f"UPDATE FM SET LastFMUsername={username}, LastUpdated = {int(time.time())} WHERE User={ctx.author.id}")
        await ctx.send("Username Updated!")
    DBConn.commit()


@bot.command()
async def fm(ctx):
    fmSelect = f"SELECT LastFMUsername FROM FM WHERE User = {ctx.author.id}"
    DB.execute(fmSelect)
    username = DB.fetchone()
    if username is not None:
        try:
            user = lastfm.get_user(username[0])
            current_track = user.get_now_playing()

            if current_track is None:
                current_track = user.get_recent_tracks(limit=1)[0]
                track = str(current_track.track)
                album = current_track.album
                artist = track[0:track.find('-') - 1]
                track = track[track.find('-') + 2:]

                embedFM = discord.Embed(title="Last Played", colour=0x753543)
                embedFM.set_author(
                    name=username[0], icon_url=ctx.author.avatar_url)
                embedFM.add_field(
                    name="Album", value=album, inline=True)
                embedFM.add_field(name="Song", value=track, inline=True)
                embedFM.add_field(
                    name="Artist", value=artist, inline=False)
            else:
                imageurl = current_track.get_cover_image(2)

                embedFM = discord.Embed(title="Now Playing", colour=0x753543)
                embedFM.set_author(
                    name=username[0], icon_url=ctx.author.avatar_url)
                embedFM.set_image(url=imageurl)
                embedFM.add_field(
                    name="Album", value=current_track.get_album(), inline=True)
                embedFM.add_field(
                    name="Song", value=current_track.title, inline=True)
                embedFM.add_field(
                    name="Artist", value=current_track.artist, inline=False)
            await ctx.send(embed=embedFM)
        except Exception as e:
            await ctx.send("Uh Oh! I couldn't get your status")
            print(e)
    else:
        await ctx.send("Please set your username with !setfm")


@bot.command()
@notPingEveryone()
async def rate(ctx, *, text):
    await ctx.send(f"I would rate {text} **{randint(0,10)} out of 10**")


@bot.command()
async def magic8ball(ctx):
    await ctx.send(txtutils.magic8ball())


@bot.command()
@commands.has_role(config['staff_Role'])
@notPingEveryone()
async def say(ctx, *, text):
    try:
        channel = ctx.message.channel_mentions[0]
        txtindex = ctx.message.content.find('>') + 1
        text = ctx.message.content[txtindex:]
    except IndexError:
        channel = ctx.channel
    await channel.send(text)


@bot.command()
async def ping(ctx):
    msgResp = await ctx.send("Bot is up!")
    editStamp = utilities.msdiff(ctx.message.created_at, msgResp.created_at)
    strResp = f"Pong! `{editStamp}ms`"
    await msgResp.edit(content=strResp)


@bot.command()
async def uptime(ctx):
    nowtime = time.time()
    uptime = utilities.seconds_to_units(int(nowtime - intStartTime))
    await ctx.send(f"Tommy has been online for `{uptime}`.")


@bot.command()
@commands.has_role(config['staff_Role'])
async def kick(ctx, user):
    staffRole = bot.get_guild(
        config['server_ID']).get_role(config['staff_Role'])
    user = ctx.message.mentions[0]
    if staffRole not in user.roles:
        await user.kick(reason=ctx.author.name)
        await ctx.send(f"{user.mention} has been kicked!")
    else:
        await ctx.send("You cannot kick another staff member!")


@bot.command()
@commands.has_role(config['staff_Role'])
async def ban(ctx, user):
    staffRole = bot.get_guild(
        config['server_ID']).get_role(config['staff_Role'])
    user = ctx.message.mentions[0]
    if staffRole not in user.roles:
        await user.ban(reason=ctx.author.name)
        await ctx.send(f"{user.mention} has been banned!")
    else:
        await ctx.send("You cannot ban another staff member!")


@bot.command()
@commands.has_role(config['staff_Role'])
async def mute(ctx, user, mutetime):
    user = ctx.message.mentions[0]
    guild = bot.get_guild(config['server_ID'])
    muteRole = guild.get_role(config['mute_Role'])
    defaultRole = guild.get_role(config['join_Role'])
    timeToMute = int(mutetime) * 60 + int(time.time())
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


@bot.command()
@commands.has_role(config['staff_Role'])
async def unmute(ctx, user):
    user = ctx.message.mentions[0]
    guild = bot.get_guild(config['server_ID'])
    muteRole = guild.get_role(config['mute_Role'])
    defaultRole = guild.get_role(config['join_Role'])
    if muteRole in user.roles:
        await user.remove_roles(muteRole)
        await user.add_roles(defaultRole)
        await user.send("You have been unmuted")
        await ctx.send("User has been unmuted")


@bot.command()
@commands.has_role(config['staff_Role'])
async def warn(ctx, user, *, reason):
    user = ctx.message.mentions[0]
    try:
        DB.execute(warnInsert, (user.id, reason,
                                int(time.time()), ctx.author.id))
        DBConn.commit()
        await user.send(f"You have been warned for `{reason}`")
        await ctx.send("User has been warned")
    except Exception as e:
        await ctx.send("Unable to warn user")
        print(e)


@bot.command()
@commands.has_role(config['staff_Role'])
async def chkwarn(ctx, user):
    user = ctx.message.mentions[0]

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


@bot.command()
async def daily(ctx):
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
            timeToDaily = utilities.seconds_to_units(dailyDate - int(time.time()))
            await ctx.send(f"You have `{timeToDaily}` until you can use !daily")


@bot.command()
async def remind(ctx, remindtime, *, reason):
    try:
        remindEpoch = int(time.time()) + (int(remindtime) * 60)
        author = ctx.message.author
        remindInsert = f"INSERT INTO Reminders (User, Reminder, Date) VALUES ({author.id},'{reason}',{remindEpoch})"
        DB.execute(remindInsert)
        DBConn.commit()
        await ctx.send(f"You will be reminded in {remindtime} minutes for `{reason}`")
    except ValueError:
        await ctx.send("Please do not use decimals")


@bot.command()
async def myreminders(ctx):
    author = ctx.message.author
    remindSelect = f"SELECT Reminder, Date FROM Reminders WHERE User = {author.id}"
    DB.execute(remindSelect)
    reminds = DB.fetchall()
    if len(reminds) > 0:
        remindString = "Your reminders: \n```\n"
        for remind in reminds:
            reason = remind[0]
            date = ceil((remind[1] - int(time.time())) / 60)
            remindString += f"{reason}  in about {date} minutes \n"
        remindString += "```"
        await ctx.send(remindString)
    else:
        await ctx.send("You have no reminders")


@bot.command()
async def score(ctx):
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

    unameDraw.text((143, 18), userToScore.name, font=unameFnt, fill=(255, 255, 255))
    unameDraw.text((16, 261), str(credits), font=unameFnt, fill=(255, 255, 255))
    unameDraw.text((16, 340), str(pointsToNext), font=unameFnt, fill=(255, 255, 255))
    levelDraw.text((143, 130), str(levels), font=levelFnt, fill=(255, 255, 255))
    rankDraw.text((407, 109), str(rank), font=rankFnt, fill=(255, 255, 255))

    imgByteArr = io.BytesIO()
    scoreImage.save(imgByteArr, format='PNG')
    imgByteArr.seek(0)
    sendFile = discord.File(fp=imgByteArr, filename="score.png")

    await ctx.send(file=sendFile)


@bot.command()
async def createtag(ctx, name, *, content):
    author = ctx.message.author
    checkSelect = f"SELECT count(TagName) FROM Tags WHERE TagName = '{name}'"
    DB.execute(checkSelect)
    count = DB.fetchone()
    if count is not None:
        if count[0] != 1:
            creditCheck = f"SELECT Credits FROM Credits WHERE User = {author.id}"
            DB.execute(creditCheck)
            credits = DB.fetchone()
            if credits is not None:
                if credits[0] >= 1000:
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
                    tagPrompt = f"Would you like to create the tag `{name}` with content `{content}`?"
                    await ctx.send(f"Creating a tag will cost `1000 credits`. \n{tagPrompt}")
                    try:
                        await bot.wait_for('message', check=check, timeout=30)
                        nowTime = int(time.time())
                        tagInsert = f"INSERT INTO Tags (TagName, User, Content, LastUpdated) VALUES ('{name}', {author.id}, '{content}', {nowTime})"
                        DB.execute(tagInsert)
                        creditsUpdate = f"UPDATE Credits SET Credits = Credits - 1000 WHERE User = {author.id}"
                        DB.execute(creditsUpdate)
                        DBConn.commit()
                        await ctx.send("Tag Created!")
                    except asyncio.TimeoutError:
                        await ctx.send("Timeout reached. Tag creation cancelled!")
                    except SaidNoError:
                        await ctx.send("Tag creation cancelled")

                else:
                    await ctx.send("You do not have enough credits!")
        else:
            await ctx.send(f"Tag `{name}` already exists!")
    else:
        await ctx.send("Error creating tag")


@bot.command()
async def deletetag(ctx, tag):
    author = ctx.message.author
    tagSelect = f"SELECT User FROM Tags WHERE TagName ='{tag}'"
    DB.execute(tagSelect)
    tagResult = DB.fetchone()
    if tagResult is not None:
        userCreated = tagResult[0]
        if author.id == userCreated:
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
            await ctx.send(f"Are you sure you want to delete your tag titled `{tag}`?")
            try:
                await bot.wait_for('message', check=check, timeout=30)
                tagDelete = f"DELETE FROM Tags WHERE TagName ='{tag}'"
                DB.execute(tagDelete)
                DBConn.commit()
                await ctx.send("Tag deleted!")
            except asyncio.TimeoutError:
                await ctx.send("Timeout reached. Tag deletion cancelled!")
            except SaidNoError:
                await ctx.send("Tag deletion cancelled")
        else:
            await ctx.send("You did not create this tag, so you cannot delete it!")
    else:
        await ctx.send("Tag does not exist")


@bot.command()
async def tag(ctx, name):
    tagSelect = f"SELECT Content FROM Tags WHERE TagName ='{name}'"
    DB.execute(tagSelect)
    tagResult = DB.fetchone()
    if tagResult is not None:
        await ctx.send(f"{tagResult[0]}")
    else:
        await ctx.send("Tag does not exist")


@bot.command()
async def edittag(ctx, name, *, content):
    author = ctx.message.author
    tagSelect = f"SELECT User,Content FROM Tags WHERE TagName ='{name}'"
    DB.execute(tagSelect)
    tagResult = DB.fetchone()
    if tagResult is not None:
        userCreated = tagResult[0]
        if author.id == userCreated:
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
            await ctx.send(f"Are you sure you want to edit your tag titled `{name}` from \n`{tagResult[1]}` to `{content}`?")
            try:
                await bot.wait_for('message', check=check, timeout=30)
                tagDelete = f"UPDATE Tags SET Content = '{content}' WHERE TagName ='{name}'"
                DB.execute(tagDelete)
                DBConn.commit()
                await ctx.send("Tag Edited!")
            except asyncio.TimeoutError:
                await ctx.send("Timeout reached. Tag edit cancelled!")
            except SaidNoError:
                await ctx.send("Tag edit cancelled")
        else:
            await ctx.send("You did not create this tag, so you cannot edit it!")
    else:
        await ctx.send("Tag does not exist")


@bot.command()
async def mytags(ctx):
    author = ctx.message.author
    tagSelect = f"SELECT TagName FROM Tags WHERE User = {author.id}"
    DB.execute(tagSelect)
    tags = DB.fetchall()
    if len(tags) > 0:
        userTags = "Here are your tags\n```\n"
        for tag in tags:
            userTags += f"{tag[0]}\n"
        userTags += "```"
        await ctx.send(userTags)
    else:
        await ctx.send("You have no tags")


@bot.command()
async def donate(ctx, user, amount):
    if len(ctx.message.mentions) > 0:
        user = ctx.message.mentions[0]
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
                        await bot.wait_for('message', check=check, timeout=30)
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

    else:
        await ctx.send("You didn't mention a user!")


@bot.command()
async def alltop(ctx, page=1):
    rankEnd = (10 * page)
    rankStart = rankEnd - 10
    rankSelect = "SELECT User, Points, Level FROM Levels ORDER BY Points Desc"
    DB.execute(rankSelect)
    rankSelect = DB.fetchall()
    users = []
    if rankSelect is not None:
        rankSelect = rankSelect[rankStart:rankEnd]
        for user in rankSelect:
            users.append(bot.get_user(user[0]))
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
        await ctx.send("Couldn't get ranks. Try again later")


@bot.command()
async def top(ctx, page=1):
    rankEnd = (10 * page)
    rankStart = rankEnd - 10
    rankSelect = "SELECT User, MonthPoints, MonthLevel FROM Levels ORDER BY MonthPoints Desc"
    DB.execute(rankSelect)
    rankSelect = DB.fetchall()
    users = []
    if rankSelect is not None:
        rankSelect = rankSelect[rankStart:rankEnd]
        for user in rankSelect:
            users.append(bot.get_user(user[0]))
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
        await ctx.send("Couldn't get ranks. Try again later")


@bot.command()
@commands.has_role(config['staff_Role'])
async def exit(ctx):
    await ctx.send("Goodbye")
    DB.close()
    await bot.close()
    quit()


@bot.listen()
async def on_message(message):
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


@bot.event
async def on_ready():
    print("Logged in")

    # Message Testing Channel #
    chanTest = bot.get_channel(config['testing_Channel'])
    await chanTest.send("Bot has started")
    await minutetasks()

    # Update Status #
    guild = bot.get_guild(config['server_ID'])
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(
                                  f"with {guild.member_count} members"))

bot.run(config['token'])
