"""
Module: bot.services.ytdl

Gestion de la récupération et de la conversion du flux audio depuis YouTube.
Cette classe utilise yt_dlp pour extraire les métadonnées et l'URL du flux
sans téléchargement, puis crée un PCMVolumeTransformer prêt à être joué
par un client Discord.
"""
import asyncio
import yt_dlp
import discord
from bot.config import YDL_OPTIONS, FFMPEG_OPTIONS

class YTDLSource:
    """
    Gestion de la récupération et de la conversion du flux audio depuis YouTube.

    Cette classe utilise yt_dlp pour extraire les métadonnées et l'URL du flux
    sans téléchargement, puis crée un PCMVolumeTransformer prêt à être joué
    par un client Discord.
    """
    ytdl = yt_dlp.YoutubeDL(YDL_OPTIONS)

    @classmethod
    async def from_query(cls, query: str) -> discord.PCMVolumeTransformer:
        """
        Extrait l'URL audio de la vidéo YouTube correspondant à la query,
        et retourne un PCMVolumeTransformer à volume fixe (0.5).
        """
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: cls.ytdl.extract_info(query, download=False)
        )
        url = data["url"]
        return discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            volume=0.5
        )
