import asyncio
import logging

import discord
from discord.ext import commands
import yt_dlp

from bot.config import GUILD_ID, YDL_OPTIONS, FFMPEG_OPTIONS
from bot.stats.stats import increment_play_count

log = logging.getLogger(__name__)


def _create_source(url: str) -> discord.AudioSource:
    """
    Crée une source audio Opus via FFmpeg pour un playback fluide.
    """
    return discord.FFmpegOpusAudio(
        executable="ffmpeg",
        source=url,
        before_options=FFMPEG_OPTIONS["before_options"],
        options=FFMPEG_OPTIONS["options"],
    )


async def _get_audio_source(query: str) -> discord.AudioSource | None:
    """
    Extrait la meilleure URL audio via yt_dlp puis renvoie
    un FFmpegOpusAudio prêt à jouer.
    """
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
        # file et verrou par guild
        self.queues: dict[int, list[tuple[str, str]]] = {}
        self.locks: dict[int, asyncio.Lock] = {}

    async def _play_next(self, guild_id: int, vc: discord.VoiceClient):
        """
        Joue la prochaine piste ou déconnecte si queue vide.
        """
        queue = self.queues.get(guild_id, [])
        if not queue:
            log.info(f"[MusicCog] Queue vide pour guild {guild_id}, disconnect")
            return await vc.disconnect()

        query, title = queue.pop(0)
        log.info(f"[MusicCog] Now playing {title!r} ({query}) in guild {guild_id}")

        # Extraction du flux
        try:
            source = await _get_audio_source(query)
            if source is None:
                raise RuntimeError("No URL in info")
        except Exception as e:
            log.error(f"[MusicCog] Erreur extraction pour {title!r}: {e}", exc_info=True)
            return await self._play_next(guild_id, vc)

        # Callback pour chaîner
        def _after(err: Exception | None):
            if err:
                log.error(f"[MusicCog] Playback error on {title!r}: {err}", exc_info=True)
            # schedule next
            self.bot.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._play_next(guild_id, vc))
            )

        # Lancement non-bloquant
        try:
            vc.play(source, after=_after)
        except Exception as e:
            log.error(f"[MusicCog] Impossible de jouer {title!r}: {e}", exc_info=True)
            return await self._play_next(guild_id, vc)

    @discord.slash_command(
        name="play",
        description="Joue une musique depuis YouTube",
        guild_ids=[GUILD_ID]
    )
    async def play(
        self,
        ctx: discord.ApplicationContext,
        query: discord.Option(str, "Titre ou URL YouTube", required=True)
    ):
        # defer initial response
        await ctx.defer()
        channel = getattr(ctx.author.voice, "channel", None)
        if not channel:
            return await ctx.followup.send(
                "❌ Tu dois être dans un salon vocal.", ephemeral=True
            )

        # Connexion ou déplacement
        vc = ctx.guild.voice_client
        if not vc or not vc.is_connected():
            vc = await channel.connect()
        elif vc.channel.id != channel.id:
            await vc.move_to(channel)

        # Recherche rapide pour le titre + stats
        def search_extract():
            with yt_dlp.YoutubeDL({"format": "bestaudio"}) as ydl:
                res = ydl.extract_info(f"ytsearch:{query}", download=False)
                if not res or "entries" not in res or not res["entries"]:
                    return None
                return res["entries"][0]

        info = await asyncio.to_thread(search_extract)
        if not info:
            return await ctx.followup.send("❌ Aucun résultat trouvé.")

        title = info.get("title", "Musique inconnue")
        increment_play_count(title, ctx.author.name)

        guild_id = ctx.guild.id
        self.queues.setdefault(guild_id, [])
        self.locks.setdefault(guild_id, asyncio.Lock())

        async with self.locks[guild_id]:
            self.queues[guild_id].append((query, title))
            if vc.is_playing():
                await ctx.followup.send(f"⏸️ **{title}** ajoutée à la file.")
            else:
                await self._play_next(guild_id, vc)
                await ctx.followup.send(f"▶️ Lecture de **{title}**")

    @discord.slash_command(
        name="queue",
        description="Affiche la file d'attente (embed)",
        guild_ids=[GUILD_ID]
    )
    async def queue(self, ctx: discord.ApplicationContext):
        guild_id = ctx.guild.id
        q = self.queues.get(guild_id, [])
        if not q:
            return await ctx.respond("🎵 La file est vide.", ephemeral=True)

        embed = discord.Embed(
            title="📝 File d’attente",
            color=discord.Color.blurple()
        )
        for idx, (_, title) in enumerate(q, start=1):
            embed.add_field(name=f"{idx}.", value=title, inline=False)

        await ctx.respond(embed=embed)

    @discord.slash_command(
        name="skip",
        description="Passe à la musique suivante et affiche le titre",
        guild_ids=[GUILD_ID]
    )
    async def skip(self, ctx: discord.ApplicationContext):
        guild_id = ctx.guild.id
        vc = ctx.guild.voice_client
        if not vc or not vc.is_connected():
            return await ctx.respond(
                "❌ Je ne suis pas connecté en vocal.", ephemeral=True
            )
        if not vc.is_playing():
            return await ctx.respond(
                "❌ Rien à passer.", ephemeral=True
            )

        # Préparer le titre à venir
        q = self.queues.get(guild_id, [])
        next_title = q[0][1] if q else None

        # Stopper la piste actuelle (déclenche le callback pour enchaîner)
        vc.stop()

        # Annoncer la suite
        if next_title:
            embed = discord.Embed(
                title="Prochaine piste",
                description=f"▶️ **{next_title}**",
                color=discord.Color.blurple()
            )
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("⏭️ Fin de la file.")

def setup(bot: commands.Bot):
    bot.add_cog(MusicCog(bot))
