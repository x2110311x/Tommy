import asyncio
import io
import discord
import requests
import numpy as np
from random import randint 
from time import time
import yaml

from discord.ext import commands
from include import DB
from os.path import abspath


# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['Giveaway']
# Database connections #
DBConn = None

class SaidNoError(Exception):
    pass

class Giveway(commands.Cog, name="Giveaway Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['entergiveaway']['brief'], usage=helpInfo['entergiveaway']['usage'])
    async def entergiveaway(self, ctx):
        await ctx.send("Sorry, entries have closed now")
    
    @commands.has_role(555582817442988052)
    @commands.command()
    async def pickwinners(self, ctx):
        msg = await ctx.send("`RANDOMLY CHOOSING WINNERS`")
        bigboySelect = "SELECT LVL.User, ceil(LVL.MonthPoints/51) as Entries FROM TommyBot.Levels as LVL, TommyBot.Giveaway as G WHERE LVL.User = G.User"
        entries = await DB.select_all(bigboySelect, DBConn)
        allEntries = []
        if entries is not None:
            for user in entries:
                for x in range(0,int(user[1])):
                    allEntries.append(user[0])
        print("entries generated")
        if len(allEntries) != 177:
            await ctx.send("ERROR. ENTRIES DOES NOT MATCH EXPECTED")
        else:
            permutationList = np.random.permutation(allEntries).tolist()
            print("Permuation created")
            chosenWinner1 = permutationList[randint(0,1000000000)%177]
            chosenWinner2 = permutationList[randint(0,1000000000)%177]

            while(chosenWinner1 == chosenWinner2): # Safety Check
                chosenWinner2 = permutationList[randint(0,1000000000)%177]

            chosenWinner3 = permutationList[randint(0,1000000000)%177]

            while(chosenWinner1 == chosenWinner3 or chosenWinner2 == chosenWinner3): # Safety Check
                chosenWinner3 = permutationList[randint(0,1000000000)%177]

            chosenWinner4 = permutationList[randint(0,1000000000)%177]

            while(chosenWinner1 == chosenWinner4 or chosenWinner2 == chosenWinner4 or chosenWinner3 == chosenWinner4): # Safety Check
                chosenWinner4 = permutationList[randint(0,1000000000)%177]
            
            await asyncio.sleep(2)
            await msg.edit(content="`THE WINNERS HAVE BEEN CHOSEN. DRUMROLL PLEASE`\n:drum: :drum: :drum: ")
            print("Edit. Sleeping")
            await asyncio.sleep(10)
            print("announcing")
            await ctx.send(f"The 1st place winner of the t-shirt pool is <@{chosenWinner1}>.\nThe 2nd place winner is <@{chosenWinner2}>.")
            await asyncio.sleep(5)
            await ctx.send(f"The 1st place winner of the vinyl pool is <@{chosenWinner3}>.\nThe 2nd place winner is <@{chosenWinner4}>.")
            await asyncio.sleep(3)
            await ctx.send("Congratulations. A staff member will DM you shortly about your prize")

    @commands.Cog.listener()
    async def on_ready(self):
        global DBConn
        DBConn = await DB.connect()
        
def setup(bot):
    bot.add_cog(Giveway(bot))
