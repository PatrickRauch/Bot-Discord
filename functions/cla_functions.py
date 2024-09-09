# Importa os módulos necessários
import discord  # Importa o módulo discord para interagir com a API do Discord
from discord import app_commands  # Importa app_commands para criar comandos de aplicação
from database import query, add, edit  # Importa funções para interagir com o banco de dados
import logging  # Importa o módulo de logging para registrar eventos
import re  # Importa o módulo de expressões regulares
from datetime import datetime  # Adicione esta importação no topo do arquivo
import asyncio

# Configura o logger para este módulo
logger = logging.getLogger('bot')  # Cria um logger específico para o bot

# Define a classe ClaCog que herda de app_commands.Group
class ClaCog(app_commands.Group):
    def __init__(self):
        # Inicializa a classe pai com nome e descrição para o grupo de comandos
        super().__init__(name="cla", description="Comandos relacionados a clãs")
        # Registra no log que a classe foi inicializada
        logger.info("ClaCog inicializado")

    # Define o comando 'status' para mostrar o status do clã do usuário
    @app_commands.command(name="status", description="Mostra o status do seu clã")
    async def cla_status(self, interaction: discord.Interaction):
        logger.info(f"Solicitação de status de clã para o usuário {interaction.user.id}")
        await interaction.response.defer(ephemeral=True)

        try:
            # Busca todos os clãs do usuário
            clas_do_usuario = self._buscar_clas_por_membro(str(interaction.user.id))
            if not clas_do_usuario:
                await interaction.followup.send("Você não está em nenhum clã.")
                return

            logger.info(f"Clãs encontrados para o usuário: {clas_do_usuario}")
            logger.info(f"ID do servidor atual: {interaction.guild.id}")

            # Verifica se o servidor já está cadastrado
            servidor_id = interaction.guild.id
            servidor_existente = query("servidores", "id", "discord_id = %s", (servidor_id,))
            if not servidor_existente:
                # Adiciona o servidor se ele não existir
                novo_servidor_id = add("servidores", {"nome": interaction.guild.name, "discord_id": servidor_id})
                if not novo_servidor_id:
                    await interaction.followup.send("Erro: Não foi possível registrar o servidor.")
                    return
                servidor_id_atual = novo_servidor_id
                logger.info(f"Novo servidor registrado com ID: {servidor_id_atual}")
            else:
                servidor_id_atual = servidor_existente[0][0]
            
            logger.info(f"ID do servidor atual no banco de dados: {servidor_id_atual}")

            # Filtra os clãs ativos do servidor atual
            clas_ativos_servidor = []
            for cla in clas_do_usuario:
                cla_id, lider_id, nome_cla, tag_cla, membros_ids, ult_atualizacao, id_modificou, servidor_id, ativo = cla
                logger.info(f"Verificando clã: {nome_cla}, servidor_id: {servidor_id}, ativo: {ativo}")
                if ativo and servidor_id == servidor_id_atual:
                    clas_ativos_servidor.append(cla)
                    logger.info(f"Clã adicionado: {nome_cla}")

            if not clas_ativos_servidor:
                await interaction.followup.send("Você não está em nenhum clã ativo neste servidor.")
                return

            if len(clas_ativos_servidor) > 1:
                mensagem = "Você está em múltiplos clãs ativos neste servidor:\n\n"
                for cla in clas_ativos_servidor:
                    mensagem += self._formatar_cla_info(cla, interaction.guild) + "\n\n"
                await interaction.followup.send(mensagem)
            else:
                mensagem = self._formatar_cla_info(clas_ativos_servidor[0], interaction.guild)
                await interaction.followup.send(mensagem)

        except Exception as e:
            logger.error(f"Erro ao buscar status do clã: {str(e)}", exc_info=True)
            await interaction.followup.send("Ocorreu um erro ao buscar as informações do clã.")

    def _buscar_clas_por_membro(self, discord_id):
        membro_query = query("membros", "id", "discord_id = %s", (discord_id,))
        if not membro_query:
            return None

        membro_id = membro_query[0][0]

        cla_query = query("cla", "*", "members_cla @> ARRAY[%s]", (membro_id,))
        if not cla_query:
            return None

        return cla_query

    def _formatar_cla_info(self, cla_info, guild):
        cla_id, lider_id, nome_cla, tag_cla, membros_ids, ult_atualizacao, id_modificou, servidor_id, ativo = cla_info

        lider_query = query("membros", "discord_id", "id = %s", (lider_id,))
        lider_discord_id = lider_query[0][0] if lider_query else "Desconhecido"

        membros_query = query("membros", "discord_id", f"id = ANY(ARRAY{membros_ids})")
        membros_discord_ids = [membro[0] for membro in membros_query]

        ultimo_modificador_id = id_modificou[-1] if id_modificou and isinstance(id_modificou, list) else None
        ultimo_modificador_query = query("membros", "discord_id", "id = %s", (ultimo_modificador_id,)) if ultimo_modificador_id else None
        ultimo_modificador_discord_id = ultimo_modificador_query[0][0] if ultimo_modificador_query else "Desconhecido"

        mensagem = f"**Nome do Clã:** {nome_cla}\n"
        mensagem += f"**TAG:** {tag_cla}\n"
        mensagem += f"**Líder:** <@{lider_discord_id}>\n"
        mensagem += f"**Ativo:** {'Sim' if ativo else 'Não'}\n"
        mensagem += f"**Última Atualização:** {ult_atualizacao}\n"
        mensagem += f"**Última Modificação por:** <@{ultimo_modificador_discord_id}>\n"
        mensagem += f"**Servidor ID:** {servidor_id}\n"
        mensagem += "**Membros:**\n"

        for discord_id in membros_discord_ids:
            membro = guild.get_member(int(discord_id))
            if membro:
                mensagem += f"- {membro.mention}\n"
            else:
                mensagem += f"- <@{discord_id}>\n"

        return mensagem

    def _buscar_clas_por_membro(self, discord_id):
        membro_query = query("membros", "id", "discord_id = %s", (discord_id,))
        if not membro_query:
            return None

        membro_id = membro_query[0][0]

        cla_query = query("cla", "*", "members_cla @> ARRAY[%s]", (membro_id,))
        if not cla_query:
            return None

        return cla_query

    # Comando para criar um novo clã
    @app_commands.command(name="criar", description="Cria um novo clã")
    async def criar_cla(self, interaction: discord.Interaction, nome: str, tag: str, membros: str):
        logger.info(f"Solicitação de criação de clã para o usuário {interaction.user.id}")
        await interaction.response.defer(ephemeral=True)

        try:
            # Verifica se o usuário já é membro de algum clã no servidor atual
            usuario_em_cla = query("cla", "id", "members_cla @> ARRAY[(SELECT id FROM membros WHERE discord_id = %s)] AND servidor_id = %s", (str(interaction.user.id), interaction.guild.id))
            if usuario_em_cla:
                await interaction.followup.send("Erro: Você já é membro de um clã neste servidor e não pode criar ou participar de outro.")
                return

            # Verifica se o nome do clã já existe
            if query("cla", "id", "name_cla = %s AND servidor_id = %s", (nome, interaction.guild.id)):
                await interaction.followup.send("Erro: Já existe um clã com esse nome neste servidor.")
                return

            # Verifica se a TAG já existe
            if query("cla", "id", "tag_cla = %s AND servidor_id = %s", (tag, interaction.guild.id)):
                await interaction.followup.send("Erro: Já existe um clã com essa TAG neste servidor.")
                return

            # Verifica se o servidor já está cadastrado
            servidor_id = interaction.guild.id
            servidor_existente = query("servidores", "id", "discord_id = %s", (servidor_id,))
            if not servidor_existente:
                # Adiciona o servidor se ele não existir
                novo_servidor_id = add("servidores", {"nome": interaction.guild.name, "discord_id": servidor_id})
                if not novo_servidor_id:
                    await interaction.followup.send("Erro: Não foi possível registrar o servidor.")
                    return
                servidor_id_db = novo_servidor_id
            else:
                servidor_id_db = servidor_existente[0][0]

            # Processa a lista de membros
            membros_lista = re.findall(r'<@!?(\d+)>', membros)
            membros_lista = [str(interaction.user.id)] + membros_lista  # Adiciona o criador como primeiro membro
            
            logger.info(f"Lista de membros processada: {membros_lista}")

            # Verifica e cadastra os membros
            membros_ids = []
            membros_ja_em_cla = []
            for membro_id in membros_lista:
                logger.info(f"Processando membro: {membro_id}")
                
                # Verifica se o membro já está em um clã no servidor atual
                membro_em_cla = query("cla", "id", "members_cla @> ARRAY[(SELECT id FROM membros WHERE discord_id = %s)] AND servidor_id = %s", (membro_id, servidor_id_db))
                if membro_em_cla:
                    membros_ja_em_cla.append(membro_id)
                    logger.info(f"Membro {membro_id} já está em um clã neste servidor")
                    continue

                membro_query = query("membros", "id", "discord_id = %s", (membro_id,))
                if membro_query:
                    membros_ids.append(membro_query[0][0])
                    logger.info(f"Membro {membro_id} já cadastrado no banco de dados")
                else:
                    try:
                        membro = await interaction.guild.fetch_member(int(membro_id))
                        if membro:
                            novo_membro = add("membros", {"discord_id": membro_id, "nome": membro.name})
                            if novo_membro:
                                membros_ids.append(novo_membro[0])
                                logger.info(f"Novo membro adicionado: {membro.name} ({membro_id})")
                            else:
                                logger.error(f"Falha ao adicionar novo membro: {membro_id}")
                        else:
                            logger.error(f"Membro não encontrado: {membro_id}")
                    except Exception as e:
                        logger.error(f"Erro ao adicionar novo membro {membro_id}: {str(e)}")
                        continue

            # Verifica se há membros suficientes para criar o clã
            if len(membros_ids) < 2:
                mensagem = "Não foi possível criar um clã com apenas uma pessoa.\n"
                if membros_ja_em_cla:
                    mensagem += "Os seguintes membros já estão em outros clãs:\n"
                    mensagem += "\n".join([f"- <@{membro_id}>" for membro_id in membros_ja_em_cla])
                await interaction.followup.send(mensagem)
                return

            # Obtém o timestamp atual no formato 'aaaa-mm-dd hh:mm:ss'
            timestamp_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Cria o clã
            novo_cla = add("cla", {
                "lider_id": membros_ids[0],
                "name_cla": nome,
                "tag_cla": tag,
                "members_cla": membros_ids,
                "servidor_id": servidor_id_db,
                "ativo": True,
                "ult_atualizacao": timestamp_atual,
                "id_modificou": [membros_ids[0]]
            })

            if novo_cla:
                mensagem = f"Clã '{nome}' criado com sucesso com {len(membros_ids)} membros!"
                if membros_ja_em_cla:
                    mensagem += "\nOs seguintes membros não foram adicionados pois já estão em outros clãs:\n"
                    mensagem += "\n".join([f"- <@{membro_id}>" for membro_id in membros_ja_em_cla])
                await interaction.followup.send(mensagem)
                logger.info(f"Clã '{nome}' criado com sucesso")
            else:
                await interaction.followup.send("Erro ao criar o clã. Por favor, tente novamente.")
                logger.error(f"Falha ao criar o clã '{nome}'")

        except Exception as e:
            logger.error(f"Erro ao criar clã: {str(e)}", exc_info=True)
            await interaction.followup.send("Ocorreu um erro ao criar o clã. Por favor, tente novamente mais tarde.")

    @app_commands.command(name="editar", description="Adiciona ou remove membros do clã")
    @app_commands.choices(acao=[
        app_commands.Choice(name="Adicionar", value="adicionar"),
        app_commands.Choice(name="Remover", value="remover")
    ])
    async def editar_membros_cla(self, interaction: discord.Interaction, acao: app_commands.Choice[str], membros: str):
        logger.info(f"Solicitação de edição de membros do clã para o usuário {interaction.user.id}")
        await interaction.response.defer(ephemeral=True)

        try:
            # Verifica se o usuário é membro de algum clã
            cla_info = query("cla", "*", "members_cla @> ARRAY[(SELECT id FROM membros WHERE discord_id = %s)]", (str(interaction.user.id),))
            if not cla_info:
                await interaction.followup.send("Erro: Você não é membro de nenhum clã.")
                return

            # Desempacota os 8 valores retornados pela consulta
            cla_id, lider_id, nome_cla, tag_cla, membros_atuais, servidor_id, ativo, ult_atualizacao, id_modificou = cla_info[0]

            # Processa a lista de membros
            novos_membros = re.findall(r'<@!?(\d+)>', membros)
            
            membros_atualizados = membros_atuais.copy()
            membros_processados = []
            membros_nao_processados = []
            membros_ja_em_cla = []

            for membro_id in novos_membros:
                membro_query = query("membros", "id", "discord_id = %s", (membro_id,))
                if not membro_query:
                    # Tenta adicionar o novo membro ao banco de dados
                    membro = await interaction.guild.fetch_member(int(membro_id))
                    if membro:
                        novo_membro = add("membros", {"discord_id": membro_id, "nome": membro.name})
                        if novo_membro:
                            membro_query = [(novo_membro[0],)]
                        else:
                            membros_nao_processados.append(membro_id)
                            continue
                    else:
                        membros_nao_processados.append(membro_id)
                        continue

                membro_id_db = membro_query[0][0]

                # Verifica se o membro a ser removido é o líder
                if acao.value == 'remover' and membro_id_db == lider_id:
                    membros_nao_processados.append(membro_id)
                    continue

                # Verifica se o membro já está em um clã (para adição)
                if acao.value == 'adicionar':
                    membro_em_cla = query("cla", "name_cla", "members_cla @> ARRAY[%s]", (membro_id_db,))
                    if membro_em_cla:
                        membros_ja_em_cla.append((membro_id, membro_em_cla[0][0]))
                        continue

                if acao.value == 'adicionar':
                    if membro_id_db not in membros_atualizados:
                        membros_atualizados.append(membro_id_db)
                        membros_processados.append(membro_id)
                elif acao.value == 'remover':
                    if membro_id_db in membros_atualizados:
                        membros_atualizados.remove(membro_id_db)
                        membros_processados.append(membro_id)

            # Verifica se o número de membros está dentro do limite
            if len(membros_atualizados) > 13:
                await interaction.followup.send("Erro: O clã não pode ter mais de 13 membros.")
                return

            if len(membros_atualizados) < 2:
                await interaction.followup.send("Erro: O clã deve ter pelo menos 2 membros.")
                return

            # Atualiza o clã no banco de dados
            timestamp_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            usuario_id = query("membros", "id", "discord_id = %s", (str(interaction.user.id),))[0][0]
            edit("cla", {
                "members_cla": membros_atualizados,
                "ult_atualizacao": timestamp_atual,
                "id_modificou": id_modificou + [usuario_id]
            }, "id = %s", (cla_id,))

            # Prepara a mensagem de resposta
            acao_passado = "adicionados" if acao.value == 'adicionar' else "removidos"
            mensagem = f"Membros {acao_passado} com sucesso: " + ", ".join([f"<@{m}>" for m in membros_processados])
            if membros_nao_processados:
                mensagem += f"\nMembros não processados: " + ", ".join([f"<@{m}>" for m in membros_nao_processados])
            if membros_ja_em_cla:
                mensagem += "\nMembros não adicionados por já estarem em um clã:"
                for membro, cla in membros_ja_em_cla:
                    mensagem += f"\n- <@{membro}> | {cla}"

            await interaction.followup.send(mensagem)
            logger.info(f"Membros do clã '{nome_cla}' atualizados com sucesso por {interaction.user.id}")

        except Exception as e:
            logger.error(f"Erro ao editar membros do clã: {str(e)}", exc_info=True)
            await interaction.followup.send("Ocorreu um erro ao editar os membros do clã. Por favor, tente novamente mais tarde.")

    

    @app_commands.command(name="list", description="Lista todos os clãs cadastrados neste servidor")
    @app_commands.checks.has_permissions(administrator=True)
    async def listar_clas(self, interaction: discord.Interaction):
        logger.info(f"Solicitação de listagem de clãs pelo usuário {interaction.user.id} no servidor {interaction.guild.id}")
        await interaction.response.defer(ephemeral=False)

        try:
            # Obtém o discord_id do servidor
            discord_id_servidor = interaction.guild.id

            # Obtém o id do banco de dados do servidor em questão
            servidor_query = query("servidores", "id", "discord_id = %s", (discord_id_servidor,))
            if not servidor_query:
                await interaction.followup.send("Este servidor não está cadastrado no banco de dados.")
                return

            servidor_id_db = servidor_query[0][0]

            # Busca os clãs do servidor atual, exceto o clã com id 1
            clas = query("cla", "*", "servidor_id = %s AND id != 1", (servidor_id_db,))
            if not clas:
                await interaction.followup.send("Não há clãs cadastrados neste servidor.")
                return

            await interaction.followup.send("**Lista de Clãs Cadastrados neste Servidor:**")

            for cla in clas:
                cla_info = self._formatar_cla_info(cla, interaction.guild)
                await interaction.channel.send(f"­\n{cla_info}\n{'='*40}")
                await asyncio.sleep(1)  # Aguarda 1 segundo antes de enviar a próxima mensagem

            logger.info(f"Listagem de clãs concluída pelo usuário {interaction.user.id} no servidor {interaction.guild.id}")

        except Exception as e:
            logger.error(f"Erro ao listar clãs: {str(e)}", exc_info=True)
            await interaction.followup.send("Ocorreu um erro ao listar os clãs. Por favor, tente novamente mais tarde.")

    def _formatar_cla_info(self, cla_info, guild):
        cla_id, lider_id, nome_cla, tag_cla, membros_ids, ult_atualizacao, id_modificou, servidor_id, ativo = cla_info

        lider_query = query("membros", "discord_id", "id = %s", (lider_id,))
        lider_discord_id = lider_query[0][0] if lider_query else "Desconhecido"

        membros_query = query("membros", "discord_id", f"id = ANY(ARRAY{membros_ids})")
        membros_discord_ids = [membro[0] for membro in membros_query]

        ultimo_modificador_id = id_modificou[-1] if id_modificou and isinstance(id_modificou, list) else None
        ultimo_modificador_query = query("membros", "discord_id", "id = %s", (ultimo_modificador_id,)) if ultimo_modificador_id else None
        ultimo_modificador_discord_id = ultimo_modificador_query[0][0] if ultimo_modificador_query else "Desconhecido"

        mensagem = f"**Nome do Clã:** {nome_cla}\n"
        mensagem += f"**TAG:** {tag_cla}\n"
        mensagem += f"**Líder:** <@{lider_discord_id}>\n"
        mensagem += f"**QTD Membros:** **{len(membros_discord_ids)}**\n"
        mensagem += f"**Última Atualização:** {ult_atualizacao}\n"
        mensagem += f"**Última Modificação por:** <@{ultimo_modificador_discord_id}>\n"
        mensagem += "**Membros:**\n"

        for discord_id in membros_discord_ids:
            membro = guild.get_member(int(discord_id))
            if membro:
                mensagem += f"- {membro.mention}\n"
            else:
                mensagem += f"- <@{discord_id}>\n"

        return mensagem

    @listar_clas.error
    async def listar_clas_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("Você não tem permissão para usar este comando. Apenas administradores podem listar todos os clãs.", ephemeral=True)
        else:
            logger.error(f"Erro não tratado no comando listar_clas: {str(error)}", exc_info=True)
            await interaction.response.send_message("Ocorreu um erro ao executar o comando. Por favor, tente novamente mais tarde.", ephemeral=True)

