import psycopg2
from datetime import datetime
from model.atendimentos import Atendimento
from conexion.postgres_queries import PostgresQueries
from controller.controller_cliente import Controller_Cliente
from controller.controller_atendente import Controller_Atendente
from utils import config


class Controller_Atendimento:
    def __init__(self, db: PostgresQueries = None):
        self.db = db
        self.ctrl_cliente = Controller_Cliente()
        self.ctrl_atendente = Controller_Atendente()

    def get_conexao(self, can_write: bool = True) -> PostgresQueries:
        if self.db is not None:
            self.db.can_write = can_write
            return self.db
        return PostgresQueries(can_write=can_write)


    def criar_chamado(self, id_cliente: int, titulo: str, descricao: str) -> Atendimento:
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0 or not isinstance(titulo, str) or not titulo.strip() or not isinstance(descricao, str) or not descricao.strip():
            raise ValueError("Cliente, título e descrição são obrigatórios.")

        postgres = self.get_conexao(can_write=True)
        try:
            postgres.connect()
            with postgres.transaction():

                postgres.cur.execute("select id_cliente, nome from clientes where id_cliente = %s", (id_cliente,))
                cliente = postgres.cur.fetchone()
                if not cliente:
                    raise LookupError("Cliente não encontrado.")

                query = """
                    insert into chamados (id_cliente, nome, descricao, status)
                    values (%s, %s, %s, 'aberto')
                    returning id_chamado, id_cliente, id_atendente, nome, descricao,
                              data_abertura, data_fechamento, status
                """
                postgres.cur.execute(query, (id_cliente, titulo.strip(), descricao.strip()))
                row = postgres.cur.fetchone()

                novo_chamado = self._com_associacoes(Atendimento(
                    id_chamado=row[0],
                    id_cliente=row[1],
                    id_atendente=row[2],
                    nome=row[3],
                    descricao=row[4],
                    data_abertura=row[5],
                    data_fechamento=row[6],
                    status=row[7]
                ))
                return novo_chamado
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()

    def listar_chamados_cliente(self, id_cliente: int, apenas_ativos: bool = False) -> list:
        postgres = self.get_conexao(can_write=False)
        try:
            postgres.connect()

            query = """
                select id_chamado, id_cliente, id_atendente, nome, descricao,
                       data_abertura, data_fechamento, status
                from chamados
                where id_cliente = %s
            """
            if apenas_ativos:
                query += " and status in ('aberto', 'em andamento')"

            query += " order by data_abertura desc, id_chamado desc"

            postgres.cur.execute(query, (id_cliente,))
            rows = postgres.cur.fetchall()

            chamados = []
            for r in rows:
                chamados.append(self._com_associacoes(Atendimento(
                    id_chamado=r[0],
                    id_cliente=r[1],
                    id_atendente=r[2],
                    nome=r[3],
                    descricao=r[4],
                    data_abertura=r[5],
                    data_fechamento=r[6],
                    status=r[7]
                )))
            return chamados
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()

    def consultar_detalhes(self, id_chamado: int) -> Atendimento:
        postgres = self.get_conexao(can_write=False)
        try:
            postgres.connect()

            query = """
                select id_chamado, id_cliente, id_atendente, nome, descricao,
                       data_abertura, data_fechamento, status
                from chamados
                where id_chamado = %s
            """
            postgres.cur.execute(query, (id_chamado,))
            r = postgres.cur.fetchone()
            if not r:
                return None

            return self._com_associacoes(Atendimento(
                id_chamado=r[0],
                id_cliente=r[1],
                id_atendente=r[2],
                nome=r[3],
                descricao=r[4],
                data_abertura=r[5],
                data_fechamento=r[6],
                status=r[7]
            ))
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()

    def cancelar_chamado(self, id_chamado: int, id_cliente: int) -> bool:
        postgres = self.get_conexao(can_write=True)
        try:
            postgres.connect()
            with postgres.transaction():

                postgres.cur.execute(
                    "select id_chamado, id_cliente, status from chamados where id_chamado = %s",
                    (id_chamado,)
                )
                chamado = postgres.cur.fetchone()
                if not chamado:
                    print(f"Chamado {id_chamado} não encontrado.")
                    return False

                if chamado[1] != id_cliente:
                    print("Você só pode cancelar chamados que foram abertos por você.")
                    return False

                if chamado[2] != "aberto":
                    print(f"O chamado não pode ser cancelado pois já está com status '{chamado[2]}'.")
                    return False

                postgres.cur.execute(
                    "delete from chamados where id_chamado = %s and id_cliente = %s and status = 'aberto' and id_atendente is null",
                    (id_chamado, id_cliente)
                )
                return postgres.cur.rowcount > 0
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()


    def assumir_proximo_chamado(self, id_atendente: int) -> Atendimento:
        postgres = self.get_conexao(can_write=True)
        try:
            postgres.connect()
            with postgres.transaction():

                postgres.cur.execute("select id_atendente, nome from atendentes where id_atendente = %s", (id_atendente,))
                atendente = postgres.cur.fetchone()
                if not atendente:
                    print(f"Atendente {id_atendente} não encontrado.")
                    return None

                query = """
                    update chamados
                    set id_atendente = %s, status = 'em andamento'
                    where id_chamado = (
                        select id_chamado
                        from chamados
                        where status = 'aberto' and id_atendente is null
                        order by data_abertura asc nulls last, id_chamado asc
                        limit 1 for update skip locked
                    )
                    returning id_chamado, id_cliente, id_atendente, nome, descricao,
                              data_abertura, data_fechamento, status
                """
                postgres.cur.execute(query, (id_atendente,))
                row = postgres.cur.fetchone()
                if not row:
                    return None

                return self._com_associacoes(Atendimento(
                    id_chamado=row[0],
                    id_cliente=row[1],
                    id_atendente=row[2],
                    nome=row[3],
                    descricao=row[4],
                    data_abertura=row[5],
                    data_fechamento=row[6],
                    status=row[7]
                ))
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()

    def listar_meus_chamados(self, id_atendente: int) -> list:
        postgres = self.get_conexao(can_write=False)
        try:
            postgres.connect()

            query = """
                select id_chamado, id_cliente, id_atendente, nome, descricao,
                       data_abertura, data_fechamento, status
                from chamados
                where id_atendente = %s and status = 'em andamento'
                order by data_abertura asc
            """
            postgres.cur.execute(query, (id_atendente,))
            rows = postgres.cur.fetchall()

            chamados = []
            for r in rows:
                chamados.append(self._com_associacoes(Atendimento(
                    id_chamado=r[0],
                    id_cliente=r[1],
                    id_atendente=r[2],
                    nome=r[3],
                    descricao=r[4],
                    data_abertura=r[5],
                    data_fechamento=r[6],
                    status=r[7]
                )))
            return chamados
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()

    def listar_historico_atendente(self, id_atendente: int) -> list:
        postgres = self.get_conexao(can_write=False)
        try:
            postgres.connect()

            query = """
                select id_chamado, id_cliente, id_atendente, nome, descricao,
                       data_abertura, data_fechamento, status
                from chamados
                where id_atendente = %s and status = 'resolvido'
                order by data_fechamento desc
            """
            postgres.cur.execute(query, (id_atendente,))
            rows = postgres.cur.fetchall()

            chamados = []
            for r in rows:
                chamados.append(self._com_associacoes(Atendimento(
                    id_chamado=r[0],
                    id_cliente=r[1],
                    id_atendente=r[2],
                    nome=r[3],
                    descricao=r[4],
                    data_abertura=r[5],
                    data_fechamento=r[6],
                    status=r[7]
                )))
            return chamados
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()

    def resolver_chamado(self, id_chamado: int, id_atendente: int) -> Atendimento:
        postgres = self.get_conexao(can_write=True)
        try:
            postgres.connect()
            with postgres.transaction():

                postgres.cur.execute(
                    "select id_chamado, id_atendente, status from chamados where id_chamado = %s",
                    (id_chamado,)
                )
                chamado = postgres.cur.fetchone()
                if not chamado:
                    raise LookupError("Chamado não encontrado.")

                if chamado[1] != id_atendente:
                    raise PermissionError("Esse chamado pertence a outro atendente.")

                if chamado[2] != "em andamento":
                    raise RuntimeError("O chamado precisa estar em andamento para ser resolvido.")

                query = """
                    update chamados
                    set status = 'resolvido', data_fechamento = current_timestamp
                    where id_chamado = %s and id_atendente = %s and status = 'em andamento'
                    returning id_chamado, id_cliente, id_atendente, nome, descricao,
                              data_abertura, data_fechamento, status
                """
                postgres.cur.execute(query, (id_chamado, id_atendente))
                row = postgres.cur.fetchone()
                if row is None:
                    raise RuntimeError("Chamado alterado por outra sessão. Atualize a lista.")
                return self._com_associacoes(Atendimento(
                    id_chamado=row[0],
                    id_cliente=row[1],
                    id_atendente=row[2],
                    nome=row[3],
                    descricao=row[4],
                    data_abertura=row[5],
                    data_fechamento=row[6],
                    status=row[7]
                ))
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()


    def listar_todos(self, operador=None) -> list:
        self.ctrl_atendente.exigir_manutencao(operador)
        postgres = self.get_conexao(can_write=False)
        try:
            postgres.connect()

            query = """
                select id_chamado, id_cliente, id_atendente, nome, descricao,
                       data_abertura, data_fechamento, status
                from chamados
                order by id_chamado asc
            """
            postgres.cur.execute(query)
            rows = postgres.cur.fetchall()

            chamados = []
            for r in rows:
                chamados.append(self._com_associacoes(Atendimento(
                    id_chamado=r[0],
                    id_cliente=r[1],
                    id_atendente=r[2],
                    nome=r[3],
                    descricao=r[4],
                    data_abertura=r[5],
                    data_fechamento=r[6],
                    status=r[7]
                )))
            return chamados
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()

    def atualizar_chamado(self, id_chamado: int, titulo: str, descricao: str, operador=None) -> Atendimento:
        self.ctrl_atendente.exigir_manutencao(operador)
        if not isinstance(id_chamado, int) or isinstance(id_chamado, bool) or id_chamado <= 0 or not isinstance(titulo, str) or not titulo.strip() or not isinstance(descricao, str) or not descricao.strip():
            print("Dados inválidos para atualização.")
            return None

        postgres = self.get_conexao(can_write=True)
        try:
            postgres.connect()
            with postgres.transaction():

                query = """
                    update chamados
                    set nome = %s, descricao = %s
                    where id_chamado = %s
                    returning id_chamado, id_cliente, id_atendente, nome, descricao,
                              data_abertura, data_fechamento, status
                """
                postgres.cur.execute(query, (titulo.strip(), descricao.strip(), id_chamado))
                row = postgres.cur.fetchone()
                if not row:
                    print(f"Chamado {id_chamado} não encontrado.")
                    return None

                return self._com_associacoes(Atendimento(
                    id_chamado=row[0],
                    id_cliente=row[1],
                    id_atendente=row[2],
                    nome=row[3],
                    descricao=row[4],
                    data_abertura=row[5],
                    data_fechamento=row[6],
                    status=row[7]
                ))
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()

    def excluir_chamado_admin(self, id_chamado: int, operador=None) -> bool:
        self.ctrl_atendente.exigir_manutencao(operador)
        postgres = self.get_conexao(can_write=True)
        try:
            postgres.connect()
            with postgres.transaction():

                postgres.cur.execute("delete from chamados where id_chamado = %s", (id_chamado,))
                linhas_afetadas = postgres.cur.rowcount

                if linhas_afetadas == 0:
                    print(f"Chamado {id_chamado} não encontrado para exclusão.")
                    return False
                return True
        except psycopg2.Error as erro:
            postgres._informar_erro(erro)
        finally:
            if self.db is None:
                postgres.close()

    def _com_associacoes(self, atendimento):
        atendimento.set_cliente(self.ctrl_cliente.buscar_por_id(atendimento.get_id_cliente()))
        if atendimento.get_id_atendente() is not None:
            atendimento.set_atendente(self.ctrl_atendente.buscar_por_id(atendimento.get_id_atendente()))
        return atendimento

    def inserir_chamado(self, operador):
        self.ctrl_atendente.exigir_manutencao(operador)
        cliente = config.selecionar(self.ctrl_cliente.listar_clientes(operador))
        titulo = config.campo("Título")
        descricao = config.campo("Descrição")
        chamado = self.criar_chamado(cliente.get_id_cliente(), titulo, descricao)
        if chamado is None:
            raise RuntimeError("Não foi possível abrir o chamado.")
        print("Registro criado:", chamado.to_string())
        return chamado

    def atualizar_registro(self, operador):
        self.ctrl_atendente.exigir_manutencao(operador)
        item = config.selecionar(self.listar_todos(operador))
        atributo, valor = config.escolher_atributo({"1": "titulo", "2": "descricao"})
        titulo = valor if atributo == "titulo" else item.get_nome()
        descricao = valor if atributo == "descricao" else item.get_descricao()
        chamado = self.atualizar_chamado(item.get_id_chamado(), titulo, descricao, operador)
        if chamado is None:
            raise RuntimeError("O chamado foi alterado ou removido.")
        print("Registro atualizado:", chamado.to_string())
        return chamado

    def excluir_registro(self, operador):
        self.ctrl_atendente.exigir_manutencao(operador)
        item = config.selecionar(self.listar_todos(operador))
        if not config.confirmar("Confirma a exclusão do registro?"):
            return None
        if not self.excluir_chamado_admin(item.get_id_chamado(), operador):
            raise LookupError("Chamado não encontrado.")
        print("Registro excluído:", item.to_string())
        return item
