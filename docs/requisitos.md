# Requisitos das telas

## Funcionais

1. Menu inicial com abertura, consulta, login e saída; navegação contínua.
2. Busca por email antes de cadastrar cliente; reaproveitar cliente existente.
3. Novo cadastro com nome, email e telefone, confirmação e retorno para corrigir email.
4. Abertura com título, descrição, confirmação e resultado com identificador.
5. Consulta diferenciando cliente inexistente, sem chamados e sem chamados abertos.
6. Seleção numerada, detalhes, responsável ausente e cancelamento confirmado.
7. Login com senha oculta, credenciais inválidas sem sessão e logout.
8. Submenu do atendente com fila automática, histórico, meus chamados e relatórios.
9. Resolução confirmada usando a identidade da sessão e exibição do resultado.
10. Manutenção local de clientes, atendentes e chamados, com listagem prévia,
    seleção, inclusão, atualização sem alterar chave, remoção confirmada e retorno.
11. Dois relatórios: agrupamento de tempo total até resolução e detalhes com junção.
12. Splash com identificação acadêmica e contagens fornecidas pelo módulo de relatórios.

## Regras e limites

Entradas vazias e opções inválidas devem permitir nova tentativa. Email deve ter
formato básico válido; telefone permanece texto, contendo dígitos. Senhas não
aparecem em listagens, detalhes ou mensagens de falha de login.

Estados persistidos: aberto, em andamento, resolvido. Título mapeia para nome;
não há coluna nova. Cancelamento é DELETE, permitido apenas para aberto do
titular. Resolução exige responsável autenticado, estado válido e fechamento.
A fila deve ser atômica no banco. Esses controles persistentes são das controladoras.

As políticas de retorno, cadastro confirmado e manutenção estão detalhadas em
[contratos_cli.md](contratos_cli.md). A política de senha, normalização definitiva
de email, acesso à manutenção, nomes completos da equipe e convenção de datas
precisam de confirmação do grupo. Não existe nova entidade ou novo estado.
