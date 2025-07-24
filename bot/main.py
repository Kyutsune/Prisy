"""
PrisyBot - Un bot Discord pour la musique et les utilitaires.
Utilise discord.py pour gérer les interactions Discord et yt-dlp pour la musique.
"""

import asyncio
import logging

import discord
from discord.ext import commands
from discord import Object

from bot.config import GUILD_ID, TOKEN

logging.basicConfig(level=logging.INFO)
# on masque le warning “Privileged message content intent is missing…”
logging.getLogger("discord.ext.commands.bot").setLevel(logging.ERROR)

intents = discord.Intents.default()
intents.message_content = False
intents.voice_states = True


class PrisyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def close(self):
        logging.info("🔌 Shutdown: déconnexion des salons vocaux…")
        for guild in self.guilds:
            vc = guild.voice_client
            if vc and vc.is_connected():
                logging.info("  • Déconnexion de %s", guild.name)
                await vc.disconnect()
        logging.info("🔌 Fermeture du Bot")
        await super().close()


async def main():
    bot = PrisyBot()

    @bot.event
    async def on_ready():
        logging.info("✅ Connecté en tant que %s", bot.user)
        try:
            synced = await bot.tree.sync(guild=Object(id=GUILD_ID))
            logging.info(
                "🔄 %d commandes synchronisées pour le serveur %s",
                len(synced),
                GUILD_ID
            )
        except Exception as e:
            logging.error("❌ Erreur de synchronisation des commandes : %s", e)

    # Chargement asynchrone des cogs
    await bot.load_extension("bot.cogs.utility")
    await bot.load_extension("bot.cogs.music")

    # Démarrage du bot
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
