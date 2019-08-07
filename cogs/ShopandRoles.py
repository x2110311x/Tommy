import asyncio
import discord
import time
import yaml

from discord.ext import commands
from include import DB
from os.path import abspath

with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

with open(abspath('./include/roles.yml'), 'r') as rolesFile:
    shopRoles = yaml.safe_load(rolesFile)

helpInfo = helpInfo['ShopandRoles']

DBConn = None

reactions = ['🇦', '🇧', '🇨', '🇩', '🇪']


class SaidNoError(Exception):
    pass


async def shop_messages(bot):
    shopChan = bot.get_channel(config['shop_Channel'])
    await shopChan.purge()

    embedT1 = discord.Embed(title="Tier 1 Roles", colour=0xDCE4EA)

    count = 0
    for role in shopRoles['Tier1']:
        title = f"{reactions[count]} | {shopRoles['Tier1'][role]['name']} (#{shopRoles['Tier1'][role]['color']})"
        if role == 555586664827715584:
            content = f"{shopRoles['Tier1'][role]['price']} Credits | Level {shopRoles['Tier1'][role]['level']}"
        else:
            content = f"{shopRoles['Tier1'][role]['price']} Credits"
        embedT1.add_field(name=title, value=content, inline=False)
        count += 1
    embedT1.set_footer(text="Click the reaction to buy the role")

    msgT1 = await shopChan.send(embed=embedT1)
    for x in range(0, count):
        await msgT1.add_reaction(reactions[x])

    embedT2 = discord.Embed(title="Tier 2 Roles", colour=0xC9D6DF)
    count = 0
    for role in shopRoles['Tier2']:
        title = f"{reactions[count]} | {shopRoles['Tier2'][role]['name']} (#{shopRoles['Tier2'][role]['color']})"
        content = f"{shopRoles['Tier2'][role]['price']} Credits"
        embedT2.add_field(name=title, value=content, inline=False)
        count += 1
    embedT2.set_footer(text="Click the reaction to buy the role")

    msgT2 = await shopChan.send(embed=embedT2)
    for x in range(0, count):
        await msgT2.add_reaction(reactions[x])

    embedT3 = discord.Embed(title="Tier 3 Roles", colour=0x98ADBC)
    count = 0
    for role in shopRoles['Tier3']:
        title = f"{reactions[count]} | {shopRoles['Tier3'][role]['name']} (#{shopRoles['Tier3'][role]['color']})"
        content = f"{shopRoles['Tier3'][role]['price']} Credits"
        embedT3.add_field(name=title, value=content, inline=False)
        count += 1
    embedT3.set_footer(text="Click the reaction to buy the role")

    msgT3 = await shopChan.send(embed=embedT3)
    for x in range(0, count):
        await msgT3.add_reaction(reactions[x])


