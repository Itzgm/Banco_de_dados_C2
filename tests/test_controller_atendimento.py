import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from model.atendimentos import Atendimento
from controller.controller_atendimento import Controller_Atendimento


class TestControllerAtendimento(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_db.cur = MagicMock()
        self.mock_db.conn = MagicMock()
        self.mock_db.conn.closed = 0
        self.mock_db.cur.closed = False
        self.controller = Controller_Atendimento(db=self.mock_db)

    def test_modelo_atendimento(self):
        agora = datetime(2026, 10, 29, 10, 0)
        atendimento = Atendimento(
            id_chamado=1,
            id_cliente=10,
            id_atendente=2,
            nome="Problema no login",
            descricao="Não consigo logar",
            data_abertura=agora,
            status="aberto"
        )
        self.assertEqual(atendimento.get_id_chamado(), 1)
        self.assertEqual(atendimento.get_id_cliente(), 10)
        self.assertEqual(atendimento.get_id_atendente(), 2)
        self.assertEqual(atendimento.get_nome(), "Problema no login")
        self.assertEqual(atendimento.get_status(), "aberto")
        self.assertIn("Problema no login", atendimento.to_string())

    def test_criar_chamado_sucesso(self):
        # 1ª chamada: valida se o cliente existe
        # 2ª chamada: insert returning do chamado
        self.mock_db.cur.fetchone.side_effect = [
            (10, "Carlos"),
            (1, 10, None, "Erro na tela", "Descrição do erro", datetime(2026, 10, 29), None, "aberto")
        ]

        chamado = self.controller.criar_chamado(10, "Erro na tela", "Descrição do erro")
        self.assertIsNotNone(chamado)
        self.assertEqual(chamado.get_id_chamado(), 1)
        self.assertEqual(chamado.get_status(), "aberto")
        self.mock_db.conn.commit.assert_called()

    def test_criar_chamado_cliente_inexistente(self):
        self.mock_db.cur.fetchone.return_value = None
        chamado = self.controller.criar_chamado(999, "Título", "Desc")
        self.assertIsNone(chamado)

    def test_listar_chamados_cliente(self):
        self.mock_db.cur.fetchall.return_value = [
            (1, 10, 2, "Chamado 1", "Desc 1", datetime(2026, 10, 29), None, "em andamento"),
            (2, 10, None, "Chamado 2", "Desc 2", datetime(2026, 10, 28), None, "aberto")
        ]

        lista = self.controller.listar_chamados_cliente(10)
        self.assertEqual(len(lista), 2)
        self.assertEqual(lista[0].get_id_chamado(), 1)
        self.assertEqual(lista[1].get_id_chamado(), 2)

    def test_cancelar_chamado_sucesso(self):
        # Chamado encontrado, pertence ao cliente e está aberto
        self.mock_db.cur.fetchone.return_value = (1, 10, "aberto")

        resultado = self.controller.cancelar_chamado(1, 10)
        self.assertTrue(resultado)
        self.mock_db.conn.commit.assert_called()

    def test_cancelar_chamado_outro_cliente(self):
        # Chamado pertence ao cliente 99, mas cliente 10 tentou cancelar
        self.mock_db.cur.fetchone.return_value = (1, 99, "aberto")

        resultado = self.controller.cancelar_chamado(1, 10)
        self.assertFalse(resultado)

    def test_cancelar_chamado_em_andamento_rejeitado(self):
        # Chamado já em andamento não pode ser cancelado
        self.mock_db.cur.fetchone.return_value = (1, 10, "em andamento")

        resultado = self.controller.cancelar_chamado(1, 10)
        self.assertFalse(resultado)

    def test_assumir_proximo_chamado_sucesso(self):
        # Validação do atendente e retorno do update da fila
        self.mock_db.cur.fetchone.side_effect = [
            (2, "Atendente João"),
            (1, 10, 2, "Chamado da fila", "Desc", datetime(2026, 10, 20), None, "em andamento")
        ]

        chamado = self.controller.assumir_proximo_chamado(2)
        self.assertIsNotNone(chamado)
        self.assertEqual(chamado.get_id_chamado(), 1)
        self.assertEqual(chamado.get_status(), "em andamento")
        self.mock_db.conn.commit.assert_called()

    def test_assumir_proximo_chamado_fila_vazia(self):
        self.mock_db.cur.fetchone.side_effect = [
            (2, "Atendente João"),
            None  # Nenhum chamado retornado da query
        ]

        chamado = self.controller.assumir_proximo_chamado(2)
        self.assertIsNone(chamado)

    def test_resolver_chamado_sucesso(self):
        # Validação de status e update para resolvido
        self.mock_db.cur.fetchone.side_effect = [
            (1, 2, "em andamento"),
            (1, 10, 2, "Título", "Desc", datetime(2026, 10, 20), datetime(2026, 10, 29), "resolvido")
        ]

        resolvido = self.controller.resolver_chamado(1, 2)
        self.assertIsNotNone(resolvido)
        self.assertEqual(resolvido.get_status(), "resolvido")

    def test_resolver_chamado_outro_atendente(self):
        self.mock_db.cur.fetchone.return_value = (1, 99, "em andamento")

        resultado = self.controller.resolver_chamado(1, 2)
        self.assertIsNone(resultado)

    def test_atualizar_chamado(self):
        self.mock_db.cur.fetchone.return_value = (
            1, 10, None, "Título Atualizado", "Nova Descrição", datetime(2026, 10, 29), None, "aberto"
        )
        atualizado = self.controller.atualizar_chamado(1, "Título Atualizado", "Nova Descrição")
        self.assertIsNotNone(atualizado)
        self.assertEqual(atualizado.get_nome(), "Título Atualizado")

    def test_excluir_chamado_admin(self):
        self.mock_db.cur.rowcount = 1
        resultado = self.controller.excluir_chamado_admin(1)
        self.assertTrue(resultado)


if __name__ == "__main__":
    unittest.main()
