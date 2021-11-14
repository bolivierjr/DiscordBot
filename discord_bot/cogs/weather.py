import html
import logging
from typing import Dict, Optional, Union

from discord.ext import commands
from marshmallow import ValidationError
from peewee import DatabaseError
from requests import RequestException

from ..models.users import User, UserSchema
from ..utils.errors import LocationNotFound, WeatherNotFound
from ..utils.services import query_current_weather
from ..utils.users import AnonymousUser, get_user

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
        try:
            result: str = User.create_tables()
            await ctx.send(f"> {result}")
        except DatabaseError as exc:
            log.error(str(exc))
            await ctx.send("> There was an error with the database. Check logs.", delete_after=10)

    @commands.command(aliases=["w", "wz"])
    async def weather(self, ctx: commands.Context, *, arg: Optional[str] = None):
        lookup_user: bool = False
        if arg and arg.startswith("--user"):
            _, arg = arg.split("--user")
            lookup_user = True
        if lookup_user and not arg:
            await ctx.send(f"{ctx.message.author.mention} Please specify the user name.")
            return

        try:
            optional_user = html.escape(arg) if lookup_user and arg else ctx.message.author
            user: Union[User, AnonymousUser] = get_user(optional_user)

            if lookup_user:
                if not isinstance(user, AnonymousUser):
                    weather: str = query_current_weather("", user)
                    await ctx.send(f"```{weather}```")
                else:
                    await ctx.send(f"No such user by the name of {arg}.")

            elif not arg and isinstance(user, AnonymousUser):
                await ctx.send(f"No weather location set by {ctx.message.author.mention}")

            elif not arg:
                weather: str = query_current_weather(arg, user)
                await ctx.send(f"```{weather}```")

            else:
                deserialized_location: Dict[str, str] = UserSchema().load({"location": html.escape(arg)}, partial=True)
                weather: str = query_current_weather(deserialized_location["location"], user)
                await ctx.send(weather)

        except ValidationError as exc:
            log.error(str(exc), exc_info=True)
            if "location" in exc.messages:
                message = exc.messages["location"][0]
            await ctx.send(f"> {message}", delete_after=10)

        except DatabaseError as exc:
            log.error(str(exc), exc_info=True)
            if "not created" in str(exc):
                await ctx.send(f"> {exc}", delete_after=10)
            else:
                await ctx.send("> There is an error. Contact admin.", delete_after=10)

        except (LocationNotFound, WeatherNotFound) as exc:
            await ctx.send(f"> {exc}", delete_after=10)

        except RequestException as exc:
            log.error(str(exc), exc_info=True)
            if exc.response.status_code == 400:
                await ctx.send("> Unable to find this location.", delete_after=10)
            else:
                await ctx.send("> There is an error. Contact admin.", delete_after=10)


def setup(client: commands.Bot):
    client.add_cog(Weather(client))
