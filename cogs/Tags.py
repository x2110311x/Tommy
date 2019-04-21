import asyncio
import sqlite3
import time
import yaml

from discord.ext import commands
from os.path import abspath

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['Tags']
# Database connections #
DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()


class SaidNoError(Exception):
    pass


class Tags(commands.Cog, name="Tag Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['createtag']['brief'], usage=helpInfo['createtag']['usage'])
    async def createtag(self, ctx, tagname, *, tagContent):
        author = ctx.message.author
        checkSelect = f"SELECT count(TagName) FROM Tags WHERE TagName = '{tagname}'"
        DB.execute(checkSelect)
        count = DB.fetchone()
        if count is not None:
            if count[0] != 1:
                creditCheck = f"SELECT Credits FROM Credits WHERE User = {author.id}"
                DB.execute(creditCheck)
                credits = DB.fetchone()
                if credits is not None:
                    if credits[0] >= 1000:
                        def check(m):
                            if m.author == author and m.channel == ctx.message.channel:
                                if m.content.lower() == 'yes':
                                    return True
                                elif m.content.lower() == 'no':
                                    raise SaidNoError
                                else:
                                    return False
                            else:
                                return False
                        tagPrompt = f"Would you like to create the tag `{tagname}` with content `{tagContent}`?"
                        await ctx.send(f"Creating a tag will cost `1000 credits`. \n{tagPrompt}")
                        try:
                            await self.bot.wait_for('message', check=check, timeout=30)
                            nowTime = int(time.time())
                            tagInsert = f"INSERT INTO Tags (TagName, User, Content, LastUpdated) VALUES ('{tagname}', {author.id}, '{tagContent}', {nowTime})"
                            DB.execute(tagInsert)
                            creditsUpdate = f"UPDATE Credits SET Credits = Credits - 1000 WHERE User = {author.id}"
                            DB.execute(creditsUpdate)
                            DBConn.commit()
                            await ctx.send("Tag Created!")
                        except asyncio.TimeoutError:
                            await ctx.send("Timeout reached. Tag creation cancelled!")
                        except SaidNoError:
                            await ctx.send("Tag creation cancelled")

                    else:
                        await ctx.send("You do not have enough credits!")
            else:
                await ctx.send(f"Tag `{tagname}` already exists!")
        else:
            await ctx.send("Error creating tag")

    @commands.command(brief=helpInfo['deletetag']['brief'], usage=helpInfo['deletetag']['usage'])
    async def deletetag(self, ctx, tagname):
        author = ctx.message.author
        tagSelect = f"SELECT User FROM Tags WHERE TagName ='{tagname}'"
        DB.execute(tagSelect)
        tagResult = DB.fetchone()
        if tagResult is not None:
            userCreated = tagResult[0]
            if author.id == userCreated:
                def check(m):
                    if m.author == author and m.channel == ctx.message.channel:
                        if m.content.lower() == 'yes':
                            return True
                        elif m.content.lower() == 'no':
                            raise SaidNoError
                        else:
                            return False
                    else:
                        return False
                await ctx.send(f"Are you sure you want to delete your tag titled `{tagname}`?")
                try:
                    await self.bot.wait_for('message', check=check, timeout=30)
                    tagDelete = f"DELETE FROM Tags WHERE TagName ='{tagname}'"
                    DB.execute(tagDelete)
                    DBConn.commit()
                    await ctx.send("Tag deleted!")
                except asyncio.TimeoutError:
                    await ctx.send("Timeout reached. Tag deletion cancelled!")
                except SaidNoError:
                    await ctx.send("Tag deletion cancelled")
            else:
                await ctx.send("You did not create this tag, so you cannot delete it!")
        else:
            await ctx.send("Tag does not exist")

    @commands.command(brief=helpInfo['edittag']['brief'], usage=helpInfo['edittag']['usage'])
    async def edittag(self, ctx, tagname, *, tagContent):
        author = ctx.message.author
        tagSelect = f"SELECT User,Content FROM Tags WHERE TagName ='{tagname}'"
        DB.execute(tagSelect)
        tagResult = DB.fetchone()
        if tagResult is not None:
            userCreated = tagResult[0]
            if author.id == userCreated:
                def check(m):
                    if m.author == author and m.channel == ctx.message.channel:
                        if m.content.lower() == 'yes':
                            return True
                        elif m.content.lower() == 'no':
                            raise SaidNoError
                        else:
                            return False
                    else:
                        return False
                await ctx.send(f"Are you sure you want to edit your tag titled `{tagname}` from \n`{tagResult[1]}` to `{tagContent}`?")
                try:
                    await self.bot.wait_for('message', check=check, timeout=30)
                    tagDelete = f"UPDATE Tags SET Content = '{tagContent}' WHERE TagName ='{tagname}'"
                    DB.execute(tagDelete)
                    DBConn.commit()
                    await ctx.send("Tag Edited!")
                except asyncio.TimeoutError:
                    await ctx.send("Timeout reached. Tag edit cancelled!")
                except SaidNoError:
                    await ctx.send("Tag edit cancelled")
            else:
                await ctx.send("You did not create this tag, so you cannot edit it!")
        else:
            await ctx.send("Tag does not exist")

    @commands.command(brief=helpInfo['mytags']['brief'], usage=helpInfo['mytags']['usage'])
    async def mytags(self, ctx):
        author = ctx.message.author
        tagSelect = f"SELECT TagName FROM Tags WHERE User = {author.id}"
        DB.execute(tagSelect)
        tags = DB.fetchall()
        if len(tags) > 0:
            userTags = "Here are your tags\n```\n"
            for tag in tags:
                userTags += f"{tag[0]}\n"
            userTags += "```"
            await ctx.send(userTags)
        else:
            await ctx.send("You have no tags")

    @commands.command(brief=helpInfo['tag']['brief'], usage=helpInfo['tag']['usage'])
    async def tag(self, ctx, tagname):
        tagSelect = f"SELECT Content FROM Tags WHERE TagName ='{tagname}'"
        DB.execute(tagSelect)
        tagResult = DB.fetchone()
        if tagResult is not None:
            await ctx.send(f"{tagResult[0]}")
        else:
            await ctx.send("Tag does not exist")


def setup(bot):
    bot.add_cog(Tags(bot))
