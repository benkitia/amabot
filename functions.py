import discord
from discord.ext import commands
import os

class Functions:

    async def handle_error(self, ctx, description : str, troubleshooting : str = None):
        await ctx.send(f":warning: Something went wrong: {description}. {troubleshooting}")
    
    async def confirm_action(self, ctx, description : str, additional_info: str = None):
        await ctx.send(f":white_check_mark: {description}. {additional_info}")