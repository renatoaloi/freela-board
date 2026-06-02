## 1. Backend — alinhar controller

- [x] 1.1 Em `backend/app/api/v1/upload_controller.py`, renomear parâmetro de `POST /{tarefa_id}` de `files: list[UploadFile]` para `file: UploadFile` e remover o `for file in files:` (ler o arquivo uma vez). Manter retorno `{"filenames": [<uuid><ext>]}` para preservar o shape consumido por qualquer outro caller.
- [x] 1.2 Verificar que `_get_tarefa`, `_get_storage_path` e as rotas GET/DELETE não foram alteradas.

## 2. Frontend — helper `uploadAPI`

- [x] 2.1 Em `frontend/src/services/api.js`, remover a chave `list` do objeto `uploadAPI` (a rota `GET /upload/{tarefa_id}` deixa de existir).
- [x] 2.2 Em `frontend/src/services/api.js`, renomear o segundo parâmetro de `uploadAPI.delete` de `file_id` para `filename` (não muda o path montado, só a nomenclatura do helper).

## 3. Frontend — `FileUpload` deixa de buscar dados

- [x] 3.1 Em `frontend/src/components/Common/FileUpload.jsx`, remover o `useEffect` que chama `loadFiles()` e a função `loadFiles` em si.
- [x] 3.2 Substituir a prop `tarefaId` por duas props: `tarefaId` (para montar URLs e disparar mutations) e `anexos: string[]` (lista vinda do pai). Adicionar prop `onChange: () => void` para o pai revalidar a tarefa após upload/delete.
- [x] 3.3 Trocar o `await uploadAPI.upload(tarefaId, file, ...)` (mantém igual) e, em vez de chamar `loadFiles()` no fim, chamar `onChange()`.
- [x] 3.4 Trocar `await uploadAPI.delete(tarefaId, fileId)` por `await uploadAPI.delete(tarefaId, filename)` (passar o `filename` que está no `file.filename`/`file.id || file.filename` da renderização).
- [x] 3.5 Trocar a chamada de `getFileUrl(file.filename)` no link de download — manter como está, mas garantir que `file` aqui é a string do `anexos` (UUID+ext).

## 4. Frontend — `TarefaDetail` fornece a verdade

- [x] 4.1 Em `frontend/src/components/Tarefas/TarefaDetail.jsx`, passar para `<FileUpload>` as props `tarefaId={id}`, `anexos={tarefa.anexos || []}` e `onChange={fetchTarefa}`.
- [x] 4.2 Confirmar que `fetchTarefa` é estável (já é `useCallback`) e que o re-render de `TarefaDetail` repassa a lista atualizada para `FileUpload`.

## 5. Testes — cobrir o contrato

- [x] 5.1 Criar `backend/tests/test_upload.py` com fixtures mínimas: `client`, `headers`, `created_tarefa` (já existem em `conftest.py`).
- [x] 5.2 Adicionar teste: `POST /api/v1/upload/{tarefa_id}` com `files={"file": (BytesIO(b"x"), "a.txt")}}` retorna 201, retorna UUID em `filenames`, arquivo existe em disco e `tarefa.anexos` contém o UUID após `GET /api/v1/tarefas/{id}`.
- [x] 5.3 Adicionar teste: `POST /api/v1/upload/{tarefa_id}` com campo errado (ex.: `{"files": (...)}`) retorna 422.
- [x] 5.4 Adicionar teste: `GET /api/v1/upload/{tarefa_id}/{filename}` após upload retorna 200 com o conteúdo.
- [x] 5.5 Adicionar teste: `DELETE /api/v1/upload/{tarefa_id}/{filename}` remove arquivo do disco e tira o filename de `tarefa.anexos`.
- [x] 5.6 Rodar `cd backend && pytest -v` e garantir que nada existente quebrou.

## 6. Verificação manual ponta-a-ponta

