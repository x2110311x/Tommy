# **************************************** #
# Init.py
# Written by x2110311x
# File for initializing the databases
# **************************************** #

# Include Libraries #
import discord
import yaml
import sqlite3
from datetime import datetime, timedelta
from discord.ext import commands
from os.path import abspath

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

bot = commands.Bot(command_prefix="!")
roleInsert = "INSERT INTO Roles (Name, ID, Color, Priority) VALUES (?,?,?,?)"
categoryInsert = "INSERT INTO ChannelCategories (ID, Name) VALUES (?,?)"
channelInsert = "INSERT INTO Channels (ID, Name, Type, Category) VALUES (?,?,?,?)"
channelInsert2 = "INSERT INTO Channels (ID, Name, Type) VALUES (?,?,?)"


# Database connections #
DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()


@bot.command()
async def init_db(ctx):
    with open(abspath('./databases/structure.sql'), 'r') as structure:
        try:
            script = structure.read()
            DB.executescript(script)
            DBConn.commit()
            await ctx.send("DB initialized")
        except Exception as e:
            await ctx.send("Error")
            print(e)


@bot.command()
async def init_users_db(ctx):
    guild = bot.get_guild(config['server_ID'])
    for user in guild.members:
        if not user.bot:
            username = f"{user.name}#{user.discriminator}"
            JoinDate = int(user.joined_at.timestamp())
            CreatedDate = int(user.created_at.timestamp())

            userInsert = "INSERT INTO users (ID, Name, JoinDate, CreatedDate, PrimaryRole) VALUES (?,?,?,?,?)"
            dailyInsert = f"INSERT INTO Dailies (User) VALUES ({user.id})"
            levelInsert = f"INSERT INTO Levels (User) VALUES ({user.id})"
            creditInsert = f"INSERT INTO Credits (User) VALUES ({user.id})"
            try:
                DB.execute(userInsert, (user.id, username, JoinDate, CreatedDate, user.top_role.id))
                DB.execute(dailyInsert)
                DB.execute(levelInsert)
                DB.execute(creditInsert)
            except sqlite3.IntegrityError:
                print("IntegrityError")
    DBConn.commit()
    await ctx.send("User DB created")


@bot.command()
async def init_roles_db(ctx):
    guild = bot.get_guild(config['server_ID'])
    for role in guild.roles:
        try:
            DB.execute(roleInsert, (role.name, role.id,
                                    role.colour.value, role.position))
        except sqlite3.IntegrityError:
                print("IntegrityError")
    DBConn.commit()
    await ctx.send("Role DB created")


@bot.command()
async def init_chan_db(ctx):
    guild = bot.get_guild(config['server_ID'])
    for category in guild.categories:
        try:
            DB.execute(categoryInsert, (category.id, category.name))
        except sqlite3.IntegrityError:
                print("IntegrityError")
    DBConn.commit()
    for channel in guild.voice_channels:
        chantype = "Voice"
        try:
            if channel.category is None:
                DB.execute(channelInsert2, (channel.id, channel.name, chantype))
            else:
                DB.execute(channelInsert, (channel.id, channel.name,
                                           chantype, channel.category.id))
        except sqlite3.IntegrityError:
                print("IntegrityError")
    for channel in guild.text_channels:
        chantype = "Text"
        try:
            if channel.category is None:
                DB.execute(channelInsert2, (channel.id, channel.name, chantype))
            else:
                DB.execute(channelInsert, (channel.id, channel.name,
                                           chantype, channel.category.id))
        except sqlite3.IntegrityError:
                print("IntegrityError")
    DBConn.commit()
    await ctx.send("Channel DB created")


@bot.command()
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
    await chanTest.send("Initialization is ready")

    # Update Status #
    guild = bot.get_guild(config['server_ID'])
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(
                                  f"with {guild.member_count} members"))

bot.run(config['token'])