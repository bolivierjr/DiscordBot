import html
import logging
from typing import Dict, Optional, Union

from discord.ext import commands
from marshmallow import ValidationError
from peewee import DatabaseError, IntegrityError
from requests import RequestException

from ..models.users import User, UserSchema
from ..utils.errors import LocationNotFound, WeatherNotFound
from ..utils.services import query_current_weather, query_location
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
        arg.strip() if arg is not None else arg
        try:
            optional_user = html.escape(arg) if arg else str(ctx.message.author)
            user: Union[User, AnonymousUser] = get_user(optional_user)

            if not arg and isinstance(user, AnonymousUser):
                await ctx.send(f"No weather location set by {ctx.message.author.mention}")

            elif not arg:
                weather: str = query_current_weather(arg, user)
                await ctx.send(weather)

            else:
                deserialized_location: Dict[str, str] = UserSchema().load({"location": html.escape(arg)}, partial=True)
                weather: str = query_current_weather(deserialized_location["location"], user)
                await ctx.send(weather)

        except ValidationError as exc:
            log.error(str(exc), exc_info=True)
            if "location" in exc.messages:
                message = exc.messages["location"][0]
            await ctx.send(f"> {message}", delete_after=10)

        except (DatabaseError, IntegrityError) as exc:
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

    @commands.command()
    async def setweather(self, ctx: commands.Context, arg: str):
        format = 1
        arg.strip() if arg is not None else arg
        try:
            deserialized_location: Dict[str, str] = UserSchema().load(
                {"location": html.escape(arg), "format": format}, partial=True,
            )
            geo: Dict[str, str] = query_location(deserialized_location["location"])
            geo.update({"nick": str(ctx.message.author), "format": format})
            if geo["location"] is None:
                raise LocationNotFound("Unable to find this location.")

            user_schema: Dict[str, str] = UserSchema().load(geo)
            user, created = User.get_or_create(
                nick=str(ctx.message.author),
                defaults={
                    "format": user_schema["format"],
                    "location": user_schema["location"],
                    "region": user_schema["region"],
                    "coordinates": user_schema["coordinates"],
                },
            )

            # If created is a boolean of 0, it means it found a user.
            # Updates the user fields and saves to db.
            if not created:
                user.format = user_schema["format"]
                user.location = user_schema["location"]
                user.region = user_schema["region"]
                user.coordinates = user_schema["coordinates"]
                user.save()

            units = "imperial" if format == 1 else "metric"
            log.info(f"{ctx.message.author} set their location to {arg}")
            await ctx.send(f"{ctx.message.author.mention} set their weather to {units} first and {arg}.")

        except ValidationError as exc:
            if "location" in exc.messages:
                message = exc.messages["location"][0]
                await ctx.send(f"> {message}", delete_after=10)
            elif "format" in exc.messages:
                message = exc.messages["format"][0]
                await ctx.send(f"> {message}", delete_after=10)
            log.error(str(exc), exc_info=True)

        except (DatabaseError, IntegrityError) as exc:
            log.error(str(exc), exc_info=True)
            if "not created" in str(exc):
                await ctx.send(f"> {exc}", delete_after=10)
            elif "no such table" in str(exc):
                await ctx.send("> Users db not created yet", delete_after=10)
            else:
                await ctx.send("> There is an error. Contact admin.", delete_after=10)

        except LocationNotFound as exc:
            await ctx.send(f"> {exc}", delete_after=10)

        except RequestException as exc:
            log.error(str(exc), exc_info=True)
            await ctx.send("> Unable to find this location.", delete_after=10)


def setup(client: commands.Bot):
    client.add_cog(Weather(client))
