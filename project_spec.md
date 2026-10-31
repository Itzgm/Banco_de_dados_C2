> Versão integrada das branches de Ricardo e Davi. Consultar docs/integracao_branches.md para as mudanças de nomes, interfaces e confirmações aplicadas sobre esta especificação histórica.

# Especificação técnica — sistema de atendimento

## 1. Objetivo e escopo

Concluir, nesta pasta de estudo, uma aplicação de terminal em Python com PostgreSQL para cadastrar clientes, abrir e acompanhar chamados, atender a fila e produzir relatórios. Esta especificação organiza o trabalho necessário para uma entrega demonstrável e compatível com o planejamento e o edital da disciplina.

**Escopo:** `base_exemplo/` é uma cópia independente dos arquivos da aplicação oficial da raiz. As mudanças nesta cópia não atualizam automaticamente a aplicação oficial; antes da entrega, o grupo deve decidir qual versão apresentará e integrar e testar nela as alterações escolhidas. O banco configurado para a cópia também deve ser separado do banco oficial.

**Fontes:** `../docs/planejamento_projeto.md`, `../docs/plano_adequacao_codigo.md`, contratos e matriz em `../docs/`, edital já analisado nesses documentos e código desta pasta. O diagnóstico original do planejamento é histórico; a matriz da raiz descreve a implementação oficial, não comprova o estado desta cópia. Se houver divergência, prevalecem o edital e as decisões explícitas do usuário; dúvidas permanecem abertas até confirmação.

**Método de execução:** para cada etapa, conferir o estado existente, implementar apenas a lacuna identificada, validar os critérios e registrar o resultado antes de integrar a etapa seguinte. As etapas podem avançar em paralelo quando usarem os contratos e arquivos combinados. Não há necessidade de recriar o modelo de dados.


**Atualização de escopo:** os testes automatizados foram removidos da `base_exemplo` por solicitação do usuário. As tarefas e resultados de testes citados abaixo preservam o histórico do desenvolvimento; a verificação atual segue `docs/validacao_vm.md`.

**Atualização de arquitetura:** a organização foi substituída pela abordagem do repositório de referência: PostgresQueries direto nos controllers, CRUD/formulários por entidade e despacho por funções em principal.py. Em caso de divergência com tarefas históricas abaixo, consultar `docs/contratos_componentes.md` e `docs/refatoracao_arquitetura_original.md` para o estado implementado.

## 2. Diagnóstico da cópia

Este diagnóstico registra a análise anterior às etapas 1 a 4; não descreve todos os ajustes posteriores. Os registros em cada etapa e os testes desta cópia indicam o progresso realizado.

| Área | Situação identificada | Trabalho restante |
| --- | --- | --- |
| Banco | `sql/create_tables_atendimento.sql` define clientes, atendentes e chamados, com relacionamentos e status. | Validar instalação limpa e falhas; preservar o modelo existente e avaliar dados antigos antes de alterar restrições. |
| Conexão | `src/conexion/postgres_queries.py` oferece conexão e transações. | Conferir fechamento, rollback, mensagens e testes de falha no ambiente real. |
| Fluxos | `src/principal.py` contém menus de abertura, consulta, login, fila, histórico, resolução, relatórios e manutenção; `src/controller/sistema.py` realiza as operações. | Validar cenários completos e corrigir diferenças listadas abaixo. A presença do código não prova que todos os fluxos funcionem. |
| Identidade | Busca e login comparam email exatamente; a versão inicial utilizava hash de senha (posteriormente substituído por texto direto). | Normalizar email e tratar duplicidade e dados antigos ambíguos; revisar validações e acesso. |
| Manutenção | O menu de manutenção é apresentado após qualquer login de atendente. | Restringir às contas da lista local de emails autorizados, decisão já tomada pelo usuário, e verificar a autorização nas operações também. |
| Chamados | Há exclusão condicionada ao cliente e status, atribuição com bloqueio e resolução condicionada ao responsável. | Revalidar também ausência de responsável no cancelamento; testar concorrência, estados e mensagens. |
| Organização | A interface contém SQL direto e a controladora `Sistema` concentra operações; modelos herdados não representam necessariamente o caminho ativo. | Separar responsabilidades e integrar modelos e contratos conforme o edital e planejamento, sem mudar comportamento involuntariamente. |
| Relatórios e instalação | Existem relatórios, scripts e instruções próprias no README. | Confirmar resultados, portabilidade, tratamento de falhas e instalação na VM Linux. |
| Testes | `tests/test_integracao_postgres.py` existe e usa banco dedicado e schema temporário. | Executar e ampliar a cobertura necessária para esta cópia; os 27 testes aprovados da raiz não certificam esta versão. |
| Legado | Há arquivos de pedidos e Oracle copiados como referência. | Garantir que não sejam carregados no caminho ativo e identificar seu caráter histórico na documentação. |

