from discord.ext import commands


class AMA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.db = bot.db_pool


async def setup(bot):
    await bot.add_cog(AMA(bot))
