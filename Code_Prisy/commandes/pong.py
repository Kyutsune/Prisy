import discord
from discord import app_commands

@app_commands.command(name="pong", description="Test simple")
async def pong(interaction: discord.Interaction):
    print("Pong command executed")
    await interaction.response.send_message("🏓 Ping !")