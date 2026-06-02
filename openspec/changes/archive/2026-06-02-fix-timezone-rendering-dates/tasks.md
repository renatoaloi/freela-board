# Tasks: fix-timezone-rendering-dates

## 1. Criar helper de datas

- [x] 1.1 Criar `frontend/src/utils/date.js` exportando `formatDateBR(iso)` (split sem `new Date`, retorna `""` para entrada nula) e `getTodayLocalISO()` (getters locais, retorna `YYYY-MM-DD`).
- [x] 1.2 Adicionar comentário no topo do arquivo explicando o porquê da regra (string ISO `YYYY-MM-DD` é literal de calendário, não UTC) e que i18n está fora de escopo.

## 2. Substituir sites de renderização

- [x] 2.1 Em `frontend/src/components/Tarefas/TarefaDetail.jsx`, importar `formatDateBR` de `../../utils/date` e substituir `new Date(tarefa.data_criacao).toLocaleDateString('pt-BR')` na linha 172 por `formatDateBR(tarefa.data_criacao)`.
- [x] 2.2 Em `frontend/src/components/Tarefas/TarefaDetail.jsx`, substituir `new Date(ap.data).toLocaleDateString('pt-BR')` na linha 234 por `formatDateBR(ap.data)`.
- [x] 2.3 Em `frontend/src/components/Projetos/ProjetosList.jsx`, importar `formatDateBR` de `../../utils/date` e substituir `new Date(p.data_criacao).toLocaleDateString('pt-BR')` na linha 128 por `formatDateBR(p.data_criacao)`.
- [x] 2.4 Em `frontend/src/components/Dashboard/Dashboard.jsx`, importar `formatDateBR` de `../../utils/date` e substituir `new Date(p.data_criacao).toLocaleDateString('pt-BR')` na linha 200 por `formatDateBR(p.data_criacao)`.

## 3. Corrigir default do ApontamentoForm

- [x] 3.1 Em `frontend/src/components/Apontamentos/ApontamentoForm.jsx`, importar `getTodayLocalISO` de `../../utils/date` e substituir `new Date().toISOString().split('T')[0]` na linha 20 por `getTodayLocalISO()`.
- [x] 3.2 Em `frontend/src/components/Apontamentos/ApontamentoForm.jsx`, substituir `new Date().toISOString().split('T')[0]` na linha 50 (reset após salvar) por `getTodayLocalISO()`.

## 4. Verificação

- [x] 4.1 Rodar `cd frontend && npm run build` e confirmar que o bundle compila sem erros ou warnings novos.
- [x] 4.2 Conferir via `rg "new Date\([^)]*\)" frontend/src/components` que não restou nenhum `new Date(...).toLocaleDateString('pt-BR')` aplicado a `data_criacao` ou `ap.data` (matches legítimos, se houver, não devem incluir `.toLocaleDateString`).
- [x] 4.3 Subir backend (`cd backend && uvicorn app.main:app --reload --port 8000`) e frontend (`cd frontend && npm run dev`) e reproduzir manualmente o cenário do usuário: criar apontamento com data `11/06/2026`, voltar à lista, confirmar que exibe `11/06/2026` (não `10/06/2026`). ✓ Verificado pelo usuário em 2026-06-02.
- [x] 4.4 Atualizar `AGENTS.md` adicionando uma nota curta em "Frontend" (seção de arquitetura) sobre a regra: "Renderizar datas do backend: use `formatDateBR`/`getTodayLocalISO` de `src/utils/date.js`; nunca `new Date(iso).toLocaleDateString` ou `new Date().toISOString().split('T')[0]`."
