CREATE TABLE IF NOT EXISTS membros (
                id SERIAL PRIMARY KEY,
                discord_id BIGINT UNIQUE NOT NULL,
                nome VARCHAR(100) NOT NULL,
                steam_id VARCHAR(17) UNIQUE
                );
                
CREATE TABLE IF NOT EXISTS servidores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                discord_id BIGINT UNIQUE NOT NULL
                );

CREATE TABLE IF NOT EXISTS cla (
                id SERIAL PRIMARY KEY,
                lider_id INTEGER REFERENCES membros(id),
                name_cla VARCHAR(100) NOT NULL,
                tag_cla VARCHAR(50) NOT NULL,
                members_cla INTEGER[] CHECK (array_length(members_cla, 1) <= 13),
                servidor_id INTEGER REFERENCES servidores(id),
                ativo BOOLEAN DEFAULT TRUE,
                ult_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                id_modificou INTEGER[],
                UNIQUE(lider_id, name_cla)
                );

-- Verificar se a tabela servidores já existe e criar se não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'servidores') THEN
        CREATE TABLE servidores (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            discord_id BIGINT UNIQUE NOT NULL
        );
    END IF;
END $$;

-- Adicionar coluna steam_id à tabela membros
ALTER TABLE membros
ADD COLUMN IF NOT EXISTS steam_id VARCHAR(17) UNIQUE;

-- Adicionar colunas servidor_id e ativo à tabela cla
ALTER TABLE cla
ADD COLUMN IF NOT EXISTS servidor_id INTEGER REFERENCES servidores(id),
ADD COLUMN IF NOT EXISTS ativo BOOLEAN DEFAULT TRUE;

-- Atualizar a coluna ult_atualizacao se não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='cla' AND column_name='ult_atualizacao') THEN
        ALTER TABLE cla
        ADD COLUMN ult_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;
