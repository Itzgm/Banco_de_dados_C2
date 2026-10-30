from copy import deepcopy
from datetime import datetime

from cli.provedor import ErroOperacao


class ProvedorDemonstracao:
    """Dados temporários para demonstrar as telas sem acessar o banco."""

    def __init__(self):
        self.dados = {"clientes": {}, "atendentes": {}, "chamados": {}}
        self.sequencias = {area: 0 for area in self.dados}
        self.senhas = {}
        self.cadastrar("atendentes", "Atendente de demonstração", "atendente@exemplo.com",
                       "0011999999999", "demonstracao")

    @staticmethod
    def chave(area):
        return {"clientes": "id_cliente", "atendentes": "id_atendente",
                "chamados": "id_chamado"}[area]

    def executar(self, area, operacao, *args, **kwargs):
        return deepcopy(self._executar(area, operacao, *args, **kwargs))

    def obter(self, area, identificador):
        if identificador not in self.dados[area]:
            raise ErroOperacao("Registro não encontrado.")
        return self.dados[area][identificador]

    def cadastrar(self, area, nome, email, telefone, senha=None):
        self.verificar_email(area, email)
        self.sequencias[area] += 1
        identificador = self.sequencias[area]
        registro = {self.chave(area): identificador, "nome": nome,
                    "email": email, "telefone": telefone}
        self.dados[area][identificador] = registro
        if area == "atendentes":
            self.senhas[identificador] = senha
        return registro

    def verificar_email(self, area, email, ignorar=None):
        if any(r["email"] == email and r[self.chave(area)] != ignorar
               for r in self.dados[area].values()):
            raise ErroOperacao("Email já cadastrado. Refaça a busca.")

    def _executar(self, area, operacao, *args, **kwargs):
        if area == "relatorios":
            return self.relatorio(operacao)
        registros = list(self.dados[area].values())
        if operacao == "listar_todos":
            return registros
        if operacao == "buscar_por_email":
            return next((r for r in registros if r["email"] == args[0]), None)
        if operacao == "autenticar":
            return next((r for r in registros if r["email"] == args[0]
                         and self.senhas[r["id_atendente"]] == args[1]), None)
        if operacao.startswith("cadastrar_"):
            return self.cadastrar(area, *args, **kwargs)
        if area == "chamados":
            return self.chamados(operacao, *args, **kwargs)
        registro = self.obter(area, args[0])
        if operacao.startswith("atualizar_"):
            self.verificar_email(area, kwargs["email"], args[0])
            registro.update(kwargs)
            return registro
        if operacao.startswith("excluir_"):
            chave = self.chave(area)
            if any(c[chave] == args[0] for c in self.dados["chamados"].values()):
                raise ErroOperacao("Registro vinculado a chamados; a remoção foi bloqueada.")
            del self.dados[area][args[0]]
            self.senhas.pop(args[0], None) if area == "atendentes" else None
            return True
        raise ErroOperacao("Operação não disponível na demonstração.")

    def chamados(self, operacao, *args, **kwargs):
        registros = list(self.dados["chamados"].values())
        if operacao == "criar_chamado":
            self.obter("clientes", args[0])
            self.sequencias["chamados"] += 1
            identificador = self.sequencias["chamados"]
            registro = {
                "id_chamado": identificador, "id_cliente": args[0], "id_atendente": None,
                "nome": args[1], "descricao": args[2], "status": "aberto",
                "data_abertura": datetime.now(), "data_fechamento": None,
            }
            self.dados["chamados"][identificador] = registro
            return registro
        if operacao == "listar_chamados_cliente":
            return [r for r in registros if r["id_cliente"] == args[0]
                    and (not kwargs.get("apenas_ativos", False) or r["status"] != "resolvido")]
        if operacao in ("listar_meus_chamados", "listar_historico_atendente"):
            status = "resolvido" if operacao == "listar_historico_atendente" else "em andamento"
            return [r for r in registros if r["id_atendente"] == args[0] and r["status"] == status]
        if operacao == "assumir_proximo_chamado":
            self.obter("atendentes", args[0])
            fila = sorted((r for r in registros if r["status"] == "aberto"
                           and r["id_atendente"] is None),
                          key=lambda r: (r["data_abertura"], r["id_chamado"]))
            if not fila:
                return None
            fila[0].update(id_atendente=args[0], status="em andamento")
            return fila[0]
        registro = self.obter("chamados", args[0])
        if operacao == "consultar_detalhes":
            return registro
        if operacao == "cancelar_chamado":
            if registro["id_cliente"] != args[1] or registro["status"] != "aberto":
                raise ErroOperacao("O chamado mudou de estado ou pertence a outro cliente.")
            del self.dados["chamados"][args[0]]
            return True
        if operacao == "resolver_chamado":
            if registro["id_atendente"] != args[1] or registro["status"] != "em andamento":
                raise ErroOperacao("Chamado indisponível para resolução.")
            registro.update(status="resolvido", data_fechamento=datetime.now())
            return registro
        if operacao == "atualizar_chamado":
            registro.update(nome=kwargs["titulo"], descricao=kwargs["descricao"])
            return registro
        if operacao == "excluir_chamado_admin":
            del self.dados["chamados"][args[0]]
            return True
        raise ErroOperacao("Operação não disponível na demonstração.")

    def relatorio(self, operacao):
        if operacao == "totais":
            return {area: len(registros) for area, registros in self.dados.items()}
        chamados = list(self.dados["chamados"].values())
        if operacao == "detalhes":
            return [dict(c, cliente=self.dados["clientes"][c["id_cliente"]]["nome"],
                         responsavel=self.dados["atendentes"].get(
                             c["id_atendente"], {"nome": "Ainda não atribuído"})["nome"])
                    for c in chamados]
        if operacao == "tempo_medio":
            resultado = []
            for atendente in self.dados["atendentes"].values():
                amostra = [c for c in chamados if c["status"] == "resolvido"
                           and c["id_atendente"] == atendente["id_atendente"]]
                duracoes = [(c["data_fechamento"] - c["data_abertura"]).total_seconds()
                            for c in amostra]
                resultado.append({"atendente": atendente["nome"], "resolvidos": len(amostra),
                                  "media_minutos": sum(duracoes) / len(duracoes) / 60
                                  if duracoes else "Sem amostra"})
            return resultado
        raise ErroOperacao("Relatório indisponível.")
