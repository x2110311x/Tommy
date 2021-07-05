import discord
import time
import yaml

from datetime import datetime
from discord.ext import commands
from os.path import abspath

with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)


class AuditLogs(commands.Cog, name="Audits"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user:
            slurFound = False
            slursUsed = []
            slurlist = config['slurs']
            for slur in slurlist:
                if message.content.find(slur['word']) != -1:
                    slurFound = True
                    slursUsed.append(slur['censored'])
            if slurFound:
                slursUsedStr = "```Slurs Used:"
                for slur in slursUsed:
                    slursUsedStr += f"\n{slur}"
                slursUsedStr += "```"
                sendMessage = f"Please refrain from using slurs. A copy of your message has been sent to the Staff.\n{slursUsedStr}"
                await message.delete()
                await message.channel.send(sendMessage)

                embedSlur = discord.Embed(colour=0x753543)
                embedSlur.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                embedSlur.add_field(name="Slur Used!", value=slursUsedStr, inline=False)
                embedSlur.add_field(name="Orignal Message", value=message.content, inline=False)
                embedSlur.add_field(name="In Channel", value=message.channel.name, inline=False)
                dateCreated = message.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                embedSlur.add_field(name="Message Created At", value=dateCreated, inline=False)
                embedSlur.set_footer(text=f"© x2110311x. Original message ID: {message.id} User ID: {message.author.id}")

                slurLog = self.bot.get_channel(config['slur-log'])
                await slurLog.send(embed=embedSlur)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author != self.bot.user:
            embedDelete = discord.Embed(colour=0x753543)
            embedDelete.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            if message.content != "" and message.content is not None:
                embedDelete.add_field(name="Message deleted!", value=message.content, inline=False)
            embedDelete.add_field(name="In Channel", value=message.channel.name, inline=False)
            dateCreated = message.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
            embedDelete.add_field(name="Message Created At", value=dateCreated, inline=False)
            dateDeleted = datetime.utcfromtimestamp(int(time.time())).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
            embedDelete.add_field(name="Message Deleted At", value=dateDeleted, inline=False)
            embedDelete.set_footer(text=f"© x2110311x. Original message ID: {message.id}")
            deleteLog = self.bot.get_channel(config['delete-log'])

            if len(message.attachments) > 0:
                imgEmbed = message.attachments[0]
                img = io.BytesIO()
                await imgEmbed.save(img, use_cached=True)
                sendFile = discord.File(fp=img, filename="deleted.png")
                embedDelete.set_image(url="attachment://deleted.png")
                await deleteLog.send(file=sendFile, embed=embedDelete)
            else:
                await deleteLog.send(embed=embedDelete)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author != self.bot.user:
            try:
                if before.content != after.content:
                    embedEdit = discord.Embed(colour=0x753543)
                    embedEdit.set_author(name=before.author.name, icon_url=before.author.avatar_url)
                    embedEdit.add_field(name="Message Edited!", value=f"{after.content}", inline=False)
                    embedEdit.add_field(name="Origial Message", value=f"{before.content}", inline=False)
                    embedEdit.add_field(name="In Channel", value=f"{after.channel.name}", inline=False)
                    dateCreated = before.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                    embedEdit.add_field(name="Message Created At", value=f"{dateCreated}", inline=False)
                    dateEdited = datetime.utcfromtimestamp(int(time.time())).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
                    embedEdit.add_field(name="Message edited At", value=f"{dateEdited}", inline=False)
                    embedEdit.set_footer(text=f"© x2110311x. Original message ID: {after.id}")

                    editLog = self.bot.get_channel(config['edit-log'])
                    await editLog.send(embed=embedEdit)
            except Exception as e:
                print(e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embedJoin = discord.Embed(colour=0x753543)
        embedJoin.set_author(name=member.name, icon_url=member.avatar_url)
        embedJoin.add_field(name="User Joined!", value=f"User ID {member.id}", inline=False)
        dateJoined = member.joined_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        embedJoin.add_field(name="Joined At", value=dateJoined, inline=False)
        dateCreated = member.created_at.strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        if int(time.time()) -604800 < member.created_at.timestamp():
            dateCreated += "\n***ACCOUNT CREATED LESS THAN 1 WEEK AGO***"
        embedJoin.add_field(name="User Account Created At", value=dateCreated, inline=False)
        embedJoin.set_footer(text=f"© x2110311x. User ID {member.id}")

        joinLeaveLog = self.bot.get_channel(config['join-leave-log'])
        await joinLeaveLog.send(embed=embedJoin)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embedLeave = discord.Embed(colour=0x753543)
        embedLeave.set_author(name=member.name, icon_url=member.avatar_url)
        embedLeave.add_field(name="User Left!", value=f"User ID {member.id}", inline=False)
        dateLeft = datetime.utcfromtimestamp(int(time.time())).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        embedLeave.add_field(name="Left At", value=dateLeft, inline=False)
        embedLeave.set_footer(text=f"© x2110311x. User ID {member.id}")

        joinLeaveLog = self.bot.get_channel(config['join-leave-log'])
        await joinLeaveLog.send(embed=embedLeave)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embedBan = discord.Embed(colour=0x753543)
        embedBan.set_author(name=user.name, icon_url=user.avatar_url)
        embedBan.add_field(name="User Banned!", value=f"User ID {user.id}", inline=False)
        dateBan = datetime.utcfromtimestamp(int(time.time())).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        embedBan.add_field(name="Banned At", value=dateBan, inline=False)
        embedBan.set_footer(text=f"© x2110311x. ")

        banLog = self.bot.get_channel(config['ban_log'])
        await banLog.send(embed=embedBan)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embedUnban = discord.Embed(colour=0x753543)
        embedUnban.set_author(name=user.name, icon_url=user.avatar_url)
        embedUnban.add_field(name="User Unbanned!", value=f"User ID {user.id}", inline=False)
        dateUnban = datetime.utcfromtimestamp(int(time.time())).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        embedUnban.add_field(name="Unbanned At", value=dateUnban, inline=False)
        embedUnban.set_footer(text=f"© x2110311x. User ID {user.id}")

        banLog = self.bot.get_channel(config['ban_log'])
        await banLog.send(embed=embedUnban)

    @commands.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None


def setup(bot):
    bot.add_cog(AuditLogs(bot))
