"""
Cog utilitaires : ping, pong, leave.
"""

import discord
from discord import app_commands, Interaction, Object
from discord.ext import commands

from bot.config import GUILD_ID


class UtilityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.add_command(self.ping, guild=Object(id=GUILD_ID))
        self.bot.tree.add_command(self.pong, guild=Object(id=GUILD_ID))
        self.bot.tree.add_command(self.leave, guild=Object(id=GUILD_ID))

    @app_commands.command(name="ping", description="Répond Pong !")
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message("Pong !")

    @app_commands.command(name="pong", description="Répond Ping !")
    async def pong(self, interaction: Interaction):
        await interaction.response.send_message("Ping !")

    @app_commands.command(name="leave", description="Fait quitter le bot du salon vocal")
    async def leave(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            return await interaction.response.send_message(
                "❌ Je ne suis pas connecté en vocal.", ephemeral=True
            )
        await interaction.response.send_message("👋 Je quitte le salon vocal")
        await vc.disconnect()


async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))
