from pathlib import Path

from conexion.postgres_queries import PostgresConnection


SQL_DIRECTORY = Path(__file__).resolve().parents[1] / "sql"


def create_tables(query: str):
    postgres = PostgresConnection(can_write=True)
    try:
        postgres.connect()
        for command in query.split(";"):
            if command.strip():
                postgres.executeDDL(command)
    finally:
        postgres.close()


def generate_records(query: str, sep: str = ";"):
    if not query.strip():
        return
    postgres = PostgresConnection(can_write=True)
    try:
        postgres.connect()
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
    create_tables(query_create)
    print("Tabelas criadas com sucesso!")

    query_records = (SQL_DIRECTORY / "inserting_samples_atendimento.sql").read_text(
        encoding="utf-8"
    )
    if query_records.strip():
        print("Inserindo registros de exemplo...")
        generate_records(query_records)
        print("Registros inseridos com sucesso!")
    else:
        print("Nenhum registro de exemplo definido para atendimento.")


if __name__ == "__main__":
    run()
