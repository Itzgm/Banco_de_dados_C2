# Limpeza dos artefatos legados

> Registro histórico: os arquivos de testes automatizados foram removidos posteriormente por solicitação do usuário. Os resultados abaixo descrevem execuções anteriores; não há suíte automatizada nesta cópia. Para validar a versão atual, consulte `validacao_vm.md`.


Escopo: somente `base_exemplo`. Os arquivos do projeto principal e os bancos existentes foram preservados.

Foram removidos 27 arquivos obsoletos: conexão e credencial de exemplo Oracle, teste manual Oracle, controladoras e modelos de pedidos/produtos/fornecedores/itens, placeholder antigo de funcionários, SQL e amostras de vendas, relatórios incompatíveis com o modelo atual, diagramas de pedidos, schema duplicado e suíte vinculada à implementação antiga.

A controladora monolítica antiga também foi removida. Antes disso, o script de demonstração foi adaptado à persistência atual e à validação de senha compartilhada. Seu comportamento foi verificado com persistência simulada, sem redefinir senhas das contas existentes. Ele continua destinado exclusivamente à base de demonstração.

O teste real do instalador foi migrado para `test_controladoras_integracao.py`. Testes redundantes da implementação antiga e os três testes ignorados da interface substituída foram removidos. O login inválido passou a ser explicitamente verificado na controladora atual. As controladoras com nomes históricos `controller_funcionario.py` e `controller_atendimento.py` foram preservadas, pois implementam atendentes e chamados e estão em uso.

Validação: 40 testes aprovados em 75,720 segundos, sem falhas nem testes ignorados, usando schemas temporários no PostgreSQL isolado. A redução da contagem decorre da remoção dos casos legados e redundantes, não da interrupção dos testes de integração.

README, contratos, especificação e registros de entrega foram atualizados. Diagnósticos e resultados anteriores permanecem identificados como históricos. A execução na VM Linux e os entregáveis externos continuam pendentes.
