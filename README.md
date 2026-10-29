# Sistema de Atendimento ao Cliente

Projeto C2 de Banco de Dados — FAESA — semestre 2026/2 — Professor Howard Roatti.
Registra clientes, funcionários e atendimentos e apresenta relatórios do tempo de resolução e do histórico.

## Grupo
Preencher quatro nomes completos. O edital pede cinco integrantes: confirmem com o professor se quatro estão autorizados.
Vídeo: preencher URL após publicar.

## Instalação Linux
Requisitos: Python 3.10+ e PostgreSQL 14+. Na VM, siga primeiro as instruções de banco do professor.

    sudo apt update
    sudo apt install -y python3 python3-venv postgresql postgresql-client
    sudo service postgresql start
    sudo -u postgres createuser -P atendimento_app
    sudo -u postgres createdb -O atendimento_app atendimento_cliente
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    nano .env

Preencha .env com host, porta, banco, usuário e senha locais. Nunca envie .env ao GitHub. Rode:

    psql -h localhost -U atendimento_app -d atendimento_cliente -v ON_ERROR_STOP=1 -f sql/create_tables_atendimento.sql

Opcional, para dados fictícios:

    psql -h localhost -U atendimento_app -d atendimento_cliente -v ON_ERROR_STOP=1 -f sql/inserting_samples_atendimento.sql
    python -m src.principal

O schema não contém DROP. Execute cada script uma vez no banco correto.

## Menus
1. Relatórios: tempo médio de fechados por funcionário (AVG/GROUP BY) e atendimentos com cliente/funcionário (JOIN).
2. Inserir em clientes, funcionários e atendimentos.
3. Listar, escolher ID, confirmar e remover. FKs bloqueiam exclusão de cadastro com atendimentos.
4. Atualizar todos os campos menos ID e exibir o registro atualizado.
5. Sair. Submenus permitem repetir; 0 retorna.
Datas usam AAAA-MM-DD HH:MM. ABERTO não tem data de fechamento; FECHADO precisa de horário posterior à abertura.

Com os dados de exemplo, a média do N1 deve ser 37,50 minutos e do N2, 80,00. O relatório de detalhes deve mostrar quatro atendimentos.

## Arquivos
- sql/: schema e dados de demonstração.
- src/model/: entidades e validação.
- src/controller/: CRUD em SQL manual, sem ORM.
- src/sql/ e src/reports/: consultas e relatórios.
- src/database.py: conexão PostgreSQL.
- src/principal.py: menus.
- PROMPTS.md: registro de IA e revisão humana.

![Diagrama relacional](diagrams/diagrama_relacional_atendimento.png)

Diagrama relacional editável: diagrams/diagrama_relacional_atendimento.mmd. Imagem: diagrams/diagrama_relacional_atendimento.png.

O SQL é montado em strings, com tabelas/colunas fixas e valores escapados pelo adaptador Psycopg2, sem ORM. A execução na VM, vídeo, convite ao professor e envio no AVA devem ser finalizados pelo grupo. Consulte docs/checklist_entrega.md e docs/roteiro_video.md.
