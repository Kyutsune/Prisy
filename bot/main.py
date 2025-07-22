import asyncio
import logging
import signal
import discord
from discord.ext import commands
from bot.config import GUILD_ID, TOKEN

# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)

# ── Intents ────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = False       # toujours utile pour limiter les privilèges
intents.voice_states    = True        # indispensable pour gérer les voix

# ── Votre Bot personnalisé pour gérer le shutdown proprement ───────
class PrisyBot(discord.Bot):
    def __init__(self):
        super().__init__(
            intents=intents,
            debug_guilds=[GUILD_ID]  # sync automatique de vos slash‑commands 
        )

    async def close(self):
        # Avant de fermer la connexion, déconnecter tous les voice clients
        logging.info("🔌 Shutdown: déconnexion des salons vocaux…")
        for guild in self.guilds:
            vc = guild.voice_client
            if vc and vc.is_connected():
                logging.info(f"  • Déconnexion de {guild.name}")
                await vc.disconnect()
        logging.info("🔌 Fermeture du Bot")
        await super().close()

# ── Instanciation ──────────────────────────────────────────────────
bot = PrisyBot()

# ── Événements ────────────────────────────────────────────────────
@bot.event
async def on_ready():
    logging.info(f"✅ Connecté en tant que {bot.user}")
    # (Pas besoin d'appeler sync_commands, debug_guilds s'en occupe)

@bot.event
async def on_message(message: discord.Message):
    # Vous voulez ignorer tous les messages texte pour ne garder que les slash
    return

# ── Chargement des cogs ────────────────────────────────────────────
bot.load_extension("bot.cogs.utility")
bot.load_extension("bot.cogs.music")

# ── Lancement ─────────────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(TOKEN)