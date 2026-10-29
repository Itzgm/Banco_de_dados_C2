# Planejamento do sistema de chamados de suporte

Data da análise: 29/10/2026. Equipe: quatro desenvolvedores, identificados como Pessoas 1 a 4 até a atribuição dos nomes.

Atualização após o diagnóstico: o script canônico agora é `sql/create_tables_atendimento.sql`; o instalador foi direcionado a ele, usa caminhos independentes da pasta de execução, propaga falhas e fecha conexões. A carga passou a usar somente o placeholder de atendimento. Cliente e status do chamado foram tornados obrigatórios nos scripts de criação; a cópia em `src/sql/create_tables` foi sincronizada. O valor persistido continua sendo `em andamento`. Os itens do diagnóstico abaixo descrevem a fotografia anterior e devem ser considerados parcialmente resolvidos por essas correções. Não houve execução contra servidor real nem migração de tabelas existentes.

## 1. Objetivo e fontes

Entregar uma aplicação CLI em Python com PostgreSQL para abertura, consulta, atribuição e resolução de chamados de suporte, cumprindo também o edital da disciplina. Este documento planeja a conclusão do projeto existente. Não altera o modelo de dados e não contém implementação.

Fontes: arquivos locais do repositório, inclusive alterações ainda não commitadas; edital C2 fornecido em PDF, com 14 páginas. Referências principais: itens 2–6, entregáveis do item 7, observações do item 8, FAQ e orientações de desenvolvimento. O diagnóstico é estático: não certifica o funcionamento contra um servidor PostgreSQL nem a configuração do GitHub/AVA.

Quando houver diferença entre a experiência solicitada e o edital, os requisitos acadêmicos têm prioridade. Uma decisão pendente não autoriza remover um requisito do aceite.

## 2. Diagnóstico do estado atual

| Componente | Evidência no repositório | Estado e trabalho restante |
| --- | --- | --- |
| Modelo PostgreSQL | `src/sql/create_tables`, arquivo sem extensão | Existem três tabelas: clientes, atendentes e chamados. Há identidades, emails únicos, senha do atendente, referências, datas e restrição de status. É a referência existente; não criar outro schema. Execução no banco não confirmada. |
| Placeholders de banco | `sql/create_tables_atendimento.sql` e `sql/inserting_samples_atendimento.sql` | Vazios. Não representam uma segunda modelagem pronta. Consolidar a localização do script existente e preparar dados de demonstração compatíveis. |
| Instalação | `src/create_tables_and_records.py` | Já usa PostgresConnection, mas procura `../sql/create_tables.sql`, que não está no inventário, e ainda carrega dados do exemplo de vendas. Continua após falhas de criação e pode anunciar sucesso indevidamente; não fecha explicitamente as conexões. |
| Conexão | `src/conexion/postgres_queries.py` | Implementa conexão, leitura em três formatos, escrita, confirmação, rollback e fechamento. Há docstring de Oracle em connect e espaços finais. Commits por operação exigem cuidado para operações compostas. Não há validação atual contra banco real. |
| Dependências/configuração | `src/requirements.txt`, `.env.example`, `.env` local | Driver PostgreSQL e dotenv declarados; exemplo de configuração presente e arquivo local ignorado pelo Git. Credenciais e existência do banco não são certificadas por esta análise. |
| Cliente | `src/model/clientes.py`, `src/controller/controller_cliente.py` | Código legado usa CPF/nome, Oracle e interação de terminal dentro da controladora. Incompatível com id, email e telefone do modelo atual. Verificação de existência retorna verdadeiro quando o resultado está vazio, tornando o nome enganoso. |
| Atendente e chamado | `src/model/funcionarios.py`, `src/model/atendimentos.py`, controladoras correspondentes | Placeholders vazios. Login, fila, atribuição, encerramento e histórico não foram implementados nesses arquivos. Os nomes de arquivo diferem das tabelas; documentar o mapeamento sem criar entidades duplicadas. |
| CLI e navegação | `src/principal.py`, `src/utils/config.py` | Menu de vendas com cinco entidades. Conversão direta de opção para inteiro pode falhar; opção inválida encerra a aplicação. Os fluxos solicitados ainda não existem. Objetos antigos são construídos antes da entrada principal. |
| Splash | `src/utils/splash_screen.py` | Exibe vendas, professor como criador, semestre 2022/2 e contagens Oracle de tabelas antigas. Precisa refletir o grupo, semestre e três tabelas reais. |
| Relatórios | `src/reports/relatorios.py`, `src/sql/relatorio_*.sql` | Relatórios executáveis ainda são do exemplo Oracle/pedidos. Os três placeholders de funcionários, detalhes de atendimentos e tempo médio estão vazios. Há dependência do diretório de execução ao abrir arquivos. |
| Testes | `tests/test_postgres_queries.py`, `src/test.py` | Há 14 testes unitários da conexão com simulação; o histórico anterior registra aprovação. Não foram reexecutados neste planejamento. O teste em src ainda é Oracle. Não há evidência de testes completos dos novos fluxos. |
| Documentação e diagrama | `README.MD`, `diagrams/`, `docs/`, `prompts.md` | README e diagrama exportado tratam de pedidos/Oracle. Diagrama novo e documentos de requisitos, modelagem, testes, checklist e vídeo são placeholders. Histórico de prompts existe. Vídeo final não foi identificado. |
| Integração | Controladoras de produto, pedido, fornecedor e item de pedido; `oracle_queries.py` | Exemplo legado ainda domina o caminho principal. Desligar suas referências no produto final, após os novos componentes existirem. A remoção física pode ser decidida depois. |

