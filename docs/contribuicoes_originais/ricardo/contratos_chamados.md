> Documento original da branch, preservado para comparação. As adaptações da versão integrada estão em docs/integracao_branches.md.

# Guia de Integração - Módulo de Chamados (Pessoa 3)

Este documento explica como o restante do grupo (em especial a Pessoa 4 na CLI) deve chamar as funções da controladora de chamados (`Controller_Atendimento`) e as regras básicas de negócio.

---

## 1. Como instanciar a controladora

```python
from controller.controller_atendimento import Controller_Atendimento

ctrl_atendimento = Controller_Atendimento()
```

---

## 2. Funções do Menu do Cliente

### 2.1 Abrir um novo chamado
- **Método:** `ctrl_atendimento.criar_chamado(id_cliente, titulo, descricao)`
- **Parâmetros:**
  - `id_cliente` (int): ID do cliente logado/cadastrado.
  - `titulo` (str): título/assunto do problema.
  - `descricao` (str): detalhamento do que ocorreu.
- **Retorno:** Retorna o objeto `Atendimento` criado com o ID gerado e status inicial `'aberto'`. Retorna `None` se o cliente não existir ou faltar dados.

### 2.2 Listar chamados do cliente
- **Método:** `ctrl_atendimento.listar_chamados_cliente(id_cliente, apenas_ativos=False)`
- **Parâmetros:**
  - `id_cliente` (int): ID do cliente.
  - `apenas_ativos` (bool): se for `True`, traz só chamados `'aberto'` e `'em andamento'`. Se `False`, traz todos.
- **Retorno:** Lista de objetos `Atendimento` ordenada do mais recente para o mais antigo.

### 2.3 Ver detalhes de um chamado
- **Método:** `ctrl_atendimento.consultar_detalhes(id_chamado)`
- **Retorno:** Objeto `Atendimento` com todos os dados preenchidos, ou `None` se o chamado não existir.

### 2.4 Cancelar chamado (Exclusão pelo cliente)
- **Método:** `ctrl_atendimento.cancelar_chamado(id_chamado, id_cliente)`
- **Regras:**
  - Só apaga se o chamado pertencer àquele cliente.
  - Só apaga se o chamado ainda estiver com status `'aberto'`. Se já estiver `'em andamento'` ou `'resolvido'`, não permite cancelar.
- **Retorno:** `True` se cancelou com sucesso, `False` caso contrário.

---

## 3. Funções do Menu do Atendente

### 3.1 Assumir o próximo chamado da fila (FIFO)
- **Método:** `ctrl_atendimento.assumir_proximo_chamado(id_atendente)`
- **Comportamento:** Pega automaticamente o chamado `'aberto'` mais antigo da fila, vincula ao atendente e muda o status para `'em andamento'`.
- **Retorno:** O objeto `Atendimento` assumido, ou `None` caso a fila esteja vazia.

### 3.2 Meus chamados (em andamento)
- **Método:** `ctrl_atendimento.listar_meus_chamados(id_atendente)`
- **Retorno:** Lista de chamados com status `'em andamento'` do atendente logado.

### 3.3 Histórico de chamados (resolvidos)
- **Método:** `ctrl_atendimento.listar_historico_atendente(id_atendente)`
- **Retorno:** Lista de chamados já `'resolvido'` desse atendente, ordenados pela data de fechamento.

### 3.4 Resolver / Encerrar chamado
- **Método:** `ctrl_atendimento.resolver_chamado(id_chamado, id_atendente)`
- **Comportamento:** Move o status para `'resolvido'` e salva o horário atual como data de fechamento. Só funciona se o chamado estiver sob responsabilidade desse atendente e em andamento.
- **Retorno:** Objeto `Atendimento` atualizado, ou `None` se houver erro.

---

## 4. Manutenção de Chamados (CRUD para o Edital)

- `ctrl_atendimento.listar_todos()`: devolve a lista de todos os chamados para exibição antes de alterar ou excluir.
- `ctrl_atendimento.atualizar_chamado(id_chamado, titulo, descricao)`: altera título e descrição sem mexer no ID ou datas.
- `ctrl_atendimento.excluir_chamado_admin(id_chamado)`: exclusão direta no menu administrativo.
