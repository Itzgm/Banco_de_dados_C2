SELECT ch.id_chamado, ch.nome AS titulo, ch.descricao, ch.status,
       ch.data_abertura, ch.data_fechamento,
       c.nome AS cliente, c.email AS email_cliente,
       a.nome AS atendente
FROM chamados AS ch
JOIN clientes AS c ON c.id_cliente = ch.id_cliente
LEFT JOIN atendentes AS a ON a.id_atendente = ch.id_atendente
ORDER BY ch.data_abertura, ch.id_chamado;