Nenhuma funcionalidade completa do novo sistema pode ser declarada funcionando apenas pela presença desses arquivos. A conexão é o componente mais adiantado; o restante precisa de implementação, adaptação e validação integrada.

### Modelo existente: compatibilidades e limites

- O título apresentado ao usuário corresponde ao campo `nome` de chamados. Não adicionar uma coluna de título.
- O responsável corresponde ao atendente associado. Os placeholders chamados funcionários e atendimentos serão usados como módulos de atendentes e chamados, respectivamente.
- Os valores aceitos de status são `aberto`, `em andamento` e `resolvido`. O rótulo “em atendimento” na CLI corresponde a `em andamento` na persistência.
- A senha já possui campo em atendentes; não existe bloqueio por ausência de coluna. O formato de armazenamento e a preparação das credenciais ainda precisam de decisão.
- Cliente e atendente associados podem ser nulos no modelo. A aplicação deve exigir cliente na criação e permitir responsável ausente enquanto o chamado aguarda na fila.
- O modelo possui abertura e fechamento, mas não possui data de início do atendimento nem eventos de movimentação. Não prometer duração exclusiva do trabalho do atendente ou trilha de eventos. Histórico solicitado significa consultar chamados resolvidos já existentes.
- Datas e status não têm todas as obrigatoriedades garantidas pelo banco. Registrar dados inconsistentes encontrados e tratar entradas pela aplicação; qualquer alteração de restrições exige decisão específica, sem redefinir o schema neste plano.

## 3. Experiência e regras de negócio

### 3.1 Menu inicial e abertura

O menu inicial contém 1 — Abrir um novo chamado, 2 — Verificar meus chamados, 3 — Login do atendente e 0 — Sair. Deve reaparecer até a saída, precedido de splash com nome da aplicação, nomes reais dos integrantes, professor, disciplina, semestre e contagem de cada tabela, conforme o edital.

Ao abrir, solicitar email e consultar o cliente. Se existir, reutilizar seu identificador. Caso contrário, solicitar nome e telefone reutilizando o email. Em cada etapa do cadastro, oferecer Voltar com destino claro; permitir retornar à etapa de email e corrigi-lo, refazendo a busca. Evitar gravar cliente enquanto o cadastro ainda estiver incompleto. Após confirmar o cadastro, pedir título e descrição e criar o chamado com status aberto, abertura registrada e sem responsável ou fechamento. Confirmar sucesso com identificador e título; oferecer repetição conforme o edital.

O retorno antes de confirmar o cadastro não deve persistir alterações. O que acontece com um cliente já confirmado se a abertura posterior for abandonada é uma decisão em aberto, não uma exigência de transação conjunta.

### 3.2 Consulta e cancelamento pelo cliente

Solicitar email e distinguir cliente inexistente, cliente sem chamados e cliente sem chamados elegíveis para a listagem. Mostrar opções numeradas com identificador e título. Ao selecionar, exibir título, descrição, status e responsável; usar “Ainda não atribuído” quando não houver atendente.

Exibir 1 — Cancelar chamado e 2 — Voltar. Cancelamento é exclusão física, com confirmação explícita e nova validação de titularidade e estado no momento da operação. Confirmação negativa não apaga nada. Chamado excluído não integra histórico nem relatórios posteriores; não simular um status cancelado que não existe no modelo. Chamados resolvidos não devem ser excluídos pelo fluxo descrito para chamados em aberto.

A abrangência da expressão “em aberto” e a possibilidade de excluir um chamado já em andamento precisam ser decididas. Até a definição, usar apenas o estado literal aberto no aceite provisório dessa listagem. Se o estado mudar entre exibição e confirmação, informar a mudança e atualizar a lista; não excluir silenciosamente.

### 3.3 Login e atendimento

Login solicita email e senha. Credenciais inválidas não criam sessão. Após sucesso, manter apenas a identidade necessária do atendente na sessão e apresentar 1 — Assumir um novo chamado, 2 — Verificar histórico, 3 — Meus chamados e 0 — Sair. A senha não deve aparecer nos detalhes, relatórios ou mensagens. O destino de Sair neste submenu deve ser definido antes da integração.

Assumir é automático: escolher o chamado aberto, sem responsável, com abertura mais antiga; usar identificador como desempate determinístico. A seleção, a associação ao atendente e a mudança para em andamento precisam constituir uma operação atômica. Duas sessões não podem receber o mesmo chamado. Se outro atendente disputar o registro, reavaliar a fila de forma limitada; diferenciar fila vazia de erro no banco. Ao assumir, exibir os detalhes e o estado resultante.

