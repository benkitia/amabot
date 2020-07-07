import discord
from discord.ext import commands
import Config

bot = commands.Bot(command_prefix=Config.PREFIX)

cogs = ['cogs.admin','cogs.ama']

@bot.event
async def on_ready():
    print(f"{bot.user.name} ({bot.user.id}) is online")
    print("______________")
    try:
        for cog in cogs: 
    	    bot.load_extension(cog)
    except commands.ExtensionError as e:
        print(f"Error loading extensions: {e.__class__.__name__}: {e}")
    else:
        print("All extensions loaded successfully")
        print("______________")

bot.run(Config.TOKEN)