import json
import os
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from conexion.postgres_queries import PostgresConnection


class PostgresConnectionTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ, {
            "DB_HOST": "test-host", "DB_PORT": "5544", "DB_NAME": "test-db",
            "DB_USER": "test-user", "DB_PASSWORD": "test-password",
        })
        env.start()
        self.addCleanup(env.stop)
        driver = patch("conexion.postgres_queries.psycopg2.connect")
        self.connect_mock = driver.start()
        self.addCleanup(driver.stop)
        self.connection = MagicMock(spec_set=psycopg2.extensions.connection)
        self.cursor = MagicMock(spec_set=psycopg2.extensions.cursor)
        self.connection.closed = 0
        self.cursor.closed = False
        self.connection.cursor.return_value = self.cursor
        self.connect_mock.return_value = self.connection
        self.db = PostgresConnection(can_write=True)
        self.addCleanup(self.db.close)
        self.db.connect()

    def test_environment_config_and_repeated_connect(self):
        self.connect_mock.assert_called_once_with(
            dbname="test-db", user="test-user", password="test-password",
            host="test-host", port=5544, connect_timeout=10,
        )
        self.assertIs(self.db.connect(), self.cursor)
        self.assertEqual(self.connect_mock.call_count, 1)

    def test_dotenv_path_does_not_depend_on_working_directory(self):
        with patch("conexion.postgres_queries.load_dotenv") as loader:
            other = PostgresConnection()
        self.addCleanup(other.close)
        loader.assert_called_once_with(
            Path(__file__).resolve().parents[1] / ".env", override=False,
        )

    def test_json_has_column_names_and_serializes_dates(self):
        self.cursor.description = [("NOME",), ("DATA",)]
        self.cursor.fetchall.return_value = [("João", date(2026, 10, 28))]
        result = self.db.sqlToJson("SELECT nome, data FROM atendimentos")
        self.assertEqual(json.loads(result), [{"nome": "João", "data": "2026-10-28"}])
        self.assertIn("João", result)

    def test_empty_json_is_an_empty_list(self):
        self.cursor.description = [("NOME",)]
        self.cursor.fetchall.return_value = []
        self.assertEqual(self.db.sqlToJson("SELECT nome FROM clientes"), "[]")

    def test_dataframe_and_matrix_keep_column_names(self):
        self.cursor.description = [("CPF",), ("NOME",)]
        self.cursor.fetchall.return_value = [("123", "Ana")]
        frame = self.db.sqlToDataFrame("SELECT cpf, nome FROM clientes")
        self.assertEqual(frame.to_dict("records"), [{"cpf": "123", "nome": "Ana"}])
        matrix, columns = self.db.sqlToMatrix("SELECT cpf, nome FROM clientes")
        self.assertEqual((matrix, columns), ([["123", "Ana"]], ["cpf", "nome"]))

    def test_write_passes_parameters_separately_and_commits(self):
        query = "INSERT INTO clientes (nome) VALUES (%s)"
        params = ("D'Ávila",)
        self.db.write(query, params)
        self.cursor.execute.assert_called_once_with(query, params)
        self.connection.commit.assert_called_once_with()

    def test_ddl_commits(self):
        self.db.executeDDL("CREATE TABLE exemplo (id integer)")
        self.connection.commit.assert_called_once_with()

    def test_write_and_ddl_require_explicit_permission(self):
        self.db.can_write = False
        for method in (self.db.write, self.db.executeDDL):
            with self.assertRaises(PermissionError):
                method("SQL que nao deve ser executado")
        self.cursor.execute.assert_not_called()

    def test_sql_error_rolls_back_and_allows_next_query(self):
        self.cursor.execute.side_effect = [psycopg2.IntegrityError("FK"), None]
        with self.assertRaises(psycopg2.IntegrityError):
            self.db.write("DELETE FROM clientes WHERE cpf = %s", ("123",))
        self.connection.rollback.assert_called_once_with()
        self.connection.commit.assert_not_called()
        self.db.write("UPDATE clientes SET nome = %s", ("Ana",))
        self.connection.commit.assert_called_once_with()

    def test_commit_failure_rolls_back(self):
        self.connection.commit.side_effect = psycopg2.IntegrityError("constraint")
        with self.assertRaises(psycopg2.IntegrityError):
            self.db.write("INSERT INTO exemplo VALUES (%s)", (1,))
        self.connection.rollback.assert_called_once_with()

    def test_query_before_connect_has_clear_error(self):
        other = PostgresConnection()
        self.addCleanup(other.close)
        with self.assertRaisesRegex(RuntimeError, "connect"):
            other.sqlToMatrix("SELECT 1")

    def test_close_releases_cursor_and_connection_only_once(self):
        self.db.close()
        self.db.close()
        self.cursor.close.assert_called_once_with()
        self.connection.close.assert_called_once_with()
        self.assertIsNone(self.db.cur)
        self.assertIsNone(self.db.conn)

    def test_close_still_releases_connection_when_cursor_close_fails(self):
        self.cursor.close.side_effect = psycopg2.InterfaceError("cursor")
        with self.assertRaises(psycopg2.InterfaceError):
            self.db.close()
        self.connection.close.assert_called_once_with()
        self.assertIsNone(self.db.conn)

    def test_connection_is_closed_if_cursor_creation_fails(self):
        self.db.close()
        self.connection.reset_mock()
        self.connection.cursor.side_effect = psycopg2.InterfaceError("cursor")
        with self.assertRaises(psycopg2.InterfaceError):
            self.db.connect()
        self.connection.close.assert_called_once_with()
        self.assertIsNone(self.db.conn)


if __name__ == "__main__":
    unittest.main()
