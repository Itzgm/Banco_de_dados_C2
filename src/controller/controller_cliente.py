from conexion.postgres_queries import PostgresQueries
from model.clientes import Cliente
from controller.controller_atendente import Controller_Atendente
from utils import config, validacoes_identidade as validar



class Controller_Cliente:

    def __init__(self):
        self.ctrl_atendente = Controller_Atendente()
        self.colunas = "id_cliente, nome, email, telefone"

    def inserir_cliente(self, nome=None, email=None, telefone=None, operador=None) -> Cliente:
        if nome is None or operador is not None:
            self.ctrl_atendente.exigir_manutencao(operador)
        if nome is None:
            nome = config.campo("Nome")
            email = config.campo("Email", self.validar_email)
            telefone = config.campo("Telefone", self.validar_telefone)

        nome = self.validar_texto(nome, "Nome")
        email = self.validar_email(email)
        telefone = self.validar_telefone(telefone)

        postgres = PostgresQueries(can_write=True)
        try:
            postgres.connect()
            if self.verifica_existencia_cliente(postgres, email=email):
                raise RuntimeError("O email já está cadastrado.")
            with postgres.transaction():
                query = "insert into clientes (nome, email, telefone) values (%s, %s, %s) returning id_cliente"
                postgres.write(query, (nome, email, telefone,))
                id_cliente = int(postgres.cur.fetchone()[0])
                query = f"select {self.colunas} from clientes where id_cliente = %s"
                df_cliente = postgres.sqlToDataFrame(query, (id_cliente,))
                novo_cliente = Cliente(int(df_cliente.id_cliente.values[0]), df_cliente.nome.values[0], df_cliente.email.values[0], df_cliente.telefone.values[0])
            print("Registro criado:", novo_cliente.to_string())
            return novo_cliente
        finally:
            postgres.close()

    def atualizar_cliente(self, id_cliente=None, operador=None, nome=None, email=None, telefone=None) -> Cliente:
        self.ctrl_atendente.exigir_manutencao(operador)
        if id_cliente is None:
            registro = config.selecionar(self.listar_clientes(operador))
            id_cliente = registro.get_id_cliente()
            atributo, valor = config.escolher_atributo({"1": "nome", "2": "email", "3": "telefone"})
            if atributo == "nome":
                nome = valor
            elif atributo == "email":
                email = valor
            elif atributo == "telefone":
                telefone = valor

        id_cliente = self.validar_identificador(id_cliente)
        campos = {}
        if nome is not None:
            campos["nome"] = self.validar_texto(nome, "Nome")
        if telefone is not None:
            campos["telefone"] = self.validar_telefone(telefone)
        if email is not None:
            email = self.validar_email(email)
            existente = self.buscar_por_email(email)
            if existente is not None and existente.get_id_cliente() != id_cliente:
                raise RuntimeError("O email já está cadastrado.")
            campos["email"] = email

        if not campos:
            raise ValueError("Selecione um atributo para atualizar.")
        postgres = PostgresQueries(can_write=True)
        try:
            postgres.connect()
            if not self.verifica_existencia_cliente(postgres, id_cliente=id_cliente):
                raise LookupError("Cliente não encontrado.")
            atribuicoes = ", ".join(f"{campo} = %s" for campo in campos)
            parametros = tuple(campos.values()) + (id_cliente,)
            with postgres.transaction():
                query = f"update clientes set {atribuicoes} where id_cliente = %s"
                if postgres.write(query, parametros) == 0:
                    raise LookupError("Cliente não encontrado.")
                query = f"select {self.colunas} from clientes where id_cliente = %s"
                df_cliente = postgres.sqlToDataFrame(query, (id_cliente,))
                cliente_atualizado = Cliente(
                    int(df_cliente.id_cliente.values[0]),
                    df_cliente.nome.values[0],
                    df_cliente.email.values[0],
                    df_cliente.telefone.values[0]
                )
            print("Registro atualizado:", cliente_atualizado.to_string())
            return cliente_atualizado
        finally:
            postgres.close()

    def excluir_cliente(self, id_cliente=None, operador=None) -> Cliente | None:
        self.ctrl_atendente.exigir_manutencao(operador)
        if id_cliente is None:
            registro = config.selecionar(self.listar_clientes(operador))
            id_cliente = registro.get_id_cliente()
            if not config.confirmar("Confirma a exclusão do registro?"):
                return None
        id_cliente = self.validar_identificador(id_cliente)
        postgres = PostgresQueries(can_write=True)
        try:
            postgres.connect()
            if not self.verifica_existencia_cliente(postgres, id_cliente=id_cliente):
                raise LookupError("Cliente não encontrado.")
            with postgres.transaction():
                query = f"select {self.colunas} from clientes where id_cliente = %s for update"
                df_cliente = postgres.sqlToDataFrame(query, (id_cliente,))
                if df_cliente.empty:
                    raise LookupError("Cliente não encontrado.")
                cliente_excluido = Cliente(int(df_cliente.id_cliente.values[0]), df_cliente.nome.values[0], df_cliente.email.values[0], df_cliente.telefone.values[0])
                postgres.write("delete from clientes where id_cliente = %s", (id_cliente,))
            print("Registro excluído:", cliente_excluido.to_string())
            return cliente_excluido
        finally:
            postgres.close()

    def verifica_existencia_cliente(self, postgres: PostgresQueries, id_cliente: int = None, email: str = None) -> bool:
        if email is not None:
            query = "select id_cliente from clientes where lower(email) = lower(%s)"
            parametros = (self.validar_email(email),)
        else:
            query = "select id_cliente from clientes where id_cliente = %s"
            parametros = (self.validar_identificador(id_cliente),)
        df_cliente = postgres.sqlToDataFrame(query, parametros)
        return not df_cliente.empty

    def buscar_por_id(self, id_cliente: int) -> Cliente:
        postgres = PostgresQueries()
        try:
            postgres.connect()
            if not self.verifica_existencia_cliente(postgres, id_cliente=id_cliente):
                raise LookupError("Cliente não encontrado.")
            query = f"select {self.colunas} from clientes where id_cliente = %s"
            df_cliente = postgres.sqlToDataFrame(query, (id_cliente,))
            if df_cliente.empty:
                raise LookupError("Cliente não encontrado.")
            return Cliente(int(df_cliente.id_cliente.values[0]), df_cliente.nome.values[0], df_cliente.email.values[0], df_cliente.telefone.values[0])
        finally:
            postgres.close()

    def buscar_por_email(self, email: str) -> Cliente | None:
        email = self.validar_email(email)
        postgres = PostgresQueries()
        try:
            postgres.connect()
            query = f"select {self.colunas} from clientes where lower(email) = lower(%s)"
            df_cliente = postgres.sqlToDataFrame(query, (email,))
            if len(df_cliente) > 1:
                raise RuntimeError("Existem emails antigos ambíguos no cadastro de clientes.")
            if df_cliente.empty:
                return None
            return Cliente(int(df_cliente.id_cliente.values[0]), df_cliente.nome.values[0], df_cliente.email.values[0], df_cliente.telefone.values[0])
        finally:
            postgres.close()

    def listar_clientes(self, operador) -> list[Cliente]:
        self.ctrl_atendente.exigir_manutencao(operador)
        postgres = PostgresQueries()
        try:
            postgres.connect()
            query = f"select {self.colunas} from clientes order by id_cliente"
            df_clientes = postgres.sqlToDataFrame(query)
            registros = []
            for _, linha in df_clientes.iterrows():
                registros.append(Cliente(int(linha["id_cliente"]), linha["nome"], linha["email"], linha["telefone"]))
            return registros
        finally:
            postgres.close()

    def validar_texto(self, valor, campo: str) -> str:
        return validar.texto(valor, campo)

    def validar_email(self, email: str) -> str:
        return validar.email(email)

    def validar_telefone(self, telefone: str) -> str:
        return validar.telefone(telefone)

    def validar_identificador(self, identificador: int) -> int:
        return validar.identificador(identificador)
