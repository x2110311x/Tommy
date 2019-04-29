# **************************************** #
# Init.py
# Written by x2110311x
# File for initializing the databases
# **************************************** #

# Include Libraries #
import discord
import yaml
from datetime import datetime
from discord.ext import commands
from os.path import abspath
from include import DB

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

bot = commands.Bot(command_prefix="!")

DBConn = None


@bot.command()
async def init_users_db(ctx):
    guild = bot.get_guild(config['server_ID'])
    for user in guild.members:
        if not user.bot:
            username = f"{user.name}#{user.discriminator}"
            JoinDate = int(user.joined_at.timestamp())
            CreatedDate = int(user.created_at.timestamp())
            topRole = user.top_role.id

            userInsert = f"INSERT INTO Users (ID, Name, JoinDate, CreatedDate, PrimaryRole) VALUES ({user.id},'{username}',{JoinDate},{CreatedDate},{topRole})"
            dailyInsert = f"INSERT INTO Dailies (User) VALUES ({user.id})"
            levelInsert = f"INSERT INTO Levels (User) VALUES ({user.id})"
            creditInsert = f"INSERT INTO Credits (User) VALUES ({user.id})"
            await DB.execute(userInsert, DBConn)
            await DB.execute(dailyInsert, DBConn)
            await DB.execute(levelInsert, DBConn)
            await DB.execute(creditInsert, DBConn)
    await ctx.send("User DB created")


@bot.command()
async def init_roles_db(ctx):
    guild = bot.get_guild(config['server_ID'])
    for role in guild.roles:
        roleInsert = f"INSERT INTO Roles (Name, ID, Color, Priority) VALUES ('{role.name}',{role.id},'{role.colour.value}',{role.position})"
        await DB.execute(roleInsert, DBConn)
    await ctx.send("Role DB created")


@bot.command()
async def init_chan_db(ctx):
    guild = bot.get_guild(config['server_ID'])
    for category in guild.categories:
        categoryInsert = f"INSERT INTO ChannelCategories (ID, Name) VALUES ({category.id},'{category.name}')"
        await DB.execute(categoryInsert, DBConn)
    for channel in guild.voice_channels:
        chantype = "Voice"
        if channel.category is None:
            channelInsert2 = f"INSERT INTO Channels (ID, Name, Type) VALUES ({channel.id},'{channel.name}','{chantype}'')"
            await DB.execute(channelInsert2, DBConn)
        else:
            channelInsert = f"INSERT INTO Channels (ID, Name, Type, Category) VALUES ({channel.id},'{channel.name}','{chantype}', {channel.category.id})"
            await DB.execute(channelInsert, DBConn)
    for channel in guild.text_channels:
        chantype = "Text"
        if channel.category is None:
            channelInsert2 = f"INSERT INTO Channels (ID, Name, Type) VALUES ({channel.id},'{channel.name}','{chantype}'')"
            await DB.execute(channelInsert2, DBConn)
        else:
            channelInsert = f"INSERT INTO Channels (ID, Name, Type, Category) VALUES ({channel.id},'{channel.name}','{chantype}', {channel.category.id})"
            await DB.execute(channelInsert, DBConn)
    await ctx.send("Channel DB created")


@bot.command()
async def exit(ctx):
    await ctx.send("Goodbye")
    await bot.close()
    DB.close(DBConn)
    quit()


@bot.event
async def on_ready():
    print("Logged in")
    global DBConn
    DBConn = await DB.connect()

    # Message Testing Channel #
    chanTest = bot.get_channel(config['testing_Channel'])
    await chanTest.send("Initialization is ready")

    # Update Status #
    guild = bot.get_guild(config['server_ID'])
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(
                                  f"with {guild.member_count} members"))

bot.run(config['token'])
