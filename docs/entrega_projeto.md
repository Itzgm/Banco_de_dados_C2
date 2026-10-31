# Registro de preparação da entrega

## Versão e situação

Material preparado para `base_exemplo`, cópia de estudo independente da aplicação da raiz. O grupo deve escolher e registrar a versão que apresentará. Este documento não registra publicação, convite ou submissão como realizados.

Validação histórica anterior à remoção dos testes: 42 testes aprovados, sem testes ignorados, na versão então testada, com PostgreSQL isolado no Windows. Evidências: [matriz de aceite](matriz_aceite_etapa_7.md). Validação manual e instalação na VM permanecem pendentes.

## Materiais

| Material | Local |
| --- | --- |
| Instruções e visão geral | [README](../README.md) |
| Escopo, regras, etapas e decisões | [Especificação técnica](../project_spec.md) |
| Interfaces entre componentes | [Contratos](contratos_componentes.md) |
| Modelo relacional existente | `sql/create_tables_atendimento.sql` |
| Diagrama editável | `diagrams/diagrama_relacional_atendimento.mmd` |
| Diagrama para apresentação | [PNG exportado](../diagrams/exportados/diagrama_relacional_atendimento.png) |
| Aceite automatizado | [Matriz da etapa 7](matriz_aceite_etapa_7.md) |
| Execução por outro integrante | [Guia da VM](validacao_vm.md) |
| Apresentação | [Roteiro de vídeo](roteiro_video.md) |
| Pendências de entrega | [Checklist](checklist_entrega.md) |

O diagrama foi conferido visualmente e comparado ao script: cliente obrigatório, atendente opcional, chaves, datas e estados correspondem ao modelo. `chamados.nome` representa o título; a coluna `senha` armazena o texto direto da senha, que não integra o objeto público de atendente. Arquivos de pedidos/Oracle e a controladora monolítica antiga foram removidos. O script de demonstração usa a persistência e a validação de senha atuais.

## Revisão e autoria

Cada integrante deve revisar e explicar as partes atribuídas no planejamento e registrar contribuições efetivamente realizadas. Não atribuir autoria apenas pela distribuição proposta nem criar commits em nome de outra pessoa.

| Integrante | Revisão, contribuição e evidência real |
| --- | --- |
| Natan Ferreira Garcia | A preencher pelo integrante |
| Ricardo Otoni Ventura | A preencher pelo integrante |
| Felipe Cesconeti | A preencher pelo integrante |
| Davi Tavares da Cunha | A preencher pelo integrante |

## Decisões e ações antes do envio

1. Registrar pasta/versão final e commit aprovado pelo grupo. As alterações locais desta cópia não estão publicadas automaticamente no GitHub.
2. Confirmar com o professor o grupo de quatro e o uso de SQL parametrizado sem ORM, pois o edital menciona concatenação.
3. Confirmar regras provisórias de cancelamento e interpretação de datas sem fuso; alterações exigem revisão e novos testes afetados.
4. Executar o guia da VM, preencher as evidências e corrigir eventuais falhas.
5. Gravar e publicar o vídeo, inserir o link real no README e verificar que outro integrante consegue abri-lo.
6. Conferir contribuições e permissões do repositório, convidar `howardroatti` conforme o edital e validar o acesso.
7. Conferir prazo e instruções do AVA, enviar o endereço da versão final e registrar o comprovante.

## Dados finais

- Versão/pasta e commit apresentados: pendentes.
- Repositório para conferência: https://github.com/Itzgm/Banco_de_dados_C2 — conteúdo remoto não verificado nesta etapa.
- Link público do vídeo: pendente.
- Aceite da VM: pendente.
- Convite e acesso do professor: pendentes.
- Confirmações do professor: pendentes.
- Submissão e comprovante do AVA: pendentes.

## Atualização arquitetural

A versão atual segue a organização de example_crud_oracle, analisado diretamente, com PostgresQueries, controllers de cliente/atendente/chamado e principal por funções de despacho. A validação temporária desta refatoração aprovou 20 verificações reais no PostgreSQL. A pasta de testes permanece ausente. Ver `refatoracao_arquitetura_original.md`.
