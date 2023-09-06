import asyncio
import discord
import time
import yaml

from datetime import datetime
from discord.ext import commands, tasks
from os.path import abspath
from include import DB

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['Staff']

# Database connections #
DBConn = None

class SaidNoError(Exception):
    pass

async def processmutes(bot, DBConnect):
    while bot.is_ready():
        await asyncio.sleep(60)  # run every 60 seconds
        curTime = int(time.time())
        muteSelect = f"SELECT User FROM Mutes WHERE UnmuteTime <= {curTime}"
        unmutes = await DB.select_all(muteSelect, DBConnect)
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
                    await DB.execute(deleteMute, DBConnect)
                except AttributeError:
                    chanTest = bot.get_channel(config['testing_Channel'])
                    print(f"Unable to unmute user: {userToUnmute[0]}")
                    await chanTest.send(f"Unable to unmute user: {userToUnmute[0]}")

async def processtempbans(bot, DBConnect):
    while bot.is_ready():
        await asyncio.sleep(300)  # run every 5 minutes
        curTime = int(time.time())
        # unban #
        banSelect = f"SELECT User FROM TempBans WHERE UnbanTime <= {curTime}"
        unbans = await DB.select_all(banSelect, DBConnect)
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
                    await DB.execute(deleteMute, DBConnect)
                except AttributeError:
                    chanTest = bot.get_channel(config['testing_Channel'])
                    print(f"Unable to unban user: {userToUnban[0]}")
                    await chanTest.send(f"Unable to unban user: {userToUnban[0]}")


