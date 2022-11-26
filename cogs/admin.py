import discord
from discord.ext import commands


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, module):
        try:
            self.bot.load_extension(f'cogs.{module}')
        except commands.ExtensionError as e:
            await ctx.send(f"Failed to load module {module}", f"{e.__class__.__name__}: {e}")
        else:
            ctx.send(f"Loaded extension: {module}")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        try:
            self.bot.unload_extension(f'cogs.{module}')
        except commands.ExtensionError as e:
            await ctx.send(f"Failed to load module {module}", f"{e.__class__.__name__}: {e}")
        else:
            ctx.send(f"Unloaded extension: {module}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, module):
        try:
            self.bot.reload_extension(f'cogs.{module}')
        except commands.ExtensionError as e:
            await ctx.send(f"Failed to reload module {module}", f"{e.__class__.__name__}: {e}")
        else:
            ctx.send(f"Reload extension: {module}")

    @commands.command()
    @commands.is_owner()
    async def say(self, ctx, *, content):
        await ctx.send(f"{content}")
        await ctx.message.delete()

    @commands.command()
    async def setpresence(self, ctx, activity_type: int, *, presence: str):
        await self.bot.change_presence(activity=discord.Activity(name=presence, type=activity_type))
        ctx.send(f"Set presence to {presence}")

    @commands.command(aliases=['logout'])
    @commands.is_owner()
    async def close(self, ctx):
        ctx.send("Logging out...")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def leave(self, ctx, *, guild_id: int):
        try:
            guild = self.bot.get_guild(guild_id)
        except:
            return await ctx.send("Invalid guild", "Make sure you have the correct guild ID")
        try:
            await guild.leave()
            ctx.send(f"Left guild: {guild.name}")
        except:
            return await ctx.send("Unable to leave guild")


async def setup(bot):
    await bot.add_cog(Admin(bot))