Histórico lista somente chamados resolvidos pelo atendente da sessão e permite consultar detalhes. Meus chamados lista os atribuídos ao atendente, com identificação de status e menu numerado; a composição exata entre ativos e encerrados fica em decisão. Um chamado selecionado permite detalhes e resolução. Para resolver, confirmar existência, estado em andamento e responsável da sessão, registrar fechamento e exibir resultado atualizado. Repetir a resolução não deve alterar a data original. Não permitir resolver chamado de outro atendente.

### 3.4 Validações e erros

| Entrada/situação | Regra mínima de implementação | Definição ainda necessária |
| --- | --- | --- |
| Email | Obrigatório; remover espaços externos; verificar formato básico antes da consulta; tratar duplicidade também no banco e repetir o fluxo sem encerrar a CLI. | Política sobre maiúsculas/minúsculas, pois a unicidade atual do texto não resolve sozinha a normalização. |
| Nome, título e descrição | Rejeitar conteúdo vazio ou composto apenas de espaços. Preservar caracteres acentuados e apóstrofos. | Limites de tamanho e regras adicionais não estão especificados. |
| Telefone | Obrigatório; aceitar entrada textual para preservar zeros e prefixos; rejeitar ausência de dígitos e orientar correção. | Formatos aceitos, DDD, país e quantidade de dígitos. Não impor um padrão nacional sem acordo. |
| Senha | Obrigatória no login, entrada oculta, comparação conforme o formato de armazenamento acordado e mensagem genérica de credenciais inválidas. | Política de cadastro, tamanho, armazenamento de hash e eventual compatibilidade com dados existentes. Não inventar recuperação de senha. |
| Opção de menu | Tratar texto não numérico, número fora da lista e lista vazia, mantendo a navegação. | Padrão de teclas para Voltar nos formulários. |
| Banco indisponível/erro de integridade | Mensagem compreensível, nenhum falso sucesso, desfazer operação incompleta, liberar recursos e permitir retorno seguro. | Política de nova tentativa e eventual registro técnico sem credenciais. |

O ciclo persistido é aberto → em andamento → resolvido. Não são solicitados reabertura, transferência, múltiplos atendentes ou novos estados. O sinalizador de escrita da conexão não substitui a verificação de responsável e cliente pelas controladoras.

### 3.5 Complementos obrigatórios do edital

O edital permite personalizar o menu, mas exige acesso a relatórios e operações de inserir, remover e atualizar com seleção de entidades. A experiência acima, sozinha, não demonstra todo esse escopo. Planejar uma área complementar para clientes, atendentes e chamados, com posição e controle de acesso a decidir; não presumir que qualquer atendente seja administrador.

Essa área deve listar chave e descrição antes de alterações/exclusões, preservar chaves primárias, exibir resultados atualizados, confirmar exclusões e bloquear a remoção de clientes ou atendentes referenciados, explicando o motivo. Deve oferecer repetir operações ou voltar, conforme o item 6. A criação de atendentes precisa de um caminho acessível sem depender de um login ainda inexistente, a ser definido no marco inicial.

São obrigatórios dois relatórios distintos: uma sumarização com agrupamento e uma junção de tabelas. Planejar tempo médio entre abertura e fechamento de chamados resolvidos por atendente, explicitando que mede tempo total até resolução, e detalhes de chamados com cliente e responsável. Preservar chamados sem responsável no relatório de detalhes e definir como exibir ausência de amostra na média. Não chamar essa média de tempo de trabalho efetivo.

## 4. Contratos de integração, em texto

As operações abaixo são nomes de contratos propostos, sem assinatura de código. A CLI recebe entradas e apresenta resultados; controladoras aplicam regras e persistem; modelos representam os dados; relatórios consultam o mesmo banco. Não adotar ORM nem criar uma camada de serviços paralela sem necessidade.

### 4.1 Formatos compartilhados

- Cliente: identificador, nome, email e telefone, segundo o modelo existente.
- Atendente público: identificador, nome, email e telefone. Dados de senha são internos à autenticação/cadastro.
- Chamado: identificador, título mapeado para nome, descrição, status persistido, abertura, fechamento opcional e associações a cliente e atendente opcional.
- Objetos de modelo devem respeitar orientação a objetos, acessores e representação textual; associações devem usar objetos relacionados, conforme orientação do edital. A CLI não conhece detalhes das linhas retornadas pelo driver.
- Listagens retornam coleções, inclusive vazias; ausência de registro retorna ausência identificável. Mutação bem-sucedida retorna o registro resultante ou a identificação da exclusão; falha retorna categoria reconhecível: validação, inexistência, conflito de estado, referência impeditiva, acesso negado ou indisponibilidade. Não confundir erro com lista vazia.
- Datas devem seguir a mesma convenção de relógio e fuso em todo o projeto, a definir no marco inicial. Não misturar datas locais e UTC implicitamente.
- Controladoras não solicitam entrada nem imprimem menus. Esse afastamento do legado permite testes e trabalho independente da CLI.

