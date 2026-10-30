from datetime import datetime


class Atendimento:
    """
    Representa a entidade de domínio Chamado / Atendimento do sistema.
    Mapeada para a tabela 'chamados' do banco PostgreSQL.
    """
    STATUS_VALIDOS = ("aberto", "em andamento", "resolvido")

    def __init__(self,
                 id_chamado: int = None,
                 cliente = None,
                 atendente = None,
                 nome: str = None,
                 descricao: str = None,
                 data_abertura: datetime = None,
                 data_fechamento: datetime = None,
                 status: str = "aberto"
                 ):
        self.set_id_chamado(id_chamado)
        self.set_cliente(cliente)
        self.set_atendente(atendente)
        self.set_nome(nome)
        self.set_descricao(descricao)
        self.set_data_abertura(data_abertura)
        self.set_data_fechamento(data_fechamento)
        self.set_status(status)

    def set_id_chamado(self, id_chamado: int):
        self.id_chamado = id_chamado

    def set_cliente(self, cliente):
        self.cliente = cliente

    def set_atendente(self, atendente):
        self.atendente = atendente

    def set_nome(self, nome: str):
        self.nome = nome

    def set_titulo(self, titulo: str):
        """Alias semântico: no banco a coluna é chamada 'nome'."""
        self.set_nome(titulo)

    def set_descricao(self, descricao: str):
        self.descricao = descricao

    def set_data_abertura(self, data_abertura: datetime):
        self.data_abertura = data_abertura

    def set_data_fechamento(self, data_fechamento: datetime):
        self.data_fechamento = data_fechamento

    def set_status(self, status: str):
        if status is not None and status not in self.STATUS_VALIDOS:
            raise ValueError(
                f"Status inválido: '{status}'. Valores permitidos: {self.STATUS_VALIDOS}"
            )
        self.status = status

    def get_id_chamado(self) -> int:
        return self.id_chamado

    def get_cliente(self):
        return self.cliente

    def get_id_cliente(self) -> int:
        if self.cliente is None:
            return None
        if hasattr(self.cliente, "get_id_cliente"):
            return self.cliente.get_id_cliente()
        if hasattr(self.cliente, "id_cliente"):
            return self.cliente.id_cliente
        return self.cliente

    def get_atendente(self):
        return self.atendente

    def get_id_atendente(self) -> int:
        if self.atendente is None:
            return None
        if hasattr(self.atendente, "get_id_atendente"):
            return self.atendente.get_id_atendente()
        if hasattr(self.atendente, "id_atendente"):
            return self.atendente.id_atendente
        return self.atendente

    def get_nome(self) -> str:
        return self.nome

    def get_titulo(self) -> str:
        """Alias semântico para obter o título do chamado."""
        return self.get_nome()

    def get_descricao(self) -> str:
        return self.descricao

    def get_data_abertura(self) -> datetime:
        return self.data_abertura

    def get_data_fechamento(self) -> datetime:
        return self.data_fechamento

    def get_status(self) -> str:
        return self.status

    def to_string(self) -> str:
        # Formatação do cliente (seja objeto com get_nome ou apenas ID numérico)
        if hasattr(self.cliente, "get_nome"):
            cliente_str = f"{self.cliente.get_nome()} (ID: {self.get_id_cliente()})"
        elif self.get_id_cliente() is not None:
            cliente_str = f"Cliente ID: {self.get_id_cliente()}"
        else:
            cliente_str = "Não informado"

        # Formatação do atendente responsável
        if self.atendente is None:
            atendente_str = "Ainda não atribuído"
        elif hasattr(self.atendente, "get_nome"):
            atendente_str = f"{self.atendente.get_nome()} (ID: {self.get_id_atendente()})"
        elif self.get_id_atendente() is not None:
            atendente_str = f"Atendente ID: {self.get_id_atendente()}"
        else:
            atendente_str = "Ainda não atribuído"

        # Formatação de datas
        dt_abertura = (
            self.get_data_abertura().strftime("%d/%m/%Y %H:%M")
            if hasattr(self.get_data_abertura(), "strftime") and self.get_data_abertura()
            else str(self.get_data_abertura() or "N/D")
        )
        dt_fechamento = (
            self.get_data_fechamento().strftime("%d/%m/%Y %H:%M")
            if hasattr(self.get_data_fechamento(), "strftime") and self.get_data_fechamento()
            else ("Em aberto" if not self.get_data_fechamento() else str(self.get_data_fechamento()))
        )

        status_display = (self.get_status() or "DESCONHECIDO").upper()

        return (
            f"Chamado #{self.get_id_chamado()} | Título: {self.get_titulo()} | Status: {status_display}\n"
            f"  Cliente: {cliente_str}\n"
            f"  Responsável: {atendente_str}\n"
            f"  Abertura: {dt_abertura} | Fechamento: {dt_fechamento}\n"
            f"  Descrição: {self.get_descricao()}"
        )
