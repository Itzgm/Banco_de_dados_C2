SELECT f.id, f.nome, f.equipe,
       COUNT(a.id) FILTER (WHERE a.status='FECHADO') AS atendimentos_fechados,
       ROUND((AVG(EXTRACT(EPOCH FROM (a.data_fechamento-a.data_abertura))/60)
             FILTER (WHERE a.status='FECHADO'))::numeric, 2) AS media_minutos
FROM funcionarios f LEFT JOIN atendimentos a ON a.funcionario_id=f.id
GROUP BY f.id, f.nome, f.equipe ORDER BY f.nome;
