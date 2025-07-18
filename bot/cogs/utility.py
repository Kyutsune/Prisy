import discord
from discord.ext import commands
from bot.config import GUILD_ID

class UtilityCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="ping",
        description="Répond Pong !",
        guild_ids=[GUILD_ID]
    )
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond("Pong !")  # équivalent de interaction.response.send_message() :contentReference[oaicite:0]{index=0}

    @discord.slash_command(
        name="pong",
        description="Répond Ping !",
        guild_ids=[GUILD_ID]
    )
    async def pong(self, ctx: discord.ApplicationContext):
        await ctx.respond("Ping !")

    @discord.slash_command(
        name="leave",
        description="Fait quitter le bot du salon vocal",
        guild_ids=[GUILD_ID]
    )
    async def leave(self, ctx: discord.ApplicationContext):
        vc = ctx.guild.voice_client
        if not vc or not vc.is_connected():
            return await ctx.respond(
                "❌ Je ne suis pas connecté en vocal.",
                ephemeral=True
            )
        await ctx.respond("👋 Je quitte le salon vocal")
        await vc.disconnect()

def setup(bot: discord.Bot):
    bot.add_cog(UtilityCog(bot))