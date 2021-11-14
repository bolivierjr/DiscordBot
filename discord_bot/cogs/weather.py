import logging

from discord.ext import commands

log = logging.getLogger(__name__)


class Weather(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f"{__class__.__name__} cog is loaded and ready")

    # Commands


def setup(client: commands.Bot):
    client.add_cog(Weather(client))
