import psycopg2  # Importa o módulo psycopg2 para interagir com o PostgreSQL
from psycopg2 import pool  # Importa o módulo de pool de conexões do psycopg2
import json  # Importa o módulo json para manipular arquivos JSON
import logging  # Importa o módulo logging para registrar logs

# Configuração do logger
logger = logging.getLogger('database')
logger.setLevel(logging.INFO)

# Carrega as configurações do arquivo config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)  # Lê o arquivo de configuração e armazena em 'config'

# Configurações do banco de dados
db_config = config['database']  # Extrai as configurações específicas do banco de dados

# Cria um pool de conexões
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,  # Define o número mínimo e máximo de conexões no pool
    host=db_config['host'],  # Define o host do banco de dados
    port=db_config['port'],  # Define a porta do banco de dados
    database=db_config['nome'],  # Define o nome do banco de dados
    user=db_config['usuario'],  # Define o usuário do banco de dados
    password=db_config['senha']  # Define a senha do banco de dados
)

def executar_query(query, params=None):
    """
    Executa uma query no banco de dados.
    """
    conn = connection_pool.getconn()  # Obtém uma conexão do pool
    try:
        with conn.cursor() as cur:  # Cria um cursor para executar a query
            logger.info(f"Executando query: {query}")
            logger.info(f"Parâmetros: {params}")
            cur.execute(query, params)  # Executa a query com os parâmetros fornecidos
            conn.commit()  # Confirma a transação
            if cur.description:  # Verifica se a query retornou resultados
                resultado = cur.fetchall()  # Retorna todos os resultados
                logger.info(f"Resultado da query: {resultado}")
                return resultado
            logger.info("Query executada com sucesso (sem retorno)")
    except (Exception, psycopg2.Error) as error:
        logger.error(f"Erro ao executar query: {error}")  # Imprime mensagem de erro
    finally:
        connection_pool.putconn(conn)  # Devolve a conexão ao pool

def query(tabela, colunas="*", condicao=None, params=None):
    """
    Realiza uma consulta na tabela especificada.
    """
    query = f"SELECT {colunas} FROM {tabela}"  # Monta a query SELECT básica
    if condicao:
        query += f" WHERE {condicao}"  # Adiciona a cláusula WHERE se houver condição
    logger.info(f"Executando consulta em {tabela}")
    return executar_query(query, params)  # Executa a query

def add(tabela, dados):
    """
    Adiciona um novo registro à tabela especificada.
    """
    colunas = ", ".join(dados.keys())  # Prepara a string de colunas
    valores = ", ".join(["%s"] * len(dados))  # Prepara a string de placeholders para valores
    query = f"INSERT INTO {tabela} ({colunas}) VALUES ({valores}) RETURNING id"  # Monta a query INSERT
    logger.info(f"Adicionando novo registro em {tabela}")
    resultado = executar_query(query, tuple(dados.values()))  # Executa a query
    if resultado:
        logger.info(f"Novo registro adicionado em {tabela} com ID: {resultado[0][0]}")
        return resultado[0]  # Retorna o ID do registro inserido
    logger.warning(f"Falha ao adicionar novo registro em {tabela}")
    return None

def edit(tabela, dados, condicao, params):
    """
    Edita registros na tabela especificada que atendem à condição.
    """
    set_clause = ", ".join([f"{coluna} = %s" for coluna in dados.keys()])  # Prepara a cláusula SET
    query = f"UPDATE {tabela} SET {set_clause} WHERE {condicao}"  # Monta a query UPDATE
    logger.info(f"Editando registros em {tabela}")
    resultado = executar_query(query, tuple(dados.values()) + params)  # Executa a query
    logger.info(f"Registros atualizados em {tabela}")
    return resultado

def exclude(tabela, condicao, params):
    """
    Exclui registros da tabela especificada que atendem à condição.
    """
    query = f"DELETE FROM {tabela} WHERE {condicao}"  # Monta a query DELETE
    logger.info(f"Excluindo registros de {tabela}")
    resultado = executar_query(query, params)  # Executa a query
    logger.info(f"Registros excluídos de {tabela}")
    return resultado

def fechar_conexoes():
    """
    Fecha todas as conexões do pool.
    """
    logger.info("Fechando todas as conexões do pool")
    connection_pool.closeall()  # Fecha todas as conexões no pool
    logger.info("Todas as conexões foram fechadas")

# Exemplos de uso:
# resultados = query("usuarios", "nome, email", "idade > %s", (18,))
# add("usuarios", {"nome": "João", "email": "joao@exemplo.com", "idade": 25})
# edit("usuarios", {"email": "novo_email@exemplo.com"}, "id = %s", (1,))
# exclude("usuarios", "id = %s", (1,))
# fechar_conexoes()

# Resumo do arquivo:
# Este arquivo implementa uma camada de abstração para operações de banco de dados usando PostgreSQL.
# Ele utiliza um pool de conexões para gerenciar eficientemente as conexões com o banco de dados.
# As configurações do banco são carregadas de um arquivo JSON.
# O arquivo fornece funções para executar queries genéricas, realizar consultas (SELECT),
# adicionar novos registros (INSERT), editar registros existentes (UPDATE) e excluir registros (DELETE).
# Também inclui uma função para fechar todas as conexões do pool.
# Este módulo simplifica as operações de banco de dados e promove boas práticas de gerenciamento de conexões.
# Agora, todas as operações de banco de dados são registradas em log para facilitar o rastreamento e depuração.
