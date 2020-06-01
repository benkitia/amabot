import discord
from discord.ext import commands

token = '' 
prefix = "a!"

bot = commands.Bot(command_prefix=prefix)

cogs = ['cogs.ama','cogs.admin']

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

bot.run(token)