### 4.2 Operações e responsáveis

| Contrato | Entradas | Saída e regra observável | Provedor → consumidor |
| --- | --- | --- | --- |
| Buscar cliente por email | Email validado e normalizado pela política acordada | Cliente ou ausência, sem inserir automaticamente. | Pessoa 2 → CLI da Pessoa 4 |
| Cadastrar cliente | Nome, email e telefone confirmados | Cliente persistido com id; duplicidade sinalizada sem sobrescrever dados. | Pessoa 2 → Pessoa 4 |
| Autenticar atendente | Email e senha | Identidade pública ou credenciais inválidas; nunca devolver senha. | Pessoa 2 → Pessoa 4 |
| Criar chamado | Id do cliente, título e descrição | Chamado aberto com id e abertura; cliente deve existir. | Pessoa 3 → Pessoa 4 |
| Listar chamados do cliente | Id do cliente e filtro de estado acordado | Coleção de chamados desse cliente. | Pessoa 3 → Pessoa 4 |
| Consultar detalhes | Id do chamado e identidade/contexto de consulta | Chamado com associações; recusar consulta fora do contexto permitido. | Pessoa 3 → Pessoa 4 |
| Cancelar chamado | Id do chamado e id do cliente, após confirmação na CLI | Exclusão ou conflito; titularidade e estado conferidos na mesma operação protegida. | Pessoa 3 → Pessoa 4 |
| Assumir próximo | Id do atendente autenticado | Chamado atribuído atomicamente ou fila vazia; abertura e id ordenam a seleção. | Pessoa 3 → Pessoa 4 |
| Histórico e meus chamados | Id do atendente e filtro acordado | Histórico apenas resolvido; meus chamados conforme decisão registrada. | Pessoa 3 → Pessoa 4 |
| Resolver chamado | Id do chamado e id do atendente | Chamado resolvido com fechamento; recusa de responsável/estado inválido. | Pessoa 3 → Pessoa 4 |
| Manutenção de entidades | Entidade, id quando necessário, atributos permitidos | Inclusão/atualização/exclusão com validação e bloqueio de referência; controles de acesso definidos antes da exposição. | Pessoa 2 para clientes/atendentes e Pessoa 3 para chamados → Pessoa 4 |
| Totais de inicialização | Nenhuma entrada livre de nome de tabela | Totais identificados de clientes, atendentes e chamados. | Pessoa 1 → splash da Pessoa 4 |
| Relatório de média | Critério de amostra definido | Atendente, quantidade resolvida e duração média com unidade explícita. | Pessoa 1 → Pessoa 4 |
| Relatório de detalhes | Filtros apenas se acordados | Chamado, cliente, responsável opcional, estado e datas. | Pessoa 1 → Pessoa 4 |
| Acesso PostgreSQL | Configuração local e operação de persistência | Conexão/resultado ou erro categorizável, com liberação e controle explícito de transação. | Pessoa 1 → Pessoas 2 e 3 |

A Pessoa 1 deve entregar cedo o contrato de transação para a Pessoa 3: o commit por chamada atual não pode separar a leitura da fila de sua atribuição. A implementação futura poderá encapsular a operação de forma atômica; o mecanismo concreto será revisado sem alterar o schema.

## 5. Divisão assíncrona e propriedade dos arquivos

Cada arquivo tem um único autor principal. Revisores comentam e aprovam; pedem ajustes ao dono antes de editar. Diretórios novos citados abaixo são destinos planejados, não módulos já implementados.

| Pessoa | Área | Propriedade exclusiva |
| --- | --- | --- |
| 1 | Infraestrutura, banco existente e relatórios | `src/conexion/`, `src/create_tables_and_records.py`, `src/requirements.txt`, `.env.example`, `.gitignore`, `src/sql/`, `sql/`, `src/reports/`, `diagrams/`, `docs/modelagem.md`, `docs/contratos_persistencia.md`, `tests/test_postgres_queries.py`, futuros testes de infraestrutura/relatórios. |
| 2 | Clientes, atendentes e autenticação | `src/model/clientes.py`, `src/model/funcionarios.py`, `src/controller/controller_cliente.py`, `src/controller/controller_funcionario.py`, futuro `src/utils/validacoes_identidade.py`, `docs/contratos_identidade.md`, futuros testes de identidade. |
| 3 | Chamados, fila e ciclo de vida | `src/model/atendimentos.py`, `src/controller/controller_atendimento.py`, futuro `src/utils/validacoes_chamados.py`, `docs/contratos_chamados.md`, futuros testes de chamados e concorrência. |
| 4 | CLI, integração e entrega | `src/principal.py`, `src/utils/config.py`, `src/utils/splash_screen.py`, futuros módulos `src/cli/`, `README.MD`, `src/test.py`, demais documentos de requisitos, planejamento, testes e vídeo em `docs/`, `prompts.md`, futuros testes de CLI/aceite. |

