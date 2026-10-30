NOME_APLICACAO = "SISTEMA DE ATENDIMENTO AO CLIENTE"

MENU_PRINCIPAL = "1 - Abrir um novo chamado\n2 - Verificar meus chamados\n3 - Login\n0 - Sair"
MENU_ATENDENTE = "1 - Assumir um novo chamado\n2 - Verificar histórico\n3 - Meus chamados\n4 - Relatórios\n5 - Manutenção de cadastros (autorizados)\n0 - Sair da sessão"

MENU_RELATORIOS = "1 - Tempo médio por atendente\n2 - Detalhes dos chamados\n3 - Clientes\n4 - Atendentes\n0 - Voltar"
MENU_ENTIDADES = "1 - Clientes\n2 - Atendentes\n3 - Chamados\n0 - Voltar"
MENU_OPERACOES = "1 - Inserir\n2 - Atualizar\n3 - Excluir\n0 - Voltar"
MENU_CLIENTE_CHAMADO = "1 - Cancelar chamado\n2 - Voltar"
MENU_RESOLUCAO = "1 - Resolver chamado\n2 - Voltar"
QUERY_COUNT = "select count(1) as total_{tabela} from {tabela}"


class Voltar(Exception):
    pass


def campo(mensagem, validacao=None, senha=False):

    while True:
        valor = input(mensagem + " (0 para voltar): ")
        if not senha:
            valor = valor.strip()
        if valor in ("0", "/voltar"):
            raise Voltar()
        try:
            if validacao is not None:
                return validacao(valor)
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"{mensagem} é obrigatório.")
            return valor
        except ValueError as erro:
            print(erro)


def confirmar(mensagem):
    while True:
        resposta = input(mensagem + " [s/N]: ").strip().casefold()
        if resposta in ("", "n", "nao", "não"):
            return False
        if resposta in ("s", "sim"):
            return True
        print("Responda sim ou não.")


def selecionar(registros):
    if not registros:
        print("Nenhum registro encontrado.")
        raise Voltar()
    for posicao, registro in enumerate(registros, 1):
        if hasattr(registro, "get_id_chamado"):
            print(f"{posicao} - #{registro.get_id_chamado()} | {registro.get_nome()} | {registro.get_status()}")
        else:
            print(f"{posicao} - {registro.to_string()}")
    while True:
        escolha = campo("Escolha o número da lista")
        if escolha.isdigit() and 1 <= int(escolha) <= len(registros):
            return registros[int(escolha) - 1]
        print("Opção inválida.")


def escolher_atributo(campos):
    for opcao, atributo in campos.items():
        print(f"{opcao} - {atributo}")
    while True:
        escolha = campo("Atributo")
        if escolha in campos:
            atributo = campos[escolha]
            valor = campo("Novo valor", senha=atributo == "senha")
            return atributo, valor
        print("Atributo inválido.")


def opcao(menu, permitidas):
    while True:
        print(menu)
        try:
            valor = int(input("Escolha uma opção: "))
        except ValueError:
            valor = None
        if valor in permitidas:
            return valor
        print("Opção inválida. Tente novamente.")


def confirmar_opcao(mensagem):
    return opcao(f"{mensagem}\n1 - Sim\n0 - Não", (0, 1)) == 1


def selecionar_registro(registros, descrever):
    if not registros:
        print("Nenhum registro encontrado.")
        return None
    linhas = [f"{i} - {descrever(item)}" for i, item in enumerate(registros, 1)]
    escolha = opcao("\n".join(linhas + ["0 - Voltar"]), range(len(registros) + 1))
    if escolha == 0:
        return None
    return registros[escolha - 1]
