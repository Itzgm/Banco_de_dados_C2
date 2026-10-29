NOME_SISTEMA='Atendimento ao Cliente'
INTEGRANTES=['PREENCHER NOME 1','PREENCHER NOME 2','PREENCHER NOME 3','PREENCHER NOME 4']
PROFESSOR='Howard Roatti'
DISCIPLINA='Banco de Dados'
SEMESTRE='2026/2'
def mostrar(controllers):
    print('='*64); print(NOME_SISTEMA)
    print(f'{DISCIPLINA} | Professor: {PROFESSOR} | {SEMESTRE}')
    for nome in INTEGRANTES: print('Integrante: '+nome)
    for c in controllers.values(): print(f"{c.spec['titulo']}: {c.contar()} registro(s)")
    print('='*64)
