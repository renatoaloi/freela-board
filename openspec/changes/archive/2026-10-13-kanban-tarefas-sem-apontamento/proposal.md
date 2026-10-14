## Why

Com o filtro de competência do Kanban, uma tarefa recém-criada (que ainda não tem nenhum apontamento) não aparece em **nenhum** mês, porque o filtro só retorna tarefas que tiveram horas lançadas no período. Na prática a tarefa recém-criada "desaparece" logo depois do cadastro, e o usuário precisa adivinhar que o filtro é o culpado.

A regra atual foi definida em `fechamento-mensal-relatorios` (capability `kanban-filtro-mes`) pensando em fechamento — mas o Kanban é a tela operacional, onde tarefas novas precisam estar visíveis desde a criação até receberem o primeiro apontamento.

## What Changes

- **BREAKING (comportamento)**: com mês/ano selecionados, o Kanban passa a exibir também tarefas que **não possuem nenhum apontamento**, independentemente da competência filtrada. Continuam ocultas apenas as tarefas que têm apontamentos em **outros** meses/anos.
- A consulta de listagem de tarefas (`GET /api/v1/tarefas`) passa a incluir, quando há filtro de `mes`/`ano`, as tarefas sem apontamento algum (não apenas as que têm apontamento no período).

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `kanban-filtro-mes`: Filtro de competência passa a exibir também tarefas sem nenhum apontamento (qualquer competência), mantendo ocultas apenas as que têm apontamentos em outro período

## Impact

**Backend:**
- `backend/app/infrastructure/repositories/tarefa_repository.py` — `list_all_filtered()` passa a fazer `outerjoin` (ou subquery) para incluir tarefas sem apontamento quando `mes`/`ano` são informados
- `backend/tests/test_relatorios.py` — o teste `test_tarefas_filtradas_por_competencia` prevê que a tarefa sem apontamento fica fora do resultado filtrado; precisa ser atualizado para o novo comportamento

**Frontend:**
- Sem alteração de código esperada (`Kanban.jsx` já envia `mes`/`ano`); apenas o resultado da listagem muda

**Specs:**
- `openspec/specs/kanban-filtro-mes/spec.md` — MODIFIED na requirement "Filtro de competência considera a data dos apontamentos"
