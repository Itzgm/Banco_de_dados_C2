from src.database import consultar, literal
from src.model.entidades import Cliente, Funcionario, Atendimento

ENTIDADES={
'1':{'titulo':'Clientes','tabela':'clientes','classe':Cliente,'colunas':'id,nome,email,telefone','descricao':'nome'},
'2':{'titulo':'Funcionários','tabela':'funcionarios','classe':Funcionario,'colunas':'id,nome,equipe','descricao':'nome'},
'3':{'titulo':'Atendimentos','tabela':'atendimentos','classe':Atendimento,'colunas':'id,cliente_id,funcionario_id,assunto,descricao,data_abertura,data_fechamento,status','descricao':'assunto'},
}

class Crud:
    def __init__(self,opcao): self.spec=ENTIDADES[opcao]
    def listar(self): return consultar(f"SELECT {self.spec['colunas']} FROM {self.spec['tabela']} ORDER BY id")
    def buscar(self,id):
        rows=consultar(f"SELECT {self.spec['colunas']} FROM {self.spec['tabela']} WHERE id={literal(id)}")
        return rows[0] if rows else None
    def existe(self,id): return self.buscar(id) is not None
    def contar(self): return consultar(f"SELECT count(1) AS total FROM {self.spec['tabela']}")[0]['total']
    def inserir(self,dados):
        obj=self.spec['classe'](**dados).dados(); cols=list(obj)
        values=', '.join(literal(obj[k]) for k in cols)
        consultar(f"INSERT INTO {self.spec['tabela']} ({', '.join(cols)}) VALUES ({values})")
    def atualizar(self,id,dados):
        dados=dict(dados); dados.pop('id',None)
        obj=self.spec['classe'](id=id,**dados).dados(); obj.pop('id')
        sets=', '.join(f'{k}={literal(v)}' for k,v in obj.items())
        rows=consultar(f"UPDATE {self.spec['tabela']} SET {sets} WHERE id={literal(id)} RETURNING {self.spec['colunas']}")
        if not rows: raise ValueError('Registro não encontrado.')
        return rows[0]
    def excluir(self,id):
        rows=consultar(f"DELETE FROM {self.spec['tabela']} WHERE id={literal(id)} RETURNING id")
        if not rows: raise ValueError('Registro não encontrado.')
