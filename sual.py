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

discord_token = os.getenv("TOKEN")

BOT_PREFIX = "%" #command prefix

intents = discord.Intents.default() #sets up the bots permissons (kinda) 
intents.members = True
intents.message_content = True
intents.guilds = True
intents.messages = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents) # puts all the bot sthuff together so it can be ran
tree = app_commands.CommandTree(bot)

labid = 1328869164970020864

challonge_obj = Challonge("7BXgk4lOBgdNAomWBfbUS4E7fgRZrDVElx82Wd7x")


@bot.event
async def on_message(message):
    guildid = message.guild.id
    await tree.sync(guild=discord.Object(id=guildid))
    print("Ready!")


@tree.command(
    name="Set Report",
    description="Report da set",
    guild=discord.Object(id=1328869164970020864)
)
async def first_command(interaction):
    await interaction.response.send_message("Hello!")
 


bot.run(bot_token) #turns on the bot