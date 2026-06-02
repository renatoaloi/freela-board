# Spec: task-attachments

> Capability: `task-attachments` — how the system handles file attachments on a task (storage model, list/download/delete via the upload controller, and frontend preview/cover rendering).

## Purpose

The system stores task attachments as files on disk under `storage/{cliente_id}/{projeto_id}/{tarefa_id}/` and tracks the list of attachment filenames in a JSON column on the `tarefas` table (`TarefaModel.anexos: list[str]`). The frontend reads `tarefa.anexos` directly via `tarefasAPI.get` rather than calling a list endpoint. Downloading a file requires the `X-API-Key` header, so the frontend always fetches via the authenticated `uploadAPI.download` helper and uses `URL.createObjectURL` for rendering — direct URLs to the backend cannot carry the header and would 422 in a new tab.

## Requirements

### Requirement: Upload de anexo único por tarefa

O sistema MUST aceitar o upload de um único arquivo por chamada via `POST /api/v1/upload/{tarefa_id}`. O campo do `multipart/form-data` MUST chamar-se `file` e MUST corresponder a um único `UploadFile`. O backend MUST persistir o arquivo em `storage/{cliente_id}/{projeto_id}/{tarefa_id}/` com nome gerado a partir de UUID preservando a extensão original, e MUST adicionar esse nome à lista `tarefa.anexos`.

#### Scenario: Upload bem-sucedido
- **WHEN** cliente envia `POST /api/v1/upload/{tarefa_id}` com `multipart/form-data` contendo o campo `file` preenchido
- **THEN** o backend MUST retornar `201` com `{ "filenames": ["<uuid><ext>"] }` e o arquivo MUST estar gravado em `storage/{cliente_id}/{projeto_id}/{tarefa_id}/<uuid><ext>` e MUST aparecer em `tarefa.anexos`

#### Scenario: Campo do form errado
- **WHEN** cliente envia `POST /api/v1/upload/{tarefa_id}` com `multipart/form-data` onde o campo se chama `files` (plural) em vez de `file`
- **THEN** o backend MUST retornar `422` (validation error) — comportamento correto de validação de schema

#### Scenario: Tarefa inexistente
- **WHEN** cliente envia `POST /api/v1/upload/{tarefa_id}` com `tarefa_id` que não existe no banco
- **THEN** o backend MUST retornar `404` com `detail: "Tarefa not found"` e MUST NOT criar diretórios em `storage/`

#### Scenario: Header de autenticação com valor inválido
- **WHEN** cliente envia `POST /api/v1/upload/{tarefa_id}` com `X-API-Key` cujo valor não corresponde à chave configurada
- **THEN** o backend MUST retornar `401` com `detail: "Invalid API Key"`

### Requirement: Listagem de anexos a partir de `tarefa.anexos`

O sistema MUST expor a lista de anexos de uma tarefa através do campo `anexos` em `TarefaResponse`, retornado por `GET /api/v1/tarefas/{id}` e por `GET /api/v1/tarefas` quando o cliente filtra por `projeto_id`. O sistema MUST NOT expor uma rota `GET /api/v1/upload/{tarefa_id}` para listagem.

#### Scenario: Tarefa com anexos
- **WHEN** cliente consulta `GET /api/v1/tarefas/{id}` e a tarefa tem `anexos = ["abc.pdf", "def.png"]`
- **THEN** a resposta MUST incluir `anexos: ["abc.pdf", "def.png"]`

#### Scenario: Tarefa sem anexos
- **WHEN** cliente consulta `GET /api/v1/tarefas/{id}` de uma tarefa recém-criada
- **THEN** `anexos` MUST ser `[]` (lista vazia, não `null`)

#### Scenario: Frontend consome `tarefa.anexos` diretamente
- **WHEN** o usuário abre a aba "Anexos" de uma tarefa no frontend
- **THEN** o frontend MUST renderizar os arquivos lendo `tarefa.anexos` (vindo de `tarefasAPI.get`) e MUST NOT fazer chamada a `GET /api/v1/upload/{tarefa_id}`

### Requirement: Download de anexo via filename

