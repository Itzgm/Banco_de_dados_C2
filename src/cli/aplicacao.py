from cli.entrada import Entrada, Voltar
from cli.provedor import ErroOperacao, campo
from utils.config import MENU_ATENDENTE, MENU_PRINCIPAL, MENU_RELATORIOS
from utils.splash_screen import SplashScreen


class Aplicacao:
    def __init__(self, provedor, entrada=None):
        self.provedor = provedor
        self.entrada = entrada or Entrada()
        self.mostrar = self.entrada.escrever

    def executar(self, area, operacao, *args, **kwargs):
        return self.provedor.executar(area, operacao, *args, **kwargs)

    def proteger(self, acao):
        try:
            acao()
        except Voltar:
            self.mostrar("Retornando ao menu anterior.")
        except ErroOperacao as erro:
            self.mostrar(str(erro))

    def iniciar(self, manutencao=False):
        try:
            totais = None
            try:
                totais = self.executar("relatorios", "totais")
            except ErroOperacao as erro:
                self.mostrar(str(erro))
            self.mostrar(SplashScreen().get_updated_screen(totais))
            if manutencao:
                self.manutencao()
                return
            acoes = {1: self.abrir_chamado, 2: self.consultar, 3: self.login}
            while True:
                opcao = self.entrada.opcao(MENU_PRINCIPAL, (0, 1, 2, 3))
                if opcao == 0:
                    self.mostrar("Obrigado por utilizar o sistema. Até logo!")
                    return
                self.proteger(acoes[opcao])
        except (EOFError, KeyboardInterrupt):
            self.mostrar("\nEntrada interrompida. Até logo!")

    def identificar_cliente(self):
        while True:
            email = self.entrada.texto("Email do cliente", "email")
            cliente = self.executar("clientes", "buscar_por_email", email)
            if cliente is not None:
                return cliente
            self.mostrar("Cliente não encontrado. Preencha o cadastro.")
            try:
                nome = self.entrada.texto("Nome")
                telefone = self.entrada.texto("Telefone", "telefone")
                self.mostrar(f"Nome: {nome} | Email: {email} | Telefone: {telefone}")
                if not self.entrada.confirmar("Confirmar cadastro?"):
                    continue
                return self.executar("clientes", "cadastrar_cliente", nome, email, telefone)
            except Voltar:
                self.mostrar("Informe novamente o email para buscar o cliente.")

    def abrir_chamado(self):
        while True:
            cliente = self.identificar_cliente()
            titulo = self.entrada.texto("Título")
            descricao = self.entrada.texto("Descrição")
            if self.entrada.confirmar("Confirmar abertura do chamado?"):
                chamado = self.executar(
                    "chamados", "criar_chamado", campo(cliente, "id_cliente"), titulo, descricao
                )
                self.mostrar(f"Chamado criado: {self.resumo(chamado)}")
            if not self.entrada.confirmar("Abrir outro chamado?"):
                return

    @staticmethod
    def resumo(chamado):
        return (
            f"#{campo(chamado, 'id_chamado')} - {campo(chamado, 'nome')} "
            f"({campo(chamado, 'status')})"
        )

    def detalhes(self, chamado):
        responsavel = campo(chamado, "id_atendente")
        if responsavel is None:
            responsavel = "Ainda não atribuído"
        self.mostrar(self.resumo(chamado))
        self.mostrar(f"Descrição: {campo(chamado, 'descricao')}")
        self.mostrar(f"Cliente: {campo(chamado, 'id_cliente')}")
        self.mostrar(f"Responsável: {responsavel}")
        self.mostrar(f"Abertura: {campo(chamado, 'data_abertura')}")
        self.mostrar(f"Fechamento: {campo(chamado, 'data_fechamento') or 'Não encerrado'}")

    def consultar(self):
        email = self.entrada.texto("Email do cliente", "email")
        cliente = self.executar("clientes", "buscar_por_email", email)
        if cliente is None:
            self.mostrar("Cliente não encontrado.")
            return
        id_cliente = campo(cliente, "id_cliente")
        while True:
            todos = self.executar(
                "chamados", "listar_chamados_cliente", id_cliente, apenas_ativos=False
            )
            if not todos:
                self.mostrar("Este cliente não possui chamados.")
                return
            abertos = [c for c in todos if campo(c, "status") == "aberto"]
            if not abertos:
                self.mostrar("Este cliente não possui chamados em aberto para esta listagem.")
                return
            escolhido = self.entrada.selecionar(abertos, self.resumo)
            if escolhido is None:
                return
            try:
                chamado = self.executar(
                    "chamados", "consultar_detalhes", campo(escolhido, "id_chamado")
                )
                if campo(chamado, "id_cliente") != id_cliente:
                    raise ErroOperacao("Chamado indisponível para este cliente.")
                self.detalhes(chamado)
                opcao = self.entrada.opcao("1 - Cancelar chamado\n2 - Voltar", (1, 2))
                if opcao == 1 and self.entrada.confirmar("Excluir definitivamente o chamado?"):
                    removido = self.executar(
                        "chamados", "cancelar_chamado", campo(chamado, "id_chamado"), id_cliente
                    )
                    self.mostrar("Chamado cancelado." if removido else "Chamado alterado; lista atualizada.")
            except ErroOperacao as erro:
                self.mostrar(f"{erro} Atualizando a lista.")

    def login(self):
        email = self.entrada.texto("Email do atendente", "email")
        senha = self.entrada.texto("Senha", "senha")
        atendente = self.executar("atendentes", "autenticar", email, senha)
        del senha
        if atendente is None:
            self.mostrar("Email ou senha inválidos.")
            return
        id_atendente = campo(atendente, "id_atendente")
        self.mostrar(f"Bem-vindo(a), {campo(atendente, 'nome')}.")
        while True:
            opcao = self.entrada.opcao(MENU_ATENDENTE, range(5))
            if opcao == 0:
                self.mostrar("Você saiu da conta.")
                return
            acoes = {
                1: lambda: self.assumir(id_atendente),
                2: lambda: self.listar_atendente(id_atendente, historico=True),
                3: lambda: self.listar_atendente(id_atendente),
                4: self.relatorios,
            }
            self.proteger(acoes[opcao])

    def assumir(self, id_atendente):
        chamado = self.executar("chamados", "assumir_proximo_chamado", id_atendente)
        if chamado is None:
            self.mostrar("Nenhum chamado disponível na fila.")
        else:
            self.mostrar("Chamado atribuído.")
            self.detalhes(chamado)

    def listar_atendente(self, id_atendente, historico=False):
        operacao = "listar_historico_atendente" if historico else "listar_meus_chamados"
        while True:
            chamados = self.executar("chamados", operacao, id_atendente)
            escolhido = self.entrada.selecionar(chamados, self.resumo)
            if escolhido is None:
                return
            chamado = self.executar(
                "chamados", "consultar_detalhes", campo(escolhido, "id_chamado")
            )
            if campo(chamado, "id_atendente") != id_atendente:
                raise ErroOperacao("Chamado indisponível para este atendente.")
            self.detalhes(chamado)
            if not historico and campo(chamado, "status") == "em andamento":
                if self.entrada.confirmar("Resolver este chamado?"):
                    resultado = self.executar(
                        "chamados", "resolver_chamado", campo(chamado, "id_chamado"), id_atendente
                    )
                    self.mostrar("Chamado resolvido.")
                    self.detalhes(resultado)

    def relatorios(self):
        while True:
            opcao = self.entrada.opcao(MENU_RELATORIOS, (0, 1, 2))
            if opcao == 0:
                return
            operacao = "tempo_medio" if opcao == 1 else "detalhes"
            self.proteger(lambda: self.exibir_relatorio(operacao))

    def exibir_relatorio(self, operacao):
        registros = self.executar("relatorios", operacao)
        if not registros:
            self.mostrar("Nenhum dado disponível para este relatório.")
        for registro in registros:
            self.mostrar(" | ".join(f"{chave}: {valor}" for chave, valor in registro.items()))

    def manutencao(self):
        self.mostrar("Manutenção local: alterações afetam os registros do sistema.")
        while True:
            entidade = self.entrada.opcao(
                "1 - Clientes\n2 - Atendentes\n3 - Chamados\n0 - Voltar", range(4)
            )
            if entidade == 0:
                return
            area = {1: "clientes", 2: "atendentes", 3: "chamados"}[entidade]
            self.proteger(lambda: self.manter_entidade(area))

    def manter_entidade(self, area):
        while True:
            opcao = self.entrada.opcao(
                "1 - Inserir\n2 - Listar\n3 - Atualizar\n4 - Remover\n0 - Voltar", range(5)
            )
            if opcao == 0:
                return
            self.proteger(lambda: self.operacao_manutencao(area, opcao))

    def operacao_manutencao(self, area, opcao):
        singular = {"clientes": "cliente", "atendentes": "atendente", "chamados": "chamado"}[area]
        chave = f"id_{singular}"
        if opcao == 1 and area == "chamados":
            self.abrir_chamado()
            return
        if opcao == 1:
            dados = self.dados_identidade(area)
            if self.entrada.confirmar("Confirmar inclusão?"):
                resultado = self.executar(area, f"cadastrar_{singular}", **dados)
                self.mostrar(f"Registro criado: #{campo(resultado, chave)} - {campo(resultado, 'nome')}")
            return
        registros = self.executar(area, "listar_todos")
        descrever = lambda item: f"#{campo(item, chave)} - {campo(item, 'nome')}"
        if opcao == 2:
            if not registros:
                self.mostrar("Nenhum registro encontrado.")
            for registro in registros:
                self.mostrar(descrever(registro))
            return
        registro = self.entrada.selecionar(registros, descrever)
        if registro is None:
            return
        identificador = campo(registro, chave)
        if opcao == 3:
            if area == "chamados":
                dados = {"titulo": self.entrada.texto("Novo título"),
                         "descricao": self.entrada.texto("Nova descrição")}
            else:
                dados = self.dados_identidade(area, atualizar=True)
            if self.entrada.confirmar("Confirmar atualização?"):
                resultado = self.executar(area, f"atualizar_{singular}", identificador, **dados)
                if area == "chamados":
                    self.detalhes(resultado)
                else:
                    for atributo in (chave, "nome", "email", "telefone"):
                        self.mostrar(f"{atributo}: {campo(resultado, atributo)}")
        elif self.entrada.confirmar("Excluir definitivamente este registro?"):
            operacao = "excluir_chamado_admin" if area == "chamados" else f"excluir_{singular}"
            if self.executar(area, operacao, identificador):
                self.mostrar("Registro removido.")
            else:
                self.mostrar("Registro não removido. Atualize a listagem.")

    def dados_identidade(self, area, atualizar=False):
        dados = {
            "nome": self.entrada.texto("Nome"),
            "email": self.entrada.texto("Email", "email"),
            "telefone": self.entrada.texto("Telefone", "telefone"),
        }
        if area == "atendentes" and not atualizar:
            dados["senha"] = self.entrada.texto("Senha inicial", "senha")
        return dados