Arquivos de vendas não atribuídos individualmente serão tratados pela Pessoa 4 apenas na limpeza final acordada, sem remover arquivos pertencentes aos demais. O `.env` de cada desenvolvedor é local e não compartilhado no Git. A Pessoa 4 centraliza a integração do histórico de prompts de todos, preservando autoria e uso da resposta.

### Pessoa 1 — Infraestrutura e relatórios

| Task | Objetivo e arquivos/módulos | Dependências | Critério de pronto |
| --- | --- | --- | --- |
| P1.1 | Inventariar o script real e publicar mapeamento de campos/status em `docs/modelagem.md` e contrato em `docs/contratos_persistencia.md`. | Nenhuma; schema atual já está disponível. | Equipe identifica script canônico, tabela/atributo correspondente a cada dado e comportamento transacional, sem novo schema. |
| P1.2 | Corrigir inicialização em `src/create_tables_and_records.py`: caminho real, falha sem falso sucesso, encerramento de recursos e descarte das cargas de vendas no fluxo novo. Consolidar arquivos vazios/duplicados de criação por decisão documentada. | P1.1. | Em banco local vazio, script existente cria as três tabelas; erro é reportado e interrompe a etapa; nenhuma tabela de pedidos é exigida. |
| P1.3 | Revisar `postgres_queries.py`: documentação herdada, validação de configuração e capacidade transacional necessária à fila. | Contrato P1.1; revisar necessidades com P3.1. | Chamadas simples mantêm compatibilidade; uma operação composta pode confirmar ou desfazer integralmente; recursos são fechados. |
| P1.4 | Conferir dependências e configuração em requirements, `.env.example` e `.gitignore`; preparar amostra em `sql/inserting_samples_atendimento.sql` usando o modelo existente. | Formato de senha de P2.3 para credenciais de amostra. | Ambiente Linux instala dependências; exemplo não contém segredo real; dados conhecidos cobrem fila vazia/cheia, histórico e ausência de responsável. |
| P1.5 | Implementar consultas e módulo de relatórios já reservados em `src/sql/` e `src/reports/`; fornecer totais de inicialização sem interação de terminal. | P1.1; decisão da média. | Dois relatórios do edital disponíveis, média conferida com amostra conhecida, ausência de dados tratada e responsável nulo preservado nos detalhes. |
| P1.6 | Produzir diagrama derivado do schema existente em `diagrams/`, com atributos, chaves, obrigatoriedades e relações reais. | P1.1. | Fonte e exportação PDF/PNG/JPEG legíveis refletem o script sem inventar colunas ou obrigatoriedades. |
| P1.7 | Validar infraestrutura/relatórios no PostgreSQL local e na VM; manter testes da conexão e acrescentar cenários de falha relevantes. | P1.2–P1.5. | Evidência reproduzível de instalação, erro de conexão, rollback e totais/relatórios corretos entregue à Pessoa 4. |

Independência: começar com o schema existente, banco local isolado e amostras próprias. Não aguardar CLI. Primeiras entregas: caminho canônico, mapeamento e contrato transacional.

### Pessoa 2 — Identidade e autenticação

| Task | Objetivo e arquivos/módulos | Dependências | Critério de pronto |
| --- | --- | --- | --- |
| P2.1 | Publicar entradas, saídas e erros de identidade em `docs/contratos_identidade.md`; combinar normalização e validação mínima. | Mapeamento disponível no schema; decisões de formato podem ser registradas como pendentes. | Pessoa 4 consegue simular cliente existente, ausente, duplicado e login inválido sem aguardar banco. |
| P2.2 | Adaptar `model/clientes.py` e `controller_cliente.py` ao cliente existente por email, removendo CPF/Oracle e entrada de terminal da controladora. | P2.1; P1.1 apenas para integração. | Busca não cria cadastro; cadastro retorna id; duplicidade e email corrigido não produzem cliente errado. |
| P2.3 | Implementar atendente em `funcionarios.py` e controladora correspondente; definir formato seguro de senha com o grupo, compatível com a coluna existente. | Decisão de armazenamento e criação inicial de atendente. | Login válido retorna identidade pública; senha inválida/email ausente falham sem exposição; nenhum retorno textual revela credenciais. |
| P2.4 | Implementar validações de identidade no módulo próprio, aplicando a política acordada a cadastro, atualização e login. | P2.1 e decisões de telefone/senha. | Casos vazios, formato inválido, acentos, telefone textual e email duplicado recebem comportamento consistente e testável. |
| P2.5 | Completar inclusão, listagem, atualização e remoção de clientes/atendentes para a manutenção exigida pelo edital; manter ids e bloquear referências. | P2.2–P2.4; contrato de banco. | Cada operação retorna resultado claro; registros usados em chamados não são apagados; atualização retorna dados novos sem alterar PK. |
| P2.6 | Testar identidade com conexão simulada e banco local; entregar dados sintéticos e roteiro ao integrador. | P2.2–P2.5. | Evidência de duplicidade concorrente, login inválido, atualização, FK impeditiva e contratos compatíveis com a CLI. |

