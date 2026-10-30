# Verificações da CLI

## Evidência executada em 29/10/2026

Comando: `python tests/test_cli.py -v`.
Ambiente: Windows, Python portátil 3.12.7. Resultado: 16 testes aprovados.
Não houve acesso a PostgreSQL ou execução na VM Linux.

Cenários automatizados: opções inválidas e vazias; correção do email sem cadastro
incompleto; reaproveitamento do cliente; acentos e apóstrofos; abertura negada;
cancelamento negado e confirmado; três ausências distintas na consulta; login
inválido; senha por leitor separado; assumir, resolver, histórico e logout;
fila vazia; falha do banco simulada; atualização sem troca de chave; bloqueio de
remoção referenciada; relatórios sem responsável e sem amostra; ocultação de erro
interno; EOF com despedida.

Os controles de referência, fila e datas nesses testes são simulados. Não comprovam
o comportamento das controladoras, SQL ou concorrência em PostgreSQL.

## Roteiro manual a executar pelo grupo

1. Iniciar `python src/principal.py --demo`; conferir identificação e totais.
2. Digitar texto, vazio, número negativo e opção fora do menu; confirmar repetição.
3. Abrir chamado com novo email; voltar durante nome e telefone; corrigir email.
   Negar cadastro e confirmar depois; conferir que há um único cadastro.
4. Abrir chamado para o mesmo email, com acentos e apóstrofo; conferir id e título.
5. Consultar email inexistente, cliente sem chamados e cliente apenas com resolvidos.
6. Cancelar com resposta negativa; depois confirmar; verificar atualização da lista.
7. Testar login inválido; login válido com senha invisível; fila vazia e com registros.
8. Assumir chamado; consultar meus chamados; negar e depois confirmar resolução;
   abrir histórico e sair da conta; conferir retorno ao menu principal.
9. Abrir ambos os relatórios, com e sem amostras; conferir rótulo em minutos.
10. Reiniciar com `--demo --manutencao`; inserir, listar, atualizar e remover cada
    entidade; negar exclusão; tentar remover cliente/atendente referenciado.
11. Usar caminho absoluto a partir de outra pasta; verificar inicialização sem Oracle.
12. Repetir tudo sem `--demo`, após integrar os contratos, em PostgreSQL e VM Linux.
13. Em banco isolado, testar duas sessões assumindo a fila, disputa de cancelamento,
    resolução por outro atendente, falha de conexão, duplicidade e rollback.

Registrar aqui ambiente, data, resultado e responsável por cada execução real.
Não marcar teste manual ou de banco como aprovado com base no modo de demonstração.