## 3. Regras funcionais

### 3.1 Abertura e consulta pelo cliente

- Menu inicial: abrir chamado, verificar meus chamados, login do atendente e sair. Opções inválidas não devem encerrar a aplicação.
- Solicitar email, validar e procurar o cliente. Se não existir, solicitar nome e telefone, reutilizando o email. Permitir voltar em cada etapa e corrigir o email com nova busca; não persistir cadastro incompleto.
- Solicitar título e descrição não vazios. Criar chamado com cliente, data de abertura, status `aberto`, sem atendente e sem fechamento. O título corresponde a `chamados.nome`. Confirmar o identificador e oferecer repetição.
- Na consulta, distinguir cliente inexistente, cliente sem chamados e cliente sem chamados elegíveis. Listar os chamados literalmente `aberto`, numerados, com título e identificação. Exibir título, descrição, status e responsável ou indicação de ausência.
- Cancelar significa exclusão física após confirmação. Revalidar na própria operação cliente, status `aberto` e ausência de atendente; se algo mudou, avisar e atualizar a lista. Não excluir chamados resolvidos nem inventar status de cancelamento. A extensão desse filtro depende de decisão do grupo.

### 3.2 Atendentes e ciclo de vida

- Login por email e senha visível durante a digitação; responder de forma genérica a credenciais inválidas. Manter na sessão apenas a identidade necessária e não mostrar a senha nos dados da sessão ou relatórios. Sair do submenu encerra a sessão e retorna ao menu inicial.
- Assumir automaticamente o chamado mais antigo com status `aberto` e sem atendente, usando o identificador como desempate. A seleção e atribuição devem ser atômicas; duas sessões não podem assumir o mesmo chamado. Um registro bloqueado pode ser ignorado temporariamente; não confundir ausência momentânea com erro de banco.
- Ao assumir, registrar responsável e status `em andamento` e apresentar os dados. A expressão “em atendimento” pode ser usada na interface, mantendo o valor persistido existente.
- Meus chamados lista os atendimentos `em andamento` do próprio atendente, permite visualizar e resolver. A resolução revalida responsável e estado, registra fechamento uma única vez e não altera um fechamento anterior.
- Histórico lista chamados `resolvido` do atendente logado e permite ver detalhes. A sequência prevista é `aberto` → `em andamento` → `resolvido`; reabertura, transferência e novos estados não estão previstos.

### 3.3 Manutenção, relatórios e apresentação

- Disponibilizar inserção, atualização e exclusão de clientes, atendentes e chamados conforme o edital, somente a atendentes autenticados cujo email armazenado conste em `MANUTENCAO_EMAILS`, lista local separada por vírgulas. Lista vazia nega acesso. Conferir essa autorização também na camada que executa as operações, não apenas ocultando o menu. O cadastro público de cliente e a abertura de chamado continuam disponíveis.
- Antes de alterar ou excluir, listar identificação e descrição dos registros. Preservar chaves primárias, confirmar exclusões, tratar referências e exibir resultado ou erro. Alterações de chamado não podem deixar responsável, status e datas incoerentes.
- Exibir relatório detalhado com cliente e responsável opcional e relatório de média por atendente. A média mede o tempo entre abertura e fechamento, em segundos; não representa tempo efetivo de trabalho. Considerar atendentes sem amostra e não exibir senhas.
- A tela inicial deve apresentar aplicação, disciplina, professor, semestre, integrantes e contagem real das três tabelas, conforme o edital. Integrantes: Natan Ferreira Garcia, Ricardo Otoni Ventura, Felipe Cesconeti e Davi Tavares da Cunha.

## 4. Validação, segurança e erros

