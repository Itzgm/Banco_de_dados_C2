from datetime import datetime
from model.atendimentos import Atendimento
from conexion.postgres_queries import PostgresConnection


class Controller_Atendimento:
    """
    Controladora responsável pelo gerenciamento de chamados, fila de atendimento
    FIFO, ciclo de vida e manutenção das entidades de atendimento.
    Atende aos contratos de integração estipulados em docs/contratos_chamados.md.
    """

    def __init__(self, db: PostgresConnection = None):
        self._db = db

    def _get_connection(self, can_write: bool = True) -> PostgresConnection:
        if self._db is not None:
            self._db.can_write = can_write
            return self._db
        return PostgresConnection(can_write=can_write)

    def _execute_mutation_returning(self, query: str, params=None) -> list[dict]:
        """Executa instrução de escrita com RETURNING e confirma a transação."""
        db = self._get_connection(can_write=True)
        should_close = (self._db is None)
        try:
            db.connect()
            db.cur.execute(query, params)
            rows = db.cur.fetchall()
            columns = [col[0].lower() for col in db.cur.description] if db.cur.description else []
            db.conn.commit()
            return [dict(zip(columns, row)) for row in rows]
        except Exception:
            if db.conn and not db.conn.closed:
                db.conn.rollback()
            raise
        finally:
            if should_close:
                db.close()

    def _execute_write(self, query: str, params=None) -> int:
        """Executa instrução de escrita (UPDATE/DELETE/INSERT) sem retorno de linhas."""
        db = self._get_connection(can_write=True)
        should_close = (self._db is None)
        try:
            db.connect()
            db.cur.execute(query, params)
            rowcount = db.cur.rowcount
            db.conn.commit()
            return rowcount
        except Exception:
            if db.conn and not db.conn.closed:
                db.conn.rollback()
            raise
        finally:
            if should_close:
                db.close()

    def _execute_query(self, query: str, params=None) -> list[dict]:
        """Executa consulta de leitura e retorna lista de dicionários."""
        db = self._get_connection(can_write=False)
        should_close = (self._db is None)
        try:
            db.connect()
            db.cur.execute(query, params)
            rows = db.cur.fetchall()
            columns = [col[0].lower() for col in db.cur.description] if db.cur.description else []
            return [dict(zip(columns, row)) for row in rows]
        finally:
            if should_close:
                db.close()

    def _row_to_atendimento(self, row: dict) -> Atendimento:
        """Converte um dicionário de resultado do banco em objeto Atendimento."""
        return Atendimento(
            id_chamado=row.get("id_chamado"),
            cliente=row.get("nome_cliente") or row.get("id_cliente"),
            atendente=row.get("nome_atendente") or row.get("id_atendente"),
            nome=row.get("nome"),
            descricao=row.get("descricao"),
            data_abertura=row.get("data_abertura"),
            data_fechamento=row.get("data_fechamento"),
            status=row.get("status")
        )

    # -------------------------------------------------------------------------
    # OPERAÇÕES DO CLIENTE (Abertura, Consulta e Cancelamento)
    # -------------------------------------------------------------------------

    def criar_chamado(self, id_cliente: int, titulo: str, descricao: str) -> Atendimento:
        """
        Cria um novo chamado para o cliente especificado.
        O chamado inicia com status 'aberto' e sem atendente associado.
        """
        if not id_cliente or not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError("ID do cliente inválido.")
        if not titulo or not titulo.strip():
            raise ValueError("O título do chamado não pode ser vazio.")
        if not descricao or not descricao.strip():
            raise ValueError("A descrição do chamado não pode ser vazia.")

        # Valida se o cliente existe
        check_cli = self._execute_query(
            "SELECT id_cliente, nome FROM clientes WHERE id_cliente = %s",
            (id_cliente,)
        )
        if not check_cli:
            raise LookupError(f"Cliente com ID {id_cliente} não encontrado.")

        query = """
            INSERT INTO chamados (id_cliente, nome, descricao, status)
            VALUES (%s, %s, %s, 'aberto')
            RETURNING id_chamado, id_cliente, id_atendente, nome, descricao,
                      data_abertura, data_fechamento, status;
        """
        rows = self._execute_mutation_returning(query, (id_cliente, titulo.strip(), descricao.strip()))
        if not rows:
            raise RuntimeError("Falha ao registrar chamado no banco de dados.")

        row = rows[0]
        row["nome_cliente"] = check_cli[0]["nome"]
        return self._row_to_atendimento(row)

    def listar_chamados_cliente(self, id_cliente: int, apenas_ativos: bool = False) -> list[Atendimento]:
        """
        Retorna todos os chamados abertos por determinado cliente.
        Se apenas_ativos=True, filtra por status 'aberto' e 'em andamento'.
        """
        if not id_cliente or not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError("ID do cliente inválido.")

        query = """
            SELECT c.id_chamado, c.id_cliente, c.id_atendente, c.nome, c.descricao,
                   c.data_abertura, c.data_fechamento, c.status,
                   cli.nome AS nome_cliente,
                   ate.nome AS nome_atendente
            FROM chamados c
            INNER JOIN clientes cli ON c.id_cliente = cli.id_cliente
            LEFT JOIN atendentes ate ON c.id_atendente = ate.id_atendente
            WHERE c.id_cliente = %s
        """
        params = [id_cliente]
        if apenas_ativos:
            query += " AND c.status IN ('aberto', 'em andamento')"

        query += " ORDER BY c.data_abertura DESC, c.id_chamado DESC"

        rows = self._execute_query(query, tuple(params))
        return [self._row_to_atendimento(r) for r in rows]

    def consultar_detalhes(self, id_chamado: int) -> Atendimento:
        """
        Recupera os detalhes completos de um chamado por ID.
        """
        if not id_chamado or not isinstance(id_chamado, int) or id_chamado <= 0:
            raise ValueError("ID do chamado inválido.")

        query = """
            SELECT c.id_chamado, c.id_cliente, c.id_atendente, c.nome, c.descricao,
                   c.data_abertura, c.data_fechamento, c.status,
                   cli.nome AS nome_cliente,
                   ate.nome AS nome_atendente
            FROM chamados c
            INNER JOIN clientes cli ON c.id_cliente = cli.id_cliente
            LEFT JOIN atendentes ate ON c.id_atendente = ate.id_atendente
            WHERE c.id_chamado = %s
        """
        rows = self._execute_query(query, (id_chamado,))
        if not rows:
            raise LookupError(f"Chamado #{id_chamado} não encontrado.")
        return self._row_to_atendimento(rows[0])

    def cancelar_chamado(self, id_chamado: int, id_cliente: int) -> bool:
        """
        Realiza a exclusão física (DELETE) de um chamado solicitado pelo próprio cliente.
        Regra: somente o titular pode cancelar e apenas enquanto status for 'aberto'.
        """
        if not id_chamado or not isinstance(id_chamado, int):
            raise ValueError("ID do chamado inválido.")
        if not id_cliente or not isinstance(id_cliente, int):
            raise ValueError("ID do cliente inválido.")

        # Verifica estado atual e titularidade
        rows = self._execute_query(
            "SELECT id_chamado, id_cliente, status FROM chamados WHERE id_chamado = %s",
            (id_chamado,)
        )
        if not rows:
            raise LookupError(f"Chamado #{id_chamado} não encontrado.")

        chamado = rows[0]
        if chamado["id_cliente"] != id_cliente:
            raise PermissionError("Permissão negada: o chamado pertence a outro cliente.")
        if chamado["status"] != "aberto":
            raise ValueError(
                f"O chamado #{id_chamado} não pode ser cancelado pois seu status atual é '{chamado['status']}'. "
                "Apenas chamados 'aberto' podem ser cancelados."
            )

        deleted = self._execute_write(
            "DELETE FROM chamados WHERE id_chamado = %s AND id_cliente = %s AND status = 'aberto'",
            (id_chamado, id_cliente)
        )
        return deleted > 0

    # -------------------------------------------------------------------------
    # OPERAÇÕES DO ATENDENTE (Fila FIFO, Meus Chamados, Histórico e Resolução)
    # -------------------------------------------------------------------------

    def assumir_proximo_chamado(self, id_atendente: int) -> Atendimento | None:
        """
        Atribui automaticamente o próximo chamado disponível na fila FIFO ao atendente.
        Ordem da fila: menor data_abertura (desempate: menor id_chamado).
        Garante atomicidade e prevenção de concorrência com FOR UPDATE SKIP LOCKED.
        Retorna o Atendimento atribuído ou None se a fila estiver vazia.
        """
        if not id_atendente or not isinstance(id_atendente, int) or id_atendente <= 0:
            raise ValueError("ID do atendente inválido.")

        # Valida existência do atendente
        check_ate = self._execute_query(
            "SELECT id_atendente, nome FROM atendentes WHERE id_atendente = %s",
            (id_atendente,)
        )
        if not check_ate:
            raise LookupError(f"Atendente com ID {id_atendente} não encontrado.")

        query = """
            UPDATE chamados
            SET id_atendente = %s, status = 'em andamento'
            WHERE id_chamado = (
                SELECT id_chamado
                FROM chamados
                WHERE status = 'aberto' AND id_atendente IS NULL
                ORDER BY data_abertura ASC, id_chamado ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id_chamado, id_cliente, id_atendente, nome, descricao,
                      data_abertura, data_fechamento, status;
        """
        rows = self._execute_mutation_returning(query, (id_atendente,))
        if not rows:
            return None

        row = rows[0]
        row["nome_atendente"] = check_ate[0]["nome"]
        return self._row_to_atendimento(row)

    def listar_meus_chamados(self, id_atendente: int) -> list[Atendimento]:
        """
        Lista todos os chamados com status 'em andamento' atribuídos ao atendente logado.
        """
        if not id_atendente or not isinstance(id_atendente, int) or id_atendente <= 0:
            raise ValueError("ID do atendente inválido.")

        query = """
            SELECT c.id_chamado, c.id_cliente, c.id_atendente, c.nome, c.descricao,
                   c.data_abertura, c.data_fechamento, c.status,
                   cli.nome AS nome_cliente,
                   ate.nome AS nome_atendente
            FROM chamados c
            INNER JOIN clientes cli ON c.id_cliente = cli.id_cliente
            INNER JOIN atendentes ate ON c.id_atendente = ate.id_atendente
            WHERE c.id_atendente = %s AND c.status = 'em andamento'
            ORDER BY c.data_abertura ASC, c.id_chamado ASC
        """
        rows = self._execute_query(query, (id_atendente,))
        return [self._row_to_atendimento(r) for r in rows]

    def listar_historico_atendente(self, id_atendente: int) -> list[Atendimento]:
        """
        Lista todos os chamados já resolvidos ('resolvido') pelo atendente informado.
        """
        if not id_atendente or not isinstance(id_atendente, int) or id_atendente <= 0:
            raise ValueError("ID do atendente inválido.")

        query = """
            SELECT c.id_chamado, c.id_cliente, c.id_atendente, c.nome, c.descricao,
                   c.data_abertura, c.data_fechamento, c.status,
                   cli.nome AS nome_cliente,
                   ate.nome AS nome_atendente
            FROM chamados c
            INNER JOIN clientes cli ON c.id_cliente = cli.id_cliente
            INNER JOIN atendentes ate ON c.id_atendente = ate.id_atendente
            WHERE c.id_atendente = %s AND c.status = 'resolvido'
            ORDER BY c.data_fechamento DESC, c.id_chamado DESC
        """
        rows = self._execute_query(query, (id_atendente,))
        return [self._row_to_atendimento(r) for r in rows]

    def resolver_chamado(self, id_chamado: int, id_atendente: int) -> Atendimento:
        """
        Finaliza um chamado movimentando o status para 'resolvido' e gravando data_fechamento.
        Regra: o chamado deve estar 'em andamento' e pertencer ao atendente informado.
        """
        if not id_chamado or not isinstance(id_chamado, int):
            raise ValueError("ID do chamado inválido.")
        if not id_atendente or not isinstance(id_atendente, int):
            raise ValueError("ID do atendente inválido.")

        rows = self._execute_query(
            "SELECT id_chamado, id_atendente, status FROM chamados WHERE id_chamado = %s",
            (id_chamado,)
        )
        if not rows:
            raise LookupError(f"Chamado #{id_chamado} não encontrado.")

        chamado = rows[0]
        if chamado["id_atendente"] != id_atendente:
            raise PermissionError("Permissão negada: o chamado está sob responsabilidade de outro atendente.")
        if chamado["status"] != "em andamento":
            raise ValueError(
                f"Apenas chamados 'em andamento' podem ser resolvidos. Status atual: '{chamado['status']}'."
            )

        query = """
            UPDATE chamados
            SET status = 'resolvido', data_fechamento = CURRENT_TIMESTAMP
            WHERE id_chamado = %s AND id_atendente = %s AND status = 'em andamento'
            RETURNING id_chamado, id_cliente, id_atendente, nome, descricao,
                      data_abertura, data_fechamento, status;
        """
        updated = self._execute_mutation_returning(query, (id_chamado, id_atendente))
        if not updated:
            raise RuntimeError(f"Não foi possível concluir a resolução do chamado #{id_chamado}.")
        return self._row_to_atendimento(updated[0])

    # -------------------------------------------------------------------------
    # OPERAÇÕES DE MANUTENÇÃO ACADÊMICA (CRUD Exigido pelo Edital)
    # -------------------------------------------------------------------------

    def listar_todos(self) -> list[Atendimento]:
        """Lista todos os chamados cadastrados para seleção prévia no menu de manutenção."""
        query = """
            SELECT c.id_chamado, c.id_cliente, c.id_atendente, c.nome, c.descricao,
                   c.data_abertura, c.data_fechamento, c.status,
                   cli.nome AS nome_cliente,
                   ate.nome AS nome_atendente
            FROM chamados c
            LEFT JOIN clientes cli ON c.id_cliente = cli.id_cliente
            LEFT JOIN atendentes ate ON c.id_atendente = ate.id_atendente
            ORDER BY c.id_chamado ASC
        """
        rows = self._execute_query(query)
        return [self._row_to_atendimento(r) for r in rows]

    def atualizar_chamado(self, id_chamado: int, titulo: str, descricao: str) -> Atendimento:
        """
        Atualização acadêmica de campos descritivos sem alterar chaves primárias.
        """
        if not id_chamado or not isinstance(id_chamado, int):
            raise ValueError("ID do chamado inválido.")
        if not titulo or not titulo.strip():
            raise ValueError("O título não pode ser vazio.")
        if not descricao or not descricao.strip():
            raise ValueError("A descrição não pode ser vazia.")

        query = """
            UPDATE chamados
            SET nome = %s, descricao = %s
            WHERE id_chamado = %s
            RETURNING id_chamado, id_cliente, id_atendente, nome, descricao,
                      data_abertura, data_fechamento, status;
        """
        rows = self._execute_mutation_returning(query, (titulo.strip(), descricao.strip(), id_chamado))
        if not rows:
            raise LookupError(f"Chamado #{id_chamado} não encontrado para atualização.")
        return self._row_to_atendimento(rows[0])

    def excluir_chamado_admin(self, id_chamado: int) -> bool:
        """Exclusão física direta para o menu de manutenção administrativa do edital."""
        if not id_chamado or not isinstance(id_chamado, int):
            raise ValueError("ID do chamado inválido.")

        rowcount = self._execute_write(
            "DELETE FROM chamados WHERE id_chamado = %s",
            (id_chamado,)
        )
        if rowcount == 0:
            raise LookupError(f"Chamado #{id_chamado} não encontrado para exclusão.")
        return True
