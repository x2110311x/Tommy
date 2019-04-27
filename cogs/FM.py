import discord
import io
import json
import pylast
import requests
import sqlite3
import time
import yaml

from PIL import Image
from discord.ext import commands
from os.path import abspath


def most_frequent_colour(image):

    w, h = image.size
    pixels = image.getcolors(w * h)

    most_frequent_pixel = pixels[0]

    for count, colour in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, colour)

    return most_frequent_pixel[1]


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
                f"UPDATE FM SET LastFMUsername='{username}', LastUpdated = {int(time.time())} WHERE User={ctx.author.id}")
            await ctx.send("Username Updated!")
        DBConn.commit()

    @commands.command(brief=helpInfo['fm']['brief'], usage=helpInfo['fm']['usage'])
    async def fm(self, ctx):
        fmSelect = f"SELECT LastFMUsername FROM FM WHERE User = {ctx.author.id}"
        DB.execute(fmSelect)
        username = DB.fetchone()
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
                    imageURL = trackData['image'][1]['#text']
                    try:
                        nowPlaying = bool(trackData['@attr']['nowplaying'])
                    except KeyError:
                        nowPlaying = False
                    image = Image.open(io.BytesIO(requests.get(imageURL).content))
                    (r, g, b) = most_frequent_colour(image)
                    colorCode = discord.Colour.from_rgb(r, g, b)

                    if nowPlaying:
                        embedFM = discord.Embed(title="Now Playing", colour=colorCode)
                    else:
                        embedFM = discord.Embed(title="Last Played", colour=colorCode)
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


def setup(bot):
    bot.add_cog(FM(bot))


def teardown(bot):
    DB.close()
