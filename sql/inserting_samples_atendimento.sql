-- Dados fictícios; IDs repetidos não duplicam linhas.
BEGIN;
INSERT INTO clientes(id,nome,email,telefone) VALUES
(1,'Ana Souza','ana.souza@example.test','27990000001'),
(2,'Bruno Lima','bruno.lima@example.test','27990000002'),
(3,'Carla Mendes','carla.mendes@example.test','27990000003')
ON CONFLICT (id) DO NOTHING;
INSERT INTO funcionarios(id,nome,equipe) VALUES
(1,'Paulo Reis','Suporte N1'),(2,'Luiza Costa','Suporte N2')
ON CONFLICT (id) DO NOTHING;
INSERT INTO atendimentos(id,cliente_id,funcionario_id,assunto,descricao,data_abertura,data_fechamento,status) VALUES
(1,1,1,'Acesso ao sistema','Cliente não consegue entrar no portal','2026-10-28 09:00','2026-10-28 09:30','FECHADO'),
(2,2,1,'Atualização cadastral','Solicitação de atualização de telefone','2026-10-28 10:00','2026-10-28 10:45','FECHADO'),
(3,3,2,'Erro de pagamento','Pagamento recusado no aplicativo','2026-10-28 11:00','2026-10-28 12:20','FECHADO'),
(4,1,2,'Dúvida sobre fatura','Cliente aguarda retorno da análise','2026-10-29 08:00',NULL,'ABERTO')
ON CONFLICT (id) DO NOTHING;
COMMIT;
