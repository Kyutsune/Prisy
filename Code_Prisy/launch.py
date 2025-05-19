import discord
from discord.ext import commands
from discord import app_commands

import os
import asyncio
from commandes.play import play, loop as play_loop  
from commandes.ping import ping
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    global play_loop
    play_loop = bot.loop
    
    guild = discord.Object(id=748264244822147073)
    tree.add_command(play)
    tree.add_command(ping)
    await tree.sync(guild=guild)
    print(f"Commandes synchronisées pour le serveur {guild.id}")
    print(f"Connecté en tant que {bot.user}")
    print("Liste des serveurs :")
    for g in bot.guilds:
        print(f"- {g.name} ({g.id})")

bot.run(TOKEN)

