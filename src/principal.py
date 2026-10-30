import argparse
from pathlib import Path
from dotenv import load_dotenv
from utils import config
from utils.splash_screen import SplashScreen
from reports.relatorios import Relatorio
from controller.controller_cliente import Controller_Cliente
from controller.controller_atendente import Controller_Atendente
from controller.controller_atendimento import Controller_Atendimento


tela_inicial = SplashScreen()
ctrl_cliente = Controller_Cliente()
ctrl_atendente = Controller_Atendente()
ctrl_chamado = Controller_Atendimento()


def reports(opcao_relatorio: int = 0):
    relatorio = Relatorio()
    if opcao_relatorio == 1:
        return relatorio.get_relatorio_tempo_medio_por_atendente()
    elif opcao_relatorio == 2:
        return relatorio.get_relatorio_atendimentos_detalhados()
    elif opcao_relatorio == 3:
        return relatorio.get_relatorio_clientes()
    elif opcao_relatorio == 4:
        return relatorio.get_relatorio_atendentes()


def inserir(opcao_inserir: int = 0, operador=None):
    ctrl_atendente.exigir_manutencao(operador)
    if opcao_inserir == 1:
        return ctrl_cliente.inserir_cliente(operador=operador)
    elif opcao_inserir == 2:
        return ctrl_atendente.inserir_atendente(operador=operador)
    elif opcao_inserir == 3:
        return ctrl_chamado.inserir_chamado(operador)


def atualizar(opcao_atualizar: int = 0, operador=None):
    ctrl_atendente.exigir_manutencao(operador)
    if opcao_atualizar == 1:
        return ctrl_cliente.atualizar_cliente(operador=operador)
    elif opcao_atualizar == 2:
        return ctrl_atendente.atualizar_atendente(operador=operador)
    elif opcao_atualizar == 3:
        return ctrl_chamado.atualizar_registro(operador)


def excluir(opcao_excluir: int = 0, operador=None):
    ctrl_atendente.exigir_manutencao(operador)
    if opcao_excluir == 1:
        return ctrl_cliente.excluir_cliente(operador=operador)
    elif opcao_excluir == 2:
        return ctrl_atendente.excluir_atendente(operador=operador)
    elif opcao_excluir == 3:
        return ctrl_chamado.excluir_registro(operador)


def relatorios_menu():
    while True:
        print(config.MENU_RELATORIOS)
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            return
        if opcao not in ("1", "2", "3", "4"):
            print("Opção inválida.")
            continue
        try:
            reports(int(opcao))
        except (ValueError, LookupError, RuntimeError, PermissionError, ConnectionError) as erro:
            print(erro)


def manutencao(operador):
    ctrl_atendente.exigir_manutencao(operador)
    while True:
        ctrl_atendente.exigir_manutencao(operador)
        print(config.MENU_ENTIDADES)
        entidade = input("Entidade: ").strip()
        if entidade == "0":
            return
        if entidade not in ("1", "2", "3"):
            print("Opção inválida.")
            continue
        print(config.MENU_OPERACOES)
        operacao = input("Escolha: ").strip()
        if operacao == "0":
            continue
        if operacao not in ("1", "2", "3"):
            print("Opção inválida.")
            continue
        try:
            while True:
                if operacao == "1":
                    inserir(int(entidade), operador)
                elif operacao == "2":
                    atualizar(int(entidade), operador)
                elif operacao == "3":
                    excluir(int(entidade), operador)
                try:
                    ctrl_atendente.buscar_por_id(operador.get_id_atendente())
                except LookupError:
                    return
                if not config.confirmar("Realizar outra operação do mesmo tipo?"):
                    break
        except config.Voltar:
            pass
        except (ValueError, LookupError, RuntimeError, PermissionError, ConnectionError) as erro:
            print(erro)


def login():
    atendente = ctrl_atendente.autenticar()
    if atendente is None:
        print("Email ou senha inválidos.")
        return
    print("Bem-vindo(a),", atendente.get_nome())
    while True:
        try:
            atendente = ctrl_atendente.buscar_por_id(atendente.get_id_atendente())
        except LookupError:
            print("A conta não existe mais. Sessão encerrada.")
            return
        print(config.MENU_ATENDENTE)
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            return
        try:
            if opcao == "1":
                chamado = ctrl_chamado.assumir_proximo_chamado(atendente.get_id_atendente())
                if chamado is None:
                    print("Nenhum chamado disponível na fila.")
                else:
                    print("Chamado assumido:", chamado.to_string())
            elif opcao == "2":
                listar_atendente(atendente.get_id_atendente(), historico=True)
            elif opcao == "3":
                listar_atendente(atendente.get_id_atendente())
            elif opcao == "4":
                relatorios_menu()
            elif opcao == "5":
                manutencao(atendente)
            else:
                print("Opção inválida.")
        except config.Voltar:
            pass
        except (ValueError, LookupError, RuntimeError, PermissionError, ConnectionError) as erro:
            print(erro)


def campo(registro, nome, padrao=None):
    if isinstance(registro, dict):
        return registro.get(nome, padrao)
    getter = getattr(registro, f'get_{nome}', None)
    return getter() if callable(getter) else getattr(registro, nome, padrao)

def proteger(acao):
    try:
        acao()
    except config.Voltar:
        print("Retornando ao menu anterior.")
    except (ValueError, LookupError, RuntimeError, PermissionError, ConnectionError) as erro:
        print(erro)

