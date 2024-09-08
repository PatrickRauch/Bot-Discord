CREATE TABLE IF NOT EXISTS membros (
                id SERIAL PRIMARY KEY,
                discord_id BIGINT UNIQUE NOT NULL,
                nome VARCHAR(100) NOT NULL
                );
                
CREATE TABLE IF NOT EXISTS cla (
                id SERIAL PRIMARY KEY,
                lider_id INTEGER REFERENCES membros(id),
                name_cla VARCHAR(100) NOT NULL,
                tag_cla VARCHAR(50) NOT NULL,
                members_cla INTEGER[] CHECK (array_length(members_cla, 1) <= 13),
                ult_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                id_modificou INTEGER[],
                UNIQUE(lider_id, name_cla)
                );
