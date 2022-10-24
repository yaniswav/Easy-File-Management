import asyncio
import asqlite
import logging
import config
import logging.handlers
import os

from typing import List, Optional

import discord
from discord.ext import commands
from aiohttp import ClientSession

initial_extensions = config.initial_extensions

class FileManager(commands.Bot):

    def __init__(self, *args, db_pool):  
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=True, users=True)
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
        super().__init__(
            command_prefix="-",
            description="Gestion des CER pour la A2 Informatique",
            pm_help=None,
            help_attrs=dict(hidden=True),
            chunk_guilds_at_startup=False,
            heartbeat_timeout=150.0,
            allowed_mentions=allowed_mentions,
            intents=intents,
            enable_debug_events=True,
            
        )

        self.db_pool = db_pool

    async def setup_hook(self) -> None:

        for extension in initial_extensions:
            print(f"loading {extension}")
            await self.load_extension(extension)

async def main():

    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    async with asqlite.connect('databases/filemanager.db') as pool:
        async with FileManager(commands.when_mentioned, db_pool=pool) as bot:
            await bot.start(config.token)

# For most use cases, after defining what needs to run, we can just tell asyncio to run it:
asyncio.run(main())
