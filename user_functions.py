# Importa o módulo discord para interagir com a API do Discord
import discord

# Importa o submódulo app_commands do discord para criar comandos de aplicação (slash commands)
from discord import app_commands

# Importa as funções necessárias do módulo database
from database import query, add, edit

# Importa o módulo logging para registrar eventos e erros
import logging

# Importa a função de configuração dos comandos de clã
from functions.cla_functions import setup_cla_commands

# Importa a função de configuração dos comandos de pesquisa de usuário
from functions.user_search import setup_user_search_commands

# Configura o logger para o bot
logger = logging.getLogger('bot')

# Define a função principal para configurar os comandos de usuário
def setup_user_commands(tree: app_commands.CommandTree):
    # Registra o início da configuração dos comandos de usuário
    logger.info("Configurando comandos de usuário...")
    try:
        # Chama a função para configurar os comandos de clã
        setup_cla_commands(tree)
        
        # Chama a função para configurar os comandos de pesquisa de usuário
        setup_user_search_commands(tree)
        
        # Espaço reservado para adicionar outros comandos de usuário no futuro
        
        # Registra o sucesso da configuração dos comandos de usuário
        logger.info("Comandos de usuário configurados com sucesso")
    except Exception as e:
        # Registra qualquer erro ocorrido durante a configuração dos comandos
        logger.error(f"Erro ao configurar comandos de usuário: {e}", exc_info=True)

# Resumo do arquivo:
# Este arquivo (user_functions.py) é responsável por configurar os comandos de usuário para um bot do Discord.
# Ele importa os módulos necessários, incluindo discord, app_commands, funções de banco de dados e logging.
# A função principal setup_user_commands configura os comandos relacionados a clãs e pesquisa de usuários.
# O arquivo utiliza um sistema de logging para registrar informações e erros durante o processo de configuração.
# Ele serve como um ponto central para organizar e inicializar diferentes tipos de comandos de usuário para o bot.
