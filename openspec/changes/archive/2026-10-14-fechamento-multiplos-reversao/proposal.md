## Why

Ao tentar gerar um segundo relatório de outubro para o mesmo cliente (para teste) o sistema respondeu `409 — Já existe relatório fechado para este cliente neste mês/ano`. Essa trava foi definida no change `fechamento-mensal-relatorios` presumindo "um fechamento por cliente/mês", mas na prática o mês pode ter **mais de um faturamento** (clientes com frentes diferentes, ou um fechamento parcial seguido de outro).

O segundo problema é derivado do mesmo modelo: como o relatório é imutável, se faltar uma tarefa no fechamento não há como corrigir — só refazendo do zero, o que hoje é impossível porque as tarefas viraram `fechada` e o período está travado.

## What Changes

- **BREAKING**: cai a regra de um relatório por cliente+competência. Passa a ser permitido **mais de um fechamento do mesmo cliente no mesmo mês/ano** (bloqueio por `409` deixa de existir).
- A trava que fica é de **negócio**: uma tarefa só pode entrar em **um** relatório. Tarefa já faturada sai da lista de elegíveis (comportamento atual mantido), evitando cobrança duplicada.
- **Nova operação de reversão**: `DELETE /api/v1/relatorios/{id}` exclui o relatório fechado e **devolve as tarefas vinculadas ao status `pronta`**, tornando-as elegíveis novamente para um novo fechamento.
- Cada relatório passa a ter um **número sequencial por cliente/competência** para que a lista e o PDF distingam o 1º, 2º... fechamento do mesmo mês.

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `fechamento-mensal`: remove a exigência de um relatório por cliente+competência; passa a numerar os fechamentos por cliente/mês e a impedir apenas a repetição de tarefa já faturada
- `relatorios`: passa a expor a exclusão de relatório fechado (reversão), com devolução das tarefas para `pronta`

## Impact

**Backend:**
- Migration Alembic removendo a `UniqueConstraint uq_relatorio_competencia` de `relatorios` (SQLite exige `render_as_batch`, já configurado no `env.py`)
- `app/domain/models.py` — novo campo `numero` em `RelatorioModel`; ajuste na relação `tarefas` (já existe cascade delete-orphan em `relatorio_tarefas`)
- `app/infrastructure/repositories/relatorio_repository.py` — cálculo do próximo número por cliente/mês e exclusão em cascata dos vínculos
- `app/application/services/relatorio_service.py` — `fechar()` deixa de checar competência existente; novo `reverter(id)`; leitura expondo `numero`
- `app/api/v1/relatorio_controller.py` — `DELETE /relatorios/{id}` (substitui a ausência de escrita); remoção do 409 por competência
- `app/domain/schemas.py` — `numero` em `RelatorioResumo` e `RelatorioResponse`

**Frontend:**
- `src/components/Relatorios/RelatoriosList.jsx` — mostra o nº do fechamento e botão de reversão com confirmação (`ConfirmModal`)
- `src/components/Fechamento/FechamentoMensal.jsx` — passa a informar quando haverá um novo número de fechamento e trata o fim do 409 por competência
- `src/services/api.js` — `relatoriosAPI.reverter(id)`

**Testes:**
- `backend/tests/test_fechamento.py` — segundo fechamento do mesmo cliente/mês permitido (substitui o teste de 409), número sequencial, tarefa já faturada fora dos elegíveis
- `backend/tests/test_relatorios.py` — exclusão devolve tarefas a `pronta`, 404 em inexistente, lista reflete a remoção

**Dados:** migration de constraint; nenhum dado precisa ser migrado.
