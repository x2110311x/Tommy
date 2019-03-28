# **************************************** #
# tommy.py
# Written by x2110311x
# Main file for running Tommy Bot
# **************************************** #

# Include Libraries #
import discord
import pylast
import sqlite3
import time
import yaml
from datetime import datetime, timedelta
from discord.ext import commands
from include import imageutils, txtutils, utilities
from os.path import abspath
from PIL import Image
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


# Checks #
class PingsEveryone(commands.CheckFailure):
    pass


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
    if not username is None:
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
                    name=username, icon_url=ctx.author.avatar_url)
                embedFM.add_field(
                    name="Album", value=album, inline=True)
                embedFM.add_field(name="Song", value=track, inline=True)
                embedFM.add_field(
                    name="Artist", value=artist, inline=False)
            else:
                imageurl = current_track.get_cover_image(2)

                embedFM = discord.Embed(title="Now Playing", colour=0x753543)
                embedFM.set_author(
                    name=username, icon_url=ctx.author.avatar_url)
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
            date = datetime.fromtimestamp(warns[x][1]).strftime("%m/%d/%Y, %H:%M:%S") + " EST"
            embedWarn.add_field(name=f"{x+1}. {warns[x][0]}", value=date, inline=False)
    await ctx.send(embed=embedWarn)


@bot.command()
@commands.has_role(config['staff_Role'])
async def exit(ctx):
    await ctx.send("Goodbye")
    DB.close()
    await bot.close()
    quit()


@bot.event
async def on_ready():
    print("Logged in")

    # Message Testing Channel #
    chanTest = bot.get_channel(config['testing_Channel'])
    await chanTest.send("Bot has started")

    # Update Status #
    guild = bot.get_guild(config['server_ID'])
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(
                                  f"with {guild.member_count} members"))

bot.run(config['token'])
