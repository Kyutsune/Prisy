import discord
from discord import app_commands

GUILD_ID = 748264244822147073

@app_commands.command(name="ping", description="Test simple")
async def ping(interaction: discord.Interaction):
    print("Ping command executed")
    await interaction.response.send_message("🏓 Pong !")