O sistema MUST servir o conteúdo de um anexo via `GET /api/v1/upload/{tarefa_id}/{filename}` onde `filename` é exatamente um dos valores de `tarefa.anexos`. A resposta MUST ser o `FileResponse` do arquivo no disco.

#### Scenario: Download existente
- **WHEN** cliente faz `GET /api/v1/upload/{tarefa_id}/abc.pdf` e o arquivo existe em disco e está referenciado em `tarefa.anexos`
- **THEN** o backend MUST retornar `200` com o conteúdo binário do arquivo

#### Scenario: Download inexistente
- **WHEN** cliente faz `GET /api/v1/upload/{tarefa_id}/inexistente.pdf`
- **THEN** o backend MUST retornar `404` com `detail: "File not found"`

### Requirement: Remoção de anexo mantém `tarefa.anexos` consistente

O sistema MUST remover um anexo via `DELETE /api/v1/upload/{tarefa_id}/{filename}`. A operação MUST apagar o arquivo do disco e MUST remover o `filename` da lista `tarefa.anexos` antes de retornar.

#### Scenario: Delete bem-sucedido
- **WHEN** cliente faz `DELETE /api/v1/upload/{tarefa_id}/abc.pdf` e `abc.pdf` está em `tarefa.anexos`
- **THEN** o backend MUST retornar `200`, o arquivo MUST não existir mais em disco e `tarefa.anexos` MUST não mais conter `"abc.pdf"`

#### Scenario: Delete de filename não referenciado
- **WHEN** cliente faz `DELETE /api/v1/upload/{tarefa_id}/fantasma.pdf` onde `fantasma.pdf` não está em `tarefa.anexos`
- **THEN** o backend MUST retornar `200` (idempotente para a coluna JSON) e MUST remover o arquivo do disco se ele existir

### Requirement: Helper frontend `uploadAPI` consistente com o backend

O helper `uploadAPI` no frontend MUST expor apenas operações que têm rota correspondente no backend: `upload` (POST), `download` (GET autenticado via `X-API-Key`, retorna `Blob`), `delete` (DELETE). MUST NOT expor `list` nem `getFileUrl` (a URL direta sem header não é utilizável porque o backend exige `X-API-Key`). A assinatura de `delete` MUST usar o nome `filename` para o segundo segmento do path, refletindo o que o backend trata.

#### Scenario: Helper não tem `list` nem `getFileUrl`
- **WHEN** o bundle do frontend é importado em qualquer componente
- **THEN** `uploadAPI` MUST NOT ter as chaves `list` nem `getFileUrl`

#### Scenario: Delete usa `filename`
- **WHEN** um caller chama `uploadAPI.delete(tarefaId, filename)` com `filename` sendo um valor de `tarefa.anexos`
- **THEN** a chamada HTTP resultante MUST ser `DELETE /api/v1/upload/{tarefaId}/{filename}`

#### Scenario: Download retorna Blob autenticado
- **WHEN** um caller chama `uploadAPI.download(tarefaId, filename)`
- **THEN** a chamada HTTP MUST ser `GET /api/v1/upload/{tarefaId}/{filename}` com header `X-API-Key` MUST estar presente, e `responseType` MUST ser `blob` (a `res.data` MUST ser uma instância de `Blob`)

### Requirement: Pré-visualização de anexo em modal autenticado

O frontend MUST oferecer um modal de pré-visualização para anexos. O modal MUST ser acionado ao clicar no nome de um arquivo na lista de anexos. O modal MUST buscar o conteúdo do anexo via `uploadAPI.download` (caminho autenticado por `X-API-Key`) e MUST criar uma `blob:` URL local via `URL.createObjectURL` para renderização. O frontend MUST NOT expor links diretos `http://...:8000/api/v1/upload/...` no DOM, porque esses links não carregam o header `X-API-Key` e resultariam em 422 ao serem abertos em nova aba.