- Emails: obrigatórios, sem espaços externos, formato básico válido, normalizados e comparados sem distinção de maiúsculas. Tratar duplicidade e recusar ambiguidades em dados antigos. A unicidade atual do banco não impede inserções externas que diferem apenas por caixa; avaliar essa limitação sem presumir migração.
- Nomes, títulos e descrições: não aceitar vazio ou apenas espaços. Telefone é texto, preserva zeros e prefixos e deve conter pelo menos um dígito. Limites adicionais dependem de decisão.
- Senhas: obrigatórias, visíveis durante a digitação e armazenadas em texto direto por decisão do usuário; nunca registrar ou retornar senha em objetos públicos, relatórios ou mensagens. Não prometer recuperação de senha sem requisito.
- Tratar opções inválidas, listas vazias, duplicidade, registro ausente, conflito de estado, violação de referência e indisponibilidade do banco com mensagens distintas e sem falso sucesso. Desfazer transações incompletas e liberar conexões.
- Usar parâmetros nas consultas e não ORM; o edital menciona concatenação, portanto confirmar com o professor a aceitação de consultas parametrizadas. Não inserir credenciais em arquivos versionados.
- A identificação pública apenas por email atende ao fluxo solicitado, mas não é autenticação forte. A lista de manutenção protege o fluxo da aplicação, não substitui permissões do PostgreSQL.

## 5. Estrutura e contratos propostos

Os nomes abaixo descrevem responsabilidades e podem ser adaptados ao estilo existente; seus contratos precisam ser acordados antes da integração. Evitar SQL na CLI e evitar expor tuplas do driver diretamente à interface.

| Componente | Entrada e responsabilidade | Saída e erros |
| --- | --- | --- |
| CLI, `src/principal.py` e eventuais módulos de interface | Lê entradas, navega, solicita confirmações e chama controladoras com dados e identidade da sessão. | Exibe objetos ou mensagens; trata entradas inválidas e erros de domínio. Não executa SQL. |
| Clientes, `src/controller/controller_cliente.py` | Buscar por id/email, cadastrar e executar manutenção autorizada. | Cliente ou ausência na busca; erros explícitos de validação, duplicidade, referência e acesso. |
| Atendentes, `src/controller/controller_atendente.py` | Autenticar email/senha e manter cadastros mediante autorização. | Identidade pública ou ausência no login; erros explícitos nas demais operações. |
| Chamados, `src/controller/controller_chamado.py` | Criar, listar por cliente ou atendente, consultar, cancelar, assumir e resolver; manutenção autorizada. | Chamado, coleção ou indicação específica de ausência/conflito; operações verificam titularidade, estado e sessão. |
| Modelos, `src/model/` | Representar cliente, atendente e chamado, com cliente e atendente opcional associados. | Dados de domínio sem senha; mapear explicitamente título para `nome` do banco. |
| Persistência, `src/conexion/` | Receber operações parametrizadas e coordenar conexão, leitura e transação. | Dados mapeáveis ou erros propagados; confirmação e rollback previsíveis, inclusive para fila concorrente. |
| Autorização e validação, `src/utils/` | Normalizar e validar dados; conferir lista de emails usando identidade armazenada do atendente. | Dados válidos ou erros compreensíveis; lista vazia impede manutenção. |
| Relatórios, `src/reports/` e `src/sql/` | Consultar totais, detalhes e média sem acesso a senhas. | Resultado vazio ou dados de relatório, distinguindo falha de consulta. |

A controladora monolítica antiga foi removida após a migração; a CLI usa as controladoras separadas. Os contratos desta cópia estão em `docs/contratos_componentes.md` e foram alinhados aos contratos da raiz.

## 6. Etapas de implementação e conclusão

As etapas a seguir são a ordem sugerida para integrar o sistema. Depois de acordados os contratos da etapa 2, as etapas 3, 4, 5 e 6 podem ser desenvolvidas em paralelo com simulações; sua validação integrada depende da etapa 7. Nenhuma etapa está marcada como concluída apenas por existir código semelhante.

### Etapa 1 — Preparação do ambiente e do banco

**Registro de execução:** conexão, instalação e comportamento transacional foram verificados no PostgreSQL local isolado e por simulações; consulte o README para as instruções e limites. A execução na VM Linux permanece pendente.

**Objetivo:** obter uma base reproduzível e isolada para desenvolver e testar a cópia.

**Arquivos:** `.env.example`, `src/requirements.txt`, `src/conexion/`, `src/create_tables_and_records.py`, `sql/create_tables_atendimento.sql` e README.

**Tarefas:**

- Conferir dependências, configuração local e banco dedicado com dados fictícios; manter credenciais fora do Git.
- Verificar conexão, encerramento e transações; conferir que o instalador usa o modelo existente e não recria nem apaga dados existentes.
- Validar instalação em banco vazio, reexecução e falha intermediária, incluindo mensagem e rollback apropriados para cada etapa do instalador.

