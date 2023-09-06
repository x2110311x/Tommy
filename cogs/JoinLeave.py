import discord
import io
import requests
import yaml

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from include import DB
from discord.ext import commands
from os.path import abspath

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

# Database connections #
DBConn = None


class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = self.bot.get_guild(config['server_ID'])
        joinRole = guild.get_role(config['join_Role'])
        username = f"{member.name}#{member.discriminator}"
        JoinDate = int(member.joined_at.timestamp())
        CreatedDate = int(member.created_at.timestamp())

        userInsert = f"INSERT INTO Users (ID, JoinDate, CreatedDate, PrimaryRole) VALUES ({member.id},{JoinDate},{CreatedDate},{joinRole.id}) ON DUPLICATE KEY UPDATE LeftServer=\'F\' JoinDate={JoinDate}"
        dailyInsert = f"INSERT INTO Dailies (User) VALUES ({member.id}) ON DUPLICATE KEY UPDATE User=User"
        levelInsert = f"INSERT INTO Levels (User) VALUES ({member.id}) ON DUPLICATE KEY UPDATE User=User"
        creditInsert = f"INSERT INTO Credits (User) VALUES ({member.id}) ON DUPLICATE KEY UPDATE User=User"
        try:
        # add Role #
            await member.add_roles(joinRole)
        except:
            pass
        # Insert if new #
        try:
            await DB.execute(userInsert, DBConn)
            await DB.execute(dailyInsert, DBConn)
            await DB.execute(levelInsert, DBConn)
            await DB.execute(creditInsert, DBConn)
        except:
            pass

        # Update Status #

        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"with {guild.member_count - 3} members"))

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
        await DB.execute(f"UPDATE Users WHERE ID={member.id} SET LeftServer=\'T\'", DBConn)

        # Update Status #
        guild = self.bot.get_guild(config['server_ID'])
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"with {guild.member_count - 3} members"))

    @commands.Cog.listener()
    async def on_ready(self):
        global DBConn
        DBConn = await DB.connect()

    @commands.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None


def setup(bot):
    bot.add_cog(JoinLeave(bot))


def teardown(bot):
    DB.close()
