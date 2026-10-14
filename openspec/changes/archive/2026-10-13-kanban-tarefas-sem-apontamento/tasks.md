## 1. Backend — Filtro de competência

- [x] 1.1 Trocar o `join(ApontamentoModel)` por `outerjoin` em `TarefaRepository.list_all_filtered()` quando `mes`/`ano` forem informados
- [x] 1.2 Mover o filtro de `strftime("%m"/"%Y", ApontamentoModel.data)` para dentro da condição do `outerjoin` (ON) para preservar as linhas sem apontamento
- [x] 1.3 Incluir na condição do filtro as tarefas sem nenhum apontamento via anti-join `NOT EXISTS` correlacionado (`.correlate(TarefaModel)`), **não** `ApontamentoModel.id IS NULL` — este último incluiria tarefas com apontamentos em outro período
- [x] 1.4 Manter o `.distinct()` para não duplicar tarefas com múltiplos apontamentos no período
- [x] 1.5 Garantir que, sem `mes`/`ano`, a consulta segue sem join (comportamento atual preservado)

## 2. Testes

- [x] 2.1 Atualizar `backend/tests/test_relatorios.py::test_tarefas_filtradas_por_competencia` para o novo comportamento (tarefa sem apontamento aparece na competência)
- [x] 2.2 Adicionar teste cobrindo tarefa com apontamento em outro mês continuando oculta na competência filtrada
- [x] 2.3 Adicionar teste garantindo que uma tarefa sem apontamento aparece em mais de uma competência (ex.: 05/2026 e 06/2026)
- [x] 2.4 Rodar `cd backend && pytest -v` — verde quando não houver falhas além dos 3 testes de PDF skipados (sem GTK/cairo no ambiente local)

## 3. Documentação

- [x] 3.1 Revisar se o `README.md` descreve o filtro de mês/ano do Kanban de forma compatível com a nova regra