#### Scenario: Click em imagem abre modal com a imagem renderizada
- **WHEN** o usuário clica em um arquivo de imagem (extensão `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, `.bmp` ou `.ico`) na lista de anexos
- **THEN** o frontend MUST abrir um modal e MUST renderizar a imagem dentro de um `<img src={blobUrl}>` com `max-h-[70vh]`, contendo o conteúdo binário do arquivo

#### Scenario: Click em PDF abre modal com o PDF renderizado
- **WHEN** o usuário clica em um arquivo com extensão `.pdf` na lista de anexos
- **THEN** o frontend MUST abrir um modal e MUST renderizar o PDF dentro de um `<iframe src={blobUrl}>` com altura mínima de `70vh`

#### Scenario: Click em tipo sem preview mostra fallback
- **WHEN** o usuário clica em um arquivo cuja extensão NÃO é imagem nem PDF (ex.: `.txt`, `.zip`, `.docx`)
- **THEN** o frontend MUST abrir um modal com a mensagem "Pré-visualização não disponível para este tipo de arquivo" e MUST oferecer um botão "Baixar" que dispara download do blob local com o nome original do arquivo

#### Scenario: Modal sempre oferece botão Baixar
- **WHEN** o modal de pré-visualização exibe qualquer arquivo (imagem, PDF ou outro)
- **THEN** o modal MUST oferecer um botão "Baixar" no rodapé, MUST estar desabilitado enquanto o conteúdo está carregando, e MUST disparar download do blob local com o nome original quando clicado

#### Scenario: Falha no download mostra erro e fecha
- **WHEN** `uploadAPI.download` falha (ex.: backend retorna 401/404/500)
- **THEN** o modal MUST mostrar a mensagem "Não foi possível carregar o arquivo." e MUST NOT deixar o botão "Baixar" habilitado

#### Scenario: Blob URL é revogada ao fechar
- **WHEN** o modal é fechado (via X, ESC ou clique no backdrop)
- **THEN** o frontend MUST chamar `URL.revokeObjectURL(blobUrl)` para a URL criada, evitando leak de memória

### Requirement: Capa da tarefa a partir do primeiro anexo de imagem

Quando a tarefa possuir ao menos um anexo com extensão de imagem (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, `.bmp` ou `.ico`), o frontend MUST renderizar esse anexo como "capa" no topo da `TarefaDetail`, acima do card de título/descrição. A capa MUST ser a primeira imagem presente em `tarefa.anexos` (ordem é a de inserção). Clicar na capa MUST abrir o mesmo modal de pré-visualização descrito no requirement anterior, com a filename correspondente.

#### Scenario: Tarefa sem imagem não tem capa
- **WHEN** `tarefa.anexos` é vazio, ou contém apenas arquivos não-imagem
- **THEN** a `TarefaDetail` MUST NOT renderizar o bloco de capa

#### Scenario: Tarefa ainda carregando não quebra a UI
- **WHEN** o estado `tarefa` é `null` (estado inicial antes do `fetchTarefa` resolver, ou após erro fatal)
- **THEN** a `TarefaDetail` MUST NOT tentar ler `tarefa.anexos` antes do guard `if (!tarefa) return ...`, MUST NOT lançar `TypeError`, e MUST renderizar o estado de loading/erro/"não encontrada" sem o bloco de capa

#### Scenario: Tarefa com imagem renderiza capa
- **WHEN** `tarefa.anexos` contém ao menos um arquivo com extensão de imagem
- **THEN** a `TarefaDetail` MUST renderizar um `<img>` com `max-h-64` e `object-cover` mostrando o primeiro anexo de imagem, MUST usar a mesma blob URL autenticada do helper, e MUST abrir o modal de pré-visualização ao ser clicada

#### Scenario: Capa atualiza após upload
- **WHEN** o usuário faz upload de uma nova imagem e a tarefa é revalidada (`fetchTarefa`)
- **THEN** a capa MUST refletir o novo `tarefa.anexos` (se a nova imagem for a primeira imagem, ela MUST virar a capa; caso contrário a capa permanece a anterior)

#### Scenario: Capa some quando a única imagem é removida
- **WHEN** o usuário remove o único anexo de imagem da tarefa
- **THEN** a `TarefaDetail` MUST remover o bloco de capa no próximo render
