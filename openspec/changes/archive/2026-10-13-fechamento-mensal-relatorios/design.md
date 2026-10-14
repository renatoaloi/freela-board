## Context

Hoje o relatório é calculado sob demanda: `RelatorioService.generate()` soma **todos** os apontamentos do cliente no mês/ano via `RelatorioRepository.get_apontamentos_by_cliente_mes_ano()` / `get_tarefas_by_cliente_mes_ano()` e devolve um `RelatorioResponse` que nunca é gravado (`Relatorio` não tem modelo nem tabela). O Kanban carrega `GET /tarefas?projeto_id=&status=` e não tem noção de competência. Não existe estado "já faturado": marcar uma tarefa como `fechada` é uma ação solta no drag-and-drop.

Restrições do repo que moldam o desenho: SQLite com Alembic (`render_as_batch`), backend sync SQLAlchemy com camadas Clean (repository → service → controller), frontend sem testes e sem build de tipos, e coluna JSON já usada em `TarefaModel.anexos`. Ver `proposal.md` para motivação; requisitos em `specs/fechamento-mensal/`, `specs/kanban-filtro-mes/`, `specs/relatorios/` e `specs/relatorios-pdf/`.

## Goals / Non-Goals

**Goals:**
- Fechamento explícito do mês (cliente + competência + seleção de tarefas) gerando um relatório gravado
- Totais e dados fiscais congelados no fechamento, calculados só sobre o que foi selecionado
- Leitura/listagem/download a partir do registro gravado (`id`)
- Filtro de competência no Kanban baseado nas datas dos apontamentos

**Non-Goals:**
- Reabrir, editar ou excluir relatório fechado
- Migrar/copiar dados históricos (não existem relatórios gravados hoje)
- Vincular tarefas de status diferente de `pronta`, ou fechamentos parciais no mesmo cliente+mês
- Impedir lançamento de apontamentos em tarefa já `fechada`
- Alterar o Dashboard ou o escopo do PDF além da troca da origem dos dados

## Decisions

### D1 — Relatório gravado em tabela + coluna JSON de snapshot
Nova tabela `relatorios` (`id`, `cliente_id` FK, `mes`, `ano`, `total_horas`, `total_valor`, `data_fechamento`, `dados` JSON) mais `relatorio_tarefas` (`relatorio_id`, `tarefa_id`) para o vínculo relatório ↔ tarefa.

A coluna `dados` guarda o `RelatorioResponse` completo (cliente, dados bancários, projetos e tarefas com seus totais) já resolvido no fechamento; as colunas escalares (`total_horas`, `total_valor`, `mes`, `ano`) existem só para listagem e ordenação.

- *Alternativa*: tabelas normalizadas (`relatorio_projetos`, `relatorio_tarefas` com horas/valor). Rejeitada porque o snapshot precisa congelar inclusive nome do cliente/projeto e `valor_por_hora` vigente na data — normalizar obrigaria a duplicar esses valores de qualquer forma, com mais joins para ler.
- Coluna JSON já é padrão no repo (`anexos`), e SQLite a suporta sem custo extra neste volume (single user).

### D2 — Vínculo explícito relatório ↔ tarefa
`relatorio_tarefas` permite responder "esta tarefa já está em algum relatório?" sem varrer JSON, e sustenta a regra de elegibilidade (tarefa `fechada` não reaparece). Unique constraint `(relatorio_id, tarefa_id)`.

### D3 — Unicidade do fechamento garantida no banco
`UniqueConstraint("cliente_id", "mes", "ano")` em `relatorios`, com o service traduzindo `IntegrityError` em `409`. Service-level check isolado deixaria janela de concorrência — irrelevante para single user, mas a constraint é o custo zero aqui e documenta a regra no schema.

### D4 — Totais calculados no service a partir das linhas do período
O cálculo reaproveita as queries de agregação existentes (por projeto e por tarefa, filtrando `strftime("%m"/"%Y", ApontamentoModel.data)` igual a hoje) e filtra em Python pelas `tarefa_ids` selecionadas, montando projetos/tarefas/totais. Quantidades são pequenas (single user), e isso evita duplicar duas versões da mesma query SQL.

- *Alternativa*: filtrar os ids direto no SQL (`in_(tarefa_ids)`). Rejeitada por ora — a query parametrizada teria que ser replicada; revisitar se o volume crescer.

### D5 — Fechamento é uma transação única
`RelatorioService.fechar()` executa, na mesma sessão: validações → insert do relatório → inserts em `relatorio_tarefas` → update de `TarefaModel.status` para `fechada` → commit. Qualquer falha lança `HTTPException` **antes** do commit, então nenhum efeito parcial é visível (requisito "falha não altera nada").

