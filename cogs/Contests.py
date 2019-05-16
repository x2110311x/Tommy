import asyncio
import io
import discord
import requests
import time
import yaml

from discord.ext import commands
from include import DB
from os.path import abspath


# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

# Database connections #
DBConn = None


class SaidNoError(Exception):
    pass


class Contest(commands.Cog, name="Contest Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        if message.channel == author.dm_channel:
            if len(message.attachments) > 0:
                if len(message.attachments) > 1:
                    await message.author.send("Please send only one image")
                else:
                    imgEmbed = message.attachments[0]
                    imgUrl = requests.get(imgEmbed.url)
                    img = io.BytesIO(imgUrl.content)
                    DBCheck = await DB.select_one(f"SELECT User FROM ArtContest WHERE User = {author.id}", DBConn)
                    if DBCheck is not None:
                        await author.send("You already submitted an image.\nIf you'd like to change your entry, please contact a staff member.")
                    else:
                        def check(m):
                            if m.author == author and m.channel == author.dm_channel:
                                if m.content.lower() == 'yes':
                                    return True
                                elif m.content.lower() == 'no':
                                    raise SaidNoError
                                else:
                                    return False
                            else:
                                return False
                        await author.send("Would you like to submit this image for the Icon Contest?")
                        try:
                            await self.bot.wait_for('message', check=check, timeout=30)
                            with open(abspath(f"./images/{author.id}.jpg"), "w+b") as outfile:
                                while True:
                                    buf = img.read(16384)
                                    if not buf:
                                        break
                                    outfile.write(buf)
                            embedSubmission = discord.Embed(title="New Icon Contest Submission", colour=0x753543)
                            embedSubmission.set_author(name=author.name, icon_url=author.avatar_url)
                            embedSubmission.add_field(name="User ID:", value=author.id)
                            dateSubmitted = message.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                            embedSubmission.set_footer(text=f"© x2110311x. Submitted at : {dateSubmitted}")
                            submissionChan = self.bot.get_channel(577982304140525578)

                            insertSubmission = f"INSERT INTO ArtContest (User, DateSubmitted) VALUES ({author.id},{int(time.time())})"
                            await DB.execute(insertSubmission, DBConn)
                            await author.send("Image submitted!")
                            await submissionChan.send(embed=embedSubmission)
                            await submissionChan.send(str(imgEmbed.url))

                        except SaidNoError:
                            await author.send("No problem")
                        except asyncio.TimeoutError:
                            await author.send("Timeout reached. Please try again later.")
            else:
                if message.content.lower().find("yes") == -1 and message.content.lower().find("no") == -1:
                    DBCheck = await DB.select_one(f"SELECT count(User) FROM NameContest WHERE User = {author.id}", DBConn)
                    if DBCheck is not None and DBCheck[0] == 3:
                        await author.send("You already submitted 3 names.\nIf you'd like to change your entries, please contact a staff member.")
                    else:
                        def check(m):
                            if m.author == author and m.channel == author.dm_channel:
                                if m.content.lower() == 'yes':
                                    return True
                                elif m.content.lower() == 'no':
                                    raise SaidNoError
                                else:
                                    return False
                            else:
                                return False
                        await author.send("Would you like to submit this for the Name Contest?")
                        try:
                            await self.bot.wait_for('message', check=check, timeout=30)
                            embedSubmission = discord.Embed(title="New Name Contest Submission", colour=0x753543)
                            embedSubmission.set_author(name=author.name, icon_url=author.avatar_url)
                            embedSubmission.add_field(name="Idea", value=message.content)
                            embedSubmission.add_field(name="User ID:", value=author.id)
                            dateSubmitted = message.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                            embedSubmission.set_footer(text=f"© x2110311x. Submitted at : {dateSubmitted}")
                            submissionChan = self.bot.get_channel(577982304140525578)

                            insertSubmission = f"INSERT INTO NameContest (User, DateSubmitted, Submission) VALUES ({author.id},{int(time.time())},'{message.content}')"
                            await DB.execute(insertSubmission, DBConn)
                            await author.send("Name submitted!")
                            await submissionChan.send(embed=embedSubmission)
                        except SaidNoError:
                            await author.send("No problem")
                        except asyncio.TimeoutError:
                            await author.send("Timeout reached. Please try again later.")

    @commands.Cog.listener()
    async def on_ready(self):
        global DBConn
        DBConn = await DB.connect()


def setup(bot):
    bot.add_cog(Contest(bot))


def teardown(bot):
    DB.close()
