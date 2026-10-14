## Why

Tarefas criadas no projeto errado não podem ser corrigidas hoje: `TarefaUpdate` não aceita `projeto_id` e não existe ação de movimentação. O único caminho é excluir e recriar — o que perde os apontamentos de horas já lançados (e os anexos), e quebraria o histórico de quem já tem relatório.

Como o upload é gravado em `storage/{cliente_id}/{projeto_id}/{tarefa_id}/` (`upload_controller.py:_get_storage_path`), a troca de projeto **não é só um UPDATE de FK**: os arquivos precisam ser movidos em disco para a pasta do novo projeto, senão download e preview passam a retornar 404.

## What Changes

- **Novo endpoint de transferência**: `PATCH /api/v1/tarefas/{id}/projeto` (body: `projeto_id`) que valida o destino e move a tarefa dentro do **mesmo cliente**.
- **Anexos acompanham a tarefa**: o diretório de upload é movido para a pasta do novo projeto na mesma operação (a lista `anexos` da tarefa não muda).
- **Regras de bloqueio**: destino inexistente → 404; destino de outro cliente → 400/422; destino igual à origem → 400; tarefa `fechada` ou já vinculada a relatório fechado → 409.
- **Frontend**: ação "Mover para outro projeto" disponível na tela de detalhe da tarefa (`/tarefas/:id`) e no menu do card do Kanban, abrindo um modal com o seletor de projetos do mesmo cliente.

## Capabilities

### New Capabilities
- `tarefa-transferencia-projeto`: Transferência de uma tarefa entre projetos do mesmo cliente, com realocação dos anexos no storage e bloqueio de tarefas já fechadas ou vinculadas a relatório

### Modified Capabilities
<!-- nenhuma -->

## Impact

**Backend:**
- `app/domain/schemas.py` — novo schema `TarefaProjetoUpdate` (`projeto_id`)
- `app/api/v1/tarefa_controller.py` — novo endpoint `PATCH /tarefas/{id}/projeto`
- `app/application/services/tarefa_service.py` — novo método `mover_projeto(id, projeto_id)` com validações e realocação dos anexos
- `app/infrastructure/repositories/tarefa_repository.py` — consultas de apoio (tarefa com projeto/cliente e projetos irmãos)
- `app/application/services/upload_service.py` (**novo**) ou módulo utilitário — mover `storage/{cliente}/{projeto_origem}/{tarefa}` → `storage/{cliente}/{projeto_destino}/{tarefa}`
- Nova consulta em `RelatorioRepository`/`RelatorioTarefaModel` para checar vínculo com relatório fechado

**Frontend:**
- `src/services/api.js` — `tarefasAPI.moverProjeto(id, projeto_id)` e listagem de projetos por cliente (já existe via `projetosAPI.list(cliente_id)`)
- `src/components/Tarefas/TarefaDetail.jsx` — botão "Mover para outro projeto" + modal de seleção
- `src/components/Kanban/KanbanCard.jsx` — menu/ação que abre o mesmo modal (com recarrego do board)
- Eventual componente compartilhado (ex.: `Common/MoverTarefaProjetoModal.jsx`)

**Testes:**
- Novo `backend/tests/test_tarefa_projeto.py` validando destino do mesmo cliente, rejeição de outro cliente, 409 em tarefa fechada/vinculada a relatório, movimentação dos anexos no storage (monkeypatch de `STORAGE_PATH`, padrão já usado em `test_upload.py`)

**Dados:** sem migration — usa as tabelas existentes (`tarefas`, `projetos`, `relatorio_tarefas`).
