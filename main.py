import discord
from discord.ext import commands
import Config

bot = commands.Bot(command_prefix=Config.PREFIX)

cogs = ['cogs.admin','cogs.ama']

cluster = Config.CLUSTER
db = cluster["amabot"]
questions = db["questions"]

@bot.event
async def on_ready():
    print(f"{bot.user.name} ({bot.user.id}) is online")
    print("______________")
    print("Loading extensions...")
    try:
        for cog in cogs: 
    	    bot.load_extension(cog)
    except commands.ExtensionError as e:
        print(f"Error loading extensions: {e.__class__.__name__}: {e}")
    else:
        print("All extensions loaded successfully.")
    print("______________")
    dynamicconfig = questions.find_one(({"_id":"1","paused":"No"}))
    if dynamicconfig:
        print("Found dynamic config document.")
        print("______________")
    if not dynamicconfig:
        print("No dynamic config document found, creating one...")
        questions.insert_one(({"_id":"1","paused":"No"}))
        print("Created dynamic config document.")    
        print("______________")

bot.run(Config.TOKEN)