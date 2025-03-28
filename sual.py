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

signup_channels = []

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
async def set_report(interaction: discord.Interaction, winner: str, winner_score: int, loser: str, loser_score: int):
    # we get every single match in the tournament
    
    matches = challonge_obj.find_matches(current_tournament_id, per_page=99999)
    for match in matches:
        # make sure to not edit the match if its complete
        if match.attributes.state == "complete":
            continue
        # try block in case some attributes dont exist
        try:
            # initialize player 1 and player 2
            p1_id = ""
            p2_id = ""
            # go through the points by participant attribute to get the ids
            # there is no better way to do this
            for x in match.attributes.points_by_participant:
                if p1_id == "":
                    p1_id = str(x.participant_id)
                else:
                    p2_id = str(x.participant_id)
            # get the player objects
            player_1 = challonge_obj.show_participant(current_tournament_id, p1_id)
            player_2 = challonge_obj.show_participant(current_tournament_id, p2_id)

            # validation to make sure we are modifying the right set, and to set the winner and loser ids
            if player_1.attributes.name == winner and player_2.attributes.name == loser:
                winner_id = player_1.id
                loser_id = player_2.id

            elif player_2.attributes.name == winner and player_1.attributes.name == loser:
                winner_id = player_2.id
                loser_id = player_1.id

            else:
                continue

            # the challonge v2 api is super weird
            # im gonna make this code better later but for now it lowkey sucks, just dm me with your questions `jozz024`
            winner_str_score = "1,1" if loser_score == 0 else "1,0,1"
            loser_str_score = "0,0" if loser_score == 0 else "0,1,0"

            match_attributes = {
                "match": [
                    {
                        "participant_id": winner_id,
                        "score_set": winner_str_score,
                        "rank": 1,
                        "advancing": True
                    },
                    {
                        "participant_id": loser_id,
                        "score_set": loser_str_score,
                        "rank": 2,
                        "advancing": False
                    }
                ],
                "tie": False,
            }

            # set the match to the reported score
            challonge_obj.update_match(current_tournament_id, match.id, match_attributes)
            # send a message to the discord channel
            await interaction.response.send_message(f"Reported {winner} vs {loser} with score {winner_score} - {loser_score}!")
            return
        except AttributeError:
            continue

@bot.tree.command(
    name="set_tournament",
    description="Set the tournament",
    guild=discord.Object(id=labid)
)
async def set_tournament(interaction: discord.Interaction, tournament_id: str):
    # so current_tournament_id is a global variable
    # and so in functions we have to define global variables being changed as `global variable_name`
    # so we can set it
    if any(role.permissions.administrator for role in interaction.user.roles):
        global current_tournament_id
        current_tournament_id = tournament_id
        await interaction.response.send_message(f"Set tournament to {challonge_obj.show_tournament(tournament_id).attributes.name}")
    else:
        await interaction.response.send_message("You need to be an Admin to use this command!")

@bot.tree.command(
    name="advance_stage",
    description="Advance the tournament to the final stage",
    guild=discord.Object(id=labid)
)
async def advance_stage(interaction: discord.Interaction):
    if any(role.permissions.administrator for role in interaction.user.roles):
     challonge_obj.change_state_tournament(current_tournament_id, "finalize_group_stage")

     challonge_obj.change_state_tournament(current_tournament_id, "start")

     await interaction.response.send_message(f"Advanced tournament to the final stage")
    else:
        await interaction.response.send_message("You need to be an Admin to use this command!")


# iammartyb here, I'm thinking what I'm gonna do for signups is, they enabled signups, and people will then signup with a command. Then with a seperate command, it dms all the users to check in with a button
# upon checking in, they are added to a list with their character they signed up with, and then when the bracket generator command is enabled, they all are added.



@bot.tree.command(
    name="read_signups",
    description="Set the tournament",
    guild=discord.Object(id=labid)
)
async def set_singups(interaction: discord.Interaction, tournament_id: str, signups_channel_id: str):
    server_id = interaction.user.guild.id
    guild = bot.getguild(server_id)
    signup_channels.append(signups_channel_id)
    for x in signup_channels:
        channel = guild.get_channel(x)
        print(f"{channel}")
        # for message in channel.history(limit=None)
            



bot.run(bot_token) #turns on the bot