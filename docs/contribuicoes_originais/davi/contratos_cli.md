> Documento original da branch, preservado para comparação. As adaptações da versão integrada estão em docs/integracao_branches.md.

# Contratos da CLI — Davi Tavares

## Separação dos módulos

`src/principal.py` lê os argumentos e inicia `Aplicacao`. `src/cli/entrada.py`
valida a entrada e concentra as opções de retorno. `src/cli/aplicacao.py`
contém as telas. A CLI não executa SQL nem implementa autenticação ou transações.

`ProvedorControladoras.executar(area, operacao, *args, **kwargs)` encaminha as
chamadas aos módulos dos demais integrantes. Os objetos podem expor atributos,
acessores `get_campo()` ou dicionários. A função `campo()` faz essa adaptação.
Não é necessário alterar os modelos para atender à representação das telas.

As classes são instanciadas somente na primeira utilização. Métodos ausentes e
dependências indisponíveis geram uma mensagem de integração pendente. Erros de
infraestrutura geram mensagem genérica, sem imprimir consultas ou credenciais.
Ausência de dados deve retornar `None` ou uma lista vazia; falhas devem lançar
exceção. As controladoras não devem ler o terminal nem imprimir menus.

## Identidade — Pessoa 2

Área `clientes`: `controller.controller_cliente.Controller_Cliente`.

| Método | Parâmetros | Retorno |
| --- | --- | --- |
| buscar_por_email | email | Cliente ou None |
| cadastrar_cliente | nome, email, telefone | Cliente persistido |
| listar_todos | nenhum | Lista de clientes |
| atualizar_cliente | id_cliente, nome, email, telefone | Cliente atualizado |
| excluir_cliente | id_cliente | bool; referências devem bloquear remoção |

Área `atendentes`: `controller.controller_funcionario.Controller_Funcionario`.

| Método | Parâmetros | Retorno |
| --- | --- | --- |
| autenticar | email, senha | Identidade pública ou None |
| cadastrar_atendente | nome, email, telefone, senha | Identidade pública persistida |
| listar_todos | nenhum | Lista de identidades públicas |
| atualizar_atendente | id_atendente, nome, email, telefone | Identidade pública atualizada |
| excluir_atendente | id_atendente | bool; referências devem bloquear remoção |

Cliente expõe `id_cliente`, `nome`, `email`, `telefone`. Identidade pública do
atendente expõe `id_atendente`, `nome`, `email`, `telefone`; nunca `senha`.
O armazenamento seguro e a comparação das senhas pertencem à controladora.
O login usa `getpass`, separado da leitura normal. Não há recuperação de senha.
Atualização cadastral não troca senha nem chave primária.

## Chamados — Pessoa 3

Área `chamados`: `controller.controller_atendimento.Controller_Atendimento`.
As assinaturas acompanham as operações publicadas na branch
`ricardo/desenvolvimento`, consultada durante a implementação. Essa branch não
foi incorporada à de Davi; a integração do grupo continua pendente.

| Método | Parâmetros | Retorno |
| --- | --- | --- |
| criar_chamado | id_cliente, titulo, descricao | Chamado criado |
| listar_chamados_cliente | id_cliente, apenas_ativos=False | Lista de chamados |
| consultar_detalhes | id_chamado | Chamado ou exceção |
| cancelar_chamado | id_chamado, id_cliente | bool ou exceção de conflito |
| assumir_proximo_chamado | id_atendente | Chamado ou None para fila vazia |
| listar_meus_chamados | id_atendente | Chamados em andamento |
| listar_historico_atendente | id_atendente | Chamados resolvidos |
| resolver_chamado | id_chamado, id_atendente | Chamado atualizado |
| listar_todos | nenhum | Lista para manutenção |
| atualizar_chamado | id_chamado, titulo, descricao | Chamado atualizado |
| excluir_chamado_admin | id_chamado | bool ou exceção |

Chamado expõe `id_chamado`, `id_cliente`, `id_atendente`, `nome`, `descricao`,
`status`, `data_abertura`, `data_fechamento`. O título da tela mapeia para `nome`.
Modelos com `get_id_cliente()` e `get_id_atendente()` também são aceitos.

Cancelar e resolver exigem nova validação de titularidade e estado no banco,
na operação de escrita. Assumir precisa ser atômico entre sessões. A CLI não
substitui essas garantias. `ValueError`, `LookupError` e `PermissionError` são
apresentados como recusa da operação; mensagens dessas exceções devem ser públicas.

## Relatórios e contagens — Pessoa 1

Área `relatorios`: `reports.relatorios.Relatorio`.

| Método | Retorno |
| --- | --- |
| totais() | Dicionário com clientes, atendentes, chamados e seus totais inteiros |
| tempo_medio() | Lista de dicionários: atendente, resolvidos, media_minutos |
| detalhes() | Lista de dicionários com chamado, cliente, responsável, status e datas |

A média mede abertura até fechamento dos resolvidos, em minutos. Não mede
tempo efetivamente trabalhado. Sem resolvidos, usar `Sem amostra` ou ausência
identificável. A consulta de detalhes deve preservar responsável ausente.
Esses métodos retornam dados; a CLI apresenta os resultados e controla o retorno.

## Decisões aplicadas às telas

- `/voltar` no email retorna ao menu anterior. No nome ou telefone do novo
  cliente, retorna à busca por email e descarta os campos ainda não confirmados.
- Cadastro só é persistido depois da confirmação. Se o cliente já foi confirmado
  e a abertura for abandonada, o cadastro permanece. Não há transação conjunta.
- Consulta do cliente lista somente `aberto` para cancelamento. `em andamento`
  e `resolvido` não podem ser removidos nesse fluxo. A política segue o aceite
  provisório do planejamento e precisa ser ratificada pelo grupo.
- Meus chamados contém `em andamento`; histórico contém `resolvido`.
- Sair da conta retorna ao menu principal. Apenas 0 no menu principal encerra
  a navegação normal. EOF e interrupção do terminal encerram com despedida.
- Email é aparado, sem transformação de maiúsculas. A política definitiva de
  unicidade fica na identidade. Telefone é texto e precisa conter dígitos.
- Manutenção é uma entrada local explícita por `--manutencao`, inclusive para
  cadastrar o primeiro atendente. Não representa um papel de administrador nem
  autenticação adicional. O grupo precisa aprovar o acesso antes da entrega final.
- Relatórios ficam no submenu do atendente. Não há edição livre de status,
  responsável ou datas na manutenção de chamados.

## Demonstração e injeção

`--demo` usa exclusivamente `ProvedorDemonstracao`: dados temporários no processo,
sem PostgreSQL. A senha fixa é apenas uma credencial sintética desse modo.
Não usar esse provedor em produção ou como evidência de concorrência no banco.
Os testes também podem fornecer um provedor e uma `Entrada` a `run()`.
