import discord
import io
import json
import requests
import time
import yaml
import urllib.parse

from discord.ext import commands
from include import DB
from os.path import abspath
from PIL import Image
from PIL import ImageDraw


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
    async def fm(self, ctx, *, user=None):
        if user is None:
            userID = ctx.author.id
            iconUrl = ctx.author.avatar_url
            fmSelect = f"SELECT LastFMUsername FROM FM WHERE User = {userID}"
            username = await DB.select_one(fmSelect, DBConn)
        else:
            if len(ctx.message.mentions) > 0:
                userID = ctx.message.mentions[0].id
                iconUrl = ctx.message.mentions[0].avatar_url
                fmSelect = f"SELECT LastFMUsername FROM FM WHERE User = {userID}"
                username = await DB.select_one(fmSelect, DBConn)
            else:
                username = user
                iconUrl = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/e7981d38-6ee3-496d-a6c0-8710745bdbfc/db6zlbs-68b8cd4f-bf6b-4d39-b9a7-7475cade812f.png"

        if username is not None:
            try:
                if type(username) is tuple:
                    username = username[0]
                api_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={config['FM_API_Key']}&format=json"
                fmreponse = requests.get(api_url)
                if fmreponse.status_code != 200:
                    raise ValueError(f"Could not get status. Reponse code: {fmreponse.status_code}")
                else:
                    fmData = json.loads(fmreponse.text)
                    trackData = fmData['recenttracks']['track'][0]
                    print(1)
                    artist = trackData['artist']['#text']
                    album = trackData['album']['#text']
                    trackName = trackData['name']
                    try:
                        imageURL = trackData['image'][1]['#text']
                        if imageURL.find("http") == -1:
                            artistEncoded = urllib.parse.quote(artist)
                            albumEncoded = urllib.parse.quote(album)
                            album_api_url = f"http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={config['FM_API_Key']}&artist={artistEncoded}&album={albumEncoded}&format=json"
                            album_api_url = album_api_url.replace("%20", "+")
                            albumResponse = requests.get(album_api_url)
                            albumData = json.loads(albumResponse.text)
                            imageURL = albumData['image'][1]['#text']
                    except KeyError:
                        imageURL = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/e7981d38-6ee3-496d-a6c0-8710745bdbfc/db6zlbs-68b8cd4f-bf6b-4d39-b9a7-7475cade812f.png"
                    try:
                        nowPlaying = bool(trackData['@attr']['nowplaying'])
                    except KeyError:
                        nowPlaying = False

                    if nowPlaying:
                        embedFM = discord.Embed(title="Now Playing", colour=0x753543, url=f"https://www.last.fm/user/{username}")
                    else:
                        embedFM = discord.Embed(title="Last Played", colour=0x753543, url=f"https://www.last.fm/user/{username}")
                    embedFM.set_author(name=username, icon_url=iconUrl)
                    if trackName != '':
                        embedFM.add_field(name="Song", value=trackName, inline=True)
                    if artist != '':
                        embedFM.add_field(name="Artist", value=artist, inline=True)
                    if album != '':
                        embedFM.add_field(name="Album", value=album, inline=True)
                    else: 
                        album = "undefined"
                        embedFM.add_field(name="Album", value=album, inline=True)
                    embedFM.set_thumbnail(url=imageURL)
                await ctx.send(embed=embedFM)
            except ValueError:
                await ctx.send("I couldn't find that user! Try resetting your username")
            except Exception as e:
                await ctx.send("Oh No!!! I couldn't get your status. Perhaps the username is not set correctly")
                print(e)
        else:
            if len(ctx.message.mentions) > 0:
                await ctx.send("User has not set their username yet")
            elif user is None:
                await ctx.send("Please set your username with !setfm")

    @commands.command(brief=helpInfo['weekly']['brief'], usage=helpInfo['weekly']['usage'])
    async def weekly(self, ctx, *, user=None):
        if user is None:
            userID = ctx.author.id
            fmSelect = f"SELECT LastFMUsername FROM FM WHERE User = {userID}"
            username = await DB.select_one(fmSelect, DBConn)
        else:
            if len(ctx.message.mentions) > 0:
                userID = ctx.message.mentions[0].id
                fmSelect = f"SELECT LastFMUsername FROM FM WHERE User = {userID}"
                username = await DB.select_one(fmSelect, DBConn)
            else:
                username = user

        if username is not None:
            try:
                if type(username) is tuple:
                    username = username[0]
                api_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getweeklyalbumchart&user={username}&api_key={config['FM_API_Key']}&format=json"
                fmreponse = requests.get(api_url)
                if fmreponse.status_code != 200:
                    raise ValueError(f"Could not get status. Reponse code: {fmreponse.status_code}")
                else:
                    msg1 = await ctx.send("Generating image...")
                    fmData = json.loads(fmreponse.text)
                    albumData = fmData['weeklyalbumchart']['album'][:9]
                    count = 0
                    img = Image.new('RGB', (300, 300), color='black')
                    for album in albumData:
                        try:
                            artistEncoded = urllib.parse.quote(album['artist']['#text'])
                            albumEncoded = urllib.parse.quote(album['name'])
                            album_api_url = f"http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={config['FM_API_Key']}&artist={artistEncoded}&album={albumEncoded}&format=json"
                            album_api_url = album_api_url.replace("%20", "+")
                            albumResponse = requests.get(album_api_url)

                            albumData = json.loads(albumResponse.text)
                            imageURL = albumData['album']['image'][3]['#text']
                            albumImgUrl = requests.get(imageURL)
                            avatarImg = Image.open(io.BytesIO(albumImgUrl.content))
                            avatarImg.thumbnail((100, 100), Image.ANTIALIAS)

                        except (ValueError, KeyError, IndexError):
                            imageURL = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/e7981d38-6ee3-496d-a6c0-8710745bdbfc/db6zlbs-68b8cd4f-bf6b-4d39-b9a7-7475cade812f.png"
                            albumImgUrl = requests.get(imageURL)
                            avatarImg = Image.open(io.BytesIO(albumImgUrl.content))
                            avatarImg.thumbnail((100, 100), Image.ANTIALIAS)

                        x = int((count % 3) * 100)
                        if count >= 0 and count < 3:
                            y = 0
                        elif count >= 3 and count < 6:
                            y = 100
                        elif count >= 6 and count < 9:
                            y = 200
                        img.paste(avatarImg, (x, y))
                        count += 1

                    imgByteArr = io.BytesIO()
                    img.save(imgByteArr, format='PNG')
                    imgByteArr.seek(0)
                    sendFile = discord.File(fp=imgByteArr, filename="weekly.png")
                    embedFM = discord.Embed(title=f"Top Weekly Albums for {username}", colour=0x753543, url=f"https://www.last.fm/user/{username}")
                    embedFM.set_image(url="attachment://weekly.png")
                    await msg1.delete()
                    await ctx.send(file=sendFile, embed=embedFM)
            except ValueError:
                await ctx.send("I couldn't find that user! Try resetting your username")
            except Exception as e:
                await ctx.send("Oh No!!! I couldn't get your weekly. Perhaps the username is not set correctly")
                print(e)
        else:
            if len(ctx.message.mentions) > 0:
                await ctx.send("User has not set their username yet")
            elif user is None:
                await ctx.send("Please set your username with !setfm")

    @commands.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None

    @commands.Cog.listener()
    async def on_ready(self):
        global DBConn
        DBConn = await DB.connect()


def setup(bot):
    bot.add_cog(FM(bot))


def teardown(bot):
    DB.close()
