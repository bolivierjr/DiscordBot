import logging

from discord.ext import commands

log = logging.getLogger(__name__)


class Weather(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Weather cog is loaded and ready")

    # Commands


def setup(client):
    client.add_cog(Weather(client))
