import discord
from discord.ext import commands
import logging
from typing import Any

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class Admin(commands.Cog):
    """Módulo de administração do servidor."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="ban", help="Bane um usuário do servidor.")
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None) -> None:
        """
        Bane um usuário do servidor.

        Parâmetros:
            ctx: Contexto do comando.
            member: Membro a ser banido.
            reason: Motivo do banimento.
        """
        await member.ban(reason=reason)
        await ctx.send(f"🚨 {member.mention} foi banido. Motivo: {reason}")
        logging.info(f"Usuário {member} foi banido por {ctx.author}. Motivo: {reason}")

    @ban.error
    async def ban_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Lida com erros ao tentar banir usuários.

        Parâmetros:
            ctx: Contexto do comando.
            error: Exceção ocorrida.
        """
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para banir usuários. Os administradores serão informados sobre sua tentativa.")
            logging.warning(f"{ctx.author} tentou banir um usuário sem permissão.")

    @commands.command(name="kick", help="Expulsa um usuário do servidor.")
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = None) -> None:
        """
        Expulsa um usuário do servidor.

        Parâmetros:
            ctx: Contexto do comando.
            member: Membro a ser expulso.
            reason: Motivo da expulsão.
        """
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} foi expulso. Motivo: {reason}")
        logging.info(f"Usuário {member} foi expulso por {ctx.author}. Motivo: {reason}")

    @kick.error
    async def kick_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Lida com erros ao tentar expulsar usuários.

        Parâmetros:
            ctx: Contexto do comando.
            error: Exceção ocorrida.
        """
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para expulsar usuários. Os administradores serão informados sobre sua tentativa.")
            logging.warning(f"{ctx.author} tentou expulsar um usuário sem permissão.")

    @commands.command(name="clear", help="Apaga um número específico de mensagens.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int) -> None:
        """
        Apaga um número específico de mensagens.

        Parâmetros:
            ctx: Contexto do comando.
            amount: Quantidade de mensagens a serem apagadas.
        """
        # Apaga a mensagem de comando junto com as mensagens solicitadas
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 {amount} mensagens foram apagadas!", delete_after=5)
        logging.info(f"{ctx.author} apagou {amount} mensagens no canal {ctx.channel}.")

    @clear.error
    async def clear_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Lida com erros ao tentar apagar mensagens.

        Parâmetros:
            ctx: Contexto do comando.
            error: Exceção ocorrida.
        """
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para apagar mensagens.")
            logging.warning(f"{ctx.author} tentou apagar mensagens sem permissão.")

async def setup(bot: commands.Bot) -> None:
    """
    Carrega o módulo de administração no bot.

    Parâmetros:
        bot: Instância do bot.
    """
    await bot.add_cog(Admin(bot))
