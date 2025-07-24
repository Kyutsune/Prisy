"""
Cog de musique : play, queue, skip.
Utilise yt-dlp pour extraire les flux audio et discord.py pour la lecture.
"""

import asyncio
import logging

import discord
from discord import app_commands, Interaction, Object
from discord.ext import commands
import yt_dlp
from yt_dlp.utils import DownloadError

from bot.config import GUILD_ID, YDL_OPTIONS, FFMPEG_OPTIONS
from bot.stats.stats import increment_play_count

log = logging.getLogger(__name__)


def _create_source(url: str) -> discord.AudioSource:
    return discord.FFmpegOpusAudio(
        executable="ffmpeg",
        source=url,
        before_options=FFMPEG_OPTIONS["before_options"],
        options=FFMPEG_OPTIONS["options"],
    )


async def _get_audio_source(query: str) -> discord.AudioSource | None:
    def extract():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)
            if info and "entries" in info:
                info = info["entries"][0]
            return info

    info = await asyncio.to_thread(extract)
    if not info or "url" not in info:
        return None
    return _create_source(info["url"])


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: dict[int, list[tuple[str, str]]] = {}
        self.locks: dict[int, asyncio.Lock] = {}
        # Enregistrement des slash commands
        self.bot.tree.add_command(self.play, guild=Object(id=GUILD_ID))
        self.bot.tree.add_command(self.queue, guild=Object(id=GUILD_ID))
        self.bot.tree.add_command(self.skip, guild=Object(id=GUILD_ID))

    async def _play_next(self, guild_id: int, vc: discord.VoiceClient):
        queue = self.queues.get(guild_id, [])
        if not queue:
            log.info("[MusicCog] Queue vide pour guild %s, disconnect", guild_id)
            return await vc.disconnect()

        query, title = queue.pop(0)
        log.info("[MusicCog] Now playing %r (%s) in guild %s", title, query, guild_id)

        try:
            source = await _get_audio_source(query)
            if source is None:
                raise RuntimeError("No URL in info")
        except (DownloadError, RuntimeError, asyncio.TimeoutError, discord.ClientException) as e:
            log.error("[MusicCog] Erreur extraction pour %r: %s", title, e, exc_info=True)
            return await self._play_next(guild_id, vc)

        def _after(err: Exception | None):
            if err:
                log.error("[MusicCog] Playback error on %r: %s", title, err, exc_info=True)
            self.bot.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._play_next(guild_id, vc))
            )

        try:
            vc.play(source, after=_after)
        except (DownloadError, RuntimeError, asyncio.TimeoutError, discord.ClientException) as e:
            log.error("[MusicCog] Playback failure for %r: %s", title, e, exc_info=True)
            return await self._play_next(guild_id, vc)

    @app_commands.command(name="play", description="Joue une musique depuis YouTube")
    async def play(self, interaction: Interaction, query: str):
        await interaction.response.defer()
        channel = getattr(interaction.user.voice, "channel", None)
        if not channel:
            return await interaction.response.send_message(
                "❌ Tu dois être dans un salon vocal.", ephemeral=True
            )

        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            try:
                vc = await channel.connect()
            except (discord.ClientException, discord.errors.ConnectionClosed, asyncio.TimeoutError) as e:
                log.error("[MusicCog] Échec de connexion vocale : %s", e, exc_info=True)
                return await interaction.followup.send(
                    "❌ Impossible de rejoindre le salon vocal.", ephemeral=True
                )
        elif vc.channel.id != channel.id:
            await vc.move_to(channel)

        def search_extract():
            with yt_dlp.YoutubeDL({"format": "bestaudio"}) as ydl:
                res = ydl.extract_info(f"ytsearch:{query}", download=False)
                if not res or "entries" not in res or not res["entries"]:
                    return None
                return res["entries"][0]

        info = await asyncio.to_thread(search_extract)
        if not info:
            return await interaction.followup.send("❌ Aucun résultat trouvé.", ephemeral=True)

        title = info.get("title", "Musique inconnue")
        increment_play_count(title, interaction.user.name)

        guild_id = interaction.guild.id
        self.queues.setdefault(guild_id, [])
        self.locks.setdefault(guild_id, asyncio.Lock())

        async with self.locks[guild_id]:
            self.queues[guild_id].append((query, title))
            if vc.is_playing():
                await interaction.followup.send(f"⏸️ **{title}** ajoutée à la file.", ephemeral=True)
            else:
                await self._play_next(guild_id, vc)
                await interaction.followup.send(f"▶️ Lecture de **{title}**")

    @app_commands.command(name="queue", description="Affiche la file d'attente")
    async def queue(self, interaction: Interaction):
        guild_id = interaction.guild.id
        q = self.queues.get(guild_id, [])
        if not q:
            return await interaction.response.send_message("🎵 La file est vide.", ephemeral=True)

        embed = discord.Embed(title="📝 File d’attente", color=discord.Color.blurple())
        for idx, (_, title) in enumerate(q, start=1):
            embed.add_field(name=f"{idx}.", value=title, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="skip", description="Passe à la musique suivante")
    async def skip(self, interaction: Interaction):
        guild_id = interaction.guild.id
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            return await interaction.response.send_message(
                "❌ Je ne suis pas connecté en vocal.", ephemeral=True
            )
        if not vc.is_playing():
            return await interaction.response.send_message("❌ Rien à passer.", ephemeral=True)

        q = self.queues.get(guild_id, [])
        next_title = q[0][1] if q else None
        vc.stop()

        if next_title:
            embed = discord.Embed(
                title="Prochaine piste",
                description=f"▶️ **{next_title}**",
                color=discord.Color.blurple()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("⏭️ Fin de la file.")

async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))
