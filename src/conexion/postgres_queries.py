import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from pandas import DataFrame


class PostgresConnection:
    def __init__(self, can_write: bool = False):
        self.cur = None
        self.conn = None
        load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
        self.can_write = can_write
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.password = os.getenv("DB_PASSWORD")
        self.user = os.getenv("DB_USER", "postgres")
        self.dbname = os.getenv("DB_NAME", "postgres")

    def __del__(self):
        try:
            self.close()
        except Exception:
            # Destrutores também podem rodar durante a finalização do Python.
            pass

    def connect(self):
        '''
        Esse método realiza a conexão com o banco de dados Oracle
        Parameters:
        - user: nome do usuário criado para utilização do banco de dados
        - password: senha do usuário criado para utilização do banco de dados
        - dsn: string de conexão para acessar o banco de dados oracle
        - enconding: codificação de caracteres para não haver erros com caracteres em português
        return: um cursor que permite utilizar as funções da biblioteca cx_Oracle
        '''
        if (
            self.conn is not None and not self.conn.closed
            and self.cur is not None and not self.cur.closed
        ):
            return self.cur

        self.close()
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            connect_timeout=10,
        )
        try:
            self.cur = self.conn.cursor()
        except psycopg2.Error:
            self.close()
            raise
        return self.cur

    def _execute(self, query: str, params=None, commit: bool = False):
        if (
            self.conn is None or self.conn.closed
            or self.cur is None or self.cur.closed
        ):
            raise RuntimeError("Conecte ao PostgreSQL com connect() antes de executar SQL.")
        try:
            self.cur.execute(query, params)
            if commit:
                self.conn.commit()
        except psycopg2.Error:
            self.conn.rollback()
            raise

    def sqlToDataFrame(self, query: str, params=None) -> DataFrame:
        '''
        Esse método irá executar uma query
        Parameters:
        - query: consulta utilizada para recuperação dos dados
        return: um DataFrame da biblioteca Pandas
        '''
        self._execute(query, params)
        rows = self.cur.fetchall()
        return DataFrame(rows, columns=[col[0].lower() for col in self.cur.description])

    def sqlToMatrix(self, query: str, params=None) -> tuple:
        '''
        Esse método irá executar uma query
        Parameters:
        - query: consulta utilizada para recuperação dos dados
        return: uma matriz (lista de listas), uma lista com os nomes das colunas(atributos) da(s) tabela(s)
        '''        
        self._execute(query, params)
        rows = self.cur.fetchall()
        matrix = [list(row) for row in rows]
        columns = [col[0].lower() for col in self.cur.description]
        return matrix, columns

    def sqlToJson(self, query: str, params=None) -> str:
        '''
        Esse método irá executar uma query
        Parameters:
        - query: consulta utilizada para recuperação dos dados
        return: um objeto json
        '''
        self._execute(query, params)
        columns = [col[0].lower() for col in self.cur.description]
        rows = [dict(zip(columns, row)) for row in self.cur.fetchall()]
        return json.dumps(rows, default=str, ensure_ascii=False)

    def write(self, query: str, params=None):
        """Executa e confirma uma alteração; desfaz a transação em caso de erro."""
        if not self.can_write:
            raise PermissionError("Esta conexão não permite alterações; use can_write=True.")
        self._execute(query, params, commit=True)

    def close(self):
        try:
            if self.cur is not None and not self.cur.closed:
                self.cur.close()
        finally:
            self.cur = None
            try:
                if self.conn is not None and not self.conn.closed:
                    self.conn.close()
            finally:
                self.conn = None

    def executeDDL(self, query: str, params=None):
        '''
        Esse método irá executar o comando DDL enviado no atributo query
        Parameters:
        - query: consulta utilizada para comandos DDL
        '''
        self.write(query, params)
