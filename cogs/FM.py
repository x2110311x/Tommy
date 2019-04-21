import discord
import pylast
import sqlite3
import yaml
import time

from discord.ext import commands
from os.path import abspath


# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)


helpInfo = helpInfo['FM']
# Database connections #
DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()

password_hash = pylast.md5(config['FM_Pass'])
lastfm = pylast.LastFMNetwork(api_key=config['FM_API_Key'], api_secret=config['FM_API_Secret'],
                              username=config['FM_User'], password_hash=password_hash)

setfmInsert = "INSERT INTO FM (User, LastFMUsername, LastUpdated) VALUES (?,?,?)"


class FM(commands.Cog, name="FM Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['setfm']['brief'], usage=helpInfo['setfm']['usage'])
    async def setfm(self, ctx, *, username):
        try:
            DB.execute(setfmInsert, (ctx.author.id, username, int(time.time())))
            await ctx.send("Username Set!")
        except sqlite3.IntegrityError:
            DB.execute(
                f"UPDATE FM SET LastFMUsername={username}, LastUpdated = {int(time.time())} WHERE User={ctx.author.id}")
            await ctx.send("Username Updated!")
        DBConn.commit()

    @commands.command(brief=helpInfo['fm']['brief'], usage=helpInfo['fm']['usage'])
    async def fm(self, ctx):
        fmSelect = f"SELECT LastFMUsername FROM FM WHERE User = {ctx.author.id}"
        DB.execute(fmSelect)
        username = DB.fetchone()
        if username is not None:
            try:
                user = lastfm.get_user(username[0])
                current_track = user.get_now_playing()

                if current_track is None:
                    current_track = user.get_recent_tracks(limit=1)[0]
                    track = str(current_track.track)
                    album = current_track.album
                    artist = track[0:track.find('-') - 1]
                    track = track[track.find('-') + 2:]

                    embedFM = discord.Embed(title="Last Played", colour=0x753543)
                    embedFM.set_author(
                        name=username[0], icon_url=ctx.author.avatar_url)
                    embedFM.add_field(
                        name="Album", value=album, inline=True)
                    embedFM.add_field(name="Song", value=track, inline=True)
                    embedFM.add_field(
                        name="Artist", value=artist, inline=False)
                else:
                    imageurl = current_track.get_cover_image(2)

                    album = str(current_track.get_album())
                    trackName = str(current_track.get_correction())
                    artistName = str(current_track.artist.get_name())

                    embedFM = discord.Embed(title="Now Playing", colour=0x753543)
                    embedFM.set_author(
                        name=username[0], icon_url=ctx.author.avatar_url)
                    embedFM.set_image(url=imageurl)
                    embedFM.add_field(
                        name="Album", value=album, inline=True)
                    embedFM.add_field(
                        name="Song", value=trackName, inline=True)
                    embedFM.add_field(
                        name="Artist", value=artistName, inline=False)
                await ctx.send(embed=embedFM)
            except Exception as e:
                await ctx.send("Uh Oh! I couldn't get your status")
                print(e)
        else:
            await ctx.send("Please set your username with !setfm")


def setup(bot):
    bot.add_cog(FM(bot))


def teardown(bot):
    DB.close()
