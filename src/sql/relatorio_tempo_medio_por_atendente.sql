SELECT a.id_atendente, a.nome AS atendente,
       COUNT(ch.id_chamado) AS total_resolvidos,
       AVG(EXTRACT(EPOCH FROM (ch.data_fechamento - ch.data_abertura))) AS media_segundos
FROM atendentes AS a
LEFT JOIN chamados AS ch ON ch.id_atendente = a.id_atendente
    AND ch.status = 'resolvido'
    AND ch.data_abertura IS NOT NULL
    AND ch.data_fechamento IS NOT NULL
    AND ch.data_fechamento >= ch.data_abertura
GROUP BY a.id_atendente, a.nome
ORDER BY a.nome, a.id_atendente;
