import os


class SplashScreen:
    def get_updated_screen(self, totais=None):
        integrantes = os.getenv("EQUIPE_NOMES", "Davi Tavares; demais integrantes a confirmar")
        linhas = [
            "SISTEMA DE CHAMADOS DE SUPORTE",
            f"Equipe: {integrantes}",
            "Professor: Howard Roatti | Disciplina: Banco de Dados | Semestre: 2026/2",
        ]
        if totais is not None:
            for entidade in ("clientes", "atendentes", "chamados"):
                linhas.append(f"Total de {entidade}: {totais[entidade]}")
        else:
            linhas.append("Contagens indisponíveis.")
        return "\n".join(linhas)
