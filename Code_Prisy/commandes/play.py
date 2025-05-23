import discord
from discord import app_commands
import yt_dlp
import asyncio

from commandes.stats.stats import increment_play_count

GUILD_ID = 748264244822147073

YDL_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'noplaylist': True,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -reconnect_at_eof 1 -nostdin -thread_queue_size 1024',
    'options': '-vn -bufsize 4096k'
}

loop = None
queues = {}
locks = {}

def create_source(url):
    source = discord.FFmpegPCMAudio(
        executable="ffmpeg",
        source=url,
        before_options=FFMPEG_OPTIONS['before_options'],
        options=FFMPEG_OPTIONS['options']
    )
    return discord.PCMVolumeTransformer(source, volume=0.5)

async def get_audio_source(query):
    def extract():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)
            if info is not None and 'entries' in info:
                info = info['entries'][0]
            return info

    info = await asyncio.to_thread(extract)
    if info is None or 'url' not in info:
        return None
    url = info['url']
    return create_source(url)

async def play_next(guild_id, voice_client):
    global loop
    print(f"[play_next] File d'attente restante : {len(queues.get(guild_id, []))}")

    if loop is None:
        loop = asyncio.get_event_loop()

    if guild_id in queues and queues[guild_id]:
        next_query, next_title = queues[guild_id].pop(0)
        source = await get_audio_source(next_query)
        if source is None:
            await play_next(guild_id, voice_client)
            return

        def after_playing(error):
            if loop:
                asyncio.run_coroutine_threadsafe(play_next(guild_id, voice_client), loop)

        voice_client.play(source, after=after_playing)
        await asyncio.sleep(0.1)
    else:
        await voice_client.disconnect()
        if guild_id in locks:
            del locks[guild_id]

@app_commands.command(name="play", description="Joue une musique depuis YouTube")
@app_commands.describe(query="Titre ou lien YouTube de la musique")
async def play(interaction: discord.Interaction, query: str):
    global loop
    if loop is None and hasattr(interaction.client, 'loop'):
        loop = interaction.client.loop

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
    if not voice_client or not voice_client.is_connected():
        voice_client = await voice_channel.connect()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        result = await asyncio.to_thread(lambda: ydl.extract_info(f"ytsearch:{query}", download=False))
        if result is None or 'entries' not in result or not result['entries']:
            await interaction.followup.send("❌ Aucun résultat trouvé.")
            return
        info = result['entries'][0]
        title = info.get('title', 'musique inconnue')
        increment_play_count(title, member.name)

    guild_id = interaction.guild.id
    if guild_id not in queues:
        queues[guild_id] = []
    if guild_id not in locks:
        locks[guild_id] = asyncio.Lock()

    async with locks[guild_id]:
        if voice_client.is_playing():
            queues[guild_id].append((query, title))
            await interaction.followup.send(f"⏸️ **{title}** ajoutée à la file.")
        else:
            source = await get_audio_source(query)
            if source is None:
                await interaction.followup.send("❌ Impossible de récupérer la source audio.")
                return

            def after_playing(error):
                if loop:
                    asyncio.run_coroutine_threadsafe(play_next(guild_id, voice_client), loop)

            voice_client.play(source, after=after_playing)
            await interaction.followup.send(f"▶️ Lecture de **{title}**")

@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.command(name="queue", description="Renvoie la file d'attente")
async def queue(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.guild is None:
        await interaction.followup.send("❌ Cette commande doit être utilisée dans un serveur.")
        return
    file = queues.get(interaction.guild.id, [])
    if not file:
        await interaction.followup.send("🎵 File d’attente vide.")
    else:
        texte = "\n".join([f"{i+1}. {titre}" for i, (_, titre) in enumerate(file)])
        await interaction.followup.send(f"🎶 File d’attente :\n{texte}")

@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.command(name="skip", description="Passe à la musique suivante")
async def skip(interaction: discord.Interaction):
    await interaction.response.defer()

    if interaction.guild is None:
        await interaction.followup.send("❌ Cette commande doit être utilisée dans un serveur.")
        return

    guild_id = interaction.guild.id
    voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

    if not voice_client or not voice_client.is_connected():
        await interaction.followup.send("❌ Je ne suis pas connecté à un salon vocal.")
        return

    if not voice_client.is_playing():
        await interaction.followup.send("❌ Aucune musique en cours de lecture.")
        return

    # Stoppe la musique actuelle, ce qui déclenche `after_playing` → `play_next`
    if guild_id in locks:
        async with locks[guild_id]:
            if queues.get(guild_id):
                next_title = queues[guild_id][0][1] if len(queues[guild_id]) >= 1 else "?"
                await interaction.followup.send(f"⏭️ Passage à la musique suivante : **{next_title}**.")
                voice_client.stop()
            else:
                await interaction.followup.send(f"⏭️ Aucune musique dans la file d'attente, déconnexion.")
                voice_client.stop()
