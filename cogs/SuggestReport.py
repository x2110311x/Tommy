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
                await author.send("Suggestion Subbmitted!")

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
                await author.send("Suggestion Subbmitted!")
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


def setup(bot):
    bot.add_cog(SuggestReport(bot))
