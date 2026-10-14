## Why

Ao retomar o uso do FreelaBoard os registros existentes são de maio/2026 e não há forma de separar "o que já foi faturado" do que ainda está em andamento: o relatório é gerado sob demanda somando **todos** os apontamentos do cliente no mês/ano, sem recorte explícito e sem deixar histórico do que foi fechado. Como efeito colateral, tarefas já encerradas continuam poluindo o Kanban, que só filtra por cliente e projeto.

É preciso então um fluxo de **fechamento mensal** (escolher mês, cliente, projeto e quais tarefas entram no relatório), com o resultado **persistido** para poder ser listado, visualizado e baixado depois, e com as tarefas fechadas saindo do fluxo normal do Kanban (que passa a ter filtro por competência mês/ano).

## What Changes

- **Nova tela "Fechamento Mensal"** (`/fechamento`): escolhe cliente, mês/ano e opcionalmente um projeto, e seleciona quais tarefas entram no relatório. Apenas tarefas com status `pronta` **e** que tenham apontamentos dentro do mês/ano escolhidos são elegíveis.
- **Relatório passa a ser um registro persistido** (um por cliente + mês/ano), com horas e valores congelados no momento do fechamento (**snapshot**), calculados apenas sobre as tarefas selecionadas. **BREAKING**: não existe mais geração sob demanda a partir de todos os apontamentos do período.
- **Tarefas selecionadas vão para status `fechada`** ao concluir o fechamento (e saem das listagens operacionais do Kanban, exceto quando o filtro de competência for o mês do apontamento).
- **Tela de Relatórios deixa de gerar e passa a consumir**: lista os relatórios fechados, permite visualizar o detalhe de um deles e baixar o PDF correspondente. **BREAKING**: os endpoints de geração por `cliente_id`/`mes`/`ano` são substituídos por leitura por `id`.
- **Filtro de mês/ano no Kanban**: a tarefa pertence à competência selecionada quando tem ao menos um apontamento naquele mês/ano.

## Capabilities

### New Capabilities
- `fechamento-mensal`: Fechamento do mês — seleção de cliente/mês/ano/projeto, escolha das tarefas elegíveis (`pronta`), gravação do relatório com snapshot de horas/valores e transição das tarefas selecionadas para `fechada`
- `kanban-filtro-mes`: Filtro de competência (mês e ano) no Kanban, com base na data dos apontamentos das tarefas

### Modified Capabilities
- `relatorios`: Relatório deixa de ser calculado sob demanda sobre todos os apontamentos do período e passa a ser servido do snapshot gravado no fechamento, restrito às tarefas selecionadas; endpoints passam a ser de listagem/leitura por `id`
- `relatorios-pdf`: PDF passa a ser gerado a partir do relatório fechado (por `id`), refletindo a seleção de tarefas e os totais congelados

## Impact

**Backend:**
- `app/domain/models.py` — novos modelos `RelatorioModel` (tabela `relatorios`, unique `(cliente_id, mes, ano)`) e `RelatorioTarefaModel` (tabela `relatorio_tarefas`, vínculo relatório ↔ tarefa)
- `app/domain/schemas.py` — novos schemas de fechamento (`FechamentoCreate`, `FechamentoTarefaDisponivel`), de resumo do relatório (`RelatorioResumo`) e adaptação de `RelatorioResponse` para leitura do snapshot
- `app/infrastructure/repositories/relatorio_repository.py` — persistência/leitura do relatório fechado e consulta de tarefas elegíveis por cliente/mês/ano/projeto
- `app/application/services/relatorio_service.py` — novo método `fechar()` que consolida o snapshot e marca as tarefas como `fechada` (transação única); `generate()` deixa de ser usado como fonte da tela
- `app/application/services/relatorio_pdf_service.py` — render do PDF a partir do snapshot persistido
- `app/api/v1/relatorio_controller.py` — **BREAKING**: `GET /relatorios?cliente_id&mes&ano` e `GET /relatorios/pdf?cliente_id&mes&ano` substituídos por `GET /relatorios` (lista), `GET /relatorios/{id}`, `GET /relatorios/{id}/pdf`; novo `POST /fechamentos` e `GET /fechamentos/tarefas-elegiveis`
- `app/infrastructure/repositories/tarefa_repository.py` + `app/application/services/tarefa_service.py` + `app/api/v1/tarefa_controller.py` — filtros `mes`/`ano` (por apontamento) na listagem de tarefas usada pelo Kanban
- Nova migration Alembic criando as tabelas `relatorios` e `relatorio_tarefas`

**Frontend:**
- `src/components/Fechamento/` — nova pasta com a tela de fechamento mensal (filtros + seleção de tarefas)
- `src/components/Relatorios/RelatorioView.jsx` — reescrita como lista + detalhe + download do PDF (remoção do formulário de geração)
- `src/components/Kanban/Kanban.jsx` — seletores de mês/ano (persistidos via `usePersistedState`) integrados ao filtro
- `src/App.jsx` — nova rota `/fechamento`; `src/components/Layout/Sidebar.jsx` — novo item de menu
- `src/services/api.js` — novo `fechamentoAPI`; `relatoriosAPI` e `tarefasAPI` ajustados ao novo contrato

**Testes:**
- Novo `backend/tests/test_fechamento.py` (elegibilidade, unicidade cliente+mês, snapshot, transição para `fechada`, autenticação)
- `backend/tests/test_relatorios.py` — **BREAKING**: testes de geração sob demanda substituídos por testes de listagem/leitura/PDF por `id`

**Dados:** migration anterior segue válida; nenhum dado de apontamentos é migrado (relatórios anteriores simplesmente não existem como registros).