# Função para configurar os comandos de clã na árvore de comandos
def setup_cla_commands(tree: app_commands.CommandTree):
    # Registra no log o início da configuração dos comandos
    logger.info("Configurando comandos de clã...")
    try:
        # Cria uma instância do ClaCog
        cla_group = ClaCog()
        # Adiciona o grupo de comandos à árvore
        tree.add_command(cla_group)
        # Registra no log que os comandos foram adicionados com sucesso
        logger.info("Comandos de clã adicionados à árvore")
    except Exception as e:
        # Em caso de erro, registra o erro no log
        logger.error(f"Erro ao configurar comandos de clã: {e}", exc_info=True)

# Resumo do arquivo:
# Este arquivo define uma classe ClaCog que gerencia comandos relacionados a clãs em um bot do Discord.
# Ele inclui funcionalidades para:
# 1. Mostrar o status de um clã (comando 'status')
# 2. Criar um novo clã (comando 'criar')
# 3. Editar membros do clã (comando 'editar')
# A classe utiliza um sistema de logging para registrar eventos e erros.
# Também interage com um banco de dados para armazenar e recuperar informações sobre clãs e membros.
# O arquivo inclui métodos auxiliares para buscar informações de clãs e formatar mensagens.
# Por fim, há uma função setup_cla_commands para adicionar os comandos de clã à árvore de comandos do bot.