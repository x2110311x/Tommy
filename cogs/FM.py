import discord
import json
import requests
import time
import yaml
import urllib.parse

from discord.ext import commands
from include import DB
from os.path import abspath


# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)


helpInfo = helpInfo['FM']
# Database connections #
DBConn = None


class FM(commands.Cog, name="FM Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['setfm']['brief'], usage=helpInfo['setfm']['usage'])
    async def setfm(self, ctx, *, username):
        selectFM = f"SELECT LastUpdated FROM FM WHERE User = {ctx.author.id}"
        setfmInsert = f"INSERT INTO FM (User, LastFMUsername, LastUpdated) VALUES ({ctx.author.id},'{username}',{int(time.time())})"
        fmResult = await DB.select_one(selectFM, DBConn)
        if fmResult is not None:
            if len(fmResult) != 0:
                fmUpdate = f"UPDATE FM SET LastFMUsername='{username}', LastUpdated = {int(time.time())} WHERE User={ctx.author.id}"
                await DB.execute(fmUpdate, DBConn)
                await ctx.send("Username Updated!")
            else:
                await DB.execute(setfmInsert, DBConn)
                await ctx.send("Username Set!")
        else:
            await DB.execute(setfmInsert, DBConn)
            await ctx.send("Username Set!")

    @commands.command(brief=helpInfo['fm']['brief'], usage=helpInfo['fm']['usage'])
    async def fm(self, ctx, user = None):
        if user is None:
            user = ctx.author.id
            fmSelect = f"SELECT LastFMUsername FROM FM WHERE User = {user}"
            username = await DB.select_one(fmSelect, DBConn)
        else:
            if len(ctx.message.mentions) > 0:
                user = ctx.message.mentions[0].id
                fmSelect = f"SELECT LastFMUsername FROM FM WHERE User = {user}"
                username = await DB.select_one(fmSelect, DBConn)
                if username is None:
                    await ctx.send("User has not set a username yet!")
                    break
            else:
                username = user
        
        if username is not None:
            try:
                api_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username[0]}&api_key={config['FM_API_Key']}&format=json"
                fmreponse = requests.get(api_url)
                if fmreponse.status_code != 200:
                    raise ValueError(f"Could not get status. Reponse code: {fmreponse.status_code}")
                else:
                    fmData = json.loads(fmreponse.text)
                    trackData = fmData['recenttracks']['track'][0]
                    artist = trackData['artist']['#text']
                    album = trackData['album']['#text']
                    trackName = trackData['name']
                    try:
                        imageURL = trackData['image'][1]['#text']
                        if imageURL.find("http") == -1:
                            artistEncoded = urllib.parse.quote(artist)
                            albumEncoded = urllib.parse.quote(album)
                            album_api_url = f"http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={config['FM_API_Key']}&artist={artistEncoded}&album={albumEncoded}&format=json"
                            albumResponse = requests.get(album_api_url)
                            albumData = json.loads(albumResponse.text)
                            imageURL = albumData['image'][1]['#text']
                    except KeyError:
                        imageURL = "http://x2110311x.me/blankalbum.png"
                    try:
                        nowPlaying = bool(trackData['@attr']['nowplaying'])
                    except KeyError:
                        nowPlaying = False

                    if nowPlaying:
                        embedFM = discord.Embed(title="Now Playing", colour=0x753543, url=f"https://www.last.fm/user/{username}")
                    else:
                        embedFM = discord.Embed(title="Last Played", colour=0x753543, url=f"https://www.last.fm/user/{username}")
                    embedFM.set_author(name=username[0], icon_url=ctx.author.avatar_url)
                    embedFM.add_field(name="Song", value=trackName, inline=True)
                    embedFM.add_field(name="Artist", value=artist, inline=True)
                    embedFM.add_field(name="Album", value=album, inline=False)
                    embedFM.set_thumbnail(url=imageURL)
                await ctx.send(embed=embedFM)
            except Exception as e:
                await ctx.send("Uh Oh! I couldn't get your status")
                print(e)
        else:
            await ctx.send("Please set your username with !setfm")

    @commands.Cog.listener()
    async def on_ready(self):
        global DBConn
        DBConn = await DB.connect()


def setup(bot):
    bot.add_cog(FM(bot))


def teardown(bot):
    DB.close()
