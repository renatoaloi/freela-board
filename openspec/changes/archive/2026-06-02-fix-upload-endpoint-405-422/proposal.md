## Why

Uploads de anexos na aba "Anexos" de uma tarefa estão quebrados. O console do navegador mostra dois erros ao interagir com a tela:

- `405 Method Not Allowed` em `GET /api/v1/upload/{tarefa_id}` — disparado ao abrir a aba (e após cada upload).
- `422 Unprocessable Entity` em `POST /api/v1/upload/{tarefa_id}` — disparado ao arrastar/selecionar um arquivo.

Resultado prático: o usuário não consegue anexar PDFs nem imagens a uma tarefa, e mesmo que consiga nada aparece na lista. Investigação no código (`backend/app/api/v1/upload_controller.py`, `frontend/src/services/api.js`, `frontend/src/components/Common/FileUpload.jsx`) revela **três inconsistências entre frontend e backend** que precisam ser corrigidas em conjunto — qualquer patch parcial deixa o fluxo ainda quebrado.

## What Changes

- **Alinhar nome do campo FormData com o parâmetro do backend**: o backend aceita `files: list[UploadFile]` mas o frontend envia `formData.append('file', file)` (singular). Decidido: padronizar em **`file` (singular) no backend**, casando com a realidade de uso (um arquivo por request) e com o helper atual do frontend. O backend passa a aceitar um único `UploadFile` por chamada.
- **Remover o helper `uploadAPI.list`**: o frontend chama `GET /api/v1/upload/{tarefa_id}` mas essa rota não existe (o backend só define `POST /upload/{tarefa_id}` e `GET/DELETE /upload/{tarefa_id}/{filename}`). A lista de anexos já vem em `TarefaResponse.anexos` (campo JSON da tabela `tarefas`). `FileUpload.jsx` deve passar a consumir `tarefa.anexos` via prop, em vez de fazer fetch independente.
- **Renomear parâmetro `file_id` → `filename` em `uploadAPI.delete`**: o segundo segmento do path é tratado pelo backend como `filename` (nome UUID salvo em disco + JSON `anexos`), não como um `id` de arquivo. A assinatura JS estava enganosa. **BREAKING** apenas para o helper JS, que tem 1 caller (`FileUpload.jsx`).

Nenhuma rota de API é adicionada ou removida. Nenhuma migration. Nenhuma mudança em schema Pydantic além do parâmetro do controller.

## Capabilities

### New Capabilities

- `task-attachments`: define como o sistema lida com anexos de uma tarefa — modelo de armazenamento (filesystem + JSON column), contrato entre o que o backend persiste e o que o frontend consome para listar/exibir, e regras de validação de upload (campos, formato, quantidade por request). Introduzido porque ainda não existe nenhum spec cobrindo o subsistema de anexos.

### Modified Capabilities

- Nenhuma capability existente tem REQUIREMENTS alterados. (`openspec/specs/` está vazio no momento — não há spec prévia para anexos nem para o restante do domínio.)

## Impact

**Backend** (`backend/app/api/v1/upload_controller.py`):
- `POST /upload/{tarefa_id}`: parâmetro `files: list[UploadFile]` → `file: UploadFile`. Loop interno que itera sobre `files` vira leitura única. Nenhuma outra rota muda.
- `STORAGE_PATH`/`anexos` no DB: inalterados.

**Frontend** (`frontend/src/services/api.js`, `frontend/src/components/Common/FileUpload.jsx`, `frontend/src/components/Tarefas/TarefaDetail.jsx`):
- Remover `uploadAPI.list` de `api.js`.
- Renomear parâmetro de `uploadAPI.delete` de `file_id` para `filename`.
- `FileUpload.jsx`: receber `anexos` (lista) e `onChange`/`onUploaded` via props em vez de buscar via API; remover chamada `loadFiles()`.
- `TarefaDetail.jsx`: passar `anexos` da tarefa carregada e fazer refetch da tarefa após upload/delete (já existe `fetchTarefa`, fácil de reutilizar).

**Auth / storage / DB**: zero impacto. Token `X-API-Key`, path em disco `storage/{cliente_id}/{projeto_id}/{tarefa_id}/` e coluna JSON `tarefas.anexos` continuam iguais.

**Testes**: `backend/tests/conftest.py` e suíte atual não cobrem upload — sem regressão. Adicionar `backend/tests/test_upload.py` cobrindo o POST corrigido, GET por filename e DELETE.

## Follow-up adjustments (pós-teste manual)

Após o primeiro deploy de teste, o usuário reportou que o link `<a target="_blank">` construído pelo helper `getFileUrl` abria uma nova aba direto na URL do backend, **sem o header `X-API-Key`**, e o backend respondia com 422 (`missing header x-api-key`). Esse é o mesmo motivo pelo qual `getFileUrl` é desaconselhado: o browser, ao abrir uma URL colada diretamente, não envia headers customizados.

Decisões adicionais incorporadas a esta change:

- **Trocar `uploadAPI.getFileUrl` por `uploadAPI.download`**, que retorna um `Blob` via `api.get(..., { responseType: 'blob' })` (axios preserva o header `X-API-Key` default). Sem rotas novas no backend.
- **Modal de pré-visualização** (`FilePreviewModal.jsx`): abre ao clicar no nome de um anexo. Renderiza `<img>` para imagens, `<iframe>` para PDFs, fallback "baixar" para outros tipos. Usa `URL.createObjectURL` + `URL.revokeObjectURL` para ciclo de vida do blob. Sem mudanças de backend.
- **Capa da tarefa**: o primeiro anexo com extensão de imagem é renderizado como `capa` no topo da `TarefaDetail` (entre o botão "Voltar" e o card principal). Clicar na capa abre o mesmo modal. Sem mudanças de backend — `TarefaResponse.anexos` já carrega a informação necessária.

Nenhuma rota nova foi adicionada. Nenhuma migration. Backend inalterado a partir do fix inicial.
