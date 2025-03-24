import discord
import challonge
import dotenv
from dotenv import load_dotenv
import os
from challonge import Challonge
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Bot

load_dotenv()  # take environment variables from .env.

bot_token = os.getenv("TOKEN")

BOT_PREFIX = "%" #command prefix

intents = discord.Intents.all() # changed this to all because its easier than that list
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents) # puts all the bot sthuff together so it can be ran

labid = 1328869164970020864

challonge_obj = Challonge("7BXgk4lOBgdNAomWBfbUS4E7fgRZrDVElx82Wd7x")



## changed this to on_ready because i realized what it was doing
@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=labid))
    print(bot.user.name + " is online!") # prints to console when the bot is online

## figured out that the tree was wrong because bot already defines a tree
@bot.tree.command(
    name="set_report", # cannot have spaces in command names
    description="Report da set",
    guild=discord.Object(id=labid)
)
async def set_report(interaction: discord.Interaction, Winner: str, Loser: str, ):
    await interaction.response.send_message("Hello!")



bot.run(bot_token) #turns on the bot