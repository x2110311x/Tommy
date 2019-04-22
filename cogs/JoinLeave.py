import discord
import io
import requests
import sqlite3
import yaml

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from discord.ext import commands
from os.path import abspath

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

# Database connections #
DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()


class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        userInsert = "INSERT INTO users (ID, Name, JoinDate, CreatedDate, PrimaryRole) VALUES (?,?,?,?,?)"
        dailyInsert = f"INSERT INTO Dailies (User) VALUES ({member.id})"
        levelInsert = f"INSERT INTO Levels (User) VALUES ({member.id})"
        creditInsert = f"INSERT INTO Credits (User) VALUES ({member.id})"
        # Push user to Databases #
        username = f"{member.name}#{member.discriminator}"
        JoinDate = int(member.joined_at.timestamp())
        CreatedDate = int(member.created_at.timestamp())
        guild = self.bot.get_guild(config['server_ID'])
        joinRole = guild.get_role(config['join_Role'])
        # add Role #
        await member.add_roles(joinRole)
        # Insert if new #
        try:
            DB.execute(userInsert, (member.id, username, CreatedDate, JoinDate, member.top_role.id))
            DB.execute(dailyInsert)
            DB.execute(levelInsert)
            DB.execute(creditInsert)
            DBConn.commit()
        # Update if previously joined #
        except sqlite3.IntegrityError:
            DB.execute(
                f"UPDATE users SET Left = 'F', JoinDate={JoinDate} WHERE ID={member.id}")

        # Update Status #

        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"with {guild.member_count} members"))

        # Join Image #
        dailyImage = Image.open(abspath("./include/images/daily.png"))
        avatarURL = requests.get(member.avatar_url)
        avatarImage = Image.open(io.BytesIO(avatarURL.content))

        avatarImage.thumbnail((118, 118), Image.ANTIALIAS)
        dailyImage.paste(avatarImage, (28, 22))

        unameFnt = ImageFont.truetype(abspath("./include/fonts/calibri.ttf"), 60)
        unameDraw = ImageDraw.Draw(dailyImage)
        unameDraw.text((176, 18), f"{member.name}", font=unameFnt, fill=(0, 0, 0))
        unameDraw.text((176, 94), "Joined the server!", font=unameFnt, fill=(0, 0, 0))

        imgByteArr = io.BytesIO()
        dailyImage.save(imgByteArr, format='PNG')
        imgByteArr.seek(0)
        sendFile = discord.File(fp=imgByteArr, filename="join.png")
        joinChannel = self.bot.get_channel(config["join_Channel"])
        await joinChannel.send(file=sendFile)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Remove from user table #
        DB.execute(f"UPDATE users SET Left='T' WHERE ID={member.id}")

        # Update Status #
        guild = self.bot.get_guild(config['server_ID'])
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"with {guild.member_count} members"))


def setup(bot):
    bot.add_cog(JoinLeave(bot))


def teardown(bot):
    DB.close()