class Staff(commands.Cog, name="Staff Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.processannouncements.start()
        
    @tasks.loop(seconds=60.0, reconnect=True)
    async def processannouncements(self):
        global DBConn
        chanTest = self.bot.get_channel(config['testing_Channel'])
        print("Announce loop started")
        curTime = int(time.time())
        try:
            announceSelect = f"SELECT announcemessage, announceid FROM Announcements WHERE announcetime <= {curTime}"
            announce = await DB.select_all(announceSelect, DBConn)
            if len(announce) > 0:
                chan = self.bot.get_channel(555581004698615809)
                for announce in announce:
                    try:
                        await chanTest.send("Announcing")
                        await chan.send(announce[0])
                        deleteAnnounce = f"DELETE FROM Announcements WHERE announceid ={announce[1]}"
                        await DB.execute(deleteAnnounce, DBConn)
                    except Exception as e:
                        await chanTest.send(f"Announcement error - {e}")
        except Exception as e:
            await chanTest.send(f"Announcement error - {e}")

    @commands.command(brief=helpInfo['say']['brief'], usage=helpInfo['say']['usage'])
    @commands.has_role(config['staff_Role'])
    async def say(self, ctx, channel: discord.TextChannel = None, *, textToSay):
        if channel is None:
            channel = ctx.channel
        await channel.send(textToSay)
        await ctx.message.delete()
    
    @commands.command()
    @commands.has_role(config['staff_Role'])
    async def checkdatabase(self, ctx):
        global DBConn
        guild = ctx.guild
        sendMsg = ""
        for member in guild.members:
            selectStatement = f"SELECT count(ID) FROM Users WHERE ID={member.id}"
            dbcheck = await DB.select_one(selectStatement, DBConn)
            if dbcheck is not None and dbcheck == 0:
                if len(sendMsg) + len(f"<@{member.id}>") > 2000:
                    await ctx.send(sendMsg)
                    sendMsg = ""
                    sendMsg += f"<@{member.id}>\n"
        if len(sendMsg) > 0:
            await ctx.send(sendMsg)
        await ctx.send("Done!")
        def check(m):
            if m.author == ctx.message.author and m.channel == ctx.message.channel:
                if m.content.lower() == 'yes':
                    return True
                elif m.content.lower() == 'no':
                    raise SaidNoError
                else:
                    return False
            else:
                return False
        try:
            await ctx.send(f"{ctx.message.author.mention}, Would you like me to fix it? Say Yes or No:")
            await self.bot.wait_for('message', check=check, timeout=30)
            for member in guild.members:
                selectStatement = f"SELECT count(ID) FROM Users WHERE ID={member.id}"
                dbcheck = await DB.select_one(selectStatement, DBConn)
                if dbcheck is not None and dbcheck == 0:
                    try:
                        guild = self.bot.get_guild(config['server_ID'])
                        username = f"{member.name}#{member.discriminator}"
                        username = username.replace("'","")
                        username = username.replace('"',"")
                        JoinDate = int(member.joined_at.timestamp())
                        CreatedDate = int(member.created_at.timestamp())
                        userInsert = f"INSERT INTO Users (ID, JoinDate, CreatedDate, PrimaryRole) VALUES ({member.id},{JoinDate},{CreatedDate},{grandkids.id}) ON DUPLICATE KEY UPDATE LeftServer=\'F\', JoinDate={JoinDate}"
                        dailyInsert = f"INSERT INTO Dailies (User) VALUES ({member.id}) ON DUPLICATE KEY UPDATE User=User"
                        levelInsert = f"INSERT INTO Levels (User) VALUES ({member.id}) ON DUPLICATE KEY UPDATE User=User"
                        creditInsert = f"INSERT INTO Credits (User) VALUES ({member.id}) ON DUPLICATE KEY UPDATE User=User"
                        await DB.execute(userInsert, DBConn)
                        await DB.execute(dailyInsert, DBConn)
                        await DB.execute(levelInsert, DBConn)
                        await DB.execute(creditInsert, DBConn)
                    except Exception as e:
                        await ctx.send(f"Error adding user {member.mention}: {type(e)} - {e}")
        except SaidNoError:
            await ctx.send("Alright. Use `!checkdatabase` again later if you change your mind.")
        except asyncio.TimeoutError:
            await ctx.send("Timeout reached. Try again later")
    
    @commands.command()
    @commands.has_role(config['staff_Role'])
    async def missingkids(self, ctx):
        await ctx.send("Non-muted Users without Grandkids role: ")
        guild = ctx.message.channel.guild
        sendMsg = ""
        grandkids = guild.get_role(555585197794656256)
        muted = guild.get_role(565986630750699520)
        for member in guild.members:
            if grandkids not in member.roles and muted not in member.roles:
                if len(sendMsg) + len(f"<@{member.id}>") > 2000:
                    await ctx.send(sendMsg)
                    sendMsg = ""
                sendMsg += f"<@{member.id}>\n"
        if len(sendMsg) > 0:
            await ctx.send(sendMsg)
        await ctx.send("Done!")
        def check(m):
            if m.author == ctx.message.author and m.channel == ctx.message.channel:
                if m.content.lower() == 'yes':
                    return True
                elif m.content.lower() == 'no':
                    raise SaidNoError
                else:
                    return False
            else:
                return False
        try:
            await ctx.send(f"{ctx.message.author.mention}, Would you like me to fix it? Say Yes or No:") 
            await self.bot.wait_for('message', check=check, timeout=30)
            for member in guild.members:
                if grandkids not in member.roles and muted not in member.roles:
                    try:
                        await member.add_roles(grandkids)
                        guild = self.bot.get_guild(config['server_ID'])
                        username = f"{member.name}#{member.discriminator}"
                        JoinDate = int(member.joined_at.timestamp())
                        CreatedDate = int(member.created_at.timestamp())
                        userInsert = f"INSERT INTO Users (ID, JoinDate, CreatedDate, PrimaryRole) VALUES ({member.id},{JoinDate},{CreatedDate},{grandkids.id})ON DUPLICATE KEY UPDATE LeftServer=\'F\' JoinDate={JoinDate}"
                        dailyInsert = f"INSERT INTO Dailies (User) VALUES ({member.id}) ON DUPLICATE KEY UPDATE User=User"
                        levelInsert = f"INSERT INTO Levels (User) VALUES ({member.id}) ON DUPLICATE KEY UPDATE User=User"
                        creditInsert = f"INSERT INTO Credits (User) VALUES ({member.id}) ON DUPLICATE KEY UPDATE User=User"
                        await DB.execute(userInsert, DBConn)
                        await DB.execute(dailyInsert, DBConn)
                        await DB.execute(levelInsert, DBConn)
                        await DB.execute(creditInsert, DBConn)
                    except Exception as e:
                        await ctx.send(f"Error adding role to <@{member.id}>")
                        print(e)
            await ctx.send("Done!")
        except SaidNoError:
            await ctx.send("Alright. Use `!missingkids` again later if you change your mind.")
        except asyncio.TimeoutError:
            await ctx.send("Timeout reached. Try again later")
        
    @commands.command(brief=helpInfo['checkusertable']['brief'], usage=helpInfo['checkusertable']['usage'])
    @commands.has_role(config['staff_Role'])
    async def checkusertable(self, ctx):
        userSelect = "SELECT ID FROM Users"
        userResult = await DB.select_all(userSelect, DBConn)
        userList = []
        badEntries = ""
        guild = ctx.message.channel.guild
        for member in guild.members:
            userList.append(member.id)
        for user in userResult:
            if user[0] not in userList:
                badEntries += f"{user[0]}\n"
                await DB.execute(f"DELETE FROM Dailies WHERE User={user[0]}", DBConn)
                await DB.execute(f"DELETE FROM Credits WHERE User={user[0]}", DBConn)
                await DB.execute(f"DELETE FROM Levels WHERE User={user[0]}", DBConn)
                await DB.execute(f"DELETE FROM OwnedRoles WHERE User={user[0]}", DBConn)
                await DB.execute(f"DELETE FROM FM WHERE User={user[0]}", DBConn)
                await DB.execute(f"DELETE FROM Golds WHERE User={user[0]}", DBConn)
                await DB.execute(f"DELETE FROM Reminders WHERE User={user[0]}", DBConn)
                await DB.execute(f"UPDATE Golds SET GivenBy = 207129652345438211 WHERE GivenBy={user[0]}", DBConn)
                await DB.execute(f"DELETE FROM Users WHERE ID={user[0]}", DBConn)
        if badEntries != "":
            await ctx.send(badEntries)
            await ctx.send("Users deleted. Table fixed")
        else:
            await ctx.send("Table is clean")
                    

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
    async def ban(self, ctx, user: discord.Member, *, banreason=None):
        staffRole = self.bot.get_guild(
            config['server_ID']).get_role(config['staff_Role'])
        if staffRole not in user.roles:
            if banreason is None:
                try:
                    await user.send("You have been banned.\nAppeal at https://www.grandsondiscord.com/appeals/")
                except Exception as e:
                    await ctx.send("Unable to DM user before banning.")
                    print(e)
                await user.ban(reason=ctx.author.name)
            else:
                try:
                    await user.send(f"You have been banned for: {banreason}\nAppeal at https://www.grandsondiscord.com/appeals/")
                except Exception as e:
                    await ctx.send("Unable to DM user before banning.")
                    print(e)
                await user.ban(reason=f"{ctx.author.name}")
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
                await DB.execute(muteInsert, DBConn)
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
                await DB.execute(banInsert, DBConn)
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
        guild = self.bot.get_guild(config['server_ID'])
        staffRole = guild.get_role(config['staff_Role'])
        if staffRole not in user.roles:
            try:
                warnInsert = f"INSERT INTO Warnings (User, Reason, Date, WarnedBy) VALUES ({user.id},'{reason}',{int(time.time())},{ctx.author.id})"
                await DB.execute(warnInsert, DBConn)
                await user.send(f"You have been warned for `{reason}`")
                await ctx.send("User has been warned")
            except Exception as e:
                await ctx.send("Unable to warn user")
                print(e)
        else:
            print("You cannot warn another staff member!")

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
            await DB.execute(deleteMute, DBConn)

    @commands.command(brief=helpInfo['chkwarn']['brief'], usage=helpInfo['chkwarn']['usage'])
    @commands.has_role(config['staff_Role'])
    async def chkwarn(self, ctx, user: discord.Member):
        selectWarn = f"SELECT reason, date FROM Warnings WHERE User={user.id}"
        warns = await DB.select_all(selectWarn, DBConn)

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
    async def userinfo(self, ctx, *, user: discord.Member):
        selectWarn = f"SELECT count(date) FROM Warnings WHERE User={user.id}"
        selectDailies = f"SELECT DailyUses FROM Dailies WHERE User={user.id}"
        warns = await DB.select_one(selectWarn, DBConn)
        if warns is not None:
            warns = warns[0]
        else:
            warns = 0
        dailyUses = await DB.select_one(selectDailies, DBConn)
        dailyUses = dailyUses[0]
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
    async def roleinfo(self, ctx, *, role: discord.Role):
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
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"with {guild.member_count - 3} members"))

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        if channel.id == 555581004698615809:
            guild = self.bot.get_guild(config['server_ID'])
            pingRole = guild.get_role(560301865666084919)
            await pingRole.edit(reason="Announcement", mentionable=True)
            await asyncio.sleep(30)
            await pingRole.edit(reason="Announcement", mentionable=False)

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.mentions) >= 20:
            offender = message.author
            await offender.send(f"You have been automatically banned for mentioning {len(message.mentions)} people. DM x2110311x#2110 to appeal")
            await offender.send("https://cdn.discordapp.com/emojis/648569239489216534.png")
            await offender.ban()
            staffChan = self.bot.get_channel(555595146151067669)
            await staffChan.send(f"{offender.mention} has been automatically banned for mentioning {len(message.mentions)} people.")
            await message.delete()
        elif len(message.mentions) >= 10:
            offender = message.author
            server = self.bot.get_guild(555580515491774487)
            banditos = server.get_role(555585197794656256)
            muted = server.get_role(565986630750699520)
            await offender.remove_roles(banditos)
            await offender.add_roles(muted)
            await offender.send(f"You have been automatically muted for mentioning {len(message.mentions)} people. DM a staff member if you believe this to be a mistake.")
            staffChan = self.bot.get_channel(555595146151067669)
            await staffChan.send(f"{offender.mention} has been automatically muted for mentioning {len(message.mentions)} people.")
            await message.delete()

    @commands.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None
    
    @commands.Cog.listener()
    async def on_disconnect(self):
        self.processannouncements.cancel()
        
    @processannouncements.before_loop
    async def before_processannouncements(self):
        await self.bot.wait_until_ready()
        chanTest = self.bot.get_channel(config['testing_Channel'])
        await chanTest.send("Announcements Started")

    @commands.Cog.listener()
    async def on_ready(self):
        print("go mutes")
        global DBConn
        DBConn = await DB.connect()
        await processmutes(self.bot, DBConn)


def setup(bot):
    bot.add_cog(Staff(bot))


def teardown(bot):
    DB.close(DBConn)
