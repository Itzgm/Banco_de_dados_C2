INSERT INTO clientes (nome, email, telefone) VALUES
    ('Ana Exemplo', 'ana@example.invalid', '27999990001'),
    ('Bruno Exemplo', 'bruno@example.invalid', '27999990002');
INSERT INTO atendentes (nome, email, telefone, senha) VALUES
    ('Carla Exemplo', 'carla@example.invalid', '27999990003', 'Suporte123!'),
    ('Diego Exemplo', 'diego@example.invalid', '27999990004', 'Suporte123!');
INSERT INTO chamados (id_cliente, id_atendente, nome, descricao, data_abertura, data_fechamento, status)
SELECT c.id_cliente, NULL, 'Acesso ao sistema', 'Erro ao entrar no sistema',
       TIMESTAMP '2026-10-01 09:00:00', NULL, 'aberto'
FROM clientes c WHERE c.email = 'ana@example.invalid';
INSERT INTO chamados (id_cliente, id_atendente, nome, descricao, data_abertura, data_fechamento, status)
SELECT c.id_cliente, a.id_atendente, 'Impressora', 'Impressora desconectada',
       TIMESTAMP '2026-10-02 09:00:00', TIMESTAMP '2026-10-02 10:00:00', 'resolvido'
FROM clientes c CROSS JOIN atendentes a
WHERE c.email = 'bruno@example.invalid' AND a.email = 'carla@example.invalid';
