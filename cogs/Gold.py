import asyncio
import discord
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


class Gold(commands.Cog, name="Gilding"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id != self.bot.user.id and reaction.message.channel.id != config['shop_Channel']:
            if reaction.emoji.id == 569642972262432784:
                message = reaction.message
                if user != message.author:
                    creditsSelect = f"SELECT Credits FROM Credits WHERE User ={user.id}"
                    credits = await DB.select_one(creditsSelect, DBConn)
                    if credits is not None:
                        if credits[0] >= 2000:
                            def check(m):
                                if m.author == user and m.channel == user.dm_channel:
                                    if m.content.lower() == 'yes':
                                        return True
                                    elif m.content.lower() == 'no':
                                        raise SaidNoError
                                    else:
                                        return False
                                else:
                                    return False
                            goldPrompt = f"Would you like to give gold to {message.author.name}?"
                            await user.send(f"Giving gold will cost `2000 credits`. \n{goldPrompt}")
                            try:
                                await self.bot.wait_for('message', check=check, timeout=30)
                                goldInsert = f"INSERT INTO Golds (User, TimeGiven, GivenBy) VALUES({message.author.id}, {int(time.time())}, {user.id})"
                                await DB.execute(goldInsert, DBConn)
                                creditsUpdate = f"UPDATE Credits SET Credits = Credits - 2000 WHERE User = {user.id}"
                                await DB.execute(creditsUpdate, DBConn)
                                await user.send("Okay!")
                                await message.author.send(f"You have been given gold by {user.name} for your message: `{message.content}`")
                                embedGold = discord.Embed(colour=0x753543)
                                embedGold.set_author(
                                    name=message.author.name, icon_url=message.author.avatar_url)
                                embedGold.add_field(
                                    name="Message", value=message.content, inline=False)
                                embedGold.add_field(
                                    name="In Channel", value=message.channel.name, inline=False)
                                embedGold.add_field(name="Given by", value=user.name, inline=False)
                                goldChannel = self.bot.get_channel(config['gold_Channel'])
                                goldMsg = await goldChannel.send(embed=embedGold)
                                await goldMsg.add_reaction("⬆")
                                await goldMsg.add_reaction("⬇")

                            except SaidNoError:
                                await user.send("Giving Gold cancelled!")
                            except asyncio.TimeoutError:
                                await user.send("Timeout reached. Giving Gold cancelled!")
                        else:
                            msg = await message.channel.send(f"You don't have enough money to give gold! {user.mention}")
                            await reaction.remove(user)
                            await asyncio.sleep(3)
                            await msg.delete()
                    else:
                        msg = await user.send("Error giving gold.")
                        await reaction.remove(user)
                        await asyncio.sleep(3)
                        await msg.delete()
                else:
                    msg = await message.channel.send("You cannot give yourself gold!")
                    await reaction.remove(user)
                    await asyncio.sleep(3)
                    await msg.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        global DBConn
        DBConn = await DB.connect()


def setup(bot):
    bot.add_cog(Gold(bot))


def teardown(bot):
    DB.close()
