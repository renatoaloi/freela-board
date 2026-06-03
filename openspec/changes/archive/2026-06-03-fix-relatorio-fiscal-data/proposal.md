## Why

O relatório de horas (`GET /api/v1/relatorios`) está exibindo **0 horas e nenhuma informação do cliente** mesmo quando há apontamentos cadastrados no período. A causa-raiz é um **mismatch de schema entre backend e frontend**: o backend envia campos achatados (`cliente_nome`, `total_geral_horas`, `projeto_titulo`), mas o frontend lê campos aninhados (`cliente.nome`, `total_horas_geral`, `proj.titulo`). Todas as propriedades que o frontend acessa são `undefined`, então a UI cai em fallbacks (`—`, `0,00`, nada). O cálculo no backend está correto (verificado por spike: 4 apontamentos em Maio/2026 retornam `total_geral_horas: 12.0`); o bug é puramente de **contrato entre as camadas**.

Em paralelo, o usuário precisa que o relatório carregue **informações fiscais completas do cliente** (CNPJ, razão social, endereço, município/UF) para que o contador consiga emitir nota fiscal sem precisar abrir outro sistema. Hoje o backend só envia 3 campos do cliente (`id`, `nome`, `documento`) — insuficiente.

## What Changes

- **Refatorar o schema do relatório** para um formato **aninhado e semanticamente limpo**:
  - `cliente: { id, nome, razao_social, documento, email, endereco, complemento, bairro, cidade, estado }` (substitui `cliente_id` + `cliente_nome` + `cliente_documento` achatados).
  - `totais: { total_horas, total_valor }` (substitui `total_geral_horas` + `total_geral_valor` achatados).
  - `projetos[i].titulo` (renomeia `projeto_titulo` para `titulo`).
  - `projetos[i].tarefas: [{ tarefa_id, titulo, total_horas }]` (**novo**: detalhamento por tarefa agrupado dentro de cada projeto).
  - `mes_referencia` permanece achatado como string `"MM/YYYY"`.
- **Adicionar campos fiscais ao relatório**: `razao_social`, `endereco`, `complemento`, `bairro`, `cidade`, `estado`, `email` (todos já existem no `ClienteModel`, só não eram serializados). O `nome` fantasia continua sendo exposto ao lado da `razao_social` para o contador distinguir.
- **Wire format breaking change** em `GET /api/v1/relatorios`. **BREAKING**: o JSON de resposta muda completamente (de achatado pra aninhado). O único consumer é o `RelatorioView.jsx`, que será atualizado na mesma change.
- **Adicionar `response_model=RelatorioResponse`** ao `relatorio_controller` (hoje o endpoint retorna `dict` puro, sem validação OpenAPI). Ganha validação automática do schema e documentação Swagger precisa.
- **Adaptar o `RelatorioView.jsx`** ao novo schema: card "Dados do Cliente" com todos os campos fiscais, card "Resumo" lendo de `totais`, bloco "Detalhamento por Projeto" com sub-bloco "Tarefas" aninhado.
- **Teste de regressão** em `backend/tests/test_relatorios.py`: criar apontamento com **data fixa em mês/ano passado** (ex.: `date(2025, 5, 15)`) e gerar relatório pedindo esse mês/ano, garantindo que a query com `strftime` continua funcionando fora do mês atual. O test atual usa `date.today()`, que mascara esse cenário.
- **Manter o botão "Imprimir"** (gera PDF via `window.print()` do browser). Geração de PDF server-side com `reportlab`/`jsPDF` fica para uma change separada.

## Capabilities

### New Capabilities

- `relatorios`: contrato do endpoint `GET /api/v1/relatorios` — schema aninhado, campos fiscais do tomador, detalhamento por tarefa agrupado por projeto, totais consolidados, `mes_referencia`. Cobre a forma do response e o conjunto de regras que o frontend consome.

### Modified Capabilities

- (nenhum) — `task-attachments` e `date-handling` (únicas specs existentes) não são afetadas.

## Impact

- **Backend (3 arquivos modificados, 1 novo método no repository)**:
  - `backend/app/domain/schemas.py` — refatorar `RelatorioResponse` e criar sub-schemas `RelatorioClienteInfo`, `RelatorioTotais`, `RelatorioTarefaItem`, `RelatorioProjetoItem` (com campo `tarefas`).
  - `backend/app/application/services/relatorio_service.py` — popular o novo schema; chamar novo método do repository para tarefas.
  - `backend/app/infrastructure/repositories/relatorio_repository.py` — novo método `get_tarefas_by_cliente_mes_ano(cliente_id, mes, ano)` retornando lista de `{projeto_id, tarefa_id, titulo, total_horas}`.
  - `backend/app/api/v1/relatorio_controller.py` — adicionar `response_model=RelatorioResponse` ao endpoint `GET /relatorios`.
- **Frontend (1 arquivo modificado)**:
  - `frontend/src/components/Relatorios/RelatorioView.jsx` — adaptar leitura para `result.cliente.*`, `result.totais.*`, `proj.titulo`; renderizar campos fiscais no card do cliente; adicionar sub-bloco "Tarefas" dentro de cada projeto.
- **Testes (1 arquivo modificado, ~30 linhas)**:
  - `backend/tests/test_relatorios.py` — atualizar `test_relatorio_generation` para o novo schema (chaves `cliente.nome`, `totais.total_horas`, `projetos[0].titulo`, `projetos[0].tarefas`); adicionar `test_relatorio_mes_passado` com data fixa em mês/ano anterior ao atual.
- **API / wire format**: breaking change, conforme descrito. Único consumer é o frontend atualizado.
- **Dependências**: nada.
- **Risco de regressão**: baixo. A query `get_apontamentos_by_cliente_mes_ano` (existente) não muda; o novo método `get_tarefas_by_cliente_mes_ano` segue o mesmo padrão (`strftime` por mês/ano) e será coberto pelo novo test. O frontend é o único consumer, então a breaking change é local.
- **i18n / formatação**: o relatório usa `formatHoras` (decimal com vírgula) e `formatMoeda` (R$ X,XX) já existentes; sem mudança nesses helpers.
- **Performance**: a query nova (tarefas agrupadas) roda 1 vez por geração de relatório (operação manual do usuário, não em hot path). Sem impacto perceptível.
