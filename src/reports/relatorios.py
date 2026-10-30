from pathlib import Path
from conexion.postgres_queries import PostgresQueries


class Relatorio:
    def __init__(self):
        diretorio_sql = Path(__file__).resolve().parents[1] / "sql"
        try:
            self.query_relatorio_clientes = (diretorio_sql / "relatorio_clientes.sql").read_text(encoding="utf-8")
            self.query_relatorio_atendentes = (diretorio_sql / "relatorio_atendentes.sql").read_text(encoding="utf-8")
            self.query_relatorio_atendimentos_detalhados = (diretorio_sql / "relatorio_atendimentos_detalhados.sql").read_text(encoding="utf-8")
            self.query_relatorio_tempo_medio_por_atendente = (diretorio_sql / "relatorio_tempo_medio_por_atendente.sql").read_text(encoding="utf-8")
        except (OSError, UnicodeError) as erro:
            raise ConnectionError("Arquivo de relatório indisponível. Confira a instalação.") from erro

    def get_relatorio_clientes(self, exibir: bool = True):
        postgres = PostgresQueries()
        try:
            postgres.connect()
            df_relatorio = postgres.sqlToDataFrame(self.query_relatorio_clientes)
        finally:
            postgres.close()
        if exibir:
            print("Clientes")
            if df_relatorio.empty:
                print("Nenhum registro encontrado.")
            else:
                exibicao = df_relatorio.astype(object).where(df_relatorio.notna(), "Não disponível")
                print(exibicao.to_string(index=False))
            input("Pressione Enter para sair do relatório: ")
        return df_relatorio

    def get_relatorio_atendentes(self, exibir: bool = True):
        postgres = PostgresQueries()
        try:
            postgres.connect()
            df_relatorio = postgres.sqlToDataFrame(self.query_relatorio_atendentes)
        finally:
            postgres.close()
        if exibir:
            print("Atendentes")
            if df_relatorio.empty:
                print("Nenhum registro encontrado.")
            else:
                exibicao = df_relatorio.astype(object).where(df_relatorio.notna(), "Não disponível")
                print(exibicao.to_string(index=False))
            input("Pressione Enter para sair do relatório: ")
        return df_relatorio

    def get_relatorio_atendimentos_detalhados(self, exibir: bool = True):
        postgres = PostgresQueries()
        try:
            postgres.connect()
            df_relatorio = postgres.sqlToDataFrame(self.query_relatorio_atendimentos_detalhados)
        finally:
            postgres.close()
        if exibir:
            print("Detalhes dos chamados")
            if df_relatorio.empty:
                print("Nenhum registro encontrado.")
            else:
                exibicao = df_relatorio.astype(object).where(df_relatorio.notna(), "Não disponível")
                print(exibicao.to_string(index=False))
            input("Pressione Enter para sair do relatório: ")
        return df_relatorio

    def get_relatorio_tempo_medio_por_atendente(self, exibir: bool = True):
        postgres = PostgresQueries()
        try:
            postgres.connect()
            df_relatorio = postgres.sqlToDataFrame(self.query_relatorio_tempo_medio_por_atendente)
        finally:
            postgres.close()
        if exibir:
            print("Tempo médio por atendente")
            print("Média em segundos entre abertura e fechamento; sem amostra = não disponível.")
            if df_relatorio.empty:
                print("Nenhum registro encontrado.")
            else:
                exibicao = df_relatorio.astype(object).where(df_relatorio.notna(), "Não disponível")
                print(exibicao.to_string(index=False))
            input("Pressione Enter para sair do relatório: ")
        return df_relatorio

    def get_totais(self) -> dict:
        postgres = PostgresQueries()
        try:
            postgres.connect()
            totais = {}
            for tabela in ("clientes", "atendentes", "chamados"):
                query = f"select count(1) as total from {tabela}"
                df_total = postgres.sqlToDataFrame(query)
                totais[tabela] = int(df_total.iloc[0]["total"])
            return totais
        finally:
            postgres.close()
