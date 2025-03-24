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

bot_token = os.getenv("DISCORD_TOKEN")

BOT_PREFIX = "%" #command prefix

intents = discord.Intents.all() # changed this to all because its easier than that list
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents) # puts all the bot sthuff together so it can be ran

labid = 1328869164970020864

challonge_obj = Challonge(api_key=os.getenv("CHALLONGE_API_KEY"))

current_tournament_id = ""

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
async def set_report(interaction: discord.Interaction, winner: str, winner_score: str, loser: str, loser_score: str):
    challonge_obj.find_matches(current_tournament_id, ) #tryna search... the thingy... based on the .. thing... 


@bot.tree.command(
    name="set_tournament",
    description="Set the tournament",
    guild=discord.Object(id=labid)
)
async def set_tournament(interaction: discord.Interaction, tournament_id: str):
    # so current_tournament_id is a global variable
    # and so in functions we have to define global variables being changed as `global variable_name`
    # so we can set it
    global current_tournament_id
    current_tournament_id = tournament_id
    await interaction.response.send_message(f"Set tournament to {challonge_obj.show_tournament(tournament_id).attributes.name}")


bot.run(bot_token) #turns on the bot