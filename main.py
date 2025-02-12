import os
import time
import asyncio
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands
from secret_messages import handle_secret_message, get_secret_triggers

# Configuração do Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Carregando variáveis de ambiente
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# OBS.: GEMINI_API_KEY não está sendo usado; remova-o se não for necessário.
PREFIX = "v!"

# Configuração do Bot com todos os intents necessários
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Dicionários para gerenciar módulos e mensagens de erro
loaded_modules = {}  # Ex: {"admin_module": True, "music_module": False}
MODULE_ERROR_MESSAGES = {
    "admin_module": "🛠️ O sistema de administração está desativado. Informe os moderadores!",
    "music_module": "🎵 A jukebox está com defeito! Informe a manutenção para que possamos consertá-la!"
}

@bot.event
async def on_ready():
    logging.info("Videl está online!")

@bot.event
async def on_message(message: discord.Message):
    logging.info("Mensagem recebida de %s: %s", message.author, message.content)
    
    # Ignora mensagens de bots
    if message.author.bot:
        logging.debug("Mensagem ignorada, pois foi enviada por um bot.")
        return

    # Se a mensagem não tiver espaços (possivelmente uma mensagem secreta)
    if message.content.strip() and " " not in message.content:
        if await handle_secret_message(message):
            logging.info("Mensagem secreta processada com sucesso.")
            return

    # Processa os comandos normalmente
    await bot.process_commands(message)

@bot.command(name="commands", help="Exibe a lista de comandos disponíveis.")
async def commands_list(ctx: commands.Context):
    logging.info("Comando 'commands' executado por %s", ctx.author)
    command_list = [f"`{PREFIX}{cmd.name}` - {cmd.help}" for cmd in bot.commands if cmd.help]
    help_message = "**Lista de Comandos Disponíveis:**\n" + "\n".join(command_list)
    await ctx.send(help_message)

@bot.command(help="Verifica a latência do bot.")
async def ping(ctx: commands.Context):
    logging.info("Comando 'ping' executado por %s", ctx.author)
    start_time = time.time()
    msg = await ctx.send("Pong!")
    latency = round((time.time() - start_time) * 1000)
    await msg.edit(content=f"Pong! 🏓 Latência: {latency}ms")
    # Alternativamente, você pode usar bot.latency:
    # await ctx.send(f"Pong! 🏓 Latência: {round(bot.latency * 1000)}ms")

@bot.command(help="Exibe informações sobre o servidor.")
async def serverinfo(ctx: commands.Context):
    logging.info("Comando 'serverinfo' executado por %s", ctx.author)
    guild = ctx.guild
    embed = discord.Embed(title=f"Informações do Servidor - {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Dono", value=str(guild.owner), inline=True)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Criado em", value=guild.created_at.strftime('%d/%m/%Y'), inline=True)
    await ctx.send(embed=embed)

@bot.command(help="Exibe informações do usuário. Apenas administradores podem ver dados de outros.")
async def userinfo(ctx: commands.Context, member: discord.Member = None):
    logging.info("Comando 'userinfo' executado por %s", ctx.author)
    member = member or ctx.author
    # Se o autor não for administrador e tentar ver informações de outro usuário
    if member != ctx.author and not ctx.author.guild_permissions.administrator:
        logging.warning("Tentativa de acessar informações de outro usuário sem permissão.")
        await ctx.send("❌ Você não tem permissão para ver informações de outros usuários. Apenas administradores podem visualizar esses dados.")
        return

    embed = discord.Embed(title=f"Informações de {member.display_name}", color=discord.Color.green())
    embed.add_field(name="Nome", value=member.name, inline=True)
    join_date = member.joined_at.strftime('%d/%m/%Y') if member.joined_at else "Data não disponível"
    embed.add_field(name="Entrou em", value=join_date, inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

async def load_modules():
        
    """
    Tenta carregar módulos/extensões e registra se foram carregados com sucesso.
    """
    modules = ["admin_module", "music_module"]
    for module in modules:
        if module in bot.extensions:  # 🛑 Verificação para não carregar de novo!
            logging.warning("O módulo '%s' já estava carregado!", module)
            continue
        try:
            await bot.load_extension(module)
            loaded_modules[module] = True
            logging.info("Módulo '%s' carregado com sucesso.", module)
        except Exception as e:
            loaded_modules[module] = False
            logging.error("Erro ao carregar o módulo '%s': %s", module, e)

@bot.event
async def on_command_error(ctx, error):
    # Trata comandos não encontrados
    if isinstance(error, commands.CommandNotFound):
        # Define o módulo com base em palavras-chave na mensagem
        module = "music_module" if any(x in ctx.message.content for x in ("play", "stop")) else "admin_module"
        if not loaded_modules.get(module, True):
            # Envia a mensagem de erro definida para o módulo
            await ctx.send(MODULE_ERROR_MESSAGES[module])
        else:
            await ctx.send(f"Ohh, meu docinho! Esse comando não existe. 💖 Use `{PREFIX}commands` para ver os disponíveis! 😊")
    else:
        # Para outros tipos de erros, você pode logar ou tratá-los conforme a necessidade.
        logging.error("Erro no comando '%s': %s", ctx.command, error)

async def main():
    logging.info("Verificando carregamento do bot...")
    async with bot:
        await load_modules()
        logging.info("Iniciando o bot...")
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
