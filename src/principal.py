import argparse

from cli.aplicacao import Aplicacao
from cli.provedor import ProvedorControladoras


def run(provedor=None, entrada=None, manutencao=False):
    Aplicacao(provedor or ProvedorControladoras(), entrada).iniciar(manutencao)


def main():
    parser = argparse.ArgumentParser(description="Sistema de chamados de suporte")
    parser.add_argument("--demo", action="store_true", help="Usa dados temporários, sem PostgreSQL")
    parser.add_argument("--manutencao", action="store_true", help="Abre a manutenção local de entidades")
    argumentos = parser.parse_args()
    provedor = None
    if argumentos.demo:
        from cli.demonstracao import ProvedorDemonstracao

        print("DEMONSTRAÇÃO: dados temporários, apagados ao sair.")
        print("Login de exemplo: atendente@exemplo.com | senha: demonstracao")
        provedor = ProvedorDemonstracao()
    run(provedor, manutencao=argumentos.manutencao)


if __name__ == "__main__":
    main()
