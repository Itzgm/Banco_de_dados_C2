> Atualização de integração: a versão ativa usa Controller_Atendimento e Atendimento, provenientes de Ricardo, e fluxos públicos de Davi no principal. O detalhamento de contratos e adaptações está em integracao_branches.md; os nomes anteriores citados abaixo descrevem a base usada na cópia.

# Contratos dos componentes — arquitetura de referência

## Fluxo principal

`principal.py` mantém instâncias das controladoras e da splash e coordena os menus por funções. `inserir`, `atualizar`, `excluir` e `reports` despacham para as classes responsáveis, conforme a abordagem de `example_crud_oracle`. Não existe a classe Aplicacao nem módulo separado de CLI.

## Controllers e modelos

- `Controller_Cliente`, em `controller_cliente.py`, abre a conexão, verifica existência, valida email/nome/telefone, executa CRUD e cria objetos `Cliente` a partir dos resultados. O formulário administrativo fica nos métodos CRUD; o cadastro público continua disponível durante a abertura de chamado.
- `Controller_Atendente`, em `controller_atendente.py`, realiza CRUD e autenticação por email/senha e devolve `Atendente` sem a senha. As senhas são gravadas em texto direto e digitadas de forma visível, conforme decisão do usuário.
- `Controller_Chamado`, em `controller_chamado.py`, contém CRUD, consultas e formulários de abertura, consulta pública e atendimento. Possui controllers associados e constrói `Chamado` com um `Cliente` e um `Atendente` opcional, de forma equivalente às associações do modelo Pedido original.
- Modelos possuem construtor, getters, setters e `to_string`. O título corresponde ao campo `nome` do banco. As datas sem valor e o responsável não atribuído são representados como ausência de valor.

Quando os dados não são passados, os métodos CRUD administrativos solicitam entradas e selecionam registros. Com valores explícitos, eles também podem ser utilizados por outros fluxos do sistema. As atualizações de cliente e atendente executam a alteração, recuperam o registro em DataFrame e criam o objeto atualizado, seguindo o exemplo original. O controller de chamados possui valida_cliente e valida_atendente para construir as associações no mesmo padrão do controller de Pedido. Atualização/exclusão administrativas sempre exigem um operador autorizado; a confirmação é solicitada no caminho interativo.

## Conexão

Os controllers e relatórios usam `PostgresQueries` diretamente, sem repositório intermediário ou arquivo global de mapeamento. A classe mantém `connect`, `sqlToDataFrame`, `sqlToMatrix`, `sqlToJson`, `write`, `executeDDL` e `close`, equivalentes aos métodos de OracleQueries. `write` devolve a quantidade afetada para detectar conflitos; o cursor permite recuperar as identidades de RETURNING.

A transação explícita agrupa alteração e leitura do objeto retornado. Fora dela, a escrita confirma imediatamente. Falhas desfazem operações; transações aninhadas são recusadas. A conexão traduz falhas para exceções nativas: RuntimeError para duplicidade/conflito, ValueError para referências impeditivas e ConnectionError para indisponibilidade, sem expor credenciais. Registros ausentes usam LookupError e acesso negado usa PermissionError. Todos os usos liberam conexão/cursor com finally.

## Regras preservadas

Emails são normalizados e ambiguidades antigas são recusadas. `MANUTENCAO_EMAILS` considera o email atual armazenado do operador; lista vazia nega acesso. Cancelamento confirma e revalida cliente, estado aberto e ausência de responsável. A fila atribui o mais antigo elegível com desempate por id, em transação com bloqueio de linha. Resolução revalida responsável e estado e não substitui fechamento anterior. Histórico significa chamados resolvidos pelo atendente.

## Relatórios, SQL e utilitários

`Relatorio` carrega arquivos SQL em atributos no construtor. Cada método abre a conexão, recupera DataFrame e, por padrão, apresenta o resultado e aguarda Enter, como no exemplo. O parâmetro `exibir=False` permite consultar os dados sem interação. Estão disponíveis clientes, atendentes, detalhes e média de abertura até fechamento em segundos. Credenciais não aparecem nos relatórios.

`utils` contém somente `__init__.py`, `config.py` e `splash_screen.py`, como a referência. `config.py` concentra textos dos menus e auxiliares de entrada, confirmação e seleção. Validação dos atributos pertence a cada controller; autenticação, senha e autorização de manutenção pertencem a Controller_Atendente. Não existem módulos separados de erros, autorização, senhas ou validação. `splash_screen.py` tem consultas nomeadas e métodos de contagem para as três tabelas, preservando a arte escolhida pelo usuário. O instalador usa o schema canônico já existente em `sql/create_tables_atendimento.sql` e não altera tabelas inicializadas.

## Validação e limites

A validação desta refatoração executou 20 verificações temporárias em schema isolado no PostgreSQL, todas aprovadas. Não foi recriada a pasta de testes removida. A validação na VM Linux e o aceite acadêmico permanecem pendentes. Detalhes e referências: `refatoracao_arquitetura_original.md`.
