# Importa os módulos necessários
import discord  # Importa o módulo principal do Discord
from discord import app_commands  # Importa o submódulo de comandos de aplicação
from admin_functions import setup_admin_commands, carregar_config, verificar_atualizacoes  # Importa funções administrativas personalizadas
from user_functions import setup_user_commands  # Importa funções de usuário personalizadas
import asyncio  # Importa o módulo para programação assíncrona
import logging  # Importa o módulo para registro de logs
from discord.ext import commands  # Importa o módulo de extensão de comandos do Discord
import json  # Importa o módulo json para ler o arquivo de configuração

# Configura o logging
logging.basicConfig(level=logging.INFO)  # Configura o nível básico de logging
logger = logging.getLogger('bot')  # Cria um logger específico para o bot

# Define o ID do servidor Discord
ID_DO_SERVIDOR = 1067860113689427979  # Armazena o ID do servidor Discord

# Define a classe principal do cliente do bot
class BotClient(discord.Client):
    def __init__(self):
        # Inicializa o cliente com as intenções padrão
        super().__init__(intents=discord.Intents.default())  # Chama o construtor da classe pai
        # Flag para controlar a sincronização de comandos
        self.synced = False  # Inicializa a flag de sincronização
        # Cria uma árvore de comandos
        self.tree = app_commands.CommandTree(self)  # Cria uma árvore de comandos para o bot
        # Inicializa a tarefa de atualização
        self.update_task = None  # Inicializa a variável para a tarefa de atualização

    async def setup_hook(self):
        # Configura os comandos administrativos
        admin_commands = setup_admin_commands(self.tree, self)  # Configura os comandos administrativos
        # Adiciona cada comando administrativo à árvore
        for cmd in admin_commands:
            self.tree.add_command(cmd, guild=discord.Object(id=ID_DO_SERVIDOR))  # Adiciona comandos à árvore
        # Configura os comandos de usuário
        setup_user_commands(self.tree)  # Configura os comandos de usuário

    async def on_ready(self):
        # Espera o bot estar completamente pronto
        await self.wait_until_ready()  # Aguarda o bot estar totalmente pronto
        # Sincroniza os comandos se ainda não foram sincronizados
        if not self.synced:
            await self.tree.sync()  # Sincroniza os comandos globalmente
            await self.tree.sync(guild=discord.Object(id=ID_DO_SERVIDOR))  # Sincroniza os comandos para o servidor específico
            self.synced = True  # Marca os comandos como sincronizados
            print("Comandos sincronizados.")  # Imprime mensagem de confirmação

        # Carrega a configuração e define o status do bot
        config = carregar_config()  # Carrega as configurações do bot
        await self.change_presence(activity=discord.Game(name=config.get('status', 'Patrick Rauch Consultoria')))  # Define o status do bot
        # Imprime uma mensagem indicando que o bot está online
        print(f"Entramos como {self.user}.")  # Imprime mensagem de login bem-sucedido
        
        # Inicia a tarefa de verificação de atualizações
        if self.update_task is None:
            self.update_task = self.loop.create_task(self.verificar_atualizacoes_loop())  # Inicia a tarefa de verificação de atualizações

    async def verificar_atualizacoes_loop(self):
        # Loop infinito para verificar atualizações periodicamente
        while True:
            await verificar_atualizacoes()  # Verifica atualizações
            await asyncio.sleep(60)  # Aguarda 60 segundos antes da próxima verificação

# Cria uma instância do cliente do bot
client = BotClient()  # Instancia o cliente do bot

# Cria uma instância do bot de comandos
intents = discord.Intents.default()  # Define as intenções padrão
intents.members = True  # Habilita a intenção de membros
intents.message_content = True  # Habilita a intenção de conteúdo de mensagens

bot = commands.Bot(command_prefix='!', intents=intents)  # Cria uma instância do bot de comandos

# Bloco de inicialização do script
if __name__ == "__main__":
    # Carrega o token do arquivo config.json
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            token = config['token']
    except FileNotFoundError:
        logger.error("Arquivo config.json não encontrado.")
        exit(1)
    except KeyError:
        logger.error("Token não encontrado no arquivo config.json.")
        exit(1)
    except json.JSONDecodeError:
        logger.error("Erro ao decodificar o arquivo config.json.")
        exit(1)

    # Inicia o bot com o token de autenticação carregado do config.json
    client.run(token)

# Comando para sincronização manual dos comandos
@bot.command()
@commands.is_owner()
async def sync(ctx):
    # Registra o início da sincronização
    logger.info("Iniciando sincronização...")  # Registra o início da sincronização
    try:
        # Tenta sincronizar os comandos
        synced = await bot.tree.sync()  # Sincroniza os comandos
        # Registra e envia uma mensagem com o número de comandos sincronizados
        logger.info(f"Sincronizado {len(synced)} comando(s)")  # Registra o número de comandos sincronizados
        await ctx.send(f"Sincronizado {len(synced)} comando(s)")  # Envia mensagem de confirmação
    except Exception as e:
        # Em caso de erro, registra e envia uma mensagem de erro
        logger.error(f"Erro durante a sincronização manual: {e}", exc_info=True)  # Registra o erro
        await ctx.send(f"Erro durante a sincronização: {e}")  # Envia mensagem de erro

# Resumo do arquivo:
# Este arquivo define a estrutura principal de um bot do Discord. Ele inclui:
# 1. Importação de módulos necessários
# 2. Configuração de logging
# 3. Definição da classe BotClient, que gerencia a funcionalidade principal do bot
# 4. Configuração de comandos administrativos e de usuário
# 5. Implementação de funções para sincronização de comandos e verificação de atualizações
# 6. Criação de instâncias do cliente do bot e do bot de comandos
# 7. Inicialização do bot com um token de autenticação
# 8. Implementação de um comando de sincronização manual
# O bot é configurado para responder a comandos, verificar atualizações periodicamente e manter seu status atualizado.