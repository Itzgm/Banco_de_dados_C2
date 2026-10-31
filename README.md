# Sistema de atendimento — cópia integrada

Esta pasta é a cópia base_integrada, criada a partir da base_exemplo para integrar as branches de Ricardo e Davi. A análise, os commits de origem e as adaptações estão em [docs/integracao_branches.md](docs/integracao_branches.md). A aplicação usa Python, PostgreSQL e a interface de terminal. Seus arquivos podem ser alterados sem modificar os arquivos do projeto original. A conexão usada pela aplicação é definida no `.env` desta pasta; a validação automatizada temporária utiliza um banco isolado separado.

Requer Python 3.10 ou superior. A preparação de entrega está em [docs/entrega_projeto.md](docs/entrega_projeto.md); o grupo ainda deve confirmar se apresentará esta cópia ou a aplicação da raiz. Vídeo demonstrativo: ...Vídeo demonstrativo: [Clique para assistir à apresentação](https://youtu.be/M-h9aVHCf7s).

## Como executar nesta máquina

O PostgreSQL local de testes precisa estar iniciado. Na raiz do projeto original, siga `docs/postgres_local.md` para ligá-lo se necessário. Nesta pasta, o arquivo `.env` local já aponta para o banco da cópia e não deve ser publicado.

No PowerShell, estando na pasta `base_integrada`:

```powershell
..\.venv\Scripts\python.exe src\principal.py
```

O banco já foi inicializado nesta máquina. Para outra máquina, crie um banco vazio separado, configure `.env` a partir de `.env.example`, instale `src/requirements.txt` em um ambiente virtual e execute `src/create_tables_and_records.py` uma única vez. Depois execute `scripts/criar_atendente_demo.py` para habilitar o login fictício. O script de criação falha se as tabelas já existirem; ele não deve ser usado para recriar uma base com dados.

O instalador executa criação de tabelas e carga de exemplos em transações separadas. Se a criação falhar, ela é desfeita e a carga não começa. Se a carga falhar, apenas ela é desfeita; as tabelas já criadas permanecem. Nesse caso, examine o banco e corrija a causa antes de escolher como continuar; não repita a instalação sobre dados existentes.

## Experimente os fluxos

O menu inicial permite abrir chamado e consultá-lo pelo email do cliente. Se o email não existir, é solicitado o cadastro; digite `0` para voltar durante o cadastro. Na consulta, um chamado aberto pode ser cancelado mediante confirmação.

Para experimentar o menu do atendente, use o cadastro fictício **carla@example.invalid** e senha **Suporte123!**. A senha é pública e serve apenas para a base de demonstração. A partir desse menu é possível assumir automaticamente um chamado aberto, consultar histórico, resolver chamados e acessar relatórios.

A manutenção exige que o email do atendente autenticado conste em `MANUTENCAO_EMAILS` no `.env` desta cópia; separe vários emails por vírgula. A lista vazia impede a manutenção para todos. Para habilitar a demonstração local, inclua o email fictício acima nessa lista. Essa autorização não substitui as permissões do PostgreSQL.

A fila seleciona o chamado aberto sem atendente mais antigo. A atualização é feita na mesma transação que a escolha, usando bloqueio de linha. O histórico inclui chamados resolvidos do atendente autenticado. A média dos relatórios mede tempo entre abertura e fechamento, em segundos.

Por decisão do projeto acadêmico, a senha do atendente é salva e comparada em texto direto no banco. A senha fica visível durante a digitação e as listagens/objetos públicos não mostram a senha. Valores antigos em hash não podem ser convertidos para a senha original: redefina a senha dessas contas pela manutenção. Para a conta fictícia Carla, o script de demonstração redefine a senha pública Suporte123!. A carga SQL foi atualizada para novas instalações; não reexecute o instalador em uma base existente para aplicar essa mudança.

## Onde estudar o código

A arquitetura foi refatorada após análise direta de [example_crud_oracle](https://github.com/howardroatti/example_crud_oracle), com controllers interativos por entidade, PostgresQueries e funções de despacho no principal. As convenções estão em [docs/padrao_codigo.md](docs/padrao_codigo.md).

- `src/principal.py`: inicialização, navegação e funções de despacho `inserir`, `atualizar`, `excluir` e `reports`.
- `src/controller/controller_cliente.py`, `controller_atendente.py` e `controller_atendimento.py`: conexão direta, validações, CRUD, construção de objetos e formulários de cada entidade.
- `src/conexion/postgres_queries.py`: classe `PostgresQueries`, equivalente a OracleQueries, com consultas parametrizadas, transações e fechamento de recursos.
- `src/reports/relatorios.py` e `src/sql/`: consultas nomeadas e relatórios de clientes, atendentes, detalhes e média; a apresentação aguarda Enter para retornar.
- `src/model/`: classes de domínio usadas pelas controladoras ativas.
- `docs/contratos_componentes.md`: modelos públicos, responsabilidades e contratos das controladoras.
- `sql/create_tables_atendimento.sql`: tabelas e relacionamentos usados pela aplicação.
- `sql/inserting_samples_atendimento.sql`: registros fictícios. As contas fictícias usam a senha pública Suporte123! em texto direto.

As consultas aceitam parâmetros separados dos valores digitados. O edital menciona concatenação de SQL e proíbe ORM: confirmem com o professor se ele aceita esta forma parametrizada sem ORM. A identificação do cliente por email, sem senha, é uma simplificação do enunciado e não fornece autenticação forte.

## Pendências para a entrega acadêmica

Confirmar com o professor o acesso aos relatórios e à manutenção, revisar os critérios de CRUD do edital com todos os integrantes, executar na VM Linux da disciplina e gravar o vídeo demonstrativo. Os artefatos do exemplo de vendas e Oracle foram removidos desta cópia; a entrada é `src/principal.py`.

## Integrantes

Natan Ferreira Garcia, Ricardo Otoni Ventura, Felipe Cesconeti e Davi Tavares da Cunha.

## Preparação em Linux / VM da disciplina

1. Instale e inicie Python e PostgreSQL disponíveis na VM e crie um banco vazio próprio para o projeto. O usuário PostgreSQL precisa ter permissão para criar tabelas nesse banco.
2. Na pasta `base_integrada`, crie e ative um ambiente virtual Python; instale as dependências de `src/requirements.txt`.
3. Copie `.env.example` para `.env` e ajuste host, porta, nome do banco, usuário e senha. O arquivo `.env` é local e não deve ser enviado ao Git.
4. Execute `python src/create_tables_and_records.py` uma vez sobre o banco vazio. Para habilitar a conta fictícia dos dados de exemplo, execute `python scripts/criar_atendente_demo.py`.
5. Inicie a aplicação com `python src/principal.py`. Para instalar as dependências e executar no Linux, uma sequência típica é:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
cp .env.example .env
# Edite .env com as credenciais e o nome do banco vazio criado na VM.
python src/create_tables_and_records.py
python scripts/criar_atendente_demo.py
python src/principal.py
```

Os testes automatizados foram removidos desta cópia por solicitação do usuário. Os resultados anteriores são registros históricos; a validação da versão atual deve seguir o roteiro manual.

A VM da disciplina ainda precisa ser verificada pelo grupo. A aplicação é acadêmica: o email do cliente é suficiente para consultar/cancelar seus chamados conforme solicitado, e não constitui autenticação segura para uso público.

O procedimento de instalação e o formulário de aceite manual estão em [docs/validacao_vm.md](docs/validacao_vm.md). A aplicação usa a porta PostgreSQL definida na configuração local.

O script `scripts/criar_atendente_demo.py` utiliza a persistência e a validação de senha atuais e redefine a senha da conta fictícia, devendo ser executado apenas em banco de demonstração. Ele não pertence à inicialização normal da aplicação.

## Interface e relatórios — etapas 5 e 6

As listas de chamados exibem identificador, título e status; a seleção mostra os detalhes completos. Conflitos de cancelamento ou resolução atualizam a lista. Falhas ao consultar relatórios exibem mensagem e permitem continuar no submenu; se o banco estiver indisponível durante a apresentação inicial, a aplicação encerra com uma mensagem compreensível.

Os relatórios carregam arquivos a partir da localização do código. A configuração padrão também é localizada pela pasta da cópia, independentemente do diretório em que o comando foi iniciado; variáveis de ambiente já definidas têm precedência. Os módulos de Oracle, pedidos e a controladora monolítica antiga foram removidos desta cópia. Evidências de validação e limites: `docs/validacao_etapas_5_6.md`.

## Integração — etapa 7

Antes da remoção dos testes, a suíte integrada local passou com 42 testes aprovados, sem testes ignorados. A matriz em `docs/matriz_aceite_etapa_7.md` relaciona os cenários e suas evidências. Foram verificados fluxos completos pela CLI, manutenção das três entidades, encerramento de sessão ao excluir a própria conta, autorização baseada no email atual, titularidade, concorrência, validações e relatórios. A etapa local não substitui instalação e aceite manual na VM Linux.

## Refatoração pela arquitetura original

A comparação prévia, as correspondências arquivo a arquivo e as adaptações para PostgreSQL estão em [docs/refatoracao_arquitetura_original.md](docs/refatoracao_arquitetura_original.md). Foram removidos o repositório intermediário, o mapeamento global e a classe de aplicação concentrada. Os controllers de cada entidade usam PostgresQueries e conduzem os próprios formulários.

A refatoração foi validada por 20 verificações temporárias com banco isolado, sem recriar a pasta de testes: imports, APIs de conexão, CRUD, menus, relatórios, instalação, rollback e concorrência. A inicialização de leitura também funcionou com o `.env` atual. O banco configurado pelo usuário e suas credenciais foram preservados; a validação na VM Linux continua pendente.

A pasta `src/utils` contém somente `__init__.py`, `config.py` e `splash_screen.py`. Validação de dados, senha e autorização foram incorporadas aos controllers responsáveis. O tratamento de falhas usa exceções nativas; os controllers mantêm métodos próprios de existência, CRUD e recuperação de objetos via DataFrame.

## Particularidades da integração

O modelo ativo de chamados é `model/atendimentos.py` (Atendimento), e a controladora é `controller/controller_atendimento.py` (Controller_Atendimento), provenientes de Ricardo. Os fluxos públicos no principal foram adaptados dos de Davi e pedem confirmação numérica (1/0). A manutenção continua exigindo a lista de emails autorizados e usa s/N. O `.env` é uma cópia da configuração anterior: código separado não implica banco separado.
