SELECT a.id, c.nome AS cliente, c.email, f.nome AS funcionario, f.equipe,
       a.assunto, a.descricao, a.data_abertura, a.data_fechamento, a.status
FROM atendimentos a JOIN clientes c ON c.id=a.cliente_id
JOIN funcionarios f ON f.id=a.funcionario_id
ORDER BY a.data_abertura DESC, a.id;