Independência: usar simulações do acesso ao banco e dados públicos sintéticos; não importar controladora de chamados. O banco e suas referências resolvem o bloqueio de exclusão. Entregar contrato e cenários de identidade antes da implementação completa.

### Pessoa 3 — Chamados e fila

| Task | Objetivo e arquivos/módulos | Dependências | Critério de pronto |
| --- | --- | --- | --- |
| P3.1 | Publicar operações e erros em `docs/contratos_chamados.md`, incluindo mapeamento de estado e disputa de fila. | Schema existente; alinhamento breve com P1.1. | Pessoa 4 recebe cenários simulados de abertura, ausência, disputa, atribuição e resolução; nenhuma dependência da UI. |
| P3.2 | Implementar modelo em `atendimentos.py` e criação na controladora, associando objetos conforme edital e usando campos reais. | P3.1; contrato de Cliente/Atendente, simulável até entrega P2. | Novo chamado pertence a cliente existente, inicia aberto, sem responsável/fechamento e possui título/descrição válidos. |
| P3.3 | Implementar consulta por cliente, detalhes e cancelamento confirmado pelo consumidor. | P3.1; decisão de cancelamento para estado em andamento. | Consulta respeita titular; exclusão revalida estado, não afeta outro cliente e responde a registro já removido/modificado. |
| P3.4 | Implementar atribuição FIFO atômica na controladora, com desempate por id e proteção de concorrência. | P1.3 para teste real; lógica pode ser desenvolvida com simulação. | Duas sessões não recebem o mesmo chamado; alteração de responsável/status não fica parcial; fila vazia tem resposta própria. |
| P3.5 | Implementar meus chamados, histórico, detalhes e resolução com fechamento; validar responsável e transição. | P3.2; filtro de meus chamados decidido. | Histórico só contém resolvidos do atendente; resolução alheia é recusada; repetir ação não altera fechamento original. |
| P3.6 | Completar manutenção de chamados para o edital, preservando PK, integridade e campos controlados pelo ciclo de vida. | P3.2–P3.5; definição dos atributos editáveis. | Listagens têm id/título; resultado da atualização é retornado; nenhuma edição deixa status, responsável e datas incoerentes. |
| P3.7 | Testar ciclo completo e concorrência real em testes próprios, incluindo disputa entre cancelar, assumir e resolver. | P1.3 para concorrência; demais testes independem da CLI. | Evidências de atomicidade, ausência de duplicidade e recusa de estados inválidos; erros não viram falso sucesso. |

Independência: usar ids e objetos de identidade sintéticos respeitando o contrato, sem depender do login real. A Pessoa 3 é a única dona das mutações de chamados; relatórios da Pessoa 1 só leem esses dados.

### Pessoa 4 — CLI e integração

| Task | Objetivo e arquivos/módulos | Dependências | Critério de pronto |
| --- | --- | --- | --- |
| P4.1 | Transformar `principal.py` em coordenador da navegação, adaptar `config.py` e distribuir telas em módulos CLI próprios se necessário. | Contratos textuais; usar respostas simuladas. | Menu inicial tem as quatro opções solicitadas, repete corretamente e aceita erro de entrada sem encerrar. |
| P4.2 | Implementar tela de abertura, cadastro progressivo e Voltar com correção de email em qualquer etapa; integrar título/descrição. | P2.1/P3.1 para simulação; P2.2/P3.2 para banco. | Fluxo existente/novo é completo, correção refaz busca, confirmação mostra id e permite repetir abertura. |
| P4.3 | Implementar consulta do cliente, seleção numerada, detalhes, confirmação de DELETE e retorno coerente. | Contrato P3.1; integração P3.3. | Distingue os três casos sem resultados; confirma antes de remover; lista é atualizada após mudança de estado/exclusão. |
| P4.4 | Implementar login com senha oculta, sessão, menu do atendente, fila automática, histórico e meus chamados. | Contratos P2.1/P3.1; integração P2.3/P3.4/P3.5. | Identidade da sessão orienta todas as ações; fila não oferece escolha manual; resolução mostra resultado e navegação continua. |
| P4.5 | Adaptar splash e conectar relatórios; disponibilizar manutenção de entidades para cumprir integralmente o edital. | Acesso/menu definidos em decisão; contratos P1/P2/P3. | Contagens reais, nomes corretos, dois relatórios acessíveis e CRUD demonstrável com seleção, confirmação, repetição e retorno. |
| P4.6 | Tratar erros na borda da CLI e retirar dependências ativas do legado; adaptar ou desativar claramente `src/test.py` antigo. | Entregas funcionais dos demais. | Arranque não exige cx_Oracle, não abre arquivos de vendas, não falha por diretório corrente e não anuncia sucesso após erro. |
| P4.7 | Coordenar testes de CLI/aceite em arquivos próprios; consolidar `docs/testes_manuais.md` e `docs/checklist_entrega.md`. | Simulações permitem começar cedo; aceite real após integração. | Todos os fluxos e requisitos acadêmicos têm evidências, incluindo VM Linux, retorno, listas vazias, entradas inválidas e recuperação de erro. |
| P4.8 | Reescrever `README.MD`, consolidar requisitos, roteiro e link do vídeo em docs; manter registro de IA e autoria; organizar entrega. | Instalação P1, confirmação dos fluxos P2/P3 e aceite. | Outro integrante executa na VM seguindo o README; vídeo demonstra todos os menus; checklist final registra arquivos, commits e acesso do professor. |

