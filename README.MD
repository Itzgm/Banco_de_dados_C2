# Sistema de chamados de suporte

Aplicação de terminal em Python com PostgreSQL para abertura, consulta e
atendimento de chamados. Esta branch contém a parte de CLI de Davi Tavares.

## Executar as telas sem banco

Requer Python 3.10 ou superior. Na raiz do repositório:

```sh
python src/principal.py --demo
```

O modo de demonstração não exige bibliotecas externas. Os dados são apagados
ao sair. Login sintético: `atendente@exemplo.com`; senha: `demonstracao`.

Menu inicial: abrir chamado, consultar chamados, login do atendente e sair.
No login, a senha é digitada de forma oculta. Em campos de formulário,
`/voltar` retorna à etapa indicada. Nos menus, escolha a opção de retorno.
Entradas inválidas reapresentam o menu. Logout retorna à tela principal.

Para demonstrar inclusão, listagem, atualização e remoção das três entidades:

```sh
python src/principal.py --demo --manutencao
```

A manutenção é uma entrada local separada, inclusive para cadastrar o primeiro
atendente. Seu controle de acesso precisa ser aprovado pelo grupo. Não existe
papel de administrador no modelo atual.

## Integração com PostgreSQL

A integração completa ainda depende das Pessoas 1, 2 e 3. Nesta branch, os
módulos de identidade e chamados ainda não oferecem as operações necessárias,
e os relatórios antigos não foram substituídos pelo responsável. Sem `--demo`,
a CLI informa essas pendências e permite retornar ao menu; não grava dados
simulados nem apresenta erro como sucesso.

Prepare um ambiente local:

```sh
python -m venv .venv
```

Linux: `source .venv/bin/activate`. Windows PowerShell:
`.\.venv\Scripts\Activate.ps1`.

```sh
python -m pip install -r src/requirements.txt
```

Copie `.env.example` para `.env` e preencha host, porta, banco, usuário e senha.
O banco PostgreSQL deve existir e o usuário precisa de permissão para criar as
tabelas. O arquivo `.env` é local e não deve ser versionado.

Em banco novo e vazio, execute uma única vez:

```sh
python src/create_tables_and_records.py
```

O instalador usa `sql/create_tables_atendimento.sql`. Não é uma migração nem
uma operação idempotente. Não execute sobre uma base que precisa preservar.
A carga de exemplo de atendimento está vazia nesta branch.

Após integrar os contratos de todos os módulos:

```sh
python src/principal.py
python src/principal.py --manutencao
```

Os caminhos de execução acima partem da raiz; o ponto de entrada também aceita
caminho absoluto. Ele não importa Oracle nem abre arquivos de vendas.
`src/test.py` é uma entrada alternativa para a mesma CLI, sem executar SQL legado.

Para identificar a equipe no splash, defina `EQUIPE_NOMES` com os quatro nomes.
Davi está identificado; os nomes restantes devem ser confirmados pelo grupo.
O splash usa professor Howard Roatti, Banco de Dados e semestre 2026/2.

## Verificação e entrega

```sh
python tests/test_cli.py -v
```

Os testes da CLI usam dados temporários e não precisam de PostgreSQL. O resultado
e os limites estão em [testes manuais](docs/testes_manuais.md).

- [Contratos da CLI](docs/contratos_cli.md): métodos esperados dos outros módulos.
- [Requisitos e regras](docs/requisitos.md).
- [Checklist de entrega](docs/checklist_entrega.md).
- [Roteiro do vídeo](docs/roteiro_video.md).
- [Vídeo demonstrativo](docs/video_demonstrativo.md).
- [Planejamento geral](docs/planejamento_projeto.md).

A aprovação dos testes de tela não comprova banco real, atomicidade da fila,
instalação na VM, vídeo ou entrega no AVA. Esses itens estão pendentes no checklist.
