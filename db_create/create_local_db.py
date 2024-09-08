# Importa o módulo psycopg2 para interagir com o PostgreSQL
import psycopg2
# Importa o nível de isolamento AUTOCOMMIT do psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# Importa o módulo os para operações do sistema operacional
import os
# Importa o módulo logging para registrar logs
import logging

# Configura o logging básico com nível INFO
logging.basicConfig(level=logging.INFO)
# Cria um logger para este módulo
logger = logging.getLogger(__name__)

# Define as configurações do banco de dados
DB_NAME = "seu_banco_de_dados"
DB_USER = "seu_usuario"
DB_PASSWORD = "sua_senha"
DB_HOST = "localhost"
DB_PORT = "5432"

# Define a função para criar o banco de dados
def criar_banco_de_dados():
    try:
        # Conecta ao PostgreSQL usando as configurações definidas
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        # Define o nível de isolamento como AUTOCOMMIT
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Cria um cursor para executar comandos SQL
        cursor = conn.cursor()

        # Executa o comando SQL para criar o banco de dados
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        # Registra uma mensagem de sucesso
        logger.info(f"Banco de dados '{DB_NAME}' criado com sucesso.")

        # Fecha o cursor e a conexão
        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        # Registra uma mensagem de erro se houver falha
        logger.error(f"Erro ao criar o banco de dados: {e}")

# Define a função para criar as tabelas
def criar_tabelas():
    try:
        # Conecta ao banco de dados recém-criado
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        # Cria um cursor para executar comandos SQL
        cursor = conn.cursor()

        # Abre e lê o arquivo db.sql
        with open('db.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            # Executa o script SQL lido do arquivo
            cursor.execute(sql_script)

        # Confirma as alterações no banco de dados
        conn.commit()
        # Registra uma mensagem de sucesso
        logger.info("Tabelas criadas com sucesso.")

        # Fecha o cursor e a conexão
        cursor.close()
        conn.close()

    except FileNotFoundError:
        # Registra um erro se o arquivo db.sql não for encontrado
        logger.error("Arquivo db.sql não encontrado.")
    except psycopg2.Error as e:
        # Registra um erro se houver falha ao criar as tabelas
        logger.error(f"Erro ao criar as tabelas: {e}")

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    # Chama as funções para criar o banco de dados e as tabelas
    criar_banco_de_dados()
    criar_tabelas()