Independência: construir telas com provedores simulados que retornam os contratos e as mesmas categorias de erro previstas para produção. Cada tela já deve distinguir sucesso, ausência e falha. Trocar o provedor na integração sem reescrever a navegação.

## 6. Marcos e ordem de integração

| Marco | Entregas e paralelismo | Condição para avançar |
| --- | --- | --- |
| M0 — Acordos mínimos | P1 publica fonte do schema e contrato de transação; P2 e P3 publicam seus contratos; P4 define navegação e matriz do edital. Resolver decisões que mudam contrato. | Nomes, estados, retornos, filtros e donos definidos; exemplos de cenários descritos em texto. |
| M1 — Quatro frentes independentes | P1 instala o modelo e prepara relatórios; P2 desenvolve identidade; P3 desenvolve ciclo/fila; P4 monta toda CLI com simulações. | Cada frente demonstra seu comportamento isoladamente; nenhuma espera o menu para validar regras. |
| M2 — Primeiro fluxo real | Integrar conexão, cliente, criação de chamado e CLI de abertura. | Email existente/novo, correção de email e persistência real aprovados na VM. |
| M3 — Atendimento completo | Integrar login, atribuição, consulta/cancelamento, resolução e histórico; validar concorrência. | Ciclo completo funciona; dois atendentes simultâneos não compartilham atribuição. |
| M4 — Conformidade acadêmica | Integrar manutenção de entidades, relatórios, splash e diagrama; revisar referências legadas. | Cada item 5 e 6 do edital tem um caminho demonstrável e testado. |
| M5 — Entrega | Executar instalação limpa na VM, fechar README, gravar demonstração e revisar acesso/commits. | Checklist de aceite aprovado pelo grupo e link do repositório pronto para submissão no AVA. |

O edital informa entrega em 30/10/2026; esta análise é de 29/10/2026. Distribuir M0 imediatamente e manter as quatro frentes em paralelo. Reservar tempo antes do prazo para VM e vídeo. Os marcos são condições de passagem, não estimativas de duração garantida. Não reduzir os requisitos obrigatórios para caber em uma previsão arbitrária.

## 7. Convenções de Git e colaboração

- Confirmar a branch remota de integração antes de começar. O histórico desta conversa usou `master` no remoto e `main` local; isso precisa de alinhamento explícito.
- Uma branch curta por task, identificando pessoa e objetivo. Integrar mudanças pequenas por revisão; nenhum push forçado para a branch compartilhada.
- Cada integrante registra suas contribuições com sua própria autoria, pois o edital avalia participação por commits. Não centralizar a implementação dos quatro em um único autor.
- Não usar inclusão indiscriminada de arquivos: conferir os caminhos de cada commit, respeitando a propriedade acima e o trabalho local já existente.
- Alteração de contrato exige atualizar o documento do dono e avisar consumidores antes do merge; manter comportamento anterior até ambos os lados estarem prontos ou integrar o ajuste combinado.
- Compartilhar dados sintéticos e `.env.example`; senhas reais e `.env` ficam locais. Cada pessoa usa banco próprio e um banco separado para testes que removam dados.
- Registrar prompt, fonte/modelo disponível, effort disponível e uso da resposta, respeitando solicitações explícitas do usuário sobre o registro. O edital usa `PROMPTS.md`, enquanto o projeto tem `prompts.md`; resolver grafia sem duplicar o histórico.
- Pessoa 4 coordena o checklist e as revisões finais; correções em arquivos dos demais voltam ao respectivo dono.

## 8. Critérios de aceite do projeto

- [ ] Instalação reproduzível no Linux/VM, usando o schema existente e dependências declaradas, com README suficiente para outro integrante executar.
- [ ] Menu inicial e submenu do atendente correspondem à experiência solicitada; saídas e retornos são previsíveis e entradas inválidas não derrubam a aplicação.
- [ ] Cliente existente é reutilizado; novo cliente exige nome/telefone/email; Voltar permite corrigir email em qualquer etapa sem cadastro incompleto.
- [ ] Chamado é aberto com cliente, título, descrição, abertura e estado corretos; confirmação e repetição são demonstradas.
- [ ] Consulta respeita cliente, apresenta detalhes e distingue ausência; DELETE exige confirmação e revalida estado/titularidade.
- [ ] Login usa email/senha; credenciais não vazam; operações do atendente usam a identidade autenticada.
- [ ] Atribuição é automática e FIFO, sem duplicidade sob concorrência; ausência de fila é informada corretamente.
- [ ] Histórico contém resolvidos do atendente; meus chamados respeita o filtro acordado; encerramento registra fechamento e protege responsável/estado.
- [ ] CRUD acadêmico das entidades é acessível com seleção de entidade, chave/descrição, atualização sem mudar PK, exclusão confirmada, proteção de referências e repetição.
- [ ] Dois relatórios distintos comprovam agrupamento e junção; média tem unidade, amostra definida e significado correto.
- [ ] Splash identifica aplicação e integrantes, professor/disciplina/semestre e totais das três tabelas.
- [ ] Testes relevantes de componentes, banco real, concorrência, CLI e instalação limpa possuem evidências; nenhuma conclusão se baseia só em mocks.
- [ ] Diagrama exportado representa o modelo existente; fontes, scripts e documentação estão organizados no GitHub sem compactação.
- [ ] Vídeo no YouTube mostra o objetivo e todos os menus funcionando; link consta da documentação.
- [ ] Cada integrante contribuiu com commits e consegue explicar o que implementou; acesso de howardroatti e submissão do link no AVA foram conferidos pelo grupo.

## 9. Decisões em aberto e bloqueios delimitados

| Decisão | Responsáveis por fechar | Impacto e encaminhamento |
| --- | --- | --- |
| Localização canônica do script existente | Pessoa 1, revisão do grupo | Corrigir referência de instalação e decidir o destino dos placeholders sem manter duas fontes divergentes. Não redesenhar tabelas. |
| Nomenclatura de estado | Pessoas 3 e 4 | Preservar `em andamento` no banco e mapear “em atendimento” na apresentação. Confirmar o rótulo final; não gravar valor rejeitado pela restrição atual. |
| “Em aberto” inclui em andamento? Pode cancelar após atribuição? | Grupo, coordenação P3/P4 | Bloqueia o filtro definitivo e a regra de cancelamento. Provisoriamente considerar apenas aberto, com recusa se houver mudança de estado. |
| Meus chamados inclui resolvidos? | Pessoas 3 e 4 com grupo | Definir filtro; histórico continua sendo apenas resolvidos independentemente desta escolha. |
| Acesso a relatórios e manutenção e criação do primeiro atendente | Grupo, coordenação P4/P2 | Menus descritos não bastam para o CRUD e relatórios do edital. Definir onde ficam as opções e quem acessa sem inventar papel administrativo no schema. |
| Senha e validações não especificadas | Pessoa 2 com grupo | Campo senha já existe. Definir hash, compatibilidade de dados existentes, criação de credenciais, política de senha, telefone e normalização de email. Não pressupor senha em texto simples como solução final. |
| Permissão para composição segura de consultas | Grupo com professor, coordenação P1 | FAQ exige consultas em texto com concatenação e proíbe ORM; conexão atual permite parâmetros separados. Confirmar aceitação de parametrização sem ORM e registrar orientação antes de fechar a implementação; não declarar equivalência com o texto do edital. |
| Métrica de tempo médio | Pessoa 1 com grupo | O modelo só permite medir abertura até fechamento. Se for exigido tempo desde o início do atendimento, registrar bloqueio e pedir decisão específica sobre o modelo; não inventar coluna nem calcular tempo inexistente. |
| Dados nulos e coerência das datas | Pessoas 1 e 3 | Validar chamadas existentes sem cliente, status ou abertura e fechamento inconsistente. Definir tratamento da base de demonstração sem mudança silenciosa no schema. |
| Editabilidade e requisitos acadêmicos | Pessoas 2, 3 e 4 | Definir atributos editáveis de cada entidade e evidenciar atualização genérica do edital, além da resolução de chamado. Não expor edição livre que viole ciclo de vida. |
| Saída do atendente e abandono de abertura | Pessoa 4 com grupo | Definir logout versus encerramento do programa; definir preservação de cadastro confirmado caso o chamado não seja concluído. |
| Convenção de relógio e fuso | Pessoas 1 e 3 | Timestamps existentes não informam fuso. Acordar origem e interpretação das datas para ordenação, fechamento e média. |
| Quatro desenvolvedores versus grupo de cinco no edital | Grupo com professor | Edital pede grupo de cinco, FAQ admite exceções individuais; confirmar autorização para quatro, sem inferir dispensa. Divisão técnica deste documento permanece para quatro pessoas. |
| Nomes, versão Python da VM, entrega e acesso | Grupo, coordenação P4 | Obter nomes reais, conferir ambiente alvo, colaboração do professor, prazo e envio no AVA; não são comprováveis pela análise local. |
| Registro de IA e grafia do arquivo | Pessoa 4 com grupo | Conciliar o arquivo atual com a grafia exigida pelo edital e solicitações explícitas de não registrar certos pedidos; documentar a situação antes da entrega. |

As decisões que mudam os contratos devem ser fechadas em M0. As demais podem avançar com simulações e cenários explicitamente identificados, sem apresentar comportamento provisório como requisito confirmado.
