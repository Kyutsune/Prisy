import asyncio
import yt_dlp
import discord
from bot.config import YDL_OPTIONS, FFMPEG_OPTIONS

class YTDLSource:
    ytdl = yt_dlp.YoutubeDL(YDL_OPTIONS)

    @classmethod
    async def from_query(cls, query: str) -> discord.PCMVolumeTransformer:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(query, download=False))
        url = data["url"]
        return discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            volume=0.5
        )