def identificar_cliente():
    while True:
        email = config.campo('Email do cliente', ctrl_cliente.validar_email)
        cliente = ctrl_cliente.buscar_por_email(email)
        if cliente is not None:
            return cliente
        print('Cliente não encontrado. Preencha o cadastro.')
        try:
            nome = config.campo('Nome')
            telefone = config.campo('Telefone', ctrl_cliente.validar_telefone)
            print(f'Nome: {nome} | Email: {email} | Telefone: {telefone}')
            if not config.confirmar_opcao('Confirmar cadastro?'):
                continue
            return ctrl_cliente.inserir_cliente(nome, email, telefone)
        except config.Voltar:
            print('Informe novamente o email para buscar o cliente.')

def abrir_chamado():
    while True:
        cliente = identificar_cliente()
        titulo = config.campo('Título')
        descricao = config.campo('Descrição')
        if config.confirmar_opcao('Confirmar abertura do chamado?'):
            chamado = ctrl_chamado.criar_chamado(campo(cliente, 'id_cliente'), titulo, descricao)
            print(f'Chamado criado: {resumo(chamado)}')
        if not config.confirmar_opcao('Abrir outro chamado?'):
            return

def resumo(chamado):
    return f"#{campo(chamado, 'id_chamado')} - {campo(chamado, 'nome')} ({campo(chamado, 'status')})"

def detalhes(chamado):
    responsavel = campo(chamado, 'atendente')
    if responsavel is None:
        responsavel = 'Ainda não atribuído'
    else:
        responsavel = campo(responsavel, 'nome')
    print(resumo(chamado))
    print(f"Descrição: {campo(chamado, 'descricao')}")
    print(f"Cliente: {campo(chamado, 'id_cliente')}")
    print(f'Responsável: {responsavel}')
    print(f"Abertura: {campo(chamado, 'data_abertura')}")
    print(f"Fechamento: {campo(chamado, 'data_fechamento') or 'Não encerrado'}")

def consultar():
    email = config.campo('Email do cliente', ctrl_cliente.validar_email)
    cliente = ctrl_cliente.buscar_por_email(email)
    if cliente is None:
        print('Cliente não encontrado.')
        return
    id_cliente = campo(cliente, 'id_cliente')
    while True:
        todos = ctrl_chamado.listar_chamados_cliente(id_cliente, apenas_ativos=False)
        if not todos:
            print('Este cliente não possui chamados.')
            return
        abertos = [c for c in todos if campo(c, 'status') == 'aberto']
        if not abertos:
            print('Este cliente não possui chamados em aberto para esta listagem.')
            return
        escolhido = config.selecionar_registro(abertos, resumo)
        if escolhido is None:
            return
        try:
            chamado = ctrl_chamado.consultar_detalhes(campo(escolhido, 'id_chamado'))
            if campo(chamado, 'id_cliente') != id_cliente:
                raise RuntimeError('Chamado indisponível para este cliente.')
            detalhes(chamado)
            opcao = config.opcao('1 - Cancelar chamado\n2 - Voltar', (1, 2))
            if opcao == 1 and config.confirmar_opcao('Excluir definitivamente o chamado?'):
                removido = ctrl_chamado.cancelar_chamado(campo(chamado, 'id_chamado'), id_cliente)
                print('Chamado cancelado.' if removido else 'Chamado alterado; lista atualizada.')
        except RuntimeError as erro:
            print(f'{erro} Atualizando a lista.')

def assumir(id_atendente):
    chamado = ctrl_chamado.assumir_proximo_chamado(id_atendente)
    if chamado is None:
        print('Nenhum chamado disponível na fila.')
    else:
        print('Chamado atribuído.')
        detalhes(chamado)

def listar_atendente(id_atendente, historico=False):
    while True:
        chamados = ctrl_chamado.listar_historico_atendente(id_atendente) if historico else ctrl_chamado.listar_meus_chamados(id_atendente)
        escolhido = config.selecionar_registro(chamados, resumo)
        if escolhido is None:
            return
        chamado = ctrl_chamado.consultar_detalhes(campo(escolhido, 'id_chamado'))
        if campo(chamado, 'id_atendente') != id_atendente:
            raise RuntimeError('Chamado indisponível para este atendente.')
        detalhes(chamado)
        if not historico and campo(chamado, 'status') == 'em andamento':
            if config.confirmar_opcao('Resolver este chamado?'):
                resultado = ctrl_chamado.resolver_chamado(campo(chamado, 'id_chamado'), id_atendente)
                print('Chamado resolvido.')
                detalhes(resultado)


def run():
    try:
        print(tela_inicial.get_updated_screen())
    except (ValueError, LookupError, RuntimeError, PermissionError, ConnectionError) as erro:
        print(erro)
        return
    while True:
        print(config.MENU_PRINCIPAL)
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            print("Até logo!")
            return
        try:
            if opcao == "1":
                abrir_chamado()
            elif opcao == "2":
                consultar()
            elif opcao == "3":
                login()
            else:
                print("Opção inválida.")
        except config.Voltar:
            pass
        except (ValueError, LookupError, RuntimeError, PermissionError, ConnectionError) as erro:
            print(erro)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sistema de atendimento ao cliente")
    parser.add_argument("--env-file", type=Path, help="Arquivo local de configuração opcional")
    argumentos = parser.parse_args()
    if argumentos.env_file:
        if not argumentos.env_file.is_file():
            parser.error("Arquivo de configuração não encontrado.")
        load_dotenv(argumentos.env_file, override=True)
    try:
        run()
    except (EOFError, KeyboardInterrupt):
        print("\nAplicação encerrada.")
