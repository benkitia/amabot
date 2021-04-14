import discord
from discord.ext import commands

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.functions = bot.functions

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, module):
        try:
            self.bot.load_extension(f'cogs.{module}')
        except commands.ExtensionError as e:
            await self.functions.handle_error(ctx, f"Failed to load module {module}", f"{e.__class__.__name__}: {e}")
        else:
            await self.functions.confirm_action(ctx, f"Loaded extension: {module}")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        try:
            self.bot.unload_extension(f'cogs.{module}')
        except commands.ExtensionError as e:
            await self.functions.handle_error(ctx, f"Failed to load module {module}", f"{e.__class__.__name__}: {e}")
        else:
            await self.functions.confirm_action(ctx, f"Unloaded extension: {module}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, module):
        try:
            self.bot.reload_extension(f'cogs.{module}')
        except commands.ExtensionError as e:
            await self.functions.handle_error(ctx, f"Failed to reload module {module}", f"{e.__class__.__name__}: {e}")
        else:
            await self.functions.confirm_action(ctx, f"Reload extension: {module}")

    @commands.command()
    @commands.is_owner()
    async def say(self, ctx, *, content):
        await ctx.send(f"{content}")
        await ctx.message.delete()

    @commands.command()
    async def setpresence(self, ctx, activity_type: int, *, presence: str):
        await self.bot.change_presence(activity = discord.Activity(name = presence, type = activity_type))
        await self.functions.confirm_action(ctx, f"Set presence to {presence}")

    @commands.command(aliases = ['logout'])
    @commands.is_owner()
    async def close(self, ctx):
        await self.functions.confirm_action(ctx, "Logging out...")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def leave(self, ctx, *, guild_id : int):
        try:
            guild = self.bot.get_guild(guild_id)
        except:
            return await self.functions.handle_error(ctx, "Invalid guild", "Make sure you have the correct guild ID")
        try:
            await guild.leave()
            await self.functions.confirm_action(ctx, f"Left guild: {guild.name}")
        except:
            return await self.functions.handle_error(ctx, "Unable to leave guild")

def setup(bot):
    bot.add_cog(Admin(bot))
