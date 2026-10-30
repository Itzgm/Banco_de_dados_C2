import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from model.atendimentos import Atendimento
from controller.controller_atendimento import Controller_Atendimento


class ControllerAtendimentoTests(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_db.cur = MagicMock()
        self.mock_db.conn = MagicMock()
        self.mock_db.conn.closed = 0
        self.mock_db.cur.closed = False
        self.controller = Controller_Atendimento(db=self.mock_db)

    # -------------------------------------------------------------------------
    # TESTES DO MODELO ATENDIMENTO
    # -------------------------------------------------------------------------

    def test_modelo_atendimento_validacoes_e_atributos(self):
        agora = datetime(2026, 10, 29, 14, 30)
        atendimento = Atendimento(
            id_chamado=1,
            cliente=10,
            atendente=5,
            nome="Problema de Conexão",
            descricao="Sem acesso ao banco",
            data_abertura=agora,
            status="aberto"
        )
        self.assertEqual(atendimento.get_id_chamado(), 1)
        self.assertEqual(atendimento.get_id_cliente(), 10)
        self.assertEqual(atendimento.get_id_atendente(), 5)
        self.assertEqual(atendimento.get_titulo(), "Problema de Conexão")
        self.assertEqual(atendimento.get_status(), "aberto")
        self.assertIn("Problema de Conexão", atendimento.to_string())

        # Teste de status inválido
        with self.assertRaises(ValueError):
            atendimento.set_status("invalido_status")

    # -------------------------------------------------------------------------
    # TESTES DE CRIAÇÃO DE CHAMADO (CLIENTE)
    # -------------------------------------------------------------------------

    def test_criar_chamado_com_sucesso(self):
        # 1ª consulta: validação do cliente
        # 2ª consulta: INSERT RETURNING
        self.mock_db.cur.description = [("id_cliente",), ("nome",)]
        self.mock_db.cur.fetchall.side_effect = [
            [(10, "Maria Silva")],  # Cliente encontrado
            [(101, 10, None, "Erro de login", "Não consigo acessar", datetime(2026, 10, 29), None, "aberto")]
        ]
        self.mock_db.cur.description = [
            ("id_chamado",), ("id_cliente",), ("id_atendente",),
            ("nome",), ("descricao",), ("data_abertura",),
            ("data_fechamento",), ("status",)
        ]

        # Reset description para primeira query
        def fetch_side_effect():
            pass

        # Vamos estruturar o mock de cursor para retornar as colunas certas em cada etapa
        call_count = [0]
        def custom_fetchall():
            call_count[0] += 1
            if call_count[0] == 1:
                self.mock_db.cur.description = [("id_cliente",), ("nome",)]
                return [(10, "Maria Silva")]
            else:
                self.mock_db.cur.description = [
                    ("id_chamado",), ("id_cliente",), ("id_atendente",),
                    ("nome",), ("descricao",), ("data_abertura",),
                    ("data_fechamento",), ("status",)
                ]
                return [(101, 10, None, "Erro de login", "Não consigo acessar", datetime(2026, 10, 29), None, "aberto")]

        self.mock_db.cur.fetchall = custom_fetchall

        chamado = self.controller.criar_chamado(10, "Erro de login", "Não consigo acessar")

        self.assertIsInstance(chamado, Atendimento)
        self.assertEqual(chamado.get_id_chamado(), 101)
        self.assertEqual(chamado.get_titulo(), "Erro de login")
        self.assertEqual(chamado.get_status(), "aberto")
        self.mock_db.conn.commit.assert_called()

    def test_criar_chamado_cliente_inexistente(self):
        self.mock_db.cur.description = [("id_cliente",), ("nome",)]
        self.mock_db.cur.fetchall.return_value = []  # Nenhum cliente encontrado

        with self.assertRaisesRegex(LookupError, "não encontrado"):
            self.controller.criar_chamado(999, "Título", "Descrição")

    def test_criar_chamado_validacao_campos(self):
        with self.assertRaises(ValueError):
            self.controller.criar_chamado(0, "Título", "Descrição")
        with self.assertRaises(ValueError):
            self.controller.criar_chamado(1, "", "Descrição")
        with self.assertRaises(ValueError):
            self.controller.criar_chamado(1, "Título", "   ")

    # -------------------------------------------------------------------------
    # TESTES DE LISTAGEM E DETALHES (CLIENTE)
    # -------------------------------------------------------------------------

    def test_listar_chamados_cliente(self):
        self.mock_db.cur.description = [
            ("id_chamado",), ("id_cliente",), ("id_atendente",), ("nome",),
            ("descricao",), ("data_abertura",), ("data_fechamento",), ("status",),
            ("nome_cliente",), ("nome_atendente",)
        ]
        self.mock_db.cur.fetchall.return_value = [
            (1, 10, 2, "Chamado 1", "Desc", datetime(2026, 10, 29), None, "em andamento", "João", "Atendente 1"),
            (2, 10, None, "Chamado 2", "Desc", datetime(2026, 10, 28), None, "aberto", "João", None)
        ]

        chamados = self.controller.listar_chamados_cliente(10)
        self.assertEqual(len(chamados), 2)
        self.assertEqual(chamados[0].get_id_chamado(), 1)
        self.assertEqual(chamados[1].get_id_chamado(), 2)

    def test_consultar_detalhes_inexistente(self):
        self.mock_db.cur.description = [("id_chamado",)]
        self.mock_db.cur.fetchall.return_value = []

        with self.assertRaises(LookupError):
            self.controller.consultar_detalhes(999)

    # -------------------------------------------------------------------------
    # TESTES DE CANCELAMENTO (CLIENTE)
    # -------------------------------------------------------------------------

    def test_cancelar_chamado_com_sucesso(self):
        self.mock_db.cur.description = [("id_chamado",), ("id_cliente",), ("status",)]
        self.mock_db.cur.fetchall.return_value = [(101, 10, "aberto")]
        self.mock_db.cur.rowcount = 1

        resultado = self.controller.cancelar_chamado(101, 10)
        self.assertTrue(resultado)
        self.mock_db.conn.commit.assert_called()

    def test_cancelar_chamado_outro_cliente(self):
        self.mock_db.cur.description = [("id_chamado",), ("id_cliente",), ("status",)]
        self.mock_db.cur.fetchall.return_value = [(101, 99, "aberto")]  # Pertence ao cliente 99

        with self.assertRaises(PermissionError):
            self.controller.cancelar_chamado(101, 10)  # Tentativa com cliente 10

    def test_cancelar_chamado_em_andamento_rejeitado(self):
        self.mock_db.cur.description = [("id_chamado",), ("id_cliente",), ("status",)]
        self.mock_db.cur.fetchall.return_value = [(101, 10, "em andamento")]  # Já em andamento

        with self.assertRaisesRegex(ValueError, "status atual é 'em andamento'"):
            self.controller.cancelar_chamado(101, 10)

    # -------------------------------------------------------------------------
    # TESTES DA FILA FIFO (ATENDENTE)
    # -------------------------------------------------------------------------

    def test_assumir_proximo_chamado_fifo_sucesso(self):
        call_count = [0]
        def custom_fetchall():
            call_count[0] += 1
            if call_count[0] == 1:
                self.mock_db.cur.description = [("id_atendente",), ("nome",)]
                return [(2, "Carlos Atendente")]
            else:
                self.mock_db.cur.description = [
                    ("id_chamado",), ("id_cliente",), ("id_atendente",),
                    ("nome",), ("descricao",), ("data_abertura",),
                    ("data_fechamento",), ("status",)
                ]
                return [(50, 10, 2, "Chamado mais antigo", "Detalhes", datetime(2026, 10, 20), None, "em andamento")]

        self.mock_db.cur.fetchall = custom_fetchall

        chamado = self.controller.assumir_proximo_chamado(2)
        self.assertIsNotNone(chamado)
        self.assertEqual(chamado.get_id_chamado(), 50)
        self.assertEqual(chamado.get_status(), "em andamento")
        self.mock_db.conn.commit.assert_called()

    def test_assumir_proximo_chamado_fila_vazia(self):
        call_count = [0]
        def custom_fetchall():
            call_count[0] += 1
            if call_count[0] == 1:
                self.mock_db.cur.description = [("id_atendente",), ("nome",)]
                return [(2, "Carlos Atendente")]
            else:
                self.mock_db.cur.description = [("id_chamado",)]
                return []  # Fila vazia

        self.mock_db.cur.fetchall = custom_fetchall

        chamado = self.controller.assumir_proximo_chamado(2)
        self.assertIsNone(chamado)

    # -------------------------------------------------------------------------
    # TESTES DE RESOLUÇÃO (ATENDENTE)
    # -------------------------------------------------------------------------

    def test_resolver_chamado_sucesso(self):
        call_count = [0]
        def custom_fetchall():
            call_count[0] += 1
            if call_count[0] == 1:
                self.mock_db.cur.description = [("id_chamado",), ("id_atendente",), ("status",)]
                return [(50, 2, "em andamento")]
            else:
                self.mock_db.cur.description = [
                    ("id_chamado",), ("id_cliente",), ("id_atendente",),
                    ("nome",), ("descricao",), ("data_abertura",),
                    ("data_fechamento",), ("status",)
                ]
                return [(50, 10, 2, "Título", "Desc", datetime(2026, 10, 20), datetime(2026, 10, 29), "resolvido")]

        self.mock_db.cur.fetchall = custom_fetchall

        resolvido = self.controller.resolver_chamado(50, 2)
        self.assertEqual(resolvido.get_status(), "resolvido")
        self.assertIsNotNone(resolvido.get_data_fechamento())

    def test_resolver_chamado_de_outro_atendente_rejeitado(self):
        self.mock_db.cur.description = [("id_chamado",), ("id_atendente",), ("status",)]
        self.mock_db.cur.fetchall.return_value = [(50, 99, "em andamento")]  # Atendente 99

        with self.assertRaises(PermissionError):
            self.controller.resolver_chamado(50, 2)  # Atendente 2 tentando resolver

    # -------------------------------------------------------------------------
    # TESTES DE MANUTENÇÃO (CRUD EDITAL)
    # -------------------------------------------------------------------------

    def test_atualizar_chamado_sucesso(self):
        self.mock_db.cur.description = [
            ("id_chamado",), ("id_cliente",), ("id_atendente",),
            ("nome",), ("descricao",), ("data_abertura",),
            ("data_fechamento",), ("status",)
        ]
        self.mock_db.cur.fetchall.return_value = [
            (50, 10, 2, "Novo Título", "Nova Descrição", datetime(2026, 10, 20), None, "em andamento")
        ]

        atualizado = self.controller.atualizar_chamado(50, "Novo Título", "Nova Descrição")
        self.assertEqual(atualizado.get_titulo(), "Novo Título")
        self.assertEqual(atualizado.get_descricao(), "Nova Descrição")

    def test_excluir_chamado_admin(self):
        self.mock_db.cur.rowcount = 1
        resultado = self.controller.excluir_chamado_admin(50)
        self.assertTrue(resultado)


if __name__ == "__main__":
    unittest.main()
