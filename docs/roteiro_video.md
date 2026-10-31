# Roteiro do vídeo demonstrativo

O vídeo é responsabilidade dos integrantes e deve ser gravado após confirmar que a aplicação funciona na VM Linux. Não exponham senhas pessoais ou dados reais; usem apenas os dados fictícios desta cópia.

## Preparação da gravação

- Escolher e registrar a versão final apresentada. Usar esta cópia apenas se ela for a versão acordada pelo grupo.
- Seguir `validacao_vm.md` e preparar chamados suficientes para mostrar cancelamento e resolução em registros diferentes. O chamado cancelado é excluído fisicamente e não reaparece no histórico.
- Habilitar a conta fictícia e configurar seu email em `MANUTENCAO_EMAILS` para a demonstração administrativa. Preparar também uma conta sem autorização para mostrar o bloqueio.
- Não abrir o `.env` na gravação. A senha fictícia do README é pública e exclusiva para demonstração.

1. Apresentar objetivo, grupo, disciplina e ambiente. Mostrar a splash e as quantidades de registros.
2. Demonstrar abertura por cliente existente e novo, inclusive retornar para corrigir o email; mostrar confirmação e retorno ao menu.
3. Consultar chamados pelo email, abrir detalhes, cancelar um chamado com confirmação e demonstrar a opção de voltar.
4. Fazer login com conta fictícia. Assumir um chamado automaticamente e exibir os detalhes. Abrir meus chamados, resolver e consultar o histórico.
5. Apresentar os relatórios de tempo médio e detalhes de chamados. Explicar que a média vai da abertura ao fechamento, em segundos.
6. Apresentar a manutenção de clientes, atendentes e chamados: inclusão, atualização, exclusão confirmada e bloqueio de exclusão de cliente referenciado.
7. Demonstrar saída, README, diagrama e repositório. Publicar o vídeo no YouTube e inserir o link na documentação do grupo.

## Sequência dos menus e evidências

| Parte | Caminho | O que mostrar |
| --- | --- | --- |
| Abertura | Inicial → 1 | Email corrigido com Voltar, cadastro confirmado, título/descrição e status aberto. |
| Consulta | Inicial → 2 | Lista numerada, detalhes, confirmação negativa e depois exclusão de um chamado elegível. |
| Atendimento | Inicial → 3 → login → 1 | Chamado atribuído automaticamente, responsável e mudança para em andamento. |
| Resolução | Menu do atendente → 3 → selecionar → 1 | Fechamento registrado; chamado sai dos ativos e aparece no histórico. |
| Histórico | Menu do atendente → 2 | Lista e detalhes dos resolvidos pelo atendente da sessão. |
| Relatórios | Menu do atendente → 4 → 1 e 2 | Média em segundos e detalhes; explicar ausência de amostra e responsável opcional. |
| Manutenção | Menu do atendente → 5 | CRUD de clientes, atendentes e chamados, confirmações e referências impeditivas. Não excluir a própria conta antes de terminar as demais demonstrações. |
| Acesso negado | Login com atendente fora da lista → 5 | Operação administrativa negada sem impedir o atendimento normal. |
| Encerramento | Menu do atendente → 0; inicial → 0 | Logout, saída e indicação dos arquivos de documentação e diagrama. |

Os resultados concorrentes anteriores podem ser citados como evidência histórica, informando que os arquivos de testes foram removidos; não atribuir a uma gravação de sessão única prova de concorrência.

## Publicação

Depois da gravação, conferir áudio, legibilidade e cobertura dos menus. Publicar conforme o edital, testar o acesso ao link com outro integrante e preencher o README e `entrega_projeto.md`. Até essa verificação, manter o vídeo como pendente.
