"""
PrisyBot - Un bot Discord pour la musique et les utilitaires
Ce bot utilise discord.py pour gérer les interactions avec Discord 
et yt-dlp pour la lecture de musique.
Il inclut des fonctionnalités pour jouer de la musique depuis YouTube, 
gérer une file d'attente,
et interagir avec les salons vocaux.
"""
import logging
import discord
from discord.player import AudioSource
from bot.config import GUILD_ID, TOKEN

# Monkey‑patch pour ignorer AttributeError quand _process est manquant
_original_del = AudioSource.__del__

def _safe_del(self):
    try:
        _original_del(self)
    except AttributeError:
        # Si _process n'existe pas, on passe
        pass

AudioSource.__del__ = _safe_del

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = False       # toujours utile pour limiter les privilèges
intents.voice_states    = True        # indispensable pour gérer les voix

class PrisyBot(discord.Bot):
    """
    PrisyBot - Un bot Discord pour la musique et les utilitaires.
    Ce bot utilise discord.py pour gérer les interactions avec Discord
    et yt-dlp pour la lecture de musique.
    """
    def __init__(self):
        super().__init__(
            intents=intents,
            debug_guilds=[GUILD_ID]
        )

    async def close(self):
        logging.info("🔌 Shutdown: déconnexion des salons vocaux…")
        for guild in self.guilds:
            vc = guild.voice_client
            if vc and vc.is_connected():
                logging.info("Déconnexion de %s", guild.name)
                await vc.disconnect()
        logging.info("🔌 Fermeture du Bot")
        await super().close()

bot = PrisyBot()

@bot.event
async def on_ready():
    """
    Événement appelé lorsque le bot est prêt.
    Affiche un message de confirmation dans la console.
    """
    logging.info("✅ Connecté en tant que %s", bot.user)

@bot.event
async def on_message():
    """
    Événement appelé lorsqu'un message est reçu.
    """
    return

bot.load_extension("bot.cogs.utility")
bot.load_extension("bot.cogs.music")

if __name__ == "__main__":
    bot.run(TOKEN)
