## Context

Hoje `RelatorioModel` tem `UniqueConstraint("cliente_id", "mes", "ano", name="uq_relatorio_competencia")` e `RelatorioService.fechar()` faz checagem prévia devolvendo `409`. A tabela de vínculo `relatorio_tarefas` (unique `(relatorio_id, tarefa_id)`) já impede a mesma tarefa entrar duas vezes **no mesmo** relatório, mas não em relatórios diferentes — o impedimento hoje vem da combinação "status `fechada` + exclusion por vínculo" na consulta de elegíveis (`get_tarefas_elegiveis_fechamento` usa `outerjoin` + `RelatorioTarefaModel.id.is_(None)`), que continuará sendo a trava de negócio depois de cair a constraint.

O SQLite/Alémbic do projeto roda com `render_as_batch=True` (exigido para qualquer alteração de constraint/coluna), e o startup do app aplica `alembic upgrade head`.

Requisitos em `specs/*/spec.md`; motivação em `proposal.md`.

## Goals / Non-Goals

**Goals:**
- Permitir N relatórios por cliente/mês/ano
- Numerar os fechamentos por cliente/competência para diferenciá-los na lista e no PDF
- Reverter um fechamento: apagar o relatório e devolver as tarefas a `pronta`
- Manter a trava anti-duplicidade **por tarefa** (tarefa só entra em um relatório)

**Non-Goals:**
- Editar um relatório existente (atualizar seleção/snapshot) — o caminho continua sendo reverter e fechar de novo
- Manter histórico de relatórios revertidos (`cancelado`) — decisão do usuário: exclusão definitiva
- Reverter parcialmente (remover só uma tarefa do relatório)
- Reabrir competência automaticamente ou reaproveitar número de relatório revertido

## Decisions

### D1 — Cai a constraint, entra numero sequencial
Migration remove `uq_relatorio_competencia` e adiciona a coluna `numero` (`Integer`, `nullable=False`, `default=1`) em `relatorios`. O número é calculado no service como `max(numero) + 1` entre os relatórios **existentes** daquele cliente/mês/ano (1 quando não houver nenhum).

- *Alternativa*: manter a constraint e permitir apenas um relatório por competência, criando "parcelas" como tipos diferentes. Rejeitada pelo usuário: o caso real é ter mais de um relatório no mesmo mês.
- *Alternativa*: não numerar e distinguir pela `data_fechamento`. Rejeitada: dois relatórios do mesmo mês ficariam visualmente idênticos na lista e no nome do PDF.
- Não haverá constraint `(cliente_id, mes, ano, numero)`: o cálculo roda dentro da transação do fechamento; para uso single-user isso é suficiente e evita mais uma migration de ajuste. Se aparecer concorrência, o número gerado repetido não quebra nada além da numeração.

### D2 — A trava anti-duplicidade passa a ser só por tarefa
`get_tarefas_elegiveis_fechamento()` já exclui tarefas que tenham vínculo em `relatorio_tarefas`; essa consulta passa a ser a única proteção. `fechar()` mantém ainda a checagem `tarefas_vinculadas()` (422) para cobrir o caso de duas abas/concorrência dentro do mesmo mês.

### D3 — Reverter = delete em cascata + volta a `pronta`
`RelatorioService.reverter(id)`: busca o relatório (404) → coleta os `tarefa_id` de `relatorio_tarefas` → remove o relatório (o relacionamento `tarefas` do modelo já tem `cascade="all, delete-orphan"`, então os vínculos saem junto) → para cada tarefa que esteja `fechada`, volta para `pronta` → commit.

- Ordem: apagar o vínculo e depois avaliar o status, para não reabrir tarefa que pertence a **outro** relatório ainda ativo. Como a busca dos ids é feita antes do delete, a decisão usa a lista capturada e confere se a tarefa ainda está vinculada a outro relatório antes de mexer no status.
- Tarefa que não está mais `fechada` mantém o status atual (cenário do usuário que reabriu manualmente).

### D4 — Frontend
`RelatoriosList` ganha coluna/indicação do nº do fechamento e ação "Reverter" com `ConfirmModal`; `relatoriosAPI.reverter(id)`; após sucesso recarrega a lista (com `AlertModal` em erro). `FechamentoMensal` deixa de tratar 409 por competência e passa a exibir "Fechamento nº X" quando o período já tiver relatórios.

## Risks / Trade-offs

- **Dois relatórios do mesmo mês podem confundir na hora de faturar** → mitigado número visível na lista, no detalhe e no nome do arquivo PDF (`...-fechamento-2.pdf`).
- **Número calculado sem constraint** → em teoria duas transações simultâneas poderiam repetir número; aceito para app single-user (documentado).
- **Reversão é destrutiva** (sai o relatório, nada de histórico) → escolha do usuário; o diálogo deixa claro que as tarefas voltam a `pronta`.
- **Migration em SQLite com batch**: remover constraint é operação suportada por `batch_alter_table`, já padrão no `env.py`.

## Migration Plan

1. `cd backend && python -m alembic revision --autogenerate -m "remove unique competencia and add numero"`
2. Revisar (conferir `batch_alter_table` e a coluna `numero` com default) e `alembic upgrade head`
3. Deploy: backend rebuild (`docker compose up -d --build` no Raspberry); dados existentes seguem válidos, com `numero == 1` para os relatórios já fechados
4. Rollback: `alembic downgrade -1` — a constraint é recriada; **atenção**: se já existirem dois relatórios do mesmo cliente/mês, o downgrade falha por violação de unicidade e exigirá excluir um deles antes

## Open Questions

- Nenhuma: multiplicidade, trava por tarefa e semântica da reversão foram confirmadas com o usuário.