### D6 — Endpoints substituem o modelo de geração sob demanda
- `POST /api/v1/fechamentos` — fecha o mês (body: `cliente_id`, `mes`, `ano`, `tarefa_ids`) → `201`
- `GET /api/v1/fechamentos/tarefas-elegiveis?cliente_id&mes&ano&projeto_id?` — elegíveis
- `GET /api/v1/relatorios` — **BREAKING**: passa a listar os relatórios fechados (antes era geração por query params)
- `GET /api/v1/relatorios/{id}` — detalhe do snapshot
- `GET /api/v1/relatorios/{id}/pdf` — **BREAKING**: substitui `/relatorios/pdf?cliente_id&mes&ano`

Tudo sob o `relatorio_controller.py` existente (que já abriga `/dashboard`, `/relatorios` e `/relatorios/pdf` — ver AGENTS.md). Remoção dos dois endpoints antigos em vez de mantê-los deprecados: app single user, sem consumidores externos; manter os dois modelos de leitura criaria duas fontes de verdade.

### D7 — PDF lido do snapshot
`RelatorioPdfService.generate()` passa a receber o `RelatorioResponse` reconstruído da coluna `dados` (o template Jinja e o layout A4 não mudam). O import de WeasyPrint continua **lazily** dentro de `generate()` (necessário: sem ele o app nem sobe em ambientes sem GTK/cairo, e os testes de PDF seguem atrás do guard `HAS_WEASYPRINT`).

### D8 — Kanban filtra por mês/ano reaproveitando `GET /tarefas`
`TarefaService.list_all()` ganha `mes`/`ano`; quando informados, `TarefaRepository.list_all_filtered()` faz join com `ApontamentoModel` filtrando a data e aplica `.distinct()` para não duplicar tarefas com vários apontamentos. Evita endpoint paralelo e mantém o Kanban falando a mesma linguagem das outras telas.

### D9 — Frontend espelha o recurso (lista → detalhe)
- Novo `src/components/Fechamento/FechamentoMensal.jsx` na rota `/fechamento` (filtros cliente/mês/ano/projeto + seleção de tarefas com `ConfirmModal` antes de confirmar)
- `src/components/Relatorios/RelatoriosList.jsx` (rota `/relatorios`) lista os fechamentos; `RelatorioView.jsx` passa a ser o detalhe (rota `/relatorios/:id`), reaproveitando os cards de cliente/dados bancários/resumo/projetos que já existem
- Filtro de competência no Kanban com `usePersistedState('kanban.mes' / 'kanban.ano')`, padrão = mês/ano atual

## Risks / Trade-offs

- **Snapshot congela dados do cliente/projeto**: se o cliente mudar de endereço, relatórios antigos mostrarão o dado da época → é o comportamento desejado para memória de cálculo fiscal; nada a fazer (as edições valem para o futuro).
- **Sem como corrigir um fechamento errado**: relatório é somente leitura → Mitigation: fora do escopo desta mudança; se necessário no futuro, permitir excluir e refechar (exige decisão de produto).
- **Tarefa reaberta depois de fechada**: possível pelo drag-and-drop; ela continua listada no relatório antigo (snapshot) e volta a ser elegível em outro fechamento → aceito, sem trava automática.
- **Mesma tarefa em relatórios de meses diferentes**: só se for reaberta; cada relatório soma apenas as horas da sua competência.
- **Testes existentes quebram**: `tests/test_relatorios.py` testa geração sob demanda → serão reescritos para o novo contrato (esperado, é breaking declarado).
- **PDF no Windows local**: continua sem GTK/cairo, então os testes de PDF ficam `skipped`; validar via Docker se precisar exercitar o render.

## Migration Plan

1. `cd backend && python -m alembic revision --autogenerate -m "add relatorios and relatorio_tarefas"`, revisar e aplicar (`alembic upgrade head`, também executado no startup do app)
2. Deploy normal (backend + rebuild do frontend); nada a popular — relatórios anteriores não existem como registros
3. Rollback: `docker compose down` + `alembic downgrade -1` (as duas tabelas são aditivas; `tarefas`/`apontamentos` seguem intactos e nenhum status é alterado pelo downgrade)

## Open Questions

- Lançar apontamento em tarefa já `fechada` deve ser bloqueado pela UI? Fora do escopo desta mudança (nenhuma spec depende disso); avaliar em change futuro se virar incômodo no uso.
