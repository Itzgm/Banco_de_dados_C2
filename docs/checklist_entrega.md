# Checklist de entrega — parte da CLI

Responsável: Davi Tavares. Branch: `davi/desenvolvimento`.

## Implementado nesta branch

- [x] Menu principal com loop, opções 1/2/3/0 e tratamento de entrada inválida.
- [x] Telas de abertura, cadastro confirmado, correção de email e repetição.
- [x] Consulta, seleção, detalhes e confirmação de cancelamento com atualização da lista.
- [x] Login com senha oculta, sessão local por identidade e logout.
- [x] Telas de fila automática, meus chamados, resolução confirmada e histórico.
- [x] Menus de relatórios e manutenção das três entidades com retornos previsíveis.
- [x] Splash atualizado com configuração dos nomes e consumo de contagens.
- [x] Remoção das dependências ativas de vendas/Oracle do ponto de entrada.
- [x] Adaptador de controladoras e contratos publicados em `contratos_cli.md`.
- [x] Demonstração isolada, explicitamente temporária e sem banco.
- [x] 16 testes de CLI executados e aprovados no Windows com Python 3.12.7.
- [x] README, requisitos, roteiro manual e roteiro do vídeo escritos.

## Dependências de integração — não concluídas nesta entrega

- [ ] Pessoa 2: identidade PostgreSQL e métodos públicos do contrato; senha segura.
- [ ] Pessoa 3: integrar os módulos da sua branch, preservando autoria e revisão.
- [ ] Pessoa 1: métodos de relatórios e contagens sem interação de terminal.
- [ ] Grupo: ratificar acesso à manutenção, filtros e decisões de retorno.
- [ ] Grupo: definir os quatro nomes em EQUIPE_NOMES e confirmar o semestre.
- [ ] Grupo: definir a mesma convenção de datas para abertura, fechamento e relatórios.
- [ ] Grupo: alinhar consultas seguras com o professor, conforme o planejamento.
- [ ] Grupo: confirmar autorização para quatro integrantes e prazo acadêmico.

## Evidências finais ainda necessárias

- [ ] Executar os fluxos com PostgreSQL real; não usar `--demo` como prova de persistência.
- [ ] Validar titularidade, resolução alheia, FK, duplicidade, fila concorrente e rollback.
- [ ] Instalação limpa na VM Linux seguindo o README, sem dependência do diretório atual.
- [ ] Conferir diagrama e relatórios reais com amostra conhecida.
- [ ] Executar roteiro manual e registrar resultados e responsáveis.
- [ ] Gravar o vídeo com objetivo e todos os menus integrados, publicar e inserir link.
- [ ] Conferir contribuições individuais, acesso do professor e submissão no AVA.

As telas da parte de Davi estão implementadas e verificadas com provedor simulado.
A entrega integrada ainda não pode ser declarada 100% funcional em PostgreSQL.
Os itens externos não foram marcados como concluídos por presença de placeholders
ou aprovação dos testes de demonstração.
