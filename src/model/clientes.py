class Cliente:
    def __init__(self,id_cliente: int,nome: str ,email: str ,telefone: str,
    ):
        self.set_id_cliente(id_cliente)
        self.set_nome(nome)
        self.set_email(email)
        self.set_telefone(telefone)

    def set_id_cliente(self, id_cliente: int ):
        self.id_cliente = id_cliente

    def set_nome(self, nome: str):
        self.nome = nome

    def set_email(self, email: str ):
        self.email = email

    def set_telefone(self, telefone: str ):
        self.telefone = telefone

    def get_id_cliente(self) -> int :
        return self.id_cliente

    def get_nome(self) -> str :
        return self.nome

    def get_email(self) -> str :
        return self.email

    def get_telefone(self) -> str :
        return self.telefone

    def to_string(self) -> str:
        return (
            f"ID: {self.get_id_cliente()} | Nome: {self.get_nome()} | "
            f"Email: {self.get_email()} | Telefone: {self.get_telefone()}"
        )
