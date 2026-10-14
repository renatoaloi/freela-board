## 1. Backend — Schemas e validações

- [x] 1.1 Adicionar schema `TarefaProjetoUpdate` (`projeto_id: str`) em `app/domain/schemas.py`
- [x] 1.2 Adicionar consulta em `TarefaRepository` que carregue a tarefa com o projeto/cliente atual (join) para validações
- [x] 1.3 Adicionar consulta que verifique vínculo da tarefa com relatório fechado (`RelatorioTarefaModel` por `tarefa_id`)

## 2. Backend — Serviço de transferência

- [x] 2.1 Implementar `TarefaService.mover_projeto(id, projeto_id)` com validações: tarefa existe (404), projeto destino existe (404), mesmo cliente (400), destino diferente da origem (400)
- [x] 2.2 Bloquear transferência de tarefa `fechada` ou vinculada a relatório fechado com `409`
- [x] 2.3 Adicionar helper de movimentação dos anexos (`storage/{cliente}/{projeto_origem}/{tarefa}` → `storage/{cliente}/{projeto_destino}/{tarefa}`), sem duplicar a construção do caminho do storage
- [x] 2.4 Garantir que nenhuma pasta vazia fique na origem quando não houver mais arquivos
- [x] 2.5 Reverter a movimentação dos arquivos se a persistência falhar (manter tudo como estava na origem)

## 3. Backend — Controller

- [x] 3.1 Adicionar endpoint `PATCH /api/v1/tarefas/{id}/projeto` em `tarefa_controller.py` com resposta `TarefaResponse`
- [x] 3.2 Garantir `Depends(get_api_key)` no novo endpoint (401 sem chave/chave inválida)

## 4. Frontend — Serviço e UI

- [x] 4.1 Adicionar `tarefasAPI.moverProjeto(id, projeto_id)` em `src/services/api.js`
- [x] 4.2 Criar `src/components/Common/MoverTarefaProjetoModal.jsx` com seletor de projetos do mesmo cliente (usa `projetosAPI.list(cliente_id)`)
- [x] 4.3 Adicionar ação "Mover para outro projeto" em `src/components/Tarefas/TarefaDetail.jsx` recarregando a tarefa após o sucesso
- [x] 4.4 Adicionar a mesma ação no card do Kanban (`src/components/Kanban/KanbanCard.jsx`) com recarrego do board
- [x] 4.5 Exibir erros 400/404/409 via `AlertModal` (sem `window.alert`)

## 5. Testes

- [x] 5.1 Adicionar fixture em `backend/tests/conftest.py` para um segundo projeto do mesmo cliente
- [x] 5.2 Criar `backend/tests/test_tarefa_projeto.py`: transferência válida, rejeição de cliente diferente, destino inexistente (404), origem igual ao destino (400), tarefa fechada (409), tarefa em relatório fechado (409)
- [x] 5.3 Testar realocação dos anexos com `monkeypatch` de `settings.STORAGE_PATH` para `tmp_path` (padrão de `test_upload.py`), verificando download pelo novo caminho
- [x] 5.4 Rodar `cd backend && pytest -v` — verde quando não houver falhas além dos 3 testes de PDF skipados

## 6. Documentação

- [x] 6.1 Documentar o endpoint `PATCH /tarefas/{id}/projeto` na tabela de endpoints do `README.md`
