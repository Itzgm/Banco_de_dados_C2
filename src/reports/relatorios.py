from pathlib import Path
from src.database import consultar
BASE=Path(__file__).resolve().parents[1]/'sql'
RELATORIOS={'1':('Tempo médio por funcionário','relatorio_tempo_medio_por_funcionario.sql'),
'2':('Atendimentos detalhados','relatorio_atendimentos_detalhados.sql')}
def mostrar(opcao):
    if opcao not in RELATORIOS: raise ValueError('Relatório inválido.')
    rows=consultar((BASE/RELATORIOS[opcao][1]).read_text(encoding='utf-8'))
    print()
    print(RELATORIOS[opcao][0])
    if not rows: print('Nenhum registro encontrado.'); return
    cols=list(rows[0]); widths=[max(len(c),*(len(str(r[c])) for r in rows)) for c in cols]
    print(' | '.join(c.ljust(widths[i]) for i,c in enumerate(cols)))
    print('-'*(sum(widths)+3*(len(cols)-1)))
    for r in rows: print(' | '.join(str(r[c]).ljust(widths[i]) for i,c in enumerate(cols)))
