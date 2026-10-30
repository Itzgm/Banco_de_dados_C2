MENU_PRINCIPAL = """Menu Principal
1 - Abrir chamado
2 - Consultar chamados
3 - Login do atendente
0 - Sair
"""


def exibir_acao(opcao):
    mensagens = {
        1: "A abertura de chamados ainda não está disponível.",
        2: "A consulta de chamados ainda não está disponível.",
        3: "O login do atendente ainda não está disponível.",
    }
    print(mensagens[opcao])


def run():
    while True:
        print(MENU_PRINCIPAL)
        try:
            opcao = int(input("Escolha uma opção [0-3]: "))
        except ValueError:
            print("Opção inválida. Tente novamente.")
            continue

        if opcao == 0:
            print("Obrigado por utilizar o sistema. Até logo!")
            break
        if opcao in (1, 2, 3):
            exibir_acao(opcao)
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    run()
