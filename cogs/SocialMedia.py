import yaml
from discord.ext import commands
from os.path import abspath

with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)


class SocialMedia(commands.Cog, name="Social Media Feed"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.webhook_id is not None:
            if message.channel.id == 556298180057235483:
                guild = self.bot.get_guild(config['server_ID'])
                pingRole = guild.get_role(556306011443691541)
                pingRole.edit(reason="Social Media Feed", mentionable=True)
                await message.channel.send(f"{pingRole.mention}")
                pingRole.edit(reason="Social Media Feed", mentionable=False)

            if message.channel.id == 556298669280985098:
                guild = self.bot.get_guild(config['server_ID'])
                pingRole = guild.get_role(556305967642574848)
                pingRole.edit(reason="Social Media Feed", mentionable=True)
                await message.channel.send(f"{pingRole.mention}")
                pingRole.edit(reason="Social Media Feed", mentionable=False)

            if message.channel.id == 571332531224444948:
                guild = self.bot.get_guild(config['server_ID'])
                pingRole = guild.get_role(572290246402768907)
                pingRole.edit(reason="Social Media Feed", mentionable=True)
                await message.channel.send(f"{pingRole.mention}")
                pingRole.edit(reason="Social Media Feed", mentionable=False)
        elif message.channel.id == 556304268869763092:
            guild = self.bot.get_guild(config['server_ID'])
            pingRole = guild.get_role(556306039209984001)
            pingRole.edit(reason="Social Media Feed", mentionable=True)
            await message.channel.send(f"{pingRole.mention}")
            pingRole.edit(reason="Social Media Feed", mentionable=False)


def setup(bot):
    bot.add_cog(SocialMedia(bot))
