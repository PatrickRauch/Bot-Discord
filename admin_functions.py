# Importa os módulos necessários
import discord
from discord import app_commands
import json
import importlib
import asyncio
from database import query

# Define o nome do arquivo de configuração
CONFIG_FILE = 'config.json'

# Função para carregar as configurações do arquivo JSON
def carregar_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

# Verifica se o usuário é um administrador
def is_admin(interaction: discord.Interaction) -> bool:
    config = carregar_config()
    return interaction.user.id in config.get('admin_ids', [])

# Verifica se o usuário é um administrador e envia uma mensagem se não for
async def check_admin(interaction: discord.Interaction) -> bool:
    if not is_admin(interaction):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
        return False
    return True

# Função assíncrona para verificar atualizações periodicamente
async def verificar_atualizacoes():
    while True:
        await asyncio.sleep(300)

# Configura os comandos de administração
def setup_admin_commands(tree: app_commands.CommandTree, client: discord.Client):
    # Comando para atualizar o status do bot
    @tree.command(name='atualizar_status', description='Atualiza o status do bot')
    @app_commands.guild_only()
    async def atualizar_status(interaction: discord.Interaction, novo_status: str):
        if not await check_admin(interaction):
            return
        
        config = carregar_config()
        config['status'] = novo_status
        await client.change_presence(activity=discord.Game(name=novo_status))
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        await interaction.response.send_message(f"Status atualizado para: Jogando {novo_status}", ephemeral=True)

    # Comando para recarregar um módulo específico
    @tree.command(name='recarregar', description='Recarrega um módulo específico')
    @app_commands.guild_only()
    async def recarregar(interaction: discord.Interaction, modulo: str):
        if not await check_admin(interaction):
            return
        
        try:
            await interaction.response.defer(ephemeral=True)
            importlib.reload(importlib.import_module(modulo))
            await interaction.followup.send(f"Módulo {modulo} recarregado com sucesso!")
        except Exception as e:
            await interaction.followup.send(f"Erro ao recarregar o módulo: {str(e)}")

    # Comando para recarregar as configurações
    @tree.command(name='recarregar_config', description='Recarrega as configurações')
    @app_commands.guild_only()
    async def recarregar_config(interaction: discord.Interaction):
        if not await check_admin(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)
        config = carregar_config()
        await client.change_presence(activity=discord.Game(name=config['status']))
        await interaction.followup.send("Configurações recarregadas!")

    # Retorna a lista de comandos configurados
    return [atualizar_status, recarregar, recarregar_config]

# Resumo do arquivo:
# Este arquivo contém funções e comandos relacionados à administração de um bot Discord.
# Ele inclui funções para carregar configurações, verificar permissões de administrador,
# e configurar comandos específicos para administradores. Os comandos incluem:
# - Atualizar o status do bot
# - Recarregar módulos específicos
# - Recarregar configurações
# O arquivo também define uma função para verificar atualizações periodicamente.
