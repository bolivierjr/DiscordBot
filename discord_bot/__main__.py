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
    client = commands.Bot(command_prefix=".")

    @client.event
    async def on_ready():
        print(f"{client.user} is connected")

    @client.command()
    async def ping(ctx):
        await ctx.send("Pong!")

    @client.command()
    async def load(ctx, extension):
        log.info(f"loading {extension} cog")
        client.load_extension(f"discord_bot.cogs.{extension}")

    @client.command()
    async def unload(ctx, extension):
        log.info(f"unloading {extension} cog")
        client.unload_extension(f"discord_bot.cogs.{extension}")

    @client.command()
    async def reload(ctx, extension):
        log.info(f"reloading {extension} cog")
        client.unload_extension(f"discord_bot.cogs.{extension}")
        client.load_extension(f"discord_bot.cogs.{extension}")

    for filename in os.listdir(f"{PATH}/cogs"):
        if filename.endswith(".py"):
            extension = filename[:-3]
            log.info(f"loading {extension} cog")
            client.load_extension(f"discord_bot.cogs.{extension}")

    client.run(TOKEN)


if __name__ == "__main__":
    run()
