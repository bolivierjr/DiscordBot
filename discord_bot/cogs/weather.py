import logging

from discord.ext import commands
from peewee import DatabaseError

from ..models.users import User

log = logging.getLogger(__name__)


class Weather(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    ########
    # Events
    ########
    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f"{__class__.__name__} cog is loaded and ready")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        message: str = ""
        if isinstance(error, DatabaseError):
            message = str(error)

        if message:
            ctx.send(message, delete_after=10)

    ##########
    # Commands
    ##########
    @commands.command()
    @commands.is_owner()
    async def createdb(self, ctx: commands.Context):
        result: str = User.create_tables()
        await ctx.send(f"> {result}")


def setup(client: commands.Bot):
    client.add_cog(Weather(client))
