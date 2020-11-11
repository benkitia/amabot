from discord.ext import commands


class Backend(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.errors.MissingAnyRole):
            return await ctx.send(":x: You do not have permission to run this command.")
        if isinstance(error, commands.errors.MissingRole):
            return await ctx.send(":x: You do not have permission to run this command.")


def setup(bot):
    bot.add_cog(Backend(bot))
