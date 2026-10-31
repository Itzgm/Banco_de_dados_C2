import os
import re
from conexion.postgres_queries import PostgresQueries
from model.atendentes import Atendente
from utils import config


class Controller_Atendente:

    def __init__(self):
        self.colunas = "id_atendente, nome, email, telefone"

    def inserir_atendente(self, nome=None, email=None, telefone=None, senha=None, operador=None) -> Atendente:
        self.exigir_manutencao(operador)
        if nome is None:
            nome = config.campo("Nome")
            email = config.campo("Email", self.validar_email)
            telefone = config.campo("Telefone", self.validar_telefone)
            senha = config.campo("Senha", senha=True)
        nome = self.validar_texto(nome, "Nome")
        email = self.validar_email(email)
        telefone = self.validar_telefone(telefone)
        senha = self.validar_senha(senha)
        postgres = PostgresQueries(can_write=True)
        try:
            postgres.connect()
            if self.verifica_existencia_atendente(postgres, email=email):
                raise RuntimeError("O email já está cadastrado.")
            with postgres.transaction():
                query = "insert into atendentes (nome, email, telefone, senha) values (%s, %s, %s, %s) returning id_atendente"
                postgres.write(query, (nome, email, telefone, senha))
                id_atendente = int(postgres.cur.fetchone()[0])
                query = f"select {self.colunas} from atendentes where id_atendente = %s"
                df_atendente = postgres.sqlToDataFrame(query, (id_atendente,))
                novo_atendente = Atendente(int(df_atendente.id_atendente.values[0]), df_atendente.nome.values[0], df_atendente.email.values[0], df_atendente.telefone.values[0])
            print("Registro criado:", novo_atendente.to_string())
            return novo_atendente
        finally:
            postgres.close()

    def atualizar_atendente(self, id_atendente=None, operador=None, nome=None, email=None, telefone=None, senha=None) -> Atendente:
        self.exigir_manutencao(operador)
        if id_atendente is None:
            registro = config.selecionar(self.listar_atendentes(operador))
            id_atendente = registro.get_id_atendente()
            atributo, valor = config.escolher_atributo({"1": "nome", "2": "email", "3": "telefone", "4": "senha"})
            if atributo == "nome":
                nome = valor
            elif atributo == "email":
                email = valor
            elif atributo == "telefone":
                telefone = valor
            elif atributo == "senha":
                senha = valor
        id_atendente = self.validar_identificador(id_atendente)
        campos = {}
        if nome is not None:
            campos["nome"] = self.validar_texto(nome, "Nome")
        if telefone is not None:
            campos["telefone"] = self.validar_telefone(telefone)
        if email is not None:
            email = self.validar_email(email)
            existente = self.buscar_por_email(email)
            if existente is not None and existente.get_id_atendente() != id_atendente:
                raise RuntimeError("O email já está cadastrado.")
            campos["email"] = email
        if senha is not None:
            campos["senha"] = self.validar_senha(senha)
        if not campos:
            raise ValueError("Selecione um atributo para atualizar.")
        postgres = PostgresQueries(can_write=True)
        try:
            postgres.connect()
            if not self.verifica_existencia_atendente(postgres, id_atendente=id_atendente):
                raise LookupError("Atendente não encontrado.")
            atribuicoes = ", ".join(f"{campo} = %s" for campo in campos)
            parametros = tuple(campos.values()) + (id_atendente,)
            with postgres.transaction():
                query = f"update atendentes set {atribuicoes} where id_atendente = %s"
                if postgres.write(query, parametros) == 0:
                    raise LookupError("Atendente não encontrado.")
                query = f"select {self.colunas} from atendentes where id_atendente = %s"
                df_atendente = postgres.sqlToDataFrame(query, (id_atendente,))
                atendente_atualizado = Atendente(
                    int(df_atendente.id_atendente.values[0]),
                    df_atendente.nome.values[0],
                    df_atendente.email.values[0],
                    df_atendente.telefone.values[0]
                )
            print("Registro atualizado:", atendente_atualizado.to_string())
            return atendente_atualizado
        finally:
            postgres.close()

    def excluir_atendente(self, id_atendente=None, operador=None) -> Atendente | None:
        self.exigir_manutencao(operador)
        if id_atendente is None:
            registro = config.selecionar(self.listar_atendentes(operador))
            id_atendente = registro.get_id_atendente()
            if not config.confirmar("Confirma a exclusão do registro?"):
                return None
        id_atendente = self.validar_identificador(id_atendente)
        postgres = PostgresQueries(can_write=True)
        try:
            postgres.connect()
            if not self.verifica_existencia_atendente(postgres, id_atendente=id_atendente):
                raise LookupError("Atendente não encontrado.")
            with postgres.transaction():
                query = f"select {self.colunas} from atendentes where id_atendente = %s for update"
                df_atendente = postgres.sqlToDataFrame(query, (id_atendente,))
                if df_atendente.empty:
                    raise LookupError("Atendente não encontrado.")
                atendente_excluido = Atendente(int(df_atendente.id_atendente.values[0]), df_atendente.nome.values[0], df_atendente.email.values[0], df_atendente.telefone.values[0])
                postgres.write("delete from atendentes where id_atendente = %s", (id_atendente,))
            print("Registro excluído:", atendente_excluido.to_string())
            return atendente_excluido
        finally:
            postgres.close()

    def verifica_existencia_atendente(self, postgres: PostgresQueries, id_atendente: int = None, email: str = None) -> bool:
        if email is not None:
            query = "select id_atendente from atendentes where lower(email) = lower(%s)"
            parametros = (self.validar_email(email),)
        else:
            query = "select id_atendente from atendentes where id_atendente = %s"
            parametros = (self.validar_identificador(id_atendente),)
        df_atendente = postgres.sqlToDataFrame(query, parametros)
        return not df_atendente.empty

    def buscar_por_id(self, id_atendente: int) -> Atendente:
        postgres = PostgresQueries()
        try:
            postgres.connect()
            if not self.verifica_existencia_atendente(postgres, id_atendente=id_atendente):
                raise LookupError("Atendente não encontrado.")
            query = f"select {self.colunas} from atendentes where id_atendente = %s"
            df_atendente = postgres.sqlToDataFrame(query, (id_atendente,))
            if df_atendente.empty:
                raise LookupError("Atendente não encontrado.")
            return Atendente(int(df_atendente.id_atendente.values[0]), df_atendente.nome.values[0], df_atendente.email.values[0], df_atendente.telefone.values[0])
        finally:
            postgres.close()

    def buscar_por_email(self, email: str) -> Atendente | None:
        email = self.validar_email(email)
        postgres = PostgresQueries()
        try:
            postgres.connect()
            query = f"select {self.colunas} from atendentes where lower(email) = lower(%s)"
            df_atendente = postgres.sqlToDataFrame(query, (email,))
            if len(df_atendente) > 1:
                raise RuntimeError("Existem emails antigos ambíguos no cadastro de atendentes.")
            if df_atendente.empty:
                return None
            return Atendente(int(df_atendente.id_atendente.values[0]), df_atendente.nome.values[0], df_atendente.email.values[0], df_atendente.telefone.values[0])
        finally:
            postgres.close()

    def listar_atendentes(self, operador) -> list[Atendente]:
        self.exigir_manutencao(operador)
        postgres = PostgresQueries()
        try:
            postgres.connect()
            query = f"select {self.colunas} from atendentes order by id_atendente"
            df_atendentes = postgres.sqlToDataFrame(query)
            registros = []
            for _, linha in df_atendentes.iterrows():
                registros.append(Atendente(int(linha["id_atendente"]), linha["nome"], linha["email"], linha["telefone"]))
            return registros
        finally:
            postgres.close()

    def autenticar(self, email=None, senha=None) -> Atendente | None:
        if email is None:
            email = config.campo("Email do atendente", self.validar_email)
            senha = config.campo("Senha", senha=True)
        try:
            email = self.validar_email(email)
        except ValueError:
            return None
        postgres = PostgresQueries()
        try:
            postgres.connect()
            query = f"select {self.colunas}, senha from atendentes where lower(email) = lower(%s)"
            df_atendente = postgres.sqlToDataFrame(query, (email,))
            if len(df_atendente) > 1:
                raise RuntimeError("Existem emails antigos ambíguos no cadastro de atendentes.")
            if df_atendente.empty or not isinstance(senha, str) or not senha.strip() or senha != df_atendente.iloc[0]["senha"]:
                return None
            return Atendente(int(df_atendente.id_atendente.values[0]), df_atendente.nome.values[0], df_atendente.email.values[0], df_atendente.telefone.values[0])
        finally:
            postgres.close()

    def validar_texto(self, valor, campo: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"{campo} é obrigatório.")
        return valor.strip()

    def validar_email(self, email: str) -> str:
        email = self.validar_texto(email, "Email").casefold()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Informe um email válido.")
        return email

    def validar_telefone(self, telefone: str) -> str:
        telefone = self.validar_texto(telefone, "Telefone")
        if not re.fullmatch(r"[0-9+(). \-]+", telefone) or not any(c.isdigit() for c in telefone):
            raise ValueError("Telefone deve conter dígitos e apenas símbolos usuais de telefone.")
        return telefone

    def validar_identificador(self, identificador: int) -> int:
        if isinstance(identificador, bool) or not isinstance(identificador, int) or identificador <= 0:
            raise ValueError("O identificador deve ser um inteiro positivo.")
        return identificador

    def validar_senha(self, senha: str) -> str:
        if not isinstance(senha, str) or not senha.strip():
            raise ValueError("Senha é obrigatória.")
        return senha

    def pode_manter(self, operador: Atendente) -> bool:
        if operador is None:
            return False
        emails_permitidos = []
        for email in os.getenv("MANUTENCAO_EMAILS", "").split(","):
            if email.strip():
                emails_permitidos.append(email.strip().casefold())
        if not emails_permitidos:
            return False
        postgres = PostgresQueries()
        try:
            postgres.connect()
            query = "select email from atendentes where id_atendente = %s"
            df_atendente = postgres.sqlToDataFrame(query, (operador.get_id_atendente(),))
            if df_atendente.empty:
                return False
            email_atual = df_atendente.iloc[0]["email"].strip().casefold()
            return email_atual in emails_permitidos
        finally:
            postgres.close()

    def exigir_manutencao(self, operador: Atendente):
        if not self.pode_manter(operador):
            raise PermissionError("Este atendente não está autorizado a acessar a manutenção.")
