# Modelo existente de atendimento

Fonte canônica: `sql/create_tables_atendimento.sql`. Clientes e atendentes possuem identificadores gerados automaticamente, nome, email único e telefone obrigatórios. Atendentes também possuem senha obrigatória; seu formato é decisão de autenticação e não aparece nos relatórios.

Chamados têm identificador gerado, cliente obrigatório, atendente opcional, título armazenado em `nome`, descrição, abertura, fechamento opcional e status obrigatório. O banco aceita `aberto`, `em andamento` e `resolvido`. A abertura tem valor padrão, mas ainda aceita nulo; o fechamento aceita nulo. Uma FK liga cada chamado a um cliente e outra, opcionalmente, a um atendente. Um cliente ou atendente pode aparecer em vários chamados. Sem cláusula de exclusão em cascata, vínculos existentes impedem a exclusão do registro referenciado.

O diagrama `diagrams/diagrama_relacional_atendimento.mmd` e seu PNG representam estas características. Mudanças no arquivo de criação não são migrações de bancos existentes.
