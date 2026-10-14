## Context

No change `fechamento-mensal-relatorios` o filtro de competência do Kanban foi implementado em `TarefaRepository.list_all_filtered()` (backend/app/infrastructure/repositories/tarefa_repository.py) com `join` em `ApontamentoModel` + filtro `strftime("%m"/"%Y", ApontamentoModel.data)` + `.distinct()`. Como o join é interno, **tarefas sem nenhum apontamento ficam fora do resultado** — e elas não aparecem em competência alguma.

O frontend (`Kanban.jsx`) sempre envia `mes` e `ano` (persistidos em `kanban.mes` / `kanban.ano`, padrão = mês/ano corrente), então não existe mais o "caminho sem filtro" na prática: o efeito colateral é a tarefa recém-criada desaparecer. Ver `proposal.md` para motivação e `specs/kanban-filtro-mes/spec.md` para os requisitos.

## Goals / Non-Goals

**Goals:**
- Tarefa sem nenhum apontamento volta a aparecer no Kanban com qualquer competência selecionada
- Preservar o comportamento de ocultar tarefas cujos apontamentos pertencem a **outro** período
- Não duplicar tarefas que tenham múltiplos apontamentos na competência

**Non-Goals:**
- Mudar a regra de elegibilidade do fechamento mensal (`fechamento-mensal`): lá continua valendo "status `pronta` + apontamento no mês"
- Alterar o Dashboard ou o relatório
- Adicionar UI extra (toggle "incluir sem apontamento" ou opção "Todas as competências")
- Alterar filtros por projeto/cliente

## Decisions

### D1 — Filtro no repositório com outerjoin + NOT EXISTS, sem tocar na API
`list_all_filtered(mes=..., ano=...)` troca o `join(ApontamentoModel)` por um `outerjoin` com a condição de período **dentro do ON**, de modo que a tarefa gere uma linha “nula” quando não tem apontamento na competência. A cláusula `WHERE` aceita a linha quando o apontamento casou (`ApontamentoModel.id IS NOT NULL`) **ou** a tarefa não tem apontamento algum.

> **Correção encontrada na implementação:** a versão inicial desta decisão sugeria `ApontamentoModel.id IS NULL` como critério de “sem apontamento”. Isso está errado: com o período no `ON`, uma tarefa que só tem apontamentos em **outro** mês também gera linha nula e acabaria aparecendo, violando os cenários “Tarefa sem apontamento no mês não aparece” e “Mês diferente com mesmo número”. O critério correto é `NOT EXISTS (SELECT 1 FROM apontamentos WHERE tarefa_id = tarefas.id)` — um anti-join que distingue “sem nenhum apontamento” de “sem apontamento neste período”. Em SQLAlchemy ele precisa de `.correlate(TarefaModel)`, senão o auto-correlate removeria o `FROM` do subselect e levantaria `InvalidRequestError`.

- *Alternativa 1*: definir tudo com `EXISTS` no período + `NOT EXISTS` (nenhum join). Igualmente correto e dispensaria o `.distinct()`; mantido o outerjoin por já ser a forma escrita nas tasks e ter custo equivalente neste volume.
- *Alternativa 2*: fazer duas queries (uma com apontamento no período, outra com tarefas sem nenhum apontamento) e concatenar/unir no service. Rejeitada: duplica paginação/ordenação e espalha regra de dados para a camada de aplicação.
- *Alternativa 3*: filtrar no frontend mantendo o endpoint antigo e buscando todas as tarefas. Rejeitada: o Kanban perderia o benefício do filtro e traria histórico inteiro do projeto para o browser.
- *Alternativa 4*: filtrar por `data_criacao` quando não há apontamento. Não escolhida pelo usuário — a opção aprovada foi "qualquer competência".

O outerjoin mantém o `.distinct()` já existente para não duplicar tarefas com vários apontamentos no período; uma tarefa sem apontamento gera exatamente uma linha (a linha "nula" do outerjoin).

### D2 — Regra concentrada onde já está o filtro
Nenhuma mudança em controller/service além de repassar os parâmetros (já existentes). Assim o `GET /tarefas?projeto_id=&status=&mes=&ano=` continua sendo a única fonte do Kanban e o comportamento fica coberto por um único teste de API.

### D3 — Atualização do teste existente
`tests/test_relatorios.py::test_tarefas_filtradas_por_competencia` hoje afirma que a tarefa sem apontamento fica fora da listagem filtrada. Ele será invertido para o novo comportamento, e ganhará um caso cobrindo tarefa com apontamento **em outro mês** continuando oculta (regressão do fechamento).

## Risks / Trade-offs

- **Tarefa sem horas aparece em competências passadas** (ex.: filtro 03/2026 mostra uma tarefa criada hoje sem apontamentos) → aceito: é o efeito desejado de "nunca desaparecer"; o custo é alguma poluição visual até a tarefa receber o primeiro apontamento.
- **Distinct continua necessário**; esquecê-lo duplicaria tarefas no board → o `.distinct()` atual é mantido e coberto pelo cenário "Múltiplos apontamentos não duplicam a tarefa".
- **Query pode ficar mais lenta** com muitos apontamentos por projeto (outerjoin por tarefa) → irrelevante neste volume (single user, SQLite local).

## Migration Plan

Mudança de comportamento sem schema e sem migração de dados: basta aplicar o código e reiniciar (backend local `uvicorn` ou `docker compose up -d --build` no Raspberry). Rollback = reverter o commit do repositório; a regra de elegibilidade do fechamento mensal não é afetada.

## Open Questions

- Nenhuma: a única decisão de produto (mostrar sem apontamento em qualquer competência) foi confirmada antes da escrita dos artifacts.
