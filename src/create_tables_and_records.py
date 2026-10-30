from pathlib import Path

from conexion.postgres_queries import PostgresQueries


SQL_DIRECTORY = Path(__file__).resolve().parents[1] / "sql"


def create_tables(query: str):
    
    postgres = PostgresQueries(can_write=True)
    try:
        postgres.connect()
        with postgres.transaction():
            for command in query.split(";"):
                if command.strip():
                    postgres.executeDDL(command)
    finally:
        postgres.close()


def generate_records(query: str, sep: str = ";"):
    
    if not query.strip():
        return
    postgres = PostgresQueries(can_write=True)
    try:
        postgres.connect()
        with postgres.transaction():
            for command in query.split(sep):
                if command.strip():
                    postgres.write(command)
    finally:
        postgres.close()


def run():
    
    query_create = (SQL_DIRECTORY / "create_tables_atendimento.sql").read_text(
        encoding="utf-8"
    )
    print("Criando tabelas...")
    try:
        create_tables(query_create)
    except Exception:
        print("Falha ao criar tabelas; a etapa foi desfeita. Confira o banco antes de tentar novamente.")
        raise
    print("Tabelas criadas com sucesso!")

    query_records = (SQL_DIRECTORY / "inserting_samples_atendimento.sql").read_text(
        encoding="utf-8"
    )
    if query_records.strip():
        print("Inserindo registros de exemplo...")
        try:
            generate_records(query_records)
        except Exception:
            print("Falha na carga de exemplos; a carga foi desfeita. As tabelas criadas permanecem no banco.")
            raise
        print("Registros inseridos com sucesso!")
    else:
        print("Nenhum registro de exemplo definido para atendimento.")


if __name__ == "__main__":
    run()
