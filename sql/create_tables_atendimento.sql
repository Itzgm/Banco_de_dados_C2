-- Execute uma vez em banco vazio; não apaga tabelas.
BEGIN;
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    nome VARCHAR(120) NOT NULL CHECK (length(trim(nome)) > 0),
    email VARCHAR(160) NOT NULL UNIQUE CHECK (position('@' IN email) > 1),
    telefone VARCHAR(25) NOT NULL CHECK (length(trim(telefone)) > 0)
);
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    nome VARCHAR(120) NOT NULL CHECK (length(trim(nome)) > 0),
    equipe VARCHAR(80) NOT NULL CHECK (length(trim(equipe)) > 0)
);
CREATE TABLE IF NOT EXISTS atendimentos (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
    funcionario_id INTEGER NOT NULL REFERENCES funcionarios(id) ON DELETE RESTRICT,
    assunto VARCHAR(160) NOT NULL CHECK (length(trim(assunto)) > 0),
    descricao VARCHAR(500) NOT NULL CHECK (length(trim(descricao)) > 0),
    data_abertura TIMESTAMP NOT NULL,
    data_fechamento TIMESTAMP,
    status VARCHAR(10) NOT NULL CHECK (status IN ('ABERTO', 'FECHADO')),
    CHECK ((status = 'ABERTO' AND data_fechamento IS NULL) OR
           (status = 'FECHADO' AND data_fechamento IS NOT NULL)),
    CHECK (data_fechamento IS NULL OR data_fechamento >= data_abertura)
);
CREATE INDEX IF NOT EXISTS idx_atendimentos_cliente ON atendimentos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_atendimentos_funcionario ON atendimentos(funcionario_id);
COMMIT;
