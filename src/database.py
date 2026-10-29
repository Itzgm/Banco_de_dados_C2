import os
from contextlib import closing
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import adapt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))

def literal(valor):
    """Gera literal SQL escapado pelo adaptador, sem ORM."""
    if valor is None:
        return 'NULL'
    return adapt(valor).getquoted().decode('utf-8')

def consultar(comando):
    cfg = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'dbname': os.getenv('DB_NAME', 'atendimento_cliente'),
        'user': os.getenv('DB_USER', 'atendimento_app'),
        'password': os.getenv('DB_PASSWORD', ''),
        'connect_timeout': 5,
    }
    with closing(psycopg2.connect(**cfg)) as conexao:
        with conexao:
            with conexao.cursor() as cursor:
                cursor.execute(comando)
                if cursor.description is None:
                    return []
                colunas = [c[0] for c in cursor.description]
                return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]

executar = consultar
