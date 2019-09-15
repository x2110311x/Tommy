import asyncio
import io
import discord
import requests
import time
import yaml

from discord.ext import commands
from os.path import abspath


# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)


class SaidNoError(Exception):
    pass


class Contest(commands.Cog, name="Concert Submission Commands"):
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
                    def check(m):
                        if m.author == author and m.channel == author.dm_channel:
                            if m.content.lower() == 'yes' or m.content.lower.find("yeah") != -1:
                                return True
                            elif m.content.lower() == 'no':
                                raise SaidNoError
                            else:
                                return False
                        else:
                            return False
                    await author.send("Would you like to submit this image for the VIP Present?")
                    try:
                        await self.bot.wait_for('message', check=check, timeout=30)
                        with open(abspath(f"./submissions/{author.id}-{int(time())}.jpg"), "w+b") as outfile:
                            while True:
                                buf = img.read(16384)
                                if not buf:
                                    break
                                outfile.write(buf)
                        embedSubmission = discord.Embed(title="New Image Submission", colour=0x753543)
                        embedSubmission.set_author(name=author.name, icon_url=author.avatar_url)
                        embedSubmission.add_field(name="User ID:", value=author.id)
                        dateSubmitted = message.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                        embedSubmission.set_footer(text=f"© x2110311x. Submitted at : {dateSubmitted}")
                        submissionChan = self.bot.get_channel(622900411090731018)

                        await author.send("Image submitted!")
                        await submissionChan.send(embed=embedSubmission)
                        await submissionChan.send(str(imgEmbed.url))

                    except SaidNoError:
                        await author.send("No problem")
                    except asyncio.TimeoutError:
                        await author.send("Timeout reached. Please try again later.")
            else:
                if message.content.lower().find("yes") == -1 and message.content.lower().find("no") == -1:
                    def check(m):
                        if m.author == author and m.channel == author.dm_channel:
                            if m.content.lower() == 'yes' or m.content.lower.find("yeah") != -1:
                                return True
                            elif m.content.lower() == 'no':
                                raise SaidNoError
                            else:
                                return False
                            
                    await author.send("Would you like to submit this for the VIP Present?")
                    try:
                        await self.bot.wait_for('message', check=check, timeout=30)
                        embedSubmission = discord.Embed(title="New Submission", colour=0x753543)
                        embedSubmission.set_author(name=author.name, icon_url=author.avatar_url)
                        embedSubmission.add_field(name="Idea", value=message.content)
                        embedSubmission.add_field(name="User ID:", value=author.id)
                        dateSubmitted = message.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                        embedSubmission.set_footer(text=f"© x2110311x. Submitted at : {dateSubmitted}")
                        submissionChan = self.bot.get_channel(622900411090731018)

                        filename = f"./submissions/{author.id}-{int(time())}.txt"
                        with open(abspath(filename), 'w') as outputFile:
                            outputFile.write(message.content) 
                        await author.send("Submitted!")
                        await submissionChan.send(embed=embedSubmission)
                    except SaidNoError:
                        await author.send("No problem")
                    except asyncio.TimeoutError:
                        await author.send("Timeout reached. Please try again later.")

def setup(bot):
    bot.add_cog(Contest(bot))
