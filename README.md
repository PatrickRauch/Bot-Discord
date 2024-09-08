# Bot de Discord para Gerenciamento de Clãs

Este é um bot de Discord especializado em gerenciar clãs e fornecer funcionalidades administrativas. Ele foi projetado para melhorar a experiência dos usuários em servidores de jogos, oferecendo comandos para criar e gerenciar clãs.

## Instalação e Configuração

### Requisitos

- Python 3.8 ou superior
- PostgreSQL

### Instalação das Dependências

1. Clone o repositório:
   ```
   git clone https://github.com/PatrickRauch/Bot-Discord.git BotDiscord
   cd BotDiscord
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows use: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure o arquivo `config.json` com as credenciais do seu banco de dados PostgreSQL e o token do seu bot Discord.

5. Execute o script SQL `db.sql` no seu banco de dados PostgreSQL para criar as tabelas necessárias.

6. Inicie o bot:
   ```
   python main.py
   ```

## Comandos do Usuário

### Comandos de Clã

1. `/cla status`
   - Descrição: Mostra o status do seu clã.
   - Retorno: Informações detalhadas sobre o clã, incluindo nome, TAG, líder, membros, última atualização e quem fez a última modificação.

2. `/cla criar <nome> <tag> <membros>`
   - Descrição: Cria um novo clã.
   - Parâmetros:
     - `nome`: Nome do clã
     - `tag`: TAG do clã
     - `membros`: Lista de membros (menções)
   - Retorno: Confirmação da criação do clã ou mensagem de erro se houver problemas (por exemplo, se o usuário já estiver em um clã ou se o nome/TAG já existirem).

3. `/cla editar <acao> <membros>`
   - Descrição: Adiciona ou remove membros do clã.
   - Parâmetros:
     - `acao`: "Adicionar" ou "Remover"
     - `membros`: Lista de membros (menções)
   - Retorno: Confirmação das alterações realizadas, incluindo quais membros foram processados, não processados ou já estavam em outros clãs.

## Comandos de Administração

(Nota: Estes comandos são restritos a administradores do bot)

1. `/atualizar_status <novo_status>`
   - Descrição: Atualiza o status do bot.
   - Retorno: Confirmação da atualização do status.

2. `/recarregar <modulo>`
   - Descrição: Recarrega um módulo específico do bot.
   - Retorno: Confirmação do recarregamento ou mensagem de erro.

3. `/recarregar_config`
   - Descrição: Recarrega as configurações do bot.
   - Retorno: Confirmação do recarregamento das configurações.

4. `/testar_db`
   - Descrição: Testa a conexão com o banco de dados.
   - Retorno: Confirmação da conexão bem-sucedida ou mensagem de erro.

## Como Usar

1. Certifique-se de ter as permissões necessárias no servidor.
2. Use os comandos listados acima precedidos por `/`.
3. Siga as instruções fornecidas pelo bot para cada comando.

## Notas Importantes

- Um clã pode ter no máximo 13 membros.
- O criador do clã é automaticamente adicionado como líder e primeiro membro.
- Não é possível remover o líder do clã através do comando de edição.
- O bot mantém um registro de quem fez a última modificação no clã.

## Configuração e Desenvolvimento

O bot utiliza um banco de dados PostgreSQL para armazenar informações sobre membros e clãs. Certifique-se de configurar corretamente o arquivo `config.json` com as credenciais do banco de dados e outras configurações necessárias.

## Contribuições

Este é um programa privado destinado a automatizar e gerenciar fluxos de gerenciamento de clãs em servidores de jogos no Discord. Se você tiver sugestões ou melhorias, por favor, entre em contato com a equipe de desenvolvimento.

## Licença

Este é um bot privado e não é permitida sua divulgação ou distribuição. Todos os direitos reservados.
