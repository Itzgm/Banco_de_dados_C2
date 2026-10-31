# Padrão de escrita e organização

Referência analisada diretamente: [example_crud_oracle](https://github.com/howardroatti/example_crud_oracle).

- `principal.py` usa funções de despacho e navegação, como o arquivo equivalente da referência.
- Cada controller tem construtor, métodos de existência, CRUD, consultas e formulários da entidade. A sequência é abrir conexão, validar, executar, recuperar dados, construir objeto, apresentar e retornar.
- `PostgresQueries` é a intermediária direta entre os controllers e o driver PostgreSQL. Não há módulo de repositório nem camada de mapeamento adicional.
- Modelos inicializam atributos por setters, disponibilizam getters tipados e apresentam dados por `to_string`; associações usam objetos das entidades.
- Relatórios possuem atributos com as consultas dos arquivos SQL e métodos individuais para recuperação e apresentação.
- Splash usa consultas e métodos de contagem próprios; configuração concentra menus e funções auxiliares de entrada.
- Usar nomes compreensíveis, consultas em variáveis, comentários em português e blocos explícitos. Não copiar interpolação de dados do usuário em SQL, credenciais fixas, fechamento incompleto ou inversão de significado dos métodos de existência da referência.
- Valores recebidos são parâmetros; identidades usam RETURNING. As transações e os bloqueios necessários ao atendimento concorrente são adaptações específicas do projeto.

Senhas permanecem em texto direto e visíveis na digitação, conforme as escolhas do usuário. A refatoração se limita à `base_exemplo`. Vinte verificações temporárias com PostgreSQL foram aprovadas; não existem testes permanentes nesta cópia. A execução real na VM Linux ainda está pendente.

O diretório utils mantém apenas os três arquivos da referência: __init__.py, config.py e splash_screen.py. As validações ficam nos controllers e a autorização no controller de atendentes. Erros são apresentados usando exceções nativas do Python. Controllers de cliente/atendente recuperam o DataFrame após atualização; o de chamados valida as entidades associadas por métodos próprios, como o controller de Pedido original.

O controller de Fornecedor enviado pelo usuário também foi utilizado como referência direta: os métodos CRUD aparecem primeiro, seguidos pela verificação de existência e pelas consultas auxiliares. A leitura dos atributos usa as colunas do DataFrame, a criação do objeto é explícita e os comentários acompanham as etapas de gravação, recuperação, apresentação e retorno.
