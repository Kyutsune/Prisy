import discord
from discord.ext import commands
from discord import app_commands

import os
import asyncio
from commandes.play import play, queue, skip, loop as play_loop
from commandes.ping import ping
from commandes.pong import pong
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 748264244822147073  # Ton ID de serveur ici

@bot.event
async def on_ready():
    global play_loop
    play_loop = bot.loop

    guild = discord.Object(id=GUILD_ID)
    tree.add_command(play)
    tree.add_command(queue)
    tree.add_command(ping)
    tree.add_command(pong)
    tree.add_command(skip)
    await tree.sync(guild=guild)
    print(f"Connecté en tant que {bot.user}")
    print("Liste des serveurs :")
    for g in bot.guilds:
        print(f"- {g.name} ({g.id})")

bot.run(TOKEN)
