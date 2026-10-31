# Refatoração pela arquitetura original

## Comparação antes da alteração

Referência consultada diretamente: [example_crud_oracle](https://github.com/howardroatti/example_crud_oracle), branch master. Foram analisados principal, OracleQueries, controllers de cliente e pedido, modelos de cliente e pedido, relatórios, configuração, splash e instalador.

| Referência | Situação encontrada na cópia | Alteração necessária |
| --- | --- | --- |
| `principal.py` com funções de despacho | Classe Aplicacao concentra menus e formulários | Funções de menu e despacho; formulários CRUD nos respectivos controllers. |
| Controllers usam OracleQueries diretamente | Controllers chamam função genérica executar em repositorio | Controllers usam PostgresQueries, DataFrames e objetos da própria entidade. |
| CRUD verifica existência, recupera registro e apresenta objeto | Validações existentes, mapeamento central e apresentação externa | Métodos explícitos de existência, validação, leitura e CRUD por entidade. |
| Modelos com getters/setters e associações | Modelos já possuem esses métodos, com diferenças de tipos/defaults | Uniformizar assinaturas e manter associações obrigatórias/opcionais do modelo atual. |
| Relatorio carrega SQL nos atributos e apresenta relatórios | Leitura genérica sob demanda, apresentação na Aplicacao | Consultas nomeadas por relatório e métodos explícitos com opção de apresentação. |
| Splash possui consultas e métodos de contagem | Splash depende do serviço de relatórios | Consultas às três tabelas por PostgresQueries, mantendo o formato escolhido. |
| config concentra menus e utilitários | Strings de menu também estão espalhadas na aplicação | Centralizar menus e auxiliares de navegação sem criar nova camada. |

## Funcionalidades que devem permanecer

Cadastro e correção de email, abertura, consulta e cancelamento confirmado, login, atribuição FIFO automática e atômica, atendimentos próprios, resolução única, histórico, manutenção das três entidades por lista local de emails, relatórios e contagens. Senha permanece em texto direto e visível na entrada, conforme decisões do usuário. A cópia continua independente da raiz; não recriar testes permanentes nem publicar alterações.

## Adaptações deliberadas ao PostgreSQL

Identidades e RETURNING substituem sequences e parâmetros de saída Oracle. Consultas recebem valores separados, datas seguem o schema existente e a fila usa bloqueio de linha. Recursos são fechados com finally, falhas desfazem operações transacionais e mensagens não expõem credenciais. Verificar existência retorna verdadeiro quando o registro existe; a inversão de significado observada no exemplo não será reproduzida.

Credenciais vêm do `.env` local ou variáveis de ambiente. Não alterar as tabelas existentes para executar a refatoração. A validação real deve usar schema temporário no banco isolado e também verificar inicialização de leitura na configuração atual.

## Estrutura final e correspondências

| Arquivo atual | Referência equivalente | Responsabilidade |
| --- | --- | --- |
| `src/principal.py` | `src/principal.py` | Instâncias das classes, menus e funções inserir/atualizar/excluir/reports. |
| `src/conexion/postgres_queries.py` | `src/conexion/oracle_queries.py` | PostgresQueries com as sete operações equivalentes e transações explícitas. |
| `src/controller/controller_cliente.py` | `src/controller/controller_cliente.py` | Cadastro e CRUD, existência, DataFrame, objeto Cliente e apresentação. |
| `src/controller/controller_atendente.py` | Controllers de entidades simples | CRUD e autenticação específicos de atendentes. |
| `src/controller/controller_chamado.py` | `src/controller/controller_pedido.py` | CRUD, entidades associadas e consultas; fila, cancelamento e resolução são extensões do atendimento. |
| `src/model/clientes.py`, `atendentes.py`, `chamados.py` | Modelos Cliente e Pedido | Construtores tipados, getters/setters, to_string e associações. |
| `src/reports/relatorios.py` e `src/sql/relatorio_*.sql` | Mesmos diretórios da referência | Consultas nomeadas e métodos individuais de recuperação/apresentação. |
| `src/utils/config.py`, `splash_screen.py` | Mesmos arquivos da referência | Menus e auxiliares; consultas e métodos de contagem, com arte preservada. |
| `src/create_tables_and_records.py` | Mesmo instalador da referência | Criação e carga com caminhos estáveis, transação, rollback e fechamento. |

Foram retirados `repositorio.py`, `mapeamento.py`, os controllers com nomes de funcionário/atendimento e os dois arquivos SQL de relatório com nomenclatura de funcionário. Os equivalentes foram substituídos pelos nomes das entidades reais, sem manter duas implementações. Não há ORM, framework ou classe de aplicação centralizando formulários.

## Validação executada

Vinte verificações temporárias passaram, sem falhas ou casos ignorados, em 29,470 segundos. O script de verificação foi mantido fora da aplicação, em pasta temporária; a pasta `tests` removida pelo usuário não foi recriada.

O banco isolado recebeu apenas schemas temporários próprios, removidos ao concluir. Foram exercitados todos os imports, os três formatos de leitura, escrita/rollback, CRUD das três entidades, referência impeditiva, emails, senha direta, acesso negado, atualização do email autorizado, titularidade, fila FIFO/desempate, atribuição concorrente, cancelamento contra atribuição, resolução simultânea e fechamento único.

Os cenários de CLI utilizaram respostas de teclado simuladas com controllers e PostgreSQL reais: abertura/correção de email, cancelamento, login, fila, resolução, histórico, quatro relatórios, CRUD administrativo e exclusão da própria conta. Também foram executados instalador e configuração da conta fictícia no schema temporário e inicialização por subprocesso fora do diretório do projeto. A entrada da aplicação foi conferida separadamente em modo de leitura no `.env` atual.

Limites: a VM Linux da disciplina, a revisão manual pelo grupo e os entregáveis externos ainda não foram comprovados. Os 42 testes registrados em etapas anteriores são históricos e não representam a validação desta nova arquitetura.

## Alinhamento dos utilitários e controllers

Os arquivos utils/autorizacao.py, erros.py, senhas.py e validacoes_identidade.py foram removidos. Permanecem somente __init__.py, config.py e splash_screen.py. Cada controller valida seus atributos, e Controller_Atendente reúne autenticação, validação de senha e autorização pela lista local. O principal e a conexão usam exceções nativas do Python. Atualizações recuperam um DataFrame e constroem o objeto atualizado; associações de chamado são validadas por valida_cliente e valida_atendente, no padrão do controller de Pedido.

Após este alinhamento, as 20 verificações temporárias foram reexecutadas e aprovadas em 30,605 segundos, sem falhas ou testes ignorados. A pasta de testes continua ausente e o banco da aplicação foi preservado.