class ShopandRoles(commands.Cog, name="Role Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['pingroles']['brief'], usage=helpInfo['pingroles']['usage'])
    async def pingroles(self, ctx):
        user = ctx.message.author

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

        await ctx.send("Check your DMs for more info")

        roleList = []
        for role in config['pingable_Roles']:
            roleList.append(ctx.message.guild.get_role(role))

        try:
            for role in roleList:
                await user.send(f"Do you want the {role.name} role?")
                try:
                    await self.bot.wait_for('message', check=check, timeout=30)
                    await ctx.message.author.add_roles(role)
                except SaidNoError:
                    await ctx.message.author.remove_roles(role)
            await user.send("Roles Set! All done!")
        except asyncio.TimeoutError:
            await user.send("Timeout reached. Try again later!")

    @commands.command(brief=helpInfo['chooserole']['brief'], usage=helpInfo['chooserole']['usage'])
    async def chooserole(self, ctx):
        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.message.author and m.content.isdigit()

        guild = self.bot.get_guild(config['server_ID'])
        roleSelect = f"SELECT Role FROM OwnedRoles WHERE User={ctx.message.author.id}"
        rolesResult = await DB.select_all(roleSelect, DBConn)
        if len(rolesResult) > 0:
            msgStr = "**Your Owned Roles:** \n"
            ownedRoles = []
            for role in rolesResult:
                thisRole = guild.get_role(role[0])
                ownedRoles.append(thisRole)
                msgStr += f"{ownedRoles.index(thisRole)}.\t{thisRole.mention}\n"
            msgStr += "\n\n Say the number to activate your chosen role"
            await ctx.send(msgStr)
            try:
                usermsg = await self.bot.wait_for('message', check=check, timeout=30)
                try:
                    chosenRole = ownedRoles[int(usermsg.content)]

                    for role in ownedRoles:
                        if role.id != 555586664827715584:
                            await ctx.message.author.remove_roles(role)
                    await ctx.message.author.add_roles(chosenRole)
                    await ctx.send(f"You activated the {chosenRole.mention} role!")
                except IndexError:
                    await ctx.send(f"{usermsg.content} wasn't an option. Run the command again")
                    userUpdate = f"UPDATE Users Set PrimaryRole = {ctx.message.author.top_role.id} WHERE ID = {ctx.message.author.id}"
                    await DB.execute(userUpdate, DBConn)

            except SaidNoError:
                pass
            except asyncio.TimeoutError:
                await ctx.send("30 second timeout reached. Come back later!")
        else:
            await ctx.send("You don't have any roles to choose from!")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
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
        if user != self.bot.user:
            guild = self.bot.get_guild(config['server_ID'])
            message = reaction.message
            if message.channel.id == config['shop_Channel']:
                if reaction.emoji in reactions:
                    embed = message.embeds[0]
                    if embed.title == "Tier 1 Roles":
                        creditsSelect = f"SELECT Credits FROM Credits WHERE User ={user.id}"
                        credits = await DB.select_one(creditsSelect, DBConn)
                        if credits is not None:
                            if credits[0] >= 15000:
                                count = 0
                                for role in shopRoles['Tier1']:
                                    if count == reactions.index(reaction.emoji):
                                        roleObj = guild.get_role(role)
                                        roleSelect = f"SELECT count(*) FROM OwnedRoles WHERE User={user.id} AND Role = {roleObj.id}"
                                        roleResult = await DB.select_one(roleSelect, DBConn)
                                        if roleResult[0] == 0:
                                            if roleObj.id == 555586664827715584:
                                                levelSelect = f"SELECT Level FROM Levels WHERE User ={user.id}"
                                                levelsResult = await DB.select_one(levelSelect, DBConn)
                                                if levelsResult[0] >= shopRoles['Tier1'][role]['level']:
                                                    await user.send("Would you like to purchase `Toe Tag` for `15000 credits`?")
                                                    try:
                                                        await self.bot.wait_for('message', check=check, timeout=30)
                                                        purchaseInsert = f"INSERT INTO OwnedRoles (PurchaseDate, Role, User) VALUES ({int(time.time())},{roleObj.id},{user.id})"
                                                        creditsUpdate = f"UPDATE Credits SET Credits = Credits - 15000 WHERE User = {user.id}"
                                                        await DB.execute(creditsUpdate, DBConn)
                                                        await DB.execute(purchaseInsert, DBConn)
                                                        await user.add_roles(roleObj)
                                                        await user.send("You have purchased the `Toe Tag` role.")
                                                    except SaidNoError:
                                                        await user.send("Role Purchase cancelled!")
                                                    except asyncio.TimeoutError:
                                                        await user.send("Timeout reached. Role Purchase cancelled!")
                                                else:
                                                    msg = await message.channel.send(f"{user.mention} Your level is not high enough to purchase this role!")
                                                    await asyncio.sleep(5)
                                                    await msg.delete()
                                            else:
                                                await user.send(f"Would you like to buy the `{roleObj.name}` role for `15000 credits`?")
                                                try:
                                                    await self.bot.wait_for('message', check=check, timeout=30)
                                                    purchaseInsert = f"INSERT INTO OwnedRoles (PurchaseDate, Role, User) VALUES ({int(time.time())},{roleObj.id},{user.id})"
                                                    creditsUpdate = f"UPDATE Credits SET Credits = Credits - 15000 WHERE User = {user.id}"
                                                    await DB.execute(creditsUpdate, DBConn)
                                                    await DB.execute(purchaseInsert, DBConn)
                                                    await user.send(f"You have purchased the `{roleObj.name}` role. Please use `!chooserole` in <#555581400414289935> to activate it")
                                                except SaidNoError:
                                                    await user.send("Role Purchase cancelled!")
                                                except asyncio.TimeoutError:
                                                    await user.send("Timeout reached. Role Purchase cancelled!")
                                        else:
                                            if roleObj.id != 555586664827715584:
                                                msg = await message.channel.send(f"{user.mention} You already have this role! Please use `!chooserole` in <#555581400414289935> to activate it")
                                            else:
                                                msg = await message.channel.send(f"{user.mention} You already have this role!")
                                            await asyncio.sleep(5)
                                            await msg.delete()
                                    count += 1
                            else:
                                msg = await message.channel.send(f"{user.mention} You do not have enough credits to purchase this role!")
                                await asyncio.sleep(5)
                                await msg.delete()
                    elif embed.title == "Tier 2 Roles":
                        creditsSelect = f"SELECT Credits FROM Credits WHERE User ={user.id}"
                        credits = await DB.select_one(creditsSelect, DBConn)
                        if credits is not None:
                            if credits[0] >= 10000:
                                count = 0
                                for role in shopRoles['Tier2']:
                                    if count == reactions.index(reaction.emoji):
                                        roleObj = guild.get_role(role)
                                        roleSelect = f"SELECT count(*) FROM OwnedRoles WHERE User={user.id} AND Role = {roleObj.id}"
                                        roleResult = await DB.select_one(roleSelect, DBConn)
                                        if roleResult[0] == 0:
                                            await user.send(f"Would you like to buy the `{roleObj.name}` role for `10000 credits`?")
                                            try:
                                                await self.bot.wait_for('message', check=check, timeout=30)
                                                purchaseInsert = f"INSERT INTO OwnedRoles (PurchaseDate, Role, User) VALUES ({int(time.time())},{roleObj.id},{user.id})"
                                                creditsUpdate = f"UPDATE Credits SET Credits = Credits - 10000 WHERE User = {user.id}"
                                                await DB.execute(creditsUpdate, DBConn)
                                                await DB.execute(purchaseInsert, DBConn)
                                                await user.send(f"You have purchased the `{roleObj.name}` role. Please use `!chooserole` in <#555581400414289935> to activate it")
                                            except SaidNoError:
                                                await user.send("Role Purchase cancelled!")
                                            except asyncio.TimeoutError:
                                                await user.send("Timeout reached. Role Purchase cancelled!")
                                        else:
                                            msg = await message.channel.send(f"{user.mention} You already have this role! Please use `!chooserole` in <#555581400414289935> to activate it")
                                            await asyncio.sleep(5)
                                            await msg.delete()
                                    count += 1
                            else:
                                msg = await message.channel.send(f"{user.mention} You do not have enough credits to purchase this role!")
                                await asyncio.sleep(5)
                                await msg.delete()
                    elif embed.title == "Tier 3 Roles":
                        creditsSelect = f"SELECT Credits FROM Credits WHERE User ={user.id}"
                        credits = await DB.select_one(creditsSelect, DBConn)
                        if credits is not None:
                            if credits[0] >= 5000:
                                count = 0
                                for role in shopRoles['Tier3']:
                                    if count == reactions.index(reaction.emoji):
                                        roleObj = guild.get_role(role)
                                        roleSelect = f"SELECT count(*) FROM OwnedRoles WHERE User={user.id} AND Role = {roleObj.id}"
                                        roleResult = await DB.select_one(roleSelect, DBConn)
                                        if roleResult[0] == 0:
                                            await user.send(f"Would you like to buy the `{roleObj.name}` role for `5000 credits`?")
                                            try:
                                                await self.bot.wait_for('message', check=check, timeout=30)
                                                purchaseInsert = f"INSERT INTO OwnedRoles (PurchaseDate, Role, User) VALUES ({int(time.time())},{roleObj.id},{user.id})"
                                                creditsUpdate = f"UPDATE Credits SET Credits = Credits - 5000 WHERE User = {user.id}"
                                                await DB.execute(creditsUpdate, DBConn)
                                                await DB.execute(purchaseInsert, DBConn)
                                                await user.send(f"You have purchased the `{roleObj.name}` role. Please use `!chooserole` in <#555581400414289935> to activate it")
                                            except SaidNoError:
                                                await user.send("Role Purchase cancelled!")
                                            except asyncio.TimeoutError:
                                                await user.send("Timeout reached. Role Purchase cancelled!")
                                        else:
                                            msg = await message.channel.send(f"{user.mention} You already have this role! Please use `!chooserole` in <#555581400414289935> to activate it")
                                            await asyncio.sleep(5)
                                            await msg.delete()
                                    count += 1
                            else:
                                msg = await message.channel.send(f"{user.mention} You do not have enough credits to purchase this role!")
                                await asyncio.sleep(5)
                                await msg.delete()
                await reaction.message.remove_reaction(reaction.emoji, user)

    @commands.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None

    @commands.Cog.listener()
    async def on_ready(self):
        global DBConn
        DBConn = await DB.connect()
        await shop_messages(self.bot)


def setup(bot):
    bot.add_cog(ShopandRoles(bot))


def teardown(bot):
    DB.close(DBConn)
