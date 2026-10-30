from datetime import datetime


class Atendimento:
    def __init__(self,
                 id_chamado: int = None,
                 id_cliente: int = None,
                 id_atendente: int = None,
                 nome: str = None,
                 descricao: str = None,
                 data_abertura: datetime = None,
                 data_fechamento: datetime = None,
                 status: str = "aberto"
                ):
        self.set_id_chamado(id_chamado)
        self.set_id_cliente(id_cliente)
        self.set_id_atendente(id_atendente)
        self.set_nome(nome)
        self.set_descricao(descricao)
        self.set_data_abertura(data_abertura)
        self.set_data_fechamento(data_fechamento)
        self.set_status(status)

    def set_id_chamado(self, id_chamado: int):
        self.id_chamado = id_chamado

    def set_id_cliente(self, id_cliente: int):
        self.id_cliente = id_cliente

    def set_id_atendente(self, id_atendente: int):
        self.id_atendente = id_atendente

    def set_nome(self, nome: str):
        self.nome = nome

    def set_titulo(self, titulo: str):
        self.nome = titulo

    def set_descricao(self, descricao: str):
        self.descricao = descricao

    def set_data_abertura(self, data_abertura: datetime):
        self.data_abertura = data_abertura

    def set_data_fechamento(self, data_fechamento: datetime):
        self.data_fechamento = data_fechamento

    def set_status(self, status: str):
        self.status = status

    def get_id_chamado(self) -> int:
        return self.id_chamado

    def get_id_cliente(self) -> int:
        return self.id_cliente

    def get_id_atendente(self) -> int:
        return self.id_atendente

    def get_nome(self) -> str:
        return self.nome

    def get_titulo(self) -> str:
        return self.nome

    def get_descricao(self) -> str:
        return self.descricao

    def get_data_abertura(self) -> datetime:
        return self.data_abertura

    def get_data_fechamento(self) -> datetime:
        return self.data_fechamento

    def get_status(self) -> str:
        return self.status

    def to_string(self) -> str:
        data_abert = self.get_data_abertura().strftime("%d/%m/%Y %H:%M") if self.get_data_abertura() else "N/D"
        data_fech = self.get_data_fechamento().strftime("%d/%m/%Y %H:%M") if self.get_data_fechamento() else "Em aberto"
        atendente = f"ID {self.get_id_atendente()}" if self.get_id_atendente() else "Não atribuído"

        return (
            f"Chamado: {self.get_id_chamado()} | "
            f"Título: {self.get_nome()} | "
            f"Status: {self.get_status()} | "
            f"Cliente: {self.get_id_cliente()} | "
            f"Atendente: {atendente} | "
            f"Abertura: {data_abert} | "
            f"Fechamento: {data_fech}"
        )
