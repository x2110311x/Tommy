# **************************************** #
# tommy.py
# Written by x2110311x
# Main file for running Tommy Bot
# **************************************** #

# Included Libraries #
import discord
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
userInsert = f"INSERT INTO users (ID, Name, JoinDate, CreatedDate, PrimaryRole) VALUES (?,?,?,?,?)"
dailyInsert = f"INSERT INTO Dailies (User) VALUES (?)"
levelInsert = f"INSERT INTO Levels (User) VALUES (?)"
creditInsert = f"INSERT INTO Credits (User) VALUES (?)"


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
        DB.execute(dailyInsert, member.id)
        DB.execute(levelInsert, member.id)
        DB.execute(creditInsert, member.id)
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
@notPingEveryone()
async def rate(ctx, *, text):
    await ctx.send(f"I would rate {text} **{randint(0,10)} out of 10**")


@bot.command()
async def magic8ball(ctx):
    await ctx.send(txtutils.magic8ball())


@bot.command()
@commands.has_role(config['roles']['staff_roles']['staff'])
@notPingEveryone()
async def say(ctx, channel, *, text):
    channel = ctx.message.channel_mentions[0]
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
@commands.has_role(config['roles']['staff_roles']['bot_maker'])
async def exit(ctx):
    await ctx.send("Goodbye")
    DB.close()
    await bot.close()
    quit()


@bot.event
async def on_ready():
    print("Logged in")

    # Message Testing Channel #
    chanTest = bot.get_channel(config['channel_IDs']['staff']['bot-testing'])
    await chanTest.send("Bot has started")

    # Update Status #
    guild = bot.get_guild(config['server_ID'])
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(
                                  f"with {guild.member_count} members"))

bot.run(config['token'])
