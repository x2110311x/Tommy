import asyncio
import discord
import yaml

from discord.ext import commands
from json import dumps as jsdumps
from requests import post
from os.path import abspath

with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['SuggestionReport']


class SaidCancelError(Exception):
    pass


class SaidNoError(Exception):
    pass


class SuggestReport(commands.Cog, name="Suggestion and Report Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['suggest']['brief'], usage=helpInfo['suggest']['usage'])
    async def suggest(self, ctx, *, suggestion: str = None):
        author = ctx.message.author

        def check(m):
            return m.author == author and m.channel == author.dm_channel
        if suggestion is None:
            await ctx.send("Please check your DMs")
            await author.send("What is your suggestion?\nPlease note that bot suggestions can be done with !botsuggest")
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30)
                suggestion = msg.content
                embedSuggestion = discord.Embed(colour=0x753543)
                embedSuggestion.set_author(name=author.name, icon_url=author.avatar_url)
                embedSuggestion.add_field(name="New Server Suggestion", value=suggestion)
                dateSubmitted = msg.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                embedSuggestion.set_footer(text=f"© x2110311x. Submitted at : {dateSubmitted}")

                suggestChan = self.bot.get_channel(config['suggestions_channel'])
                await suggestChan.send(embed=embedSuggestion)
                await author.send("Suggestion Submitted!")

            except asyncio.TimeoutError:
                await ctx.send("Timeout reached. Suggestion cancelled!")
        else:
            embedSuggestion = discord.Embed(colour=0x753543)
            embedSuggestion.set_author(name=author.name, icon_url=author.avatar_url)
            embedSuggestion.add_field(name="New Server Suggestion", value=suggestion)
            dateSubmitted = ctx.message.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
            embedSuggestion.set_footer(text=f"© x2110311x. Submitted at : {dateSubmitted}")

            suggestChan = self.bot.get_channel(config['suggestions_channel'])
            await suggestChan.send(embed=embedSuggestion)
            await ctx.send("Suggestion Submitted!")

    @commands.command(brief=helpInfo['botsuggest']['brief'], usage=helpInfo['botsuggest']['usage'])
    async def botsuggest(self, ctx, *, suggestion: str = None):
        author = ctx.message.author

        def check(m):
            return m.author == author and m.channel == author.dm_channel

        if suggestion is None:
            await ctx.send("Please check your DMs")
            await author.send("What is your bot suggestion?")
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30)
                suggestion = msg.content
                dateSubmitted = msg.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                submitUser = f"{author.name}#{author.discriminator} : {author.id}"

                submitData = {
                    "User": submitUser,
                    "Suggestion": suggestion,
                    "TimeSubmitted": dateSubmitted
                }
                response = post(
                    config['botSuggestHook'], data=jsdumps(submitData),
                    headers={'Content-Type': 'application/json'}
                )
                await author.send("Suggestion Submitted!")
            except asyncio.TimeoutError:
                await ctx.send("Timeout reached. Suggestion cancelled!")
        else:
            dateSubmitted = ctx.message.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
            submitUser = f"{author.name}#{author.discriminator} : {author.id}"
            submitData = {
                "User": submitUser,
                "Suggestion": suggestion,
                "TimeSubmitted": dateSubmitted
            }
            response = post(
                config['botSuggestHook'], data=jsdumps(submitData),
                headers={'Content-Type': 'application/json'}
            )
            await ctx.send("Suggestion Submitted!")

    @commands.command(brief=helpInfo['botsuggest']['brief'], usage=helpInfo['botsuggest']['usage'])
    async def report(self, ctx):
        author = ctx.message.author

        def check2(m):
            if m.author == author and m.channel == author.dm_channel:
                if m.content.lower() == 'yes':
                    return True
                elif m.content.lower() == 'no':
                    raise SaidNoError
                else:
                    return False
            else:
                return False

        def check(m):
            if m.author == author and m.channel == author.dm_channel:
                if m.content.lower() == "cancel":
                    raise SaidCancelError()
                else:
                    return True
            else:
                return False

        await ctx.message.delete()
        dmMsg = await ctx.send("Check your DMs")
        await author.send("You can say cancel at any time to cancel the report")
        await author.send("What is the name or ID of the user you want to report?")
        await asyncio.sleep(2)
        await dmMsg.delete()
        try:
            userMsg = await self.bot.wait_for('message', check=check, timeout=30)
            await author.send("What channel did this happen in?")
            chanMsg = await self.bot.wait_for('message', check=check, timeout=30)
            await author.send("What is the reason for reporting this user?")
            reasonMsg = await self.bot.wait_for('message', check=check, timeout=30)
            await author.send("When did this happen?")
            whenMsg = await self.bot.wait_for('message', check=check, timeout=30)
            await author.send("Any other comments?")
            commentsMsg = await self.bot.wait_for('message', check=check, timeout=30)

            dateSubmitted = ctx.message.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
            embedReport = discord.Embed(title="New report submission", colour=0x753543)
            embedReport.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embedReport.add_field(name="Reported User", value=userMsg.content, inline=False)
            embedReport.add_field(name="Happened in", value=chanMsg.content, inline=False)
            embedReport.add_field(name="Time of incidence", value=whenMsg.content, inline=False)
            embedReport.add_field(name="Reason for report", value=reasonMsg.content, inline=False)
            embedReport.add_field(name="Other comments", value=commentsMsg.content, inline=False)
            embedReport.set_footer(text=f"© x2110311x. Submitted at : {dateSubmitted}")

            await author.send(embed=embedReport)
            await author.send("Would you like to send this report?")
            await self.bot.wait_for('message', check=check2, timeout=30)

            reportChan = self.bot.get_channel(config['submitted_reports'])
            await reportChan.send(embed=embedReport)
            await author.send("Your report has been submitted")
        except SaidCancelError:
            await author.send("Okay, you can send one again at any time")
        except SaidNoError:
            await author.send("Okay, you can send one again at any time")
        except asyncio.TimeoutError:
            await author.send("Timeout reached. Report cancelled!")


def setup(bot):
    bot.add_cog(SuggestReport(bot))
