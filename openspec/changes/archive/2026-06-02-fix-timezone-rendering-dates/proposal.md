## Why

O frontend está renderizando datas vindas do backend com **defasagem de um dia** em fusos a oeste do UTC (ex.: Brasil, UTC-3). Ao digitar `11/06/2026` em um apontamento, o usuário vê `10/06/2026` na lista. O mesmo bug aparece na data de criação de tarefas, projetos e no card "Últimos projetos" do Dashboard. A causa-raiz é `new Date("YYYY-MM-DD")`, que a spec ECMAScript define como **UTC midnight** — `toLocaleDateString('pt-BR')` então converte para o fuso local, recuando um dia em fusos negativos. O backend está correto (Pydantic `date` + SQLAlchemy `Date` + SQLite guardam e devolvem a string ISO limpa); o bug é puro de **renderização no frontend** e se repete em 4 sites. O default do `ApontamentoForm` (`new Date().toISOString().split('T')[0]`) tem problema espelhado: após 21h BRT, o "hoje" vira "amanhã".

## What Changes

- Adicionar `frontend/src/utils/date.js` exportando `formatDateBR(iso)` (formata `YYYY-MM-DD` → `dd/MM/yyyy` sem conversão de fuso) e `getTodayLocalISO()` (devolve a data de hoje no fuso do navegador, formato `YYYY-MM-DD`).
- Substituir os 4 sites `new Date(x).toLocaleDateString('pt-BR')` por `formatDateBR(x)` em:
  - `frontend/src/components/Tarefas/TarefaDetail.jsx` (linha 172 — `tarefa.data_criacao`; linha 234 — `ap.data`).
  - `frontend/src/components/Projetos/ProjetosList.jsx` (linha 128 — `p.data_criacao`).
  - `frontend/src/components/Dashboard/Dashboard.jsx` (linha 200 — `p.data_criacao`).
- Substituir o default inicial de data em `frontend/src/components/Apontamentos/ApontamentoForm.jsx` (linha 20 e linha 50) por `getTodayLocalISO()`.
- **Sem mudanças no backend.** Storage, schema, validação e serialização permanecem como estão — `ApontamentoCreate.data`, `TarefaCreate.data_criacao`, `ProjetoCreate.data_criacao` continuam aceitando e devolvendo `YYYY-MM-DD` (Pydantic v2 + SQLAlchemy `Date` + SQLite).
- **Sem novas dependências.** Continua zero-dep fora de React/Router/Axios/Tailwind/Heroicons.

## Capabilities

### New Capabilities

- `date-handling`: convenção do frontend para **receber, exibir e gerar datas** que vieram do backend. Garante que a string `YYYY-MM-DD` é tratada como literal de calendário (sem conversão de fuso) e centraliza a formatação em um único helper. Aplica-se a qualquer data de domínio (`apontamento.data`, `tarefa.data_criacao`, `projeto.data_criacao`).

### Modified Capabilities

- (nenhum) — `task-attachments` (única spec existente) não é afetado: as datas de `created_at`/`updated_at` da resposta não são renderizadas com `toLocaleDateString` em lugar nenhum, e a parte de anexos não envolve datas.

## Impact

- **Frontend (1 novo arquivo, 4 modificados)**:
  - `frontend/src/utils/date.js` (novo, ~15 linhas).
  - `frontend/src/components/Tarefas/TarefaDetail.jsx`.
  - `frontend/src/components/Projetos/ProjetosList.jsx`.
  - `frontend/src/components/Dashboard/Dashboard.jsx`.
  - `frontend/src/components/Apontamentos/ApontamentoForm.jsx`.
- **Backend**: nada.
- **Banco / storage**: nada.
- **API / contrato externo**: nada — formato `YYYY-MM-DD` continua sendo o wire format.
- **Dependências**: nada.
- **Testes**:
  - Backend: 38 testes existentes permanecem válidos (eles não cobrem formatação, só que o backend guarda/retorna ISO, que continua correto).
  - Frontend: não há infra de teste de componente no repo. Validação do fix será manual (reproduzir o cenário do usuário: digitar `11/06/2026`, salvar, recarregar, conferir que continua `11/06/2026`).
  - Critério de aceitação manual: criar apontamento com data X, voltar pra lista, ver data X (não X-1).
- **Risco de regressão**: baixo. A mudança elimina a categoria de bug (conversão de fuso em string ISO), não introduz novo comportamento além de "mostrar o que foi salvo".
- **i18n**: o app é pt-BR single-user local; formato `dd/MM/yyyy` hard-coded no helper é consistente com o resto da UI. Sem impacto.
