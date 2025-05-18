import discord
from discord import app_commands
import yt_dlp
import asyncio

from commandes.stats.stats import increment_play_count

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# La variable loop pour stocker la boucle asyncio principale
loop = None

def create_source(url):
    return discord.FFmpegPCMAudio(
        executable="ffmpeg",
        source=url,
        before_options=FFMPEG_OPTIONS['before_options'],
        options=FFMPEG_OPTIONS['options']
    )

async def get_audio_source(query):
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(query, download=False)
        if info is not None and 'entries' in info:
            info = info['entries'][0]
        if info is None or 'url' not in info:
            return None
        url = info['url']
        return create_source(url)

queues = {}
locks = {}

async def play_next(guild_id, voice_client):
    global loop
    print(f"[play_next] On va jouer la prochaine musique, nombre de musique encore dans la file d'attente : {len(queues.get(guild_id, []))}")
    
    # Vérification de sécurité pour s'assurer que loop n'est pas None
    if loop is None:
        print("[play_next] ERREUR: La boucle asyncio est None, utilisation de la boucle courante")
        loop = asyncio.get_event_loop()
    
    if guild_id in queues and queues[guild_id]:
        next_query, next_title = queues[guild_id].pop(0)
        print(f"[play_next] Lecture de : {next_title}")

        source = await get_audio_source(next_query)
        if source is None:
            print("[play_next] Impossible de récupérer la source audio, lecture suivante")
            await play_next(guild_id, voice_client)
            return

        def after_playing(error):
            print("[play_next] Musique terminée, appel à la suivante")
            if error:
                print(f"[play_next] Erreur lors de la lecture : {error}")
            
            # Vérification de la boucle avant d'appeler run_coroutine_threadsafe
            if loop is not None:
                asyncio.run_coroutine_threadsafe(play_next(guild_id, voice_client), loop)
            else:
                print("[play_next] ERREUR CRITIQUE: La boucle asyncio est None, impossible de continuer la file d'attente")

        voice_client.play(source, after=after_playing)
        await asyncio.sleep(0.1)
    else:
        print(f"[play_next] Queue vide, déconnexion")
        await voice_client.disconnect()
        if guild_id in locks:
            del locks[guild_id]

@app_commands.command(name="play", description="Joue une musique depuis YouTube")
@app_commands.describe(query="Titre ou lien YouTube de la musique")
async def play(interaction: discord.Interaction, query: str):
    global loop
    
    # Assignation de la boucle à chaque appel de commande pour garantir sa présence
    if loop is None and hasattr(interaction.client, 'loop'):
        loop = interaction.client.loop
        print(f"[play] Boucle assignée depuis interaction.client: {loop}")

    await interaction.response.defer()

    if interaction.guild is None:
        await interaction.followup.send("❌ Cette commande doit être utilisée dans un serveur.")
        return

    member = interaction.guild.get_member(interaction.user.id)
    voice_channel = member.voice.channel if member and member.voice else None
    if not voice_channel:
        await interaction.followup.send("❌ Tu dois être dans un salon vocal.")
        return

    voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
    if not isinstance(voice_client, discord.VoiceClient) or not voice_client.is_connected():
        voice_client = await voice_channel.connect()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        result = ydl.extract_info(f"ytsearch:{query}", download=False)
        if result is None or 'entries' not in result or not result['entries']:
            await interaction.followup.send("❌ Aucun résultat trouvé pour cette recherche.")
            return
        info = result['entries'][0]
        title = info.get('title', 'musique inconnue')
        increment_play_count(title)

    guild_id = interaction.guild.id

    if guild_id not in queues:
        queues[guild_id] = []
    if guild_id not in locks:
        locks[guild_id] = asyncio.Lock()

    async with locks[guild_id]:
        if voice_client.is_playing():
            queues[guild_id].append((query, title))
            await interaction.followup.send(f"⏸️ **{title}** ajoutée à la file d'attente.")
        else:
            source = await get_audio_source(query)
            if source is None:
                await interaction.followup.send("❌ Impossible de récupérer la source audio.")
                return

            def after_playing(error):
                print("[play] Musique terminée, lancement de la suivante")
                if error:
                    print(f"[play] Erreur lors de la lecture : {error}")
                
                # Vérification de la boucle avant d'appeler run_coroutine_threadsafe
                if loop is not None:
                    asyncio.run_coroutine_threadsafe(play_next(guild_id, voice_client), loop)
                else:
                    print("[play] ERREUR CRITIQUE: La boucle asyncio est None, impossible de continuer la file d'attente")

            voice_client.play(source, after=after_playing)
            await interaction.followup.send(f"▶️ Lecture de **{title}**")