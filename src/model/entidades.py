from datetime import datetime
import re

def texto(valor, limite, rotulo):
    valor = str(valor).strip()
    if not valor or len(valor) > limite or any(ord(c) < 32 for c in valor):
        raise ValueError(f'{rotulo}: informe texto com até {limite} caracteres.')
    return valor

def id_positivo(valor):
    try: numero = int(valor)
    except (ValueError, TypeError): raise ValueError('O ID deve ser inteiro positivo.') from None
    if numero < 1 or numero > 2147483647:
        raise ValueError('O ID deve estar entre 1 e 2147483647.')
    return numero

class Cliente:
    def __init__(self, id, nome, email, telefone):
        self.id=id_positivo(id); self.nome=texto(nome,120,'Nome')
        self.email=texto(email,160,'E-mail').lower()
        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', self.email):
            raise ValueError('Informe um e-mail válido.')
        self.telefone=texto(telefone,25,'Telefone')
    def get_id(self): return self.id
    def set_id(self,v): self.id=id_positivo(v)
    def get_nome(self): return self.nome
    def set_nome(self,v): self.nome=texto(v,120,'Nome')
    def get_email(self): return self.email
    def set_email(self,v):
        value=texto(v,160,'E-mail').lower()
        dominio=value.split('@',1)
        if value.count('@')!=1 or '.' not in dominio[1]: raise ValueError('Informe um e-mail válido.')
        self.email=value
    def get_telefone(self): return self.telefone
    def set_telefone(self,v): self.telefone=texto(v,25,'Telefone')
    def dados(self): return {'id':self.id,'nome':self.nome,'email':self.email,'telefone':self.telefone}
    def to_string(self): return f'{self.id} | {self.nome} | {self.email} | {self.telefone}'

class Funcionario:
    def __init__(self,id,nome,equipe):
        self.id=id_positivo(id); self.nome=texto(nome,120,'Nome'); self.equipe=texto(equipe,80,'Equipe')
    def get_id(self): return self.id
    def set_id(self,v): self.id=id_positivo(v)
    def get_nome(self): return self.nome
    def set_nome(self,v): self.nome=texto(v,120,'Nome')
    def get_equipe(self): return self.equipe
    def set_equipe(self,v): self.equipe=texto(v,80,'Equipe')
    def dados(self): return {'id':self.id,'nome':self.nome,'equipe':self.equipe}
    def to_string(self): return f'{self.id} | {self.nome} | {self.equipe}'

class Atendimento:
    def __init__(self,id,cliente_id,funcionario_id,assunto,descricao,data_abertura,data_fechamento,status):
        self.id=id_positivo(id); self.cliente_id=id_positivo(cliente_id); self.funcionario_id=id_positivo(funcionario_id)
        self.assunto=texto(assunto,160,'Assunto'); self.descricao=texto(descricao,500,'Descrição')
        self.data_abertura=self._data(data_abertura,True); self.data_fechamento=self._data(data_fechamento,False)
        self.status=str(status).strip().upper()
        if self.status not in ('ABERTO','FECHADO'): raise ValueError('Status deve ser ABERTO ou FECHADO.')
        if self.status=='ABERTO' and self.data_fechamento is not None: raise ValueError('Atendimento aberto não pode ter fechamento.')
        if self.status=='FECHADO' and self.data_fechamento is None: raise ValueError('Atendimento fechado precisa de fechamento.')
        if self.data_fechamento and self.data_fechamento<self.data_abertura: raise ValueError('Fechamento anterior à abertura.')
    def get_id(self): return self.id
    def set_id(self,v): self.id=id_positivo(v)
    def get_cliente_id(self): return self.cliente_id
    def set_cliente_id(self,v): self.cliente_id=id_positivo(v)
    def get_funcionario_id(self): return self.funcionario_id
    def set_funcionario_id(self,v): self.funcionario_id=id_positivo(v)
    def get_assunto(self): return self.assunto
    def set_assunto(self,v): self.assunto=texto(v,160,'Assunto')
    def get_descricao(self): return self.descricao
    def set_descricao(self,v): self.descricao=texto(v,500,'Descrição')
    def get_data_abertura(self): return self.data_abertura
    def set_data_abertura(self,v): self.data_abertura=self._data(v,True)
    def get_data_fechamento(self): return self.data_fechamento
    def set_data_fechamento(self,v): self.data_fechamento=self._data(v,False)
    def get_status(self): return self.status
    def set_status(self,v):
        value=str(v).strip().upper()
        if value not in ('ABERTO','FECHADO'): raise ValueError('Status deve ser ABERTO ou FECHADO.')
        self.status=value
    @staticmethod
    def _data(valor,obrigatoria):
        if valor in (None,'') and not obrigatoria: return None
        if isinstance(valor,datetime): return valor
        try: return datetime.strptime(str(valor).strip(),'%Y-%m-%d %H:%M')
        except ValueError: raise ValueError('Use AAAA-MM-DD HH:MM.') from None
    def dados(self):
        return {'id':self.id,'cliente_id':self.cliente_id,'funcionario_id':self.funcionario_id,
        'assunto':self.assunto,'descricao':self.descricao,'data_abertura':self.data_abertura,
        'data_fechamento':self.data_fechamento,'status':self.status}
    def to_string(self):
        return f'{self.id} | Cliente {self.cliente_id} | Funcionário {self.funcionario_id} | {self.assunto} | {self.status}'
