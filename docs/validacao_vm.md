# Instalação e aceite manual na VM Linux

Status: procedimento preparado; execução na VM ainda não comprovada. Preencher os registros abaixo durante uma execução real por outro integrante.

## Preparação

1. Identificar o commit e a versão escolhida para entrega. Se o grupo apresentar esta cópia, trabalhar em `base_exemplo` e não na pasta `src` da raiz do repositório.
2. Conferir Python 3.10 ou superior, PostgreSQL disponível, acesso ao banco e possibilidade de instalar as dependências de `src/requirements.txt`. O teste local foi feito no PostgreSQL 18; outras versões precisam ser verificadas no ambiente efetivo.
3. Criar um banco vazio exclusivo e um usuário com permissão para conexão e criação de tabelas. Preparar o ambiente virtual e instalar dependências seguindo o README. Não usar um banco que contenha dados do grupo ou de terceiros para a instalação limpa.
4. Copiar `.env.example` para `.env` e ajustar host, porta, banco, usuário e senha. A lista `MANUTENCAO_EMAILS` deve conter o email da conta de demonstração autorizada. Não mostrar o conteúdo desse arquivo no vídeo.
5. Conferir se variáveis `DB_*` já exportadas no terminal apontam para outro ambiente: elas têm precedência sobre o `.env`. Corrigir o ambiente antes de conectar.
6. Executar o instalador uma vez, configurar a conta fictícia pelo script de demonstração e iniciar `src/principal.py` conforme o README. O script de demonstração redefine a senha da conta fictícia; utilizá-lo somente na base dedicada de exemplos.

## Validação da versão atual

Os testes automatizados foram removidos por solicitação do usuário. Executar o roteiro manual abaixo e registrar as evidências próprias da VM. Resultados automatizados antigos são históricos e não substituem essa execução.

## Aceite manual

| Verificação | Resultado esperado | Resultado real / evidência |
| --- | --- | --- |
| Inicialização | Nome do sistema, integrantes e totais reais das tabelas; menu continua após opção inválida. | A preencher |
| Cliente novo e correção de email | Voltar em nome/telefone refaz busca; cadastro incompleto não é gravado. | A preencher |
| Abertura | Cliente existente é reutilizado; chamado nasce aberto, sem responsável e sem fechamento. | A preencher |
| Consulta pública | Ausência de cliente e de chamados é informada; detalhes apresentam título, descrição, status e responsável. | A preencher |
| Cancelamento | Confirmação negativa mantém registro; positiva remove chamado elegível. | A preencher |
| Login | Email/senha inválidos não criam sessão; senha fica visível durante a digitação. | A preencher |
| Fila | Atribuição automática do mais antigo; não oferece seleção manual de chamado. | A preencher |
| Atendimento | Meus chamados permite detalhes e resolução; histórico exibe os resolvidos do próprio atendente. | A preencher |
| Relatórios | Detalhes e média em segundos coerentes com os dados; ausência de amostra indicada. | A preencher |
| Manutenção | CRUD das três entidades; exclusão com confirmação; referências impedem exclusão indevida. | A preencher |
| Autorização | Conta fora da lista e lista vazia não permitem manutenção. | A preencher |
| Retornos e saída | Voltar não grava formulário incompleto; logout retorna ao menu inicial; sair encerra. | A preencher |
| Diretório diferente | Entrada por caminho absoluto e relatórios funcionam fora da pasta do projeto. | A preencher |

Falhas de servidor durante operação devem ser testadas em ambiente dedicado e registradas separadamente; não parar serviços compartilhados da VM. As verificações anteriores de falha simulada estão descritas como histórico na matriz da etapa 7.

## Registro da execução

- Integrante executor e revisor: a preencher.
- Data, commit e pasta apresentada: a preencher.
- Distribuição Linux, versões de Python/PostgreSQL e dependências instaladas: a preencher.
- Comandos executados, cenários manuais aprovados e falhas encontradas: a preencher.
- Evidências dos cenários manuais e falhas encontradas: a preencher.
- Correções e nova validação necessária: a preencher.
- Aceite final do grupo: pendente.
