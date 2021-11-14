import logging
import os
from os.path import abspath, dirname

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PATH = dirname(abspath(__file__))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S",
)
log = logging.getLogger(__name__)


def run():
    client = commands.Bot(command_prefix="git.")

    ########
    # Events
    ########
    @client.event
    async def on_ready():
        log.info(f"{client.user} is connected")

    @client.command()
    async def ping(ctx: commands.Context):
        await ctx.send("Pong!")

    ##########
    # Commands
    ##########
    @client.command()
    @commands.is_owner()
    async def load(ctx: commands.Context, extension: str):
        log.info(f"loading {extension} cog")
        await ctx.send(f"> loading {extension}")
        client.load_extension(f"discord_bot.cogs.{extension}")

    @client.command()
    @commands.is_owner()
    async def unload(ctx: commands.Context, extension: str):
        log.info(f"> unloading {extension} cog")
        await ctx.send(f"unloading {extension}")
        client.unload_extension(f"discord_bot.cogs.{extension}")

    @client.command()
    @commands.is_owner()
    async def reload(ctx: commands.Context, extension: str):
        log.info(f"reloading {extension} cog")
        await ctx.send(f"> reloading {extension}")
        client.unload_extension(f"discord_bot.cogs.{extension}")
        client.load_extension(f"discord_bot.cogs.{extension}")

    ###########################
    # Loads all cogs on startup
    ###########################
    for filename in os.listdir(f"{PATH}/cogs"):
        if filename.endswith(".py"):
            extension = filename[:-3]
            log.info(f"loading {extension} cog")
            client.load_extension(f"discord_bot.cogs.{extension}")

    client.run(TOKEN)


if __name__ == "__main__":
    run()
