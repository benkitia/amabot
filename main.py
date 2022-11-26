# Heavily based on this example from the discord.py repo: https://github.com/Rapptz/discord.py/blob/master/examples/advanced_startup.py - Benson

import asyncio
import logging
import os
from typing import List, Optional

import asyncpg
import discord
from aiohttp import ClientSession
from config import Config
from discord.ext import commands


class CustomBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str] = ['cogs.admin', 'cogs.ama'],
        db_pool: asyncpg.Pool,
        web_client: ClientSession,
        testing_guild_id: Optional[int] = Config.guild_id,
        **kwargs,
    ):
        super().__init__(intents=discord.Intents.default(), *args, **kwargs)
        self.db_pool = db_pool
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions
        self.config = Config()

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # Copy in global commands to test with, then sync to the testing guild
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)


async def main():
    # Set up logging
    discord.utils.setup_logging(level=logging.INFO, root=False)

    # Connect to database, create pool , start bot
    async with ClientSession() as our_client, asyncpg.create_pool(dsn=os.getenv('DB_URL', ''), min_size=1, max_size=1, command_timeout=30) as pool:
        async with CustomBot(commands.when_mentioned, db_pool=pool, web_client=our_client) as bot:
            await bot.start(os.getenv('DISCORD_TOKEN', ''))

asyncio.run(main())
