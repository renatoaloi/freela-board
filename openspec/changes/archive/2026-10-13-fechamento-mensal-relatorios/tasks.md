## 1. Backend — Modelo de dados e migration

- [x] 1.1 Adicionar `RelatorioModel` em `app/domain/models.py`: `id` (UUID), `cliente_id` (FK `clientes.id`), `mes`, `ano`, `total_horas`, `total_valor`, `data_fechamento` (DateTime), `dados` (JSON), timestamps, `UniqueConstraint("cliente_id", "mes", "ano")`
- [x] 1.2 Adicionar `RelatorioTarefaModel` em `app/domain/models.py`: `relatorio_id` (FK `relatorios.id`), `tarefa_id` (FK `tarefas.id`), `UniqueConstraint("relatorio_id", "tarefa_id")`
- [x] 1.3 Gerar migration: `cd backend && python -m alembic revision --autogenerate -m "add relatorios and relatorio_tarefas"`
- [x] 1.4 Revisar e aplicar migration: `python -m alembic upgrade head`

## 2. Backend — Schemas

- [x] 2.1 Adicionar `FechamentoCreate` (`cliente_id`, `mes` 1-12, `ano`, `tarefa_ids` lista não vazia) em `app/domain/schemas.py`
- [x] 2.2 Adicionar `FechamentoTarefaDisponivel` (`tarefa_id`, `titulo`, `projeto_id`, `projeto_titulo`, `status`, `total_horas_periodo`) em `app/domain/schemas.py`
- [x] 2.3 Adicionar `RelatorioResumo` (`id`, `cliente_id`, `cliente_nome`, `mes`, `ano`, `total_horas`, `total_valor`, `data_fechamento`) em `app/domain/schemas.py`
- [x] 2.4 Ajustar `RelatorioResponse` para carregar do snapshot (incluir campo `id`) mantendo `cliente`, `mes_referencia`, `totais`, `projetos`, `dados_bancarios`

## 3. Backend — Repository

- [x] 3.1 Adicionar método de tarefas elegíveis em `RelatorioRepository` (junção cliente → projetos → tarefas → apontamentos, filtro `status == "pronta"` + `strftime("%m"/"%Y")` do mês/ano, `projeto_id` opcional, excluindo tarefas já vinculadas a outro relatório)
- [x] 3.2 Adicionar persistência em `RelatorioRepository`: `create_relatorio(...)` e `add_tarefas(relatorio_id, tarefa_ids)`
- [x] 3.3 Adicionar leitura em `RelatorioRepository`: `list_relatorios()` (ordem decrescente ano/mês) e `get_relatorio_by_id(id)`
- [x] 3.4 Adicionar consulta em `RelatorioRepository` que devolva tarefa_ids já vinculados a algum relatório (`tarefas_vinculadas(tarefa_ids)`)

## 4. Backend — Service de fechamento

- [x] 4.1 Implementar `RelatorioService.fechar(data: FechamentoCreate)`: valida cliente (404), mes/ano, lista não vazia (422), tarefas pertencentes ao cliente e com `status == "pronta"` (400/422)
- [x] 4.2 Calcular snapshot no `fechar()`: horas por tarefa restritas ao mês, agrupamento por projeto, `valor_total = total_horas * valor_por_hora`, totais gerais arredondados para 2 casas
- [x] 4.3 Incluir dados fiscais do cliente e dados bancários no snapshot congelado
- [x] 4.4 Gravar relatório + vínculos em `relatorio_tarefas` e atualizar `status` das tarefas para `fechada` na mesma transação (rollback completo em falha)
- [x] 4.5 Retornar `409` quando já existir relatório para o mesmo cliente + mês + ano (checagem no service + tratamento de integrity error)
- [x] 4.6 Implementar `RelatorioService.listar()` e `RelatorioService.obter(id)` (404 quando inexistente) a partir do snapshot gravado

## 5. Backend — PDF do relatório fechado

- [x] 5.1 Ajustar `RelatorioPdfService.generate()` para receber o `RelatorioResponse` reconstruído do snapshot (sem alterar template/layout)
- [x] 5.2 Manter `filename()` derivando nome de cliente/mês/ano a partir do registro gravado
- [x] 5.3 Garantir que o import de WeasyPrint continue lazy dentro de `generate()`

## 6. Backend — Controllers (breaking)

