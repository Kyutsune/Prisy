import asyncio
import logging
import signal
import discord
from discord.ext import commands
from bot.config import GUILD_ID, TOKEN

logging.basicConfig(level=logging.INFO)
intents = discord.Intents.default()
intents.message_content = False
bot = commands.Bot(command_prefix=None, intents=intents)

@bot.event
async def on_message(message: discord.Message):
    return  # Ignore all messages to prevent command processing

@bot.event
async def on_ready():
    logging.info(f"✅ Connecté en tant que {bot.user}")
    synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    logging.info(f"📤 {len(synced)} commandes synchronisées pour la guilde : {[cmd.name for cmd in synced]}")

async def _shutdown():
    logging.info("🔌 Shutdown: déconnexion des salons vocaux…")
    # déconnecte des vocaux sur chaque guild
    for guild in bot.guilds:
        vc = guild.voice_client
        if vc and vc.is_connected():
            logging.info(f"  • Déconnexion de {guild.name}")
            await vc.disconnect()
    logging.info("🔌 Fermeture du Bot")
    await bot.close()

async def main():
    # charger les cogs
    for cog in ("bot.cogs.utility", "bot.cogs.music"):
        await bot.load_extension(cog)

    # installer un handler de signal SIGINT (Ctrl+C)
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(
        signal.SIGINT,
        lambda: asyncio.create_task(_shutdown())
    )

    # démarrer le bot (bloquant jusqu'à bot.close())
    await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # En cas de SIGINT avant que notre handler ne prenne la main
        logging.info("🛑 Ctrl+C détecté, arrêt immédiat.")