- [x] 6.1 Subir backend (`uvicorn app.main:app --reload --port 8000`) e frontend (`npm run dev`). Limpar `storage/freelaboard.db` para começar do zero.
- [x] 6.2 Criar cliente → projeto → tarefa. Abrir a tarefa, aba "Anexos". Confirmar que **NÃO** aparece `GET /api/v1/upload/...` 405 no console do browser.
- [x] 6.3 Arrastar um arquivo PDF. Confirmar que **NÃO** aparece 422; arquivo aparece na lista após o upload.
- [x] 6.4 Clicar no link de download. Confirmar que abre o arquivo.
- [x] 6.5 Excluir o anexo. Confirmar que some da lista, arquivo some do disco e `tarefa.anexos` não o referencia mais.

## 7. Follow-up — preview modal e capa (pós-teste manual)

Bug encontrado: `<a href={uploadAPI.getFileUrl(...)} target="_blank">` jogava o browser na URL direta do backend, sem header `X-API-Key`, gerando 422 ao abrir. Solução: trocar a URL por uma chamada axios autenticada (Blob) e abrir um modal de preview.

- [x] 7.1 Em `frontend/src/services/api.js`, substituir `getFileUrl: (tarefa_id, filename) => "http://..."` por `download: (tarefa_id, filename) => api.get(\`/upload/${tarefa_id}/${filename}\`, { responseType: 'blob' })`.
- [x] 7.2 Criar `frontend/src/components/Common/FilePreviewModal.jsx` que recebe `tarefaId`, `filename`, `isOpen`, `onClose`. Faz fetch via `uploadAPI.download`, cria `URL.createObjectURL`, classifica o arquivo por extensão (image/pdf/other), renderiza `<img>` para imagens, `<iframe>` para PDF, fallback com botão "Baixar" para outros. Revoga a URL no cleanup.
- [x] 7.3 Em `frontend/src/components/Common/FileUpload.jsx`, trocar o `<a href={getFileUrl(...)} target="_blank">` por um `<button>` que abre o `FilePreviewModal` com o filename clicado. Remover a chamada `getFileUrl` (não existe mais).
- [x] 7.4 Em `frontend/src/components/Tarefas/TarefaDetail.jsx`, importar `uploadAPI` e `FilePreviewModal`. Adicionar `coverModalFile` no state. Calcular `coverImage = pickCoverImage(tarefa.anexos)`. Renderizar `<TaskCover>` acima do card principal (apenas se houver cover). Renderizar `<FilePreviewModal>` no final, controlado por `coverModalFile`.
- [x] 7.5 Definir `TaskCover` (mini-componente) dentro de `TarefaDetail.jsx`: busca seu próprio blob via `uploadAPI.download`, renderiza um `<img max-h-64 object-cover>` como botão. Clicar chama `onOpen(filename)` (que abre o modal).
- [x] 7.6 Atualizar `specs/task-attachments/spec.md`: (a) trocar o requirement do helper para listar `download` em vez de `getFileUrl`; (b) adicionar requirement "Pré-visualização de anexo em modal autenticado" com 6 scenarios; (c) adicionar requirement "Capa da tarefa a partir do primeiro anexo de imagem" com 4 scenarios.
- [x] 7.7 Atualizar `proposal.md` com seção "Follow-up adjustments" descrevendo o bug do `getFileUrl` sem header e as decisões de preview + capa.
- [x] 7.8 Rodar `cd backend && pytest -q` para garantir que nada existente quebrou (38/38 deve continuar passando — backend inalterado).
- [x] 7.9 Bug pós-deploy: `TypeError: Cannot read properties of null (reading 'anexos')` no console do browser. Causa: `pickCoverImage(tarefa.anexos)` chamado ANTES do guard `if (!tarefa) return`. Fix: mover a linha para DEPOIS do guard. Adicionar scenario "Tarefa ainda carregando não quebra a UI" no spec.
