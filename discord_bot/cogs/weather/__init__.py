from discord.ext import commands

from .weather import Weather


def setup(client: commands.Bot):
    client.add_cog(Weather(client))