**Dependência:** PostgreSQL disponível. **Pronto quando:** instalação e inicialização funcionarem no banco isolado e falhas não produzirem falso sucesso; registrar os resultados.

### Etapa 2 — Contratos e modelos

**Registro de execução:** modelos públicos de atendente e chamado e contratos em `docs/contratos_componentes.md` foram preparados e testados. As controladoras e o mapeamento foram integrados nas etapas seguintes.

**Objetivo:** definir como as partes se comunicam antes de desenvolvê-las em paralelo.

**Arquivos:** `src/model/`, controladoras, utilitários de erros e contratos da seção 5.

**Tarefas:**

- Acordar entradas, saídas e erros para identidade, chamados, persistência e relatórios.
- Revisar os modelos de cliente, atendente e chamado, incluindo associações e responsável opcional; manter senhas fora dos objetos públicos.
- Consolidar as controladoras separadas e evitar duas implementações ativas da mesma regra; a migração da controladora antiga já foi concluída.

**Dependência:** modelo de dados existente. **Pronto quando:** as interfaces estiverem documentadas e puderem ser exercitadas com dados simulados, sem expor linhas do driver à CLI.

### Etapa 3 — Clientes, autenticação e autorização

**Registro de execução:** controladoras e validações integradas à CLI; manutenção protegida por lista local e testes de integração preparados. Revisar resultados e limitações no README.

**Objetivo:** concluir cadastro e identificação, protegendo a manutenção.

**Arquivos:** controladoras de cliente e atendente, `src/model/` e utilitários de validação, senha e autorização.

**Tarefas:**

- Validar nome, email e telefone; normalizar emails e tratar duplicidade e ambiguidade de registros antigos.
- Implementar login por email e senha visível durante a digitação e armazenamento em texto direto; não expor credenciais nos resultados.
- Configurar `MANUTENCAO_EMAILS` e verificar o email armazenado do atendente em cada operação administrativa. Lista vazia bloqueia manutenção; o cadastro público continua disponível.
- Completar manutenção de clientes e atendentes, respeitando referências e tratamento de erros.

**Dependência:** contratos da etapa 2. **Pronto quando:** cadastro, busca, login e manutenção passarem nos cenários válidos e inválidos, inclusive acesso negado diretamente na controladora.

### Etapa 4 — Ciclo de vida dos chamados

**Registro de execução:** controladora de chamados integrada à CLI, incluindo cancelamento condicionado, atribuição atômica e resolução; há testes de ciclo e concorrência na suíte da cópia.

**Objetivo:** concluir abertura, consulta, cancelamento, atribuição e resolução.

**Arquivos:** controladora e modelo de chamados, persistência necessária e testes próprios.

**Tarefas:**

- Abrir chamado com cliente, título, descrição e status inicial; listar e detalhar apenas os chamados cabíveis em cada fluxo.
- Cancelar com confirmação e revalidação de cliente, status e ausência de atendente na operação de exclusão.
- Atribuir automaticamente o mais antigo elegível, com desempate por identificador e transação que impeça atribuição duplicada.
- Listar atendimentos próprios e histórico; resolver somente chamado próprio em andamento e registrar fechamento uma única vez.
- Proteger a manutenção e impedir alterações que deixem status, responsável e datas incoerentes.

**Dependência:** contratos da etapa 2; banco isolado para concorrência. **Pronto quando:** ciclo, titularidade, estados e disputas entre sessões forem verificados com PostgreSQL real.

### Etapa 5 — Interface e navegação

**Registro de execução:** listas de chamados resumidas com detalhes na seleção; cancelamento e resolução em conflito atualizam a listagem; falhas dos relatórios são tratadas no submenu; exclusão da própria conta retorna à validação da sessão. Ver evidências e limites em `docs/validacao_etapas_5_6.md`.

**Objetivo:** oferecer todos os fluxos pela CLI usando os contratos acordados.

**Arquivos:** `src/principal.py` e eventuais módulos de interface.

**Tarefas:**

- Organizar menu inicial e submenu do atendente; implementar seleção numerada, opções inválidas e retorno consistente.
- Permitir correção do email durante cadastro, confirmação de cancelamento, repetição das operações e mensagens claras de ausência ou falha.
- Exibir detalhes de chamados, relatórios e manutenção conforme a sessão e autorização; remover consultas SQL diretas da interface.
- Exibir apresentação e contagens previstas no edital, com dados reais.

