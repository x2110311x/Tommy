import aiomysql
import discord
import requests
import time
import yaml

from discord.ext import commands
from os.path import abspath

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

# Database connections #
DBConn = None


async def connect():
    DBConn = await aiomysql.create_pool(host=config['DBServer'], port=3306, user=config['DBUser'], password=config['DBPass'], db="ServerStats")
    return DBConn


async def select_one(query, pool):
    async with pool.acquire() as DBConn:
        async with DBConn.cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchone()
    return result


async def select_all(query, pool):
    async with pool.acquire() as DBConn:
        async with DBConn.cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchall()
    return result


async def execute(query, pool):
    async with pool.acquire() as DBConn:
        async with DBConn.cursor() as cur:
            await cur.execute(query)
            await DBConn.commit()


def close(DBConn):
    DBConn.close()


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        global DBConn
        DBConn = await connect()

    @commands.Cog.listener()
    async def on_message(self, message):
        userID = message.author.id
        if userID != 560213065853960257:
            messageID = message.id
            channelID = message.channel.id
            msgTime = int(time.time())
            sqlInsert = f"INSERT INTO Messages (MessageID,User,Channel,Time) VALUES({messageID},{userID},{channelID},{msgTime})"
            await execute(sqlInsert, DBConn)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        userID = message.author.id
        if userID != 560213065853960257:
            messageID = message.id
            channelID = message.channel.id
            msgTime = int(time.time())
            sqlInsert = f"INSERT INTO Deleted (MessageID,User,Channel,Time) VALUES({messageID},{userID},{channelID},{msgTime})"
            await execute(sqlInsert, DBConn)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        userID = before.author.id
        if userID != 560213065853960257:
            messageID = before.id
            channelID = before.channel.id
            msgTime = int(time.time())
            sqlInsert = f"INSERT INTO Edited (MessageID,User,Channel,Time) VALUES({messageID},{userID},{channelID},{msgTime})"
            await execute(sqlInsert, DBConn)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            userID = member.id
            joinTime = int(time.time())
            userName = f"{member.name}#{member.discriminator}"
            createdTime = member.created_at.timestamp()
            sqlInsert = f"INSERT INTO Joins (User, Time) VALUES ({userID}, {joinTime})"
            sqlInsert2 = f"INSERT INTO Users (ID,Name,JoinDate,CreatedDate) VALUES ({userID},'{userName}',{joinTime},{createdTime}) ON DUPLICATE KEY UPDATE JoinDate={joinTime}"
            await execute(sqlInsert2, DBConn)
            await execute(sqlInsert, DBConn)
        except pymysql.err.IntegrityError:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        userID = member.id
        leaveTime = int(time.time())
        sqlInsert = f"INSERT INTO Leaves (User, Time) VALUES ({userID}, {leaveTime})"
        await execute(sqlInsert, DBConn)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if isinstance(channel, discord.TextChannel):
            chanName = channel.name
            chanID = channel.id
            chanCat = channel.category
            if chanCat is None:
                chanCatId = 0
            else:
                chanCatId = channel.category.id
            sqlInsert = f"INSERT INTO Channels(ID,Name,Category) VALUES ({chanID},'{chanName}',{chanCatId})"
            await execute(sqlInsert, DBConn)
        elif isinstance(channel, discord.CategoryChannel):
            catName = channel.name
            catID = channel.id
            sqlInsert = f"INSERT INTO ChannelCategories (ID,Name) VALUES ({catID},'{catName}'')"
            await execute(sqlInsert, DBConn)

    @commands.command(brief="Only x2 can do this.", usage="Only x2 can do this.")
    @commands.has_role(555582817442988052)
    async def init_users(self, ctx):
        guild = ctx.message.channel.guild
        startTime = time.time()
        msg = await ctx.send("Rebuilding Users Table....")
        for member in guild.members:
            userID = member.id
            joinTime = member.joined_at.timestamp()
            userName = f"{member.name}#{member.discriminator}"
            createdTime = member.created_at.timestamp()
            sqlInsert = f"INSERT INTO Users (ID,Name,JoinDate,CreatedDate) VALUES ({userID},'{userName}',{joinTime},{createdTime}) ON DUPLICATE KEY UPDATE JoinDate={joinTime}"
            await execute(sqlInsert, DBConn)
        endTime = time.time()
        await msg.edit(content=f"Users Table rebuilt in {endTime - startTime} seconds.")

    @commands.command(brief="Only x2 can do this.", usage="Only x2 can do this.")
    @commands.has_role(555582817442988052)
    async def init_channels(self, ctx):
        guild = ctx.message.channel.guild
        startTime = time.time()
        msg = await ctx.send("Rebuilding Channel Table....")
        for category in guild.categories:
            sqlInsert = f"INSERT INTO ChannelCategories (ID, Name) VALUES ({category.id},'{category.name}')"
            await execute(sqlInsert, DBConn)
        for channel in guild.text_channels:
            chanName = channel.name
            chanID = channel.id
            chanCat = channel.category
            if chanCat is None:
                chanCatId = 0
            else:
                chanCatId = channel.category.id
            sqlInsert = f"INSERT INTO Channels(ID,Name,Category) VALUES ({chanID},'{chanName}',{chanCatId})"
            await execute(sqlInsert, DBConn)
        endTime = time.time()
        await msg.edit(content=f"Users Table rebuilt in {endTime - startTime} seconds.")


def setup(bot):
    bot.add_cog(Stats(bot))


def teardown(bot):
    DB.close()
