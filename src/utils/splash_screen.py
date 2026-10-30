from conexion.postgres_queries import PostgresQueries
from utils import config


class SplashScreen:
    def __init__(self):
        self.qry_total_clientes = config.QUERY_COUNT.format(tabela="clientes")
        self.qry_total_atendentes = config.QUERY_COUNT.format(tabela="atendentes")
        self.qry_total_chamados = config.QUERY_COUNT.format(tabela="chamados")
        self.created_by = "\n Natan Ferreira Garcia \nDavi Tavares da Cunha\nRicardo Otoni Ventura\n Felipe Cesconeti"
        self.professor = "Prof. M.Sc. Howard Roatti"
        self.disciplina = "Banco de Dados"
        self.semestre = "2026/2"

    def get_updated_screen(self):
        return f"""
        ########################################################
        #         {config.NOME_APLICACAO}
        #
        #  TOTAL DE REGISTROS:
        #      1 - CLIENTES:         {str(self.get_total_clientes()).rjust(5)}
        #      2 - ATENDENTES:       {str(self.get_total_atendentes()).rjust(5)}
        #      3 - CHAMADOS:         {str(self.get_total_chamados()).rjust(5)}
        #
        #  CRIADO POR: {self.created_by}
        #
        #  PROFESSOR:  {self.professor}
        #
        #  DISCIPLINA: {self.disciplina}
        #              {self.semestre}
        ########################################################
        """

    def get_total_clientes(self) -> int:
        postgres = PostgresQueries()
        try:
            postgres.connect()
            df_total = postgres.sqlToDataFrame(self.qry_total_clientes)
            return int(df_total.iloc[0]["total_clientes"])
        finally:
            postgres.close()

    def get_total_atendentes(self) -> int:
        postgres = PostgresQueries()
        try:
            postgres.connect()
            df_total = postgres.sqlToDataFrame(self.qry_total_atendentes)
            return int(df_total.iloc[0]["total_atendentes"])
        finally:
            postgres.close()

    def get_total_chamados(self) -> int:
        postgres = PostgresQueries()
        try:
            postgres.connect()
            df_total = postgres.sqlToDataFrame(self.qry_total_chamados)
            return int(df_total.iloc[0]["total_chamados"])
        finally:
            postgres.close()
