
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from conexion.postgres_queries import PostgresQueries
from controller.controller_atendente import Controller_Atendente


def run():
    postgres = PostgresQueries(can_write=True)
    try:
        postgres.connect()
        query = "update atendentes set senha = %s where email = %s"
        quantidade = postgres.write(query, (Controller_Atendente().validar_senha("Suporte123!"), "carla@example.invalid"))
        if quantidade == 0:
            raise SystemExit("Carregue os dados de exemplo antes de configurar o atendente.")
        print("Atendente fictício pronto para login.")
    finally:
        postgres.close()


if __name__ == "__main__":
    run()
