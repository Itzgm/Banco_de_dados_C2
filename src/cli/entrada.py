import re
from getpass import getpass


class Voltar(Exception):
    pass


class Entrada:
    def __init__(self, ler=input, escrever=print, ler_senha=getpass):
        self.ler = ler
        self.escrever = escrever
        self.ler_senha = ler_senha

    def opcao(self, menu, permitidas):
        while True:
            self.escrever(menu)
            try:
                valor = int(self.ler("Escolha uma opção: "))
            except ValueError:
                valor = None
            if valor in permitidas:
                return valor
            self.escrever("Opção inválida. Tente novamente.")

    def texto(self, rotulo, tipo=None):
        while True:
            leitor = self.ler_senha if tipo == "senha" else self.ler
            valor = leitor(f"{rotulo} (/voltar para retornar): ").strip()
            if valor == "/voltar":
                raise Voltar
            if not valor:
                self.escrever("Preencha este campo.")
                continue
            if tipo == "email" and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
                self.escrever("Informe um email válido.")
                continue
            if tipo == "telefone" and not any(c.isdigit() for c in valor):
                self.escrever("Informe um telefone com dígitos.")
                continue
            return valor

    def confirmar(self, mensagem):
        return self.opcao(f"{mensagem}\n1 - Sim\n0 - Não", (0, 1)) == 1

    def selecionar(self, registros, descrever):
        if not registros:
            self.escrever("Nenhum registro encontrado.")
            return None
        linhas = [f"{i} - {descrever(item)}" for i, item in enumerate(registros, 1)]
        opcao = self.opcao("\n".join(linhas + ["0 - Voltar"]), range(len(registros) + 1))
        return registros[opcao - 1] if opcao else None
