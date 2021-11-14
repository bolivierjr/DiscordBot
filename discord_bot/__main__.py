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
client = commands.Bot(command_prefix=".")


def handle_events():
    @client.event
    async def on_ready():
        log.info(f"{client.user} is connected")

    @client.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError):
        message: str = ""
        if isinstance(error, commands.NotOwner):
            message = "> You are not the owner, only owners can use this command."
        elif isinstance(error, commands.CommandInvokeError):
            message = "> There is a problem with this command"

        if message:
            await ctx.send(message, delete_after=10)
        log.error(error)


def handle_commands():
    @client.command()
    async def ping(ctx: commands.Context):
        await ctx.send("Pong!")

    @client.command()
    @commands.is_owner()
    async def load(ctx: commands.Context, extension: str):
        log.info(f"loading {extension} cog")
        client.load_extension(f"discord_bot.cogs.{extension}")
        await ctx.send(f"> loading {extension}")

    @client.command()
    @commands.is_owner()
    async def unload(ctx: commands.Context, extension: str):
        log.info(f"> unloading {extension} cog")
        client.unload_extension(f"discord_bot.cogs.{extension}")
        await ctx.send(f"unloading {extension}")

    @client.command()
    @commands.is_owner()
    async def reload(ctx: commands.Context, extension: str):
        log.info(f"reloading {extension} cog")
        client.unload_extension(f"discord_bot.cogs.{extension}")
        client.load_extension(f"discord_bot.cogs.{extension}")
        await ctx.send(f"> reloading {extension}")


def run():
    handle_events()
    handle_commands()
    # Loads all cogs on startup
    for filename in os.listdir(f"{PATH}/cogs"):
        if filename.endswith(".py"):
            extension = filename[:-3]
            log.info(f"loading {extension} cog")
            client.load_extension(f"discord_bot.cogs.{extension}")

    client.run(TOKEN)


if __name__ == "__main__":
    run()