- [x] 6.1 Em `relatorio_controller.py`: substituir `GET /relatorios?cliente_id&mes&ano` por `GET /relatorios` (lista de `RelatorioResumo`)
- [x] 6.2 Adicionar `GET /relatorios/{id}` (detalhe, `response_model=RelatorioResponse`)
- [x] 6.3 Remover `GET /relatorios/pdf?cliente_id&mes&ano` e adicionar `GET /relatorios/{id}/pdf`
- [x] 6.4 Adicionar `POST /fechamentos` e `GET /fechamentos/tarefas-elegiveis` no mesmo controller, com dependência de `X-API-Key`
- [x] 6.5 Garantir `Depends(get_api_key)` em todos os novos endpoints e checar ordem das rotas (`/{id}` após a lista)

## 7. Backend — Filtro de competência nas tarefas

- [x] 7.1 Adicionar parâmetros `mes`/`ano` em `TarefaRepository.list_all_filtered()` com join em `ApontamentoModel` e `.distinct()`
- [x] 7.2 Expor `mes`/`ano` em `TarefaService.list_all()` e em `GET /tarefas` (`tarefa_controller.py`)
- [x] 7.3 Ignorar filtro de competência quando `mes`/`ano` não forem informados (comportamento atual preservado)

## 8. Frontend — Serviço de API

- [x] 8.1 Adicionar `fechamentoAPI` em `src/services/api.js` (`tarefasElegiveis`, `fechar`)
- [x] 8.2 Ajustar `relatoriosAPI` para `list()`, `get(id)` e `downloadPdf(id)` (remover `generate`/`generatePdf` por query params)
- [x] 8.3 Ajustar `tarefasAPI.list` para aceitar `mes`/`ano`

## 9. Frontend — Tela de Fechamento Mensal

- [x] 9.1 Criar `src/components/Fechamento/FechamentoMensal.jsx` com seletores de cliente, projeto (opcional), mês e ano
- [x] 9.2 Listar tarefas elegíveis com checkbox, horas no período e projeto, com estado vazio quando não houver elegíveis
- [x] 9.3 Exibir resumo da seleção (total de horas e valor estimado) antes de confirmar
- [x] 9.4 Confirmar o fechamento via `ConfirmModal` (padrão do repo, sem `window.confirm`) e tratar erros 409/422/404 com `AlertModal`
- [x] 9.5 Adicionar rota `/fechamento` em `src/App.jsx` e item "Fechamento" em `src/components/Layout/Sidebar.jsx`

## 10. Frontend — Relatórios como lista e detalhe

- [x] 10.1 Criar `src/components/Relatorios/RelatoriosList.jsx` listando cliente, competência, horas e valor de cada relatório fechado, com estado vazio apontando para o Fechamento Mensal
- [x] 10.2 Adaptar `RelatorioView.jsx` para detalhe por `id` (rota `/relatorios/:id`), reaproveitando os cards de cliente, dados bancários, resumo e projetos
- [x] 10.3 Adicionar ação "Baixar PDF" no detalhe e na lista, usando o `Content-Disposition` do servidor
- [x] 10.4 Remover da tela o formulário de geração por cliente/mês/ano

## 11. Frontend — Filtro de competência no Kanban

- [x] 11.1 Adicionar seletores de mês e ano em `src/components/Kanban/Kanban.jsx`, persistidos com `usePersistedState('kanban.mes' / 'kanban.ano')`
- [x] 11.2 Iniciar o filtro no mês/ano corrente quando não houver valor salvo
- [x] 11.3 Incluir `mes`/`ano` na chamada de `tarefasAPI.list` e recarregar o board ao trocar a competência
- [x] 11.4 Manter os filtros de cliente/projeto existentes combinando com a competência

## 12. Testes

- [x] 12.1 Adicionar fixtures em `backend/tests/conftest.py`: apontamento em mês/ano específico e tarefa em status `pronta`
- [x] 12.2 Criar `backend/tests/test_fechamento.py`: elegibilidade (apenas `pronta` e com apontamento no mês), rejeição de tarefa vazia/de outro cliente/status inválido, unicidade cliente+mês (409), snapshot de horas/valor, transição para `fechada`, autenticação 401
- [x] 12.3 Reescrever `backend/tests/test_relatorios.py` para o novo contrato: lista, leitura por `id`, 404 em id inexistente e PDF por `id` (mantendo o guard `HAS_WEASYPRINT`)
- [x] 12.4 Rodar `cd backend && pytest -v` — verde quando não houver falhas além dos 3 testes de PDF skipados (sem GTK/cairo no ambiente local)

## 13. Documentação

- [x] 13.1 Atualizar a tabela de endpoints no `README.md` (remover geração por `cliente_id`/`mes`/`ano`, documentar fechamento, lista e leitura por `id`)
- [x] 13.2 Documentar no `README.md` o fluxo de fechamento mensal e o filtro de competência do Kanban
