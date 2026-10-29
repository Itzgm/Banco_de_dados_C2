import psycopg2
from psycopg2 import errors
from src.controller.crud import Crud, ENTIDADES
from src.model.entidades import id_positivo, texto
from src.reports.relatorios import mostrar
from src.utils import splash_screen

def ler_id(rotulo):
    while True:
        try: return id_positivo(input(rotulo+': '))
        except ValueError as e: print(e)
def sim(pergunta):
    while True:
        r=input(pergunta+' [s/n]: ').strip().lower()
        if r in ('s','sim'): return True
        if r in ('n','nao','não'): return False
        print('Responda s ou n.')
def listar(opcao,rows):
    if not rows: print('Nenhum registro encontrado.'); return
    campo=ENTIDADES[opcao]['descricao']
    for row in rows: print(f"{row['id']} | {row.get(campo,'')}")
def coletar(opcao,controllers,id=None):
    if id is None: id=ler_id('ID positivo, escolhido por você')
    if opcao=='1':
        return {'id':id,'nome':texto(input('Nome: '),120,'Nome'),
                'email':input('E-mail: ').strip(),'telefone':texto(input('Telefone: '),25,'Telefone')}
    if opcao=='2':
        return {'id':id,'nome':texto(input('Nome: '),120,'Nome'),
                'equipe':texto(input('Equipe: '),80,'Equipe')}
    print('Clientes:'); listar('1',controllers['1'].listar())
    cliente_id=ler_id('ID do cliente')
    print('Funcionários:'); listar('2',controllers['2'].listar())
    funcionario_id=ler_id('ID do funcionário')
    assunto=texto(input('Assunto: '),160,'Assunto')
    descricao=texto(input('Descrição: '),500,'Descrição')
    abertura=input('Abertura (AAAA-MM-DD HH:MM): ').strip()
    status=input('Status (ABERTO/FECHADO): ').strip().upper()
    fechamento=input('Fechamento (AAAA-MM-DD HH:MM; vazio se ABERTO): ').strip() or None
    return {'id':id,'cliente_id':cliente_id,'funcionario_id':funcionario_id,
            'assunto':assunto,'descricao':descricao,'data_abertura':abertura,
            'data_fechamento':fechamento,'status':status}
def tratar_erro(e):
    if isinstance(e,errors.UniqueViolation): print('ID ou e-mail já cadastrado.')
    elif isinstance(e,errors.ForeignKeyViolation):
        print('Exclusão bloqueada: há atendimentos vinculados. Remova-os primeiro, se apropriado.')
    elif isinstance(e,errors.CheckViolation): print('Dados não atendem às regras do sistema.')
    elif isinstance(e,psycopg2.Error): print('Erro no banco. Confira conexão e schema. SQLSTATE:',e.pgcode or 'conexão')
    else: print(e)
def operacao(acao,controllers):
    while True:
        print('Entidades: 1 Clientes | 2 Funcionários | 3 Atendimentos | 0 Voltar')
        opcao=input('Escolha: ').strip()
        if opcao=='0': return
        if opcao not in ENTIDADES: print('Opção inválida.'); continue
        ctrl=controllers[opcao]
        try:
            if acao=='inserir':
                ctrl.inserir(coletar(opcao,controllers)); print('Registro inserido.')
            else:
                rows=ctrl.listar(); listar(opcao,rows)
                if not rows: continue
                id=ler_id('ID do registro')
                if not ctrl.existe(id): print('Registro não encontrado.'); continue
                if acao=='excluir':
                    if not sim('Confirma a exclusão?'): continue
                    ctrl.excluir(id); print('Registro excluído.')
                else:
                    print('Informe todos os campos novamente; o ID será mantido.')
                    dados=coletar(opcao,controllers,id)
                    print('Registro atualizado:',ctrl.atualizar(id,dados))
        except (ValueError,psycopg2.Error) as e: tratar_erro(e)
        if not sim(f'Deseja {acao} outro registro?'): return
def menu_relatorios():
    while True:
        print('Relatórios: 1 Tempo médio por funcionário | 2 Atendimentos detalhados | 0 Voltar')
        opcao=input('Escolha: ').strip()
        if opcao=='0': return
        try: mostrar(opcao)
        except (ValueError,psycopg2.Error) as e: tratar_erro(e)
def main():
    controllers={k:Crud(k) for k in ENTIDADES}
    try: splash_screen.mostrar(controllers)
    except psycopg2.Error as e: tratar_erro(e); return 1
    while True:
        print('1 Relatórios | 2 Inserir | 3 Remover | 4 Atualizar | 5 Sair')
        op=input('Escolha: ').strip()
        if op=='1': menu_relatorios()
        elif op=='2': operacao('inserir',controllers)
        elif op=='3': operacao('excluir',controllers)
        elif op=='4': operacao('atualizar',controllers)
        elif op=='5': print('Sistema encerrado.'); return 0
        else: print('Opção inválida.')
if __name__=='__main__':
    try: raise SystemExit(main())
    except (KeyboardInterrupt,EOFError): print('Programa encerrado.')
