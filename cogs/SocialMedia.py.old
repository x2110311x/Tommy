import asyncio
import discord
import twitter
import time
import yaml
from datetime import datetime
from discord.ext import commands
from os.path import abspath

with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

twitterAPI = twitter.Api(consumer_key=config['twitterAPIKey'],
                         consumer_secret=config['twitterAPISecret'],
                         access_token_key=config['twitterAccessToken'],
                         access_token_secret=config['twitterAccessSecret'])


async def twitter_check(self):
    while self.bot.is_ready():
        tweets = twitterAPI.GetUserTimeline(screen_name="grandson", exclude_replies=False, count=10)
        for tweet in tweets:
            if int(tweet.created_at_in_seconds) >= (int(time.time()) - 31):
                embedTweet = discord.Embed(title="New Tweet from grandson", colour=0x753543)
                postedBy = tweet.user.profile_image_url
                embedTweet.set_thumbnail(url=postedBy)
                embedTweet.add_field(name=f"http://twitter.com/grandson/status/{tweet.id}", value=tweet.text)
                datePosted = datetime.utcfromtimestamp(int(tweet.created_at_in_seconds)).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                embedTweet.set_footer(text=datePosted, icon_url="http://x2110311x.me/twitter.png")
                twitterChan = self.bot.get_channel(571332531224444948)
                await twitterChan.send(embed=embedTweet)
                guild = self.bot.get_guild(config['server_ID'])
                pingRole = guild.get_role(572290246402768907)
                await pingRole.edit(reason="Social Media Feed", mentionable=True)
                await twitterChan.send(f"{pingRole.mention}")
                await pingRole.edit(reason="Social Media Feed", mentionable=False)

        await asyncio.sleep(30)


async def youtube_check(self):
    while self.bot.is_ready():
        await asyncio.sleep(300)


class SocialMedia(commands.Cog, name="Social Media Feed"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user:
            if message.webhook_id is not None:
                if message.channel.id == 556298180057235483:  # Reddit
                    guild = self.bot.get_guild(config['server_ID'])
                    pingRole = guild.get_role(556306011443691541)
                    await pingRole.edit(reason="Social Media Feed", mentionable=True)
                    await message.channel.send(f"{pingRole.mention}")
                    await pingRole.edit(reason="Social Media Feed", mentionable=False)

                if message.channel.id == 556298669280985098:  # youtube
                    guild = self.bot.get_guild(config['server_ID'])
                    pingRole = guild.get_role(556305967642574848)
                    await pingRole.edit(reason="Social Media Feed", mentionable=True)
                    await message.channel.send(f"{pingRole.mention}")
                    await pingRole.edit(reason="Social Media Feed", mentionable=False)

            elif message.channel.id == 556304268869763092:  # Polls
                guild = self.bot.get_guild(config['server_ID'])
                pingRole = guild.get_role(556306039209984001)
                await pingRole.edit(reason="Poll Ping", mentionable=True)
                await message.channel.send(f"{pingRole.mention}")
                await pingRole.edit(reason="Poll Ping", mentionable=False)

    @commands.Cog.listener()
    async def on_ready(self):
        await twitter_check(self)


def setup(bot):
    bot.add_cog(SocialMedia(bot))
