import discord
from discord.ext import commands
import json
import logging
from datetime import datetime

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('log_manager')

class LogManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self.carregar_config()
        self.canal_logs_id = self.config['canais']['logs']

    def carregar_config(self):
        try:
            with open('config.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Erro ao carregar o arquivo de configuração: {e}")
            return {}

    async def enviar_log(self, mensagem: str, cor: discord.Color = discord.Color.blue()):
        canal_logs = self.bot.get_channel(self.canal_logs_id)
        if not canal_logs:
            logger.error(f"Canal de logs não encontrado. ID: {self.canal_logs_id}")
            return

        embed = discord.Embed(
            title="Log do Servidor",
            description=mensagem,
            color=cor,
            timestamp=datetime.utcnow()
        )
        
        try:
            await canal_logs.send(embed=embed)
        except discord.HTTPException as e:
            logger.error(f"Erro ao enviar log para o canal: {e}")

    async def log_comando(self, ctx: commands.Context):
        mensagem = f"Comando usado: {ctx.command.name} por {ctx.author} ({ctx.author.id})"
        await self.enviar_log(mensagem, discord.Color.green())

    async def log_erro(self, erro: Exception, contexto: str = ""):
        mensagem = f"Erro ocorrido: {type(erro).__name__}: {str(erro)}\nContexto: {contexto}"
        await self.enviar_log(mensagem, discord.Color.red())

    async def log_membro_entrou(self, membro: discord.Member):
        mensagem = f"Novo membro entrou: {membro} ({membro.id})"
        await self.enviar_log(mensagem, discord.Color.green())

    async def log_membro_saiu(self, membro: discord.Member):
        mensagem = f"Membro saiu: {membro} ({membro.id})"
        await self.enviar_log(mensagem, discord.Color.orange())

    async def log_mensagem_deletada(self, mensagem: discord.Message):
        conteudo = mensagem.content if len(mensagem.content) <= 1000 else f"{mensagem.content[:997]}..."
        msg = f"Mensagem deletada de {mensagem.author} ({mensagem.author.id}) no canal {mensagem.channel.mention}:\n{conteudo}"
        await self.enviar_log(msg, discord.Color.red())

    async def log_mensagem_editada(self, antes: discord.Message, depois: discord.Message):
        msg = f"Mensagem editada por {antes.author} ({antes.author.id}) no canal {antes.channel.mention}:\n"
        msg += f"Antes: {antes.content}\nDepois: {depois.content}"
        await self.enviar_log(msg, discord.Color.yellow())

# Função para inicializar o LogManager
def setup_log_manager(bot: commands.Bot) -> LogManager:
    return LogManager(bot)
