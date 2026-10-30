from datetime import datetime
from model.atendimentos import Atendimento
from conexion.postgres_queries import PostgresConnection


class Controller_Atendimento:
    def __init__(self, db: PostgresConnection = None):
        self.db = db

    def get_conexao(self, can_write: bool = True) -> PostgresConnection:
        if self.db is not None:
            self.db.can_write = can_write
            return self.db
        return PostgresConnection(can_write=can_write)

    # -------------------------------------------------------------
    # Fluxo do Cliente
    # -------------------------------------------------------------

    def criar_chamado(self, id_cliente: int, titulo: str, descricao: str) -> Atendimento:
        # Validação básica dos dados recebidos
        if not id_cliente or not titulo or not descricao:
            print("Dados incompletos para abertura do chamado.")
            return None

        postgres = self.get_conexao(can_write=True)
        postgres.connect()

        # Verifica se o cliente informado existe
        postgres.cur.execute("select id_cliente, nome from clientes where id_cliente = %s", (id_cliente,))
        cliente = postgres.cur.fetchone()
        if not cliente:
            print(f"Cliente {id_cliente} não encontrado no banco de dados.")
            return None

        # Insere o novo chamado com status aberto
        query = """
            insert into chamados (id_cliente, nome, descricao, status)
            values (%s, %s, %s, 'aberto')
            returning id_chamado, id_cliente, id_atendente, nome, descricao,
                      data_abertura, data_fechamento, status
        """
        postgres.cur.execute(query, (id_cliente, titulo.strip(), descricao.strip()))
        row = postgres.cur.fetchone()
        postgres.conn.commit()

        novo_chamado = Atendimento(
            id_chamado=row[0],
            id_cliente=row[1],
            id_atendente=row[2],
            nome=row[3],
            descricao=row[4],
            data_abertura=row[5],
            data_fechamento=row[6],
            status=row[7]
        )
        return novo_chamado

    def listar_chamados_cliente(self, id_cliente: int, apenas_ativos: bool = False) -> list:
        # Busca os chamados abertos pelo cliente
        postgres = self.get_conexao(can_write=False)
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
            chamados.append(Atendimento(
                id_chamado=r[0],
                id_cliente=r[1],
                id_atendente=r[2],
                nome=r[3],
                descricao=r[4],
                data_abertura=r[5],
                data_fechamento=r[6],
                status=r[7]
            ))
        return chamados

    def consultar_detalhes(self, id_chamado: int) -> Atendimento:
        # Busca os dados detalhados de um chamado específico
        postgres = self.get_conexao(can_write=False)
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

        return Atendimento(
            id_chamado=r[0],
            id_cliente=r[1],
            id_atendente=r[2],
            nome=r[3],
            descricao=r[4],
            data_abertura=r[5],
            data_fechamento=r[6],
            status=r[7]
        )

    def cancelar_chamado(self, id_chamado: int, id_cliente: int) -> bool:
        # Exclusão física do chamado a pedido do próprio cliente
        postgres = self.get_conexao(can_write=True)
        postgres.connect()

        # Verifica se o chamado existe e pertence a este cliente
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

        # Executa o delete no banco
        postgres.cur.execute(
            "delete from chamados where id_chamado = %s and id_cliente = %s and status = 'aberto'",
            (id_chamado, id_cliente)
        )
        postgres.conn.commit()
        return True

    # -------------------------------------------------------------
    # Fluxo do Atendente
    # -------------------------------------------------------------

    def assumir_proximo_chamado(self, id_atendente: int) -> Atendimento:
        # Pega o chamado aberto mais antigo da fila (FIFO) e atribui ao atendente
        postgres = self.get_conexao(can_write=True)
        postgres.connect()

        # Valida se o atendente existe
        postgres.cur.execute("select id_atendente, nome from atendentes where id_atendente = %s", (id_atendente,))
        atendente = postgres.cur.fetchone()
        if not atendente:
            print(f"Atendente {id_atendente} não encontrado.")
            return None

        # Atualiza o próximo da fila ordenando pela data de abertura
        query = """
            update chamados
            set id_atendente = %s, status = 'em andamento'
            where id_chamado = (
                select id_chamado
                from chamados
                where status = 'aberto' and id_atendente is null
                order by data_abertura asc, id_chamado asc
                limit 1
            )
            returning id_chamado, id_cliente, id_atendente, nome, descricao,
                      data_abertura, data_fechamento, status
        """
        postgres.cur.execute(query, (id_atendente,))
        row = postgres.cur.fetchone()
        if not row:
            # Fila vazia
            return None

        postgres.conn.commit()
        return Atendimento(
            id_chamado=row[0],
            id_cliente=row[1],
            id_atendente=row[2],
            nome=row[3],
            descricao=row[4],
            data_abertura=row[5],
            data_fechamento=row[6],
            status=row[7]
        )

    def listar_meus_chamados(self, id_atendente: int) -> list:
        # Lista os chamados que estão em andamento com o atendente logado
        postgres = self.get_conexao(can_write=False)
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
            chamados.append(Atendimento(
                id_chamado=r[0],
                id_cliente=r[1],
                id_atendente=r[2],
                nome=r[3],
                descricao=r[4],
                data_abertura=r[5],
                data_fechamento=r[6],
                status=r[7]
            ))
        return chamados

    def listar_historico_atendente(self, id_atendente: int) -> list:
        # Lista chamados resolvidos pelo atendente
        postgres = self.get_conexao(can_write=False)
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
            chamados.append(Atendimento(
                id_chamado=r[0],
                id_cliente=r[1],
                id_atendente=r[2],
                nome=r[3],
                descricao=r[4],
                data_abertura=r[5],
                data_fechamento=r[6],
                status=r[7]
            ))
        return chamados

    def resolver_chamado(self, id_chamado: int, id_atendente: int) -> Atendimento:
        # Move o status para resolvido e salva a data de fechamento
        postgres = self.get_conexao(can_write=True)
        postgres.connect()

        # Valida se o chamado está com esse atendente e em andamento
        postgres.cur.execute(
            "select id_chamado, id_atendente, status from chamados where id_chamado = %s",
            (id_chamado,)
        )
        chamado = postgres.cur.fetchone()
        if not chamado:
            print(f"Chamado {id_chamado} não encontrado.")
            return None

        if chamado[1] != id_atendente:
            print("Esse chamado pertence a outro atendente.")
            return None

        if chamado[2] != "em andamento":
            print(f"O chamado precisa estar em andamento para ser resolvido (status atual: {chamado[2]}).")
            return None

        query = """
            update chamados
            set status = 'resolvido', data_fechamento = current_timestamp
            where id_chamado = %s and id_atendente = %s
            returning id_chamado, id_cliente, id_atendente, nome, descricao,
                      data_abertura, data_fechamento, status
        """
        postgres.cur.execute(query, (id_chamado, id_atendente))
        row = postgres.cur.fetchone()
        postgres.conn.commit()

        return Atendimento(
            id_chamado=row[0],
            id_cliente=row[1],
            id_atendente=row[2],
            nome=row[3],
            descricao=row[4],
            data_abertura=row[5],
            data_fechamento=row[6],
            status=row[7]
        )

    # -------------------------------------------------------------
    # Manutenção de Chamados (CRUD para o Edital)
    # -------------------------------------------------------------

    def listar_todos(self) -> list:
        # Lista todos os chamados para exibição no menu de manutenção
        postgres = self.get_conexao(can_write=False)
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
            chamados.append(Atendimento(
                id_chamado=r[0],
                id_cliente=r[1],
                id_atendente=r[2],
                nome=r[3],
                descricao=r[4],
                data_abertura=r[5],
                data_fechamento=r[6],
                status=r[7]
            ))
        return chamados

    def atualizar_chamado(self, id_chamado: int, titulo: str, descricao: str) -> Atendimento:
        # Atualiza os dados descritivos sem mexer na chave primária
        if not id_chamado or not titulo or not descricao:
            print("Dados inválidos para atualização.")
            return None

        postgres = self.get_conexao(can_write=True)
        postgres.connect()

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

        postgres.conn.commit()
        return Atendimento(
            id_chamado=row[0],
            id_cliente=row[1],
            id_atendente=row[2],
            nome=row[3],
            descricao=row[4],
            data_abertura=row[5],
            data_fechamento=row[6],
            status=row[7]
        )

    def excluir_chamado_admin(self, id_chamado: int) -> bool:
        # Exclusão direta no menu administrativo
        postgres = self.get_conexao(can_write=True)
        postgres.connect()

        postgres.cur.execute("delete from chamados where id_chamado = %s", (id_chamado,))
        linhas_afetadas = postgres.cur.rowcount
        postgres.conn.commit()

        if linhas_afetadas == 0:
            print(f"Chamado {id_chamado} não encontrado para exclusão.")
            return False
        return True
