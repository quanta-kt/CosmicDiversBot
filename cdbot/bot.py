from __future__ import annotations
import aiohttp
import discord
from discord.ext import commands
import os
import sys
import re
import traceback
from motor.motor_asyncio import AsyncIOMotorClient

from . import config


def _prefix_callable(bot: CDBot, message):
    guild_prefix = bot.guild_prefixes.get(message.guild.id) if message.guild else None
    return guild_prefix if guild_prefix else config.PREFIX


extensions = (
    "cdbot.ext.errors",
    "cdbot.ext.help",
    "cdbot.ext.util",
    "cdbot.ext.info",
    "cdbot.ext.config",
)

class CDBot(commands.Bot):
    def __init__(self, debug=False):
        self.debug = debug

        intents = discord.Intents.default()
        allowed_mentions = discord.AllowedMentions.none()
        super().__init__(_prefix_callable, intents=intents,
            allowed_mentions=allowed_mentions,
            case_insensitive=True)

        self.motor_client = AsyncIOMotorClient(os.environ.get("MONGO_URI"))
        if debug:
            self.db = self.motor_client.debug
        else:
            self.db = self.motor_client.production

        self.http_client = None
        self.error_handler_cog = None
        self.guild_prefixes = {}

    async def on_message(self, message):
        await super().on_message(message)
        if self.user.mentioned_in(message):
            prefix = self.guild_prefixes.get(message.guild.id) or config.PREFIX
            await message.channel.send(
                f"My prefix is: {prefix}\n"
                + f"Use {prefix}help to get a list of available commands!",
                reference=message,
                mention_author=True)

    async def start(self, *args, **kwargs):
        if self.http_client is None:
            self.http_client = aiohttp.ClientSession()

        # Loading extensions here to ensure http_client is initialized before cogs are added
        for ext in extensions:
            self.load_extension(ext)
        self.error_handler_cog = self.get_cog("ErrorHandler")

        # Load prefixes
        async for prefix_doc in self.db.prefixes.find():
            self.guild_prefixes[prefix_doc["_id"]] = prefix_doc["prefix"]
        return await super().start(*args, **kwargs)

    async def close(self):
        await self.http_client.close()
        return await super().close()

    async def on_error(self, event_method, *args, **kwargs):
        _, e, tb  = sys.exc_info()
        await self.error_handler_cog.report_crash(
            f"Unexpected exception in event: {event_method}\n"
            f"Event args: {args}\n"
            f"Event kwargs: {kwargs}",
            "".join(traceback.format_tb(tb)) + f"\n{e}")
