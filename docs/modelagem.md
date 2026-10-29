# Modelo relacional

## Clientes
- id: chave primária inteira positiva.
- nome, email e telefone: obrigatórios; email é único.

## Funcionários
- id: chave primária inteira positiva.
- nome e equipe: obrigatórios.

## Atendimentos
- id: chave primária inteira positiva.
- cliente_id e funcionario_id: FKs obrigatórias.
- assunto, descrição, abertura e status são obrigatórios.
- data_fechamento é nula enquanto aberto; atendimento fechado precisa de fechamento.
- fechamento não pode anteceder abertura.

## Cardinalidades
Cliente 1 para 0..N atendimentos; funcionário 1 para 0..N atendimentos.
Cada atendimento pertence a exatamente um cliente e um funcionário.
A exclusão de cliente/funcionário com histórico é restringida para preservar os atendimentos.