**Dependência:** contratos da etapa 2; pode começar com controladoras simuladas. **Pronto quando:** os menus funcionarem com simulações e, após a integração, com o banco real, sem perder sessão nem permitir manutenção não autorizada.

### Etapa 6 — Relatórios e isolamento do legado

**Registro de execução:** erros de conexão, consulta e arquivos de relatório traduzidos para erro da aplicação, com fechamento das conexões. Caminho ativo revisado sem referências a Oracle/pedidos. Ver evidências e limites em `docs/validacao_etapas_5_6.md`.

**Objetivo:** disponibilizar informações corretas e manter o caminho ativo restrito ao sistema de atendimento.

**Arquivos:** `src/reports/`, `src/sql/`, `src/conexion/` e configuração da aplicação.

**Tarefas:**

- Conferir contagens, relatório detalhado e média entre abertura e fechamento, incluindo atendente sem amostra e chamado sem responsável.
- Tratar relatórios vazios e falhas de banco sem expor senhas.
- Garantir que o início da aplicação não dependa de Oracle, arquivos de pedidos ou diretório corrente; identificar o legado como referência.

**Dependência:** conexão e schema existentes. **Pronto quando:** resultados forem conferidos com dados conhecidos e a aplicação iniciar sem dependências do exemplo antigo.

### Etapa 7 — Integração e testes

**Registro de execução:** validação automatizada local concluída com 42 testes aprovados, sem testes ignorados, na versão atual. Novos cenários cobrem CLI completa, manutenção de cliente, exclusão da própria conta, titularidade, autorização após mudança de email, validação sem persistência e datas inválidas na média. Evidências em `docs/matriz_aceite_etapa_7.md`; aceite manual e VM Linux permanecem pendentes.

**Objetivo:** comprovar que os componentes funcionam juntos e satisfazem as regras.

**Arquivos:** `tests/`, módulos integrados e registros de teste.

**Tarefas:**

- Integrar etapas 1 a 6 e executar testes de componentes, CLI e PostgreSQL isolado.
- Verificar fluxo completo de cliente e atendente, autorização, concorrência, integridade, tratamento de erros e relatórios conforme a seção 8.
- Corrigir falhas encontradas, repetir os testes afetados e registrar ambiente, resultado e limitações reais.

**Dependência:** entregas das etapas 1 a 6. **Pronto quando:** os critérios funcionais e técnicos aplicáveis da seção 8 estiverem comprovados nesta cópia; falhas e pendências devem permanecer registradas.

### Etapa 8 — Documentação e entrega acadêmica

**Registro de execução:** materiais locais preparados e revisados: README, contratos, diagrama existente, roteiro de vídeo, guia de validação na VM, checklist e `docs/entrega_projeto.md`. A etapa permanece parcialmente concluída até a execução real na VM, escolha da versão final, revisão dos integrantes e conclusão das ações externas de entrega.

**Objetivo:** preparar uma versão verificável e demonstrável para avaliação.

**Arquivos:** README, diagrama, `docs/checklist_entrega.md`, roteiro de vídeo e documentação da versão escolhida.

**Tarefas:**

- Atualizar instruções, contratos, diagrama, limitações e evidências conforme o comportamento testado.
- Instalar e executar na VM Linux da disciplina com acompanhamento de outra pessoa do grupo.
- Escolher e revisar a versão a entregar; confirmar decisões com o professor e registrar contribuições reais.
- Conferir acesso ao repositório, vídeo, link e submissão no AVA conforme o checklist.

**Dependência:** integração e testes da etapa 7. **Pronto quando:** a versão escolhida estiver demonstrada na VM e os entregáveis acadêmicos aplicáveis estiverem efetivamente concluídos e conferidos.

## 7. Trabalho paralelo da equipe

