import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cli.aplicacao import Aplicacao
from cli.demonstracao import ProvedorDemonstracao
from cli.entrada import Entrada
from cli.provedor import ErroOperacao, ProvedorControladoras


class TestCli(unittest.TestCase):
    def setUp(self):
        self.provedor = ProvedorDemonstracao()
        self.saida = []

    def app(self, respostas, senhas=()):
        respostas = iter(respostas)
        senhas = iter(senhas)
        entrada = Entrada(lambda _: next(respostas), self.saida.append,
                          lambda _: next(senhas))
        return Aplicacao(self.provedor, entrada)

    def cliente(self, email="cliente@exemplo.com"):
        return self.provedor.executar("clientes", "cadastrar_cliente", "Cliente", email, "0011")

    def chamado(self):
        cliente = self.cliente()
        return self.provedor.executar("chamados", "criar_chamado", cliente["id_cliente"],
                                     "Falha na rede", "Sem conexão")

    def test_menu_recupera_entrada_invalida(self):
        self.app(["abc", "", "-1", "9", "0"]).iniciar()
        self.assertEqual(self.saida.count("Opção inválida. Tente novamente."), 4)
        self.assertIn("Obrigado por utilizar o sistema. Até logo!", self.saida)

    def test_corrigir_email_nao_grava_cadastro_incompleto(self):
        app = self.app(["errado@exemplo.com", "Nome", "/voltar", "certo@exemplo.com",
                        "Nome certo", "0011", "1", "Rede", "Descrição", "1", "0"])
        app.abrir_chamado()
        clientes = list(self.provedor.dados["clientes"].values())
        self.assertEqual(len(clientes), 1)
        self.assertEqual(clientes[0]["email"], "certo@exemplo.com")
        self.assertEqual(len(self.provedor.dados["chamados"]), 1)

    def test_reutiliza_cliente_e_preserva_acentos(self):
        self.cliente()
        self.app(["cliente@exemplo.com", "Conexão d'água", "Descrição", "1", "0"]).abrir_chamado()
        self.assertEqual(len(self.provedor.dados["clientes"]), 1)
        self.assertEqual(self.provedor.dados["chamados"][1]["nome"], "Conexão d'água")

    def test_negar_abertura_nao_cria_chamado(self):
        self.cliente()
        self.app(["cliente@exemplo.com", "Rede", "Descrição", "0", "0"]).abrir_chamado()
        self.assertFalse(self.provedor.dados["chamados"])

    def test_negar_cancelamento_preserva_registro(self):
        self.chamado()
        self.app(["cliente@exemplo.com", "1", "1", "0", "0"]).consultar()
        self.assertEqual(len(self.provedor.dados["chamados"]), 1)

    def test_cancelamento_confirmado_atualiza_lista(self):
        self.chamado()
        self.app(["cliente@exemplo.com", "1", "1", "1"]).consultar()
        self.assertFalse(self.provedor.dados["chamados"])
        self.assertIn("Chamado cancelado.", self.saida)

    def test_consulta_distingue_ausencias(self):
        self.app(["ausente@exemplo.com"]).consultar()
        self.assertIn("Cliente não encontrado.", self.saida)
        self.cliente()
        self.app(["cliente@exemplo.com"]).consultar()
        self.assertIn("Este cliente não possui chamados.", self.saida)
        self.provedor.executar("chamados", "criar_chamado", 1, "Rede", "Falha")
        self.provedor.executar("chamados", "assumir_proximo_chamado", 1)
        self.app(["cliente@exemplo.com"]).consultar()
        self.assertIn("Este cliente não possui chamados em aberto para esta listagem.", self.saida)

    def test_login_invalido_nao_abre_sessao(self):
        self.app(["atendente@exemplo.com"], ["senha-errada"]).login()
        self.assertIn("Email ou senha inválidos.", self.saida)
        self.assertFalse(any("senha-errada" in texto for texto in self.saida))

    def test_ciclo_atendente_com_senha_oculta_e_logout(self):
        self.chamado()
        self.app(["atendente@exemplo.com", "1", "3", "1", "1", "2", "1", "0", "0"],
                 ["demonstracao"]).login()
        chamado = self.provedor.dados["chamados"][1]
        self.assertEqual(chamado["status"], "resolvido")
        self.assertIsNotNone(chamado["data_fechamento"])
        self.assertIn("Você saiu da conta.", self.saida)
        self.assertFalse(any("demonstracao" in texto for texto in self.saida))

    def test_fila_vazia(self):
        self.app([]).assumir(1)
        self.assertIn("Nenhum chamado disponível na fila.", self.saida)

    def test_falha_do_banco_retorna_ao_menu(self):
        class Indisponivel:
            def executar(self, *args, **kwargs):
                raise ErroOperacao("Banco indisponível.")
        app = self.app(["2", "cliente@exemplo.com", "0"])
        app.provedor = Indisponivel()
        app.iniciar()
        self.assertEqual(self.saida.count("Banco indisponível."), 2)
        self.assertIn("Obrigado por utilizar o sistema. Até logo!", self.saida)

    def test_manutencao_atualiza_sem_alterar_chave(self):
        self.cliente()
        self.app(["1", "Novo nome", "novo@exemplo.com", "0012", "1"]).operacao_manutencao("clientes", 3)
        self.assertEqual(self.provedor.dados["clientes"][1]["nome"], "Novo nome")
        self.assertEqual(self.provedor.dados["clientes"][1]["id_cliente"], 1)

    def test_manutencao_bloqueia_exclusao_referenciada(self):
        self.chamado()
        app = self.app(["1", "1"])
        app.proteger(lambda: app.operacao_manutencao("clientes", 4))
        self.assertTrue(self.provedor.dados["clientes"])
        self.assertTrue(any("remoção foi bloqueada" in texto for texto in self.saida))

    def test_relatorios_preservam_sem_responsavel_e_sem_amostra(self):
        self.chamado()
        self.app([]).exibir_relatorio("detalhes")
        self.app([]).exibir_relatorio("tempo_medio")
        self.assertTrue(any("Ainda não atribuído" in texto for texto in self.saida))
        self.assertTrue(any("Sem amostra" in texto for texto in self.saida))

    def test_adaptador_nao_expoe_erro_interno(self):
        class Falha:
            def executar(self):
                raise RuntimeError("dados internos")
        provedor = ProvedorControladoras()
        provedor._instancias["clientes"] = Falha()
        with self.assertRaises(ErroOperacao) as erro:
            provedor.executar("clientes", "executar")
        self.assertNotIn("dados internos", str(erro.exception))

    def test_interrupcao_de_entrada_tem_despedida(self):
        def interromper(_):
            raise EOFError
        entrada = Entrada(interromper, self.saida.append)
        Aplicacao(self.provedor, entrada).iniciar()
        self.assertIn("\nEntrada interrompida. Até logo!", self.saida)


if __name__ == "__main__":
    unittest.main()
