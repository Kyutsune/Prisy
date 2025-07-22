"""
Module: bot.cogs.utility

Cog pour les commandes utilitaires du bot.
Contient des commandes pour répondre aux ping/pong et pour quitter le salon vocal.
Cette classe utilise py-cord pour gérer les interactions avec les utilisateurs.
"""
import discord
from discord.ext import commands
from bot.config import GUILD_ID

class UtilityCog(commands.Cog):
    """
    Cog pour les commandes utilitaires du bot.
    Contient des commandes pour répondre aux ping/pong et pour quitter le salon vocal.
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="ping",
        description="Répond Pong !",
        guild_ids=[GUILD_ID]
    )
    async def ping(self, ctx: discord.ApplicationContext):
        """Répond Pong !"""
        await ctx.respond("Pong !")

    @discord.slash_command(
        name="pong",
        description="Répond Ping !",
        guild_ids=[GUILD_ID]
    )
    async def pong(self, ctx: discord.ApplicationContext):
        """Répond Ping !"""
        await ctx.respond("Ping !")

    @discord.slash_command(
        name="leave",
        description="Fait quitter le bot du salon vocal",
        guild_ids=[GUILD_ID]
    )
    async def leave(self, ctx: discord.ApplicationContext):
        """
        Fait quitter le bot du salon vocal.
        Si le bot n'est pas connecté à un salon vocal, il répond avec un message d'erreur.
        """
        vc = ctx.guild.voice_client
        if not vc or not vc.is_connected():
            return await ctx.respond(
                "❌ Je ne suis pas connecté en vocal.",
                ephemeral=True
            )
        await ctx.respond("👋 Je quitte le salon vocal")
        await vc.disconnect()

def setup(bot: discord.Bot):
    """
    Fonction pour ajouter le cog UtilityCog au bot.
    """
    bot.add_cog(UtilityCog(bot))
