import os
import re
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp
import logging
import asyncio
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Carrega variáveis do arquivo .env
load_dotenv()

# Configuração da API do Spotify
spotify = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

# Opções para o FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class Music(commands.Cog):
    """
    Módulo de música com integração ao Spotify e YouTube, gerenciamento de fila e notificações visuais.
    
    Funcionalidades:
      - Conectar/desconectar do canal de voz.
      - Tocar músicas via link ou termo de pesquisa.
      - Converter links do Spotify em query para o YouTube.
      - Manter uma fila de reprodução com indicação de posição e solicitante.
      - Comandos para pular (skip), pausar (pause), retomar (resume) e parar (stop) a reprodução.
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.music_queue: list[dict[str, any]] = []  # Fila de reprodução

    def get_youtube_url(self, query: str) -> tuple[str | None, str | None, str | None, str | None]:
        """
        Busca uma música no YouTube usando yt_dlp.
        Se a query não for um link, é prefixada com "ytsearch:".
        
        Retorna:
          - audio_url: URL do áudio
          - title: Título da música
          - thumbnail: URL da imagem (thumbnail)
          - webpage_url: URL da página do vídeo
        """
        if not query.startswith("http"):
            query = f"ytsearch:{query}"
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                audio_url = info.get('url')
                title = info.get('title')
                thumbnail = info.get('thumbnail')
                webpage_url = info.get('webpage_url')
                return audio_url, title, thumbnail, webpage_url
            except Exception as e:
                logging.error("Erro na extração do YouTube: %s", e)
                return None, None, None, None

    def get_spotify_track(self, url: str) -> tuple[str | None, str | None]:
        """
        Extrai informações de uma faixa do Spotify e converte para uma query do YouTube.
        
        Retorna:
          - search_query: String no formato "Artista - Título"
          - thumbnail: URL da capa do álbum (se disponível)
        """
        try:
            match = re.search(r"track/([a-zA-Z0-9]+)", url)
            if not match:
                logging.error("URL do Spotify inválida: %s", url)
                return None, None
            track_id = match.group(1)
            track_info = spotify.track(track_id)
            if not track_info:
                logging.error("Não foi possível obter informações do Spotify para o ID: %s", track_id)
                return None, None
            artist = track_info['artists'][0]['name']
            title = track_info['name']
            thumbnail = None
            if track_info.get('album') and track_info['album'].get('images'):
                images = track_info['album']['images']
                if images:
                    thumbnail = images[0]['url']
            search_query = f"{artist} - {title}"
            logging.info("🎵 Música encontrada no Spotify: %s", search_query)
            return search_query, thumbnail
        except Exception as e:
            logging.error("Erro na extração do Spotify: %s", e)
            return None, None

    async def start_song(self, ctx: commands.Context, song: dict[str, any]) -> None:
        """
        Inicia a reprodução de uma música usando FFmpegPCMAudio.
        Ao término, chama play_next para avançar na fila.
        """
        source = FFmpegPCMAudio(song['audio_url'], **FFMPEG_OPTIONS)
        def after_playing(error):
            if error:
                logging.error("Erro ao tocar a música: %s", error)
            asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
        ctx.voice_client.play(source, after=after_playing)
        
        # Cria um embed para "Agora Tocando" com destaque no título e imagem ampliada
        embed = discord.Embed(
            title="🎵 Agora Tocando",
            description=f"__**{song['title']}**__",
            color=discord.Color.purple()
        )
        embed.set_author(name=f"Pedido por {song['requester']}", icon_url=song['requester_avatar'])
        if song.get('webpage_url'):
            embed.add_field(name="Fonte", value=song['webpage_url'], inline=False)
        if song.get('thumbnail'):
            # Exibe a imagem em tamanho maior usando set_image
            embed.set_image(url=song['thumbnail'])
        await ctx.send(embed=embed)

    async def play_next(self, ctx: commands.Context) -> None:
        """Toca a próxima música na fila, se houver."""
        if self.music_queue:
            next_song = self.music_queue.pop(0)
            await self.start_song(ctx, next_song)
        else:
            logging.info("Fila de reprodução vazia.")

    @commands.command(name="join", help="Faz o bot entrar no canal de voz.")
    async def join(self, ctx: commands.Context) -> None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
            await ctx.send("🎶 Conectado ao canal de voz!")
        else:
            await ctx.send("Você precisa estar em um canal de voz para usar esse comando.")

    @commands.command(name="leave", help="Faz o bot sair do canal de voz.")
    async def leave(self, ctx: commands.Context) -> None:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Desconectado do canal de voz!")
        else:
            await ctx.send("Não estou conectado a nenhum canal de voz.")

    @commands.command(name="play", help="Toca uma música a partir de uma URL ou termo de pesquisa.")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        """
        Adiciona uma música à fila e inicia a reprodução se não houver música tocando.
        Se a query for do Spotify, converte-a para uma query do YouTube.
        """
        if not ctx.voice_client or (ctx.author.voice and ctx.author.voice.channel != ctx.voice_client.channel):
            await ctx.invoke(self.join)
            await asyncio.sleep(1)

        search_query = query
        thumbnail = None
        is_spotify = "spotify.com/track" in query

        if is_spotify:
            search_query, thumbnail = self.get_spotify_track(query)
            if not search_query:
                await ctx.reply("❌ Não consegui obter informações da música no Spotify. Tente novamente.")
                try:
                    await ctx.message.delete()
                except Exception as e:
                    logging.error("Erro ao deletar mensagem: %s", e)
                return

        audio_url, title, yt_thumbnail, webpage_url = self.get_youtube_url(search_query)
        if not audio_url:
            source = "Spotify" if is_spotify else "YouTube"
            await ctx.reply(f"❌ Não encontrei a música no {source}. Verifique o nome ou link e tente novamente.")
            try:
                await ctx.message.delete()
            except Exception as e:
                logging.error("Erro ao deletar mensagem: %s", e)
            return

        final_thumbnail = yt_thumbnail if yt_thumbnail else thumbnail
        song = {
            "audio_url": audio_url,
            "title": title or search_query,
            "thumbnail": final_thumbnail,
            "webpage_url": webpage_url,
            "requester": ctx.author.display_name,
            "requester_avatar": ctx.author.display_avatar.url
        }
        if ctx.voice_client.is_playing():
            self.music_queue.append(song)
            position = len(self.music_queue)
            songs_ahead = position - 1
            # Embed para notificar a adição à fila com informações visuais aprimoradas
            embed = discord.Embed(
                title="🎶 Música Adicionada à Fila!",
                description=f"__**{song['title']}**__",
                color=discord.Color.green()
            )
            embed.add_field(name="Posição na Fila", value=f"{position}", inline=True)
            embed.add_field(name="Músicas à Frente", value=f"{songs_ahead}", inline=True)
            embed.set_author(name=f"Pedido por {song['requester']}", icon_url=song['requester_avatar'])
            if song.get('webpage_url'):
                embed.add_field(name="Fonte", value=song['webpage_url'], inline=False)
            if song.get('thumbnail'):
                embed.set_image(url=song['thumbnail'])
            await ctx.reply(embed=embed)
        else:
            self.music_queue.append(song)
            await self.play_next(ctx)

        try:
            await ctx.message.delete()
        except Exception as e:
            logging.error("Erro ao deletar mensagem: %s", e)

    @commands.command(name="skip", help="Pula para a próxima música da fila.")
    async def skip(self, ctx: commands.Context) -> None:
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Pulando para a próxima música!")
        else:
            await ctx.send("❌ Nenhuma música está tocando para pular.")

    @commands.command(name="pause", help="Pausa a música atual.")
    async def pause(self, ctx: commands.Context) -> None:
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Música pausada!")
        else:
            await ctx.send("❌ Nenhuma música está tocando para pausar.")

    @commands.command(name="resume", help="Retoma a música pausada.")
    async def resume(self, ctx: commands.Context) -> None:
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Música retomada!")
        else:
            await ctx.send("❌ Não há música pausada para retomar.")

    @commands.command(name="stop", help="Para a playlist e limpa a fila.")
    async def stop(self, ctx: commands.Context) -> None:
        if ctx.voice_client:
            self.music_queue.clear()
            ctx.voice_client.stop()
            await ctx.send("⏹️ Playlist parada e fila limpa!")
        else:
            await ctx.send("❌ Não estou conectado a um canal de voz.")

async def setup(bot: commands.Bot) -> None:
    if "Music" in bot.cogs:
        logging.warning("O módulo de música já estava carregado!")
        return  # Sai imediatamente para evitar execução desnecessária
    await bot.add_cog(Music(bot))


