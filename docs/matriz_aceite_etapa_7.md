# Integração e aceite — etapa 7

> Registro histórico: os arquivos de testes automatizados foram removidos posteriormente por solicitação do usuário. Os resultados abaixo descrevem execuções anteriores; não há suíte automatizada nesta cópia. Para validar a versão atual, consulte `validacao_vm.md`.


## Escopo e execução

Versão avaliada: `base_exemplo`, com CLI e controladoras integradas. Ambiente: Windows, Python do ambiente virtual do projeto e PostgreSQL local isolado, porta 55432, banco `atendimento_base_exemplo`.

Executar a descoberta de testes em `tests/` com `EXECUTAR_TESTES_POSTGRES=1`. As suítes reais criam schemas de nomes aleatórios e removem apenas os schemas criados por elas. Não reexecutar o instalador no banco já utilizado pela aplicação para fazer esta verificação.

Os testes de CLI simulam as respostas do teclado, mas as controladoras e a persistência usam PostgreSQL real nos cenários de integração. Testes de falhas de serviço/arquivo utilizam simulações; não representam a interrupção física do servidor durante uma operação.

**Resultado histórico anterior à limpeza:** 45 testes encontrados, 42 aprovados e 3 ignorados, sem falhas, em 89,003 segundos. As duas classes de integração PostgreSQL foram executadas. Não foram necessárias correções de comportamento nos módulos ativos durante esta etapa; as alterações ampliam os testes e registram o aceite local.

**Resultado após a limpeza:** 40 testes aprovados em 75,720 segundos, sem falhas ou testes ignorados. Casos redundantes da implementação antiga foram removidos; o teste real de instalação foi preservado e o login inválido é verificado na controladora atual.

## Matriz de evidências

| Área | Cenários verificados | Evidência |
| --- | --- | --- |
| Instalação e transação | Criação em schema vazio, carga, reexecução sem sobrescrita, rollback após falha de criação/carga e mensagem de etapa parcial. | Suítes `test_controladoras_integracao` e `test_etapas_iniciais` (teste do instalador migrado). |
| Identidade | Cadastro, normalização, duplicidade, email antigo ambíguo, caracteres especiais e entradas inválidas sem persistência. | Suíte `test_controladoras_integracao`. |
| Cliente pela CLI | Cliente novo/existente, correção de email, criação, seleção, cancelamento confirmado e recusado. | Testes `test_cli_cadastro_novo_e_cancelamento_recusado` e `test_cli_fluxo_basico_e_voltar`. |
| Atendimento pela CLI | Login, atribuição automática, chamados próprios, resolução, histórico, relatórios e logout. | `test_cli_login_fila_resolucao_historico_e_relatorios`. |
| Controle de acesso | Lista vazia, email não autorizado, email atual diferente do objeto da sessão, titularidade e responsável incorretos. | Testes de autorização, lista vazia e `test_responsavel_e_titularidade_nao_podem_ser_trocados`. |
| Manutenção | Inclusão, alteração e exclusão de clientes/atendentes/chamados, referência impeditiva e exclusão da própria conta encerrando a sessão. | Testes de CRUD pela CLI e `test_cli_excluir_propria_conta_encerra_sessao`. |
| Concorrência | Cadastro simultâneo, dois atendentes disputando um chamado, dois chamados para duas sessões, cancelamento contra atribuição e resolução simultânea. | Testes concorrentes em `test_controladoras_integracao`. |
| Fila e estados | Ordem por abertura, fila sem candidatos, transição e fechamento preservado após resolução repetida. | Testes de FIFO e ciclo de vida. |
| Relatórios | Totais, responsável ausente, atendente sem amostra, média conhecida de 3600 segundos e fechamento anterior à abertura excluído da média. | Testes de relatório e `test_datas_invalidas_nao_entram_na_media`. |
| Erros e navegação | Menu inválido, relatório vazio, falhas de conexão/consulta/arquivo, atualização após conflito e apresentação inicial indisponível. | `test_cli_relatorios` e `test_etapas_iniciais`. |
| Modelos | Associações e responsável opcional; ausência de senha em modelo público. | Testes de modelos e identidade. |
| Portabilidade local | Relatórios e inicialização em subprocesso iniciado fora da pasta do projeto. | `test_inicializacao_e_relatorios_fora_do_diretorio_do_projeto`. |

## Limites do aceite

- Os testes automatizados locais não substituem a execução manual por outro integrante nem a instalação limpa na VM Linux da disciplina.
- A suíte atual não contém os testes da interface legada; os fluxos ativos são cobertos pelos testes das controladoras e CLI integrada.
- A listagem/cancelamento público permanece limitada ao estado literal `aberto`, conforme decisão provisória da especificação.
- O modelo atual não garante unicidade de emails sem distinguir maiúsculas para inserções externas; a aplicação normaliza entradas e recusa registros antigos ambíguos.
- O grupo ainda deve confirmar interpretação das datas sem fuso e exigências acadêmicas, incluindo aceitação de SQL parametrizado, vídeo e submissão.
- A matriz registra cenários concretos; não equivale a certificação de cobertura total de todas as combinações de entradas e falhas.

## Armazenamento direto de senha

Por solicitação do usuário, cadastro e atualização passaram a salvar senha em texto direto e o login compara o valor exato. A senha fica visível durante a digitação e objetos públicos não recebem a senha. A suíte atual executou 42 testes, todos aprovados em 53,638 segundos, sem testes ignorados. Os novos testes conferem o valor persistido, a atualização, espaços preservados e a rejeição de senha vazia. A conta fictícia Carla foi redefinida pelo script de demonstração; outras contas antigas com hash exigem redefinição, pois o texto original não é recuperável.
