import json
from contextlib import contextmanager
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from pandas import DataFrame


class PostgresQueries:
    def __init__(self, can_write: bool = False):
        self.cur = None
        self.conn = None
        self._in_transaction = False
        load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
        self.can_write = can_write
        self.host = os.getenv("DB_HOST", "localhost")
        try:
            self.port = int(os.getenv("DB_PORT", "5432"))
        except ValueError as erro:
            raise ConnectionError("A porta PostgreSQL configurada é inválida.") from erro
        self.password = os.getenv("DB_PASSWORD")
        self.user = os.getenv("DB_USER", "postgres")
        self.dbname = os.getenv("DB_NAME", "postgres")

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def connect(self):
        
        if (
            self.conn is not None and not self.conn.closed
            and self.cur is not None and not self.cur.closed
        ):
            return self.cur

        self.close()
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                connect_timeout=10,
            )
        except psycopg2.Error as erro:
            self._informar_erro(erro)
        try:
            self.cur = self.conn.cursor()
        except psycopg2.Error as erro:
            self.close()
            self._informar_erro(erro)
        return self.cur

    def _execute(self, query: str, params=None, commit: bool = False):
        if (
            self.conn is None or self.conn.closed
            or self.cur is None or self.cur.closed
        ):
            raise RuntimeError("Conecte ao PostgreSQL com connect() antes de executar SQL.")
        try:
            self.cur.execute(query, params)
            if commit and not self._in_transaction:
                self.conn.commit()
        except psycopg2.Error as erro:
            if not self._in_transaction:
                self.conn.rollback()
            self._informar_erro(erro)

    @contextmanager
    def transaction(self):
        
        if not self.can_write:
            raise PermissionError("Esta conexão não permite alterações.")
        if self.conn is None or self.conn.closed or self.cur is None or self.cur.closed:
            raise RuntimeError("Conecte ao PostgreSQL antes de iniciar a transação.")
        if self._in_transaction:
            raise RuntimeError("Transações aninhadas não são suportadas.")
        self._in_transaction = True
        try:
            yield self
            self.conn.commit()
        except psycopg2.Error as erro:
            self.conn.rollback()
            self._informar_erro(erro)
        except BaseException:
            self.conn.rollback()
            raise
        finally:
            self._in_transaction = False

    def sqlToDataFrame(self, query: str, params=None) -> DataFrame:
        
        self._execute(query, params)
        rows = self.cur.fetchall()
        return DataFrame(rows, columns=[col[0].lower() for col in self.cur.description])

    def sqlToMatrix(self, query: str, params=None) -> tuple:
        
        self._execute(query, params)
        rows = self.cur.fetchall()
        matrix = [list(row) for row in rows]
        columns = [col[0].lower() for col in self.cur.description]
        return matrix, columns

    def sqlToJson(self, query: str, params=None) -> str:
        
        self._execute(query, params)
        columns = [col[0].lower() for col in self.cur.description]
        rows = [dict(zip(columns, row)) for row in self.cur.fetchall()]
        return json.dumps(rows, default=str, ensure_ascii=False)

    def write(self, query: str, params=None):
        
        if not self.can_write:
            raise PermissionError("Esta conexão não permite alterações; use can_write=True.")
        self._execute(query, params, commit=True)
        return self.cur.rowcount

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
        
        self.write(query, params)

    def _informar_erro(self, erro):
        if isinstance(erro, psycopg2.errors.UniqueViolation):
            raise RuntimeError("Já existe um registro com esse email.") from erro
        if isinstance(erro, psycopg2.errors.ForeignKeyViolation):
            raise ValueError("Existem registros relacionados ou uma referência inexistente.") from erro
        raise ConnectionError("Não foi possível concluir a operação no PostgreSQL. Confira a configuração e o serviço.") from erro
