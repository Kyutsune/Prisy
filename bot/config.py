import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# ID de votre serveur de prédilection (pour le déploiement de slash-commands)
GUILD_ID = int(os.getenv("GUILD_ID", 0))

# Options YouTubeDL & FFmpeg
YDL_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'noplaylist': True,
}
FFMPEG_OPTIONS = {
    'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
        '-reconnect_at_eof 1 -nostdin -thread_queue_size 1024',
    'options': '-vn -bufsize 4096k'
}

# Token Discord (depuis .env)
TOKEN = os.getenv("DISCORD_TOKEN")
