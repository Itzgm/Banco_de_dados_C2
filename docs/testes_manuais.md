# Roteiro de testes manuais

Usar somente banco de demonstração separado. Confirmar a splash e os totais; abrir chamado com cliente existente e novo; voltar em nome e telefone e corrigir email; tentar email inválido e nome/telefone vazios. Consultar um email inexistente, cliente sem chamados e cliente com chamado aberto. Confirmar e negar cancelamento.

Fazer login inválido e válido; assumir o próximo chamado; verificar fila vazia; conferir detalhes; resolver e verificar histórico. Com atendente autorizado, incluir, atualizar e excluir clientes, atendentes e chamados; tentar excluir cliente com chamado associado. Repetir com atendente não autorizado e confirmar recusa. Abrir os dois relatórios, conferir média e campos sem responsável. Verificar interrupção de conexão, retomada dos menus e saída.

Registrar versão do Python/PostgreSQL, data, ambiente, resultado e responsável por cada cenário. A execução na VM Linux permanece pendente; não confundir os testes locais automatizados com essa evidência.