| Responsável | Domínio e arquivos de trabalho sugeridos | Independência e integração |
| --- | --- | --- |
| Natan Ferreira Garcia | Banco, conexão, instalação e relatórios: `src/conexion/`, `sql/`, `src/reports/`, `src/sql/`, instalador e testes próprios. | Usa banco local isolado e dados fictícios. Publica primeiro os contratos de transação, relatórios e instalação. |
| Ricardo Otoni Ventura | Clientes, atendentes, identidade e autorização: respectivas controladoras, modelos e utilitários de validação, senha e acesso. | Usa repositório simulado e testa com banco após o contrato de persistência; publica identidade pública, erros e contrato de autorização. |
| Felipe Cesconeti | Chamados, ciclo e fila: controladora e modelo de chamados, com testes próprios. | Usa identidades fictícias e repositório simulado; depois testa concorrência real. Publica operações, estados e retornos. |
| Davi Tavares da Cunha | CLI, integração, apresentação e documentação: `src/principal.py`, módulos de interface, README e checklist. | Desenvolve menus com respostas simuladas; integra após os contratos. Coordena teste de ponta a ponta e demonstração. |

Esta divisão é proposta de coordenação; o grupo pode trocar responsáveis. Cada arquivo compartilhado deve ter um responsável de integração. Os contratos de persistência, identidade e chamados são as entregas iniciais que destravam os demais. Criar branches individuais, commits pequenos e revisões cruzadas; integrar sem sobrescrever trabalho alheio e sem publicar credenciais. Não fazer push ou mesclagem sem a autorização aplicável.

## 8. Plano de testes e critérios de aceite

Executar testes automatizados apropriados e registrar evidências manuais nesta cópia; nunca assumir que resultados da raiz se aplicam automaticamente. Os testes com banco devem usar ambiente isolado, dados fictícios e schema temporário, sem apagar bancos ou tabelas de terceiros.

1. **Instalação:** banco vazio, instalação completa, reexecução segura, erro no meio da instalação, conexão indisponível, execução a partir de outro diretório e execução limpa na VM Linux.
2. **Cliente:** email existente e novo, correção durante cadastro, entrada inválida, duplicidade incluindo caixa diferente, dados antigos ambíguos, retorno sem persistir cadastro incompleto.
3. **Chamados públicos:** abertura, lista vazia, detalhes, cancelamento confirmado e recusado, titularidade errada e concorrência entre cancelar e assumir.
4. **Atendimento:** login válido/inválido, senha visível durante a digitação, fila vazia, ordem por data e id, duas sessões simultâneas, somente chamados próprios, resolução e tentativa repetida, histórico filtrado.
5. **Autorização e CRUD:** usuário autorizado e não autorizado, lista vazia, chamadas diretas às operações, entradas inválidas, confirmação, referências existentes e ausência de exposição de credenciais.
6. **Relatórios e interface:** contagens reais, detalhes sem responsável, média conhecida e sem amostras, opções inválidas, retorno, repetição e saída segura.
7. **Entrega:** instalar seguindo o README na VM da disciplina; apresentar menus e relatórios; verificar diagrama, vídeo, link do repositório e acesso do professor. Registrar resultados e pendências sem marcar como realizado o que ainda não foi verificado.

O sistema somente será considerado concluído quando os itens aplicáveis estiverem implementados, testados na versão escolhida para entrega e aceitos pelo grupo, e quando as exigências acadêmicas externas forem comprovadas.

## 9. Marcos e decisões em aberto

- **M1 — Contratos e ambiente:** concluir etapas 1 e 2 e permitir trabalho paralelo.
- **M2 — Ciclo principal:** integrar identidade, abertura, consulta, fila e resolução; validar concorrência em PostgreSQL.
- **M3 — Conformidade funcional:** integrar manutenção autorizada, relatórios, erros e testes; executar a matriz de aceite.
- **M4 — Entrega:** validar na VM, revisar documentação e concluir vídeo, acesso e submissão.

Decisões e verificações pendentes:

1. Confirmar com o professor se SQL parametrizado sem ORM atende ao texto do edital sobre concatenação e se o tamanho atual do grupo é aceito.
2. Confirmar se “em aberto” inclui chamados em andamento para consulta e cancelamento; até lá, manter a regra provisória de status literal `aberto` e sem responsável.
3. Definir interpretação de fuso e calendário das datas sem fuso e política adicional de formato/comprimento de telefone e senha, sem inventar requisitos.
4. Definir o tratamento de cliente já cadastrado quando a abertura posterior é abandonada e revisar atributos editáveis da manutenção.
5. Escolher a versão final para entrega e integrar somente alterações efetivamente revisadas e testadas; manter os documentos das duas versões coerentes.
6. Confirmar execução na VM, registrar contribuições reais dos integrantes, convidar `howardroatti`, gravar/publicar vídeo e enviar o link no AVA. Esses itens externos não estão comprovados por este documento.
