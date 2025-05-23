import discord
from discord import app_commands

GUILD_ID = 748264244822147073

@app_commands.guilds(discord.Object(GUILD_ID))
@app_commands.command(name="pong", description="Test simple")
async def pong(interaction: discord.Interaction):
    print("Pong command executed")
    await interaction.response.send_message("🏓 Ping !")