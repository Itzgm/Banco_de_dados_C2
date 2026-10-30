from importlib import import_module


class ErroOperacao(Exception):
    """Falha que pode ser apresentada no terminal."""


def campo(registro, nome, padrao=None):
    if isinstance(registro, dict):
        return registro.get(nome, padrao)
    getter = getattr(registro, f"get_{nome}", None)
    return getter() if callable(getter) else getattr(registro, nome, padrao)


class ProvedorControladoras:
    MODULOS = {
        "clientes": ("controller.controller_cliente", "Controller_Cliente"),
        "atendentes": ("controller.controller_funcionario", "Controller_Funcionario"),
        "chamados": ("controller.controller_atendimento", "Controller_Atendimento"),
        "relatorios": ("reports.relatorios", "Relatorio"),
    }

    def __init__(self):
        self._instancias = {}

    def executar(self, area, operacao, *args, **kwargs):
        try:
            if area not in self._instancias:
                modulo, classe = self.MODULOS[area]
                construtor = getattr(import_module(modulo), classe, None)
                if construtor is None:
                    raise ErroOperacao("Módulo ainda não integrado. Consulte o checklist de entrega.")
                self._instancias[area] = construtor()
            metodo = getattr(self._instancias[area], operacao, None)
            if not callable(metodo):
                raise ErroOperacao("Operação ainda não integrada. Consulte o checklist de entrega.")
            return metodo(*args, **kwargs)
        except ErroOperacao:
            raise
        except ModuleNotFoundError as erro:
            raise ErroOperacao("Dependência ou módulo indisponível. Confira a instalação.") from erro
        except (ValueError, LookupError, PermissionError) as erro:
            raise ErroOperacao(str(erro)) from erro
        except Exception as erro:
            raise ErroOperacao(
                "Não foi possível concluir a operação. Confira o banco e tente novamente."
            ) from erro
