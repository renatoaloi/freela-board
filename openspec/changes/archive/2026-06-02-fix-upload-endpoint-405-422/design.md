## Context

O subsistema de anexos é formado por três peças: (1) o controller FastAPI em `backend/app/api/v1/upload_controller.py`, (2) o helper axios em `frontend/src/services/api.js` (`uploadAPI`), e (3) o componente `frontend/src/components/Common/FileUpload.jsx` montado dentro de `TarefaDetail.jsx` na aba "Anexos". Hoje as três peças divergem em três pontos:

1. Backend declara `files: list[UploadFile]`; frontend envia `formData.append('file', file)`.
2. Frontend chama `GET /upload/{tarefa_id}` para listar arquivos; essa rota nunca existiu.
3. Helper `uploadAPI.delete` chama o segundo path segment de "file_id", mas o backend o trata como `filename` (o UUID salvo em `tarefa.anexos`).

A verdade de quais anexos uma tarefa tem já vive em `TarefaModel.anexos` (coluna JSON, `list[str]`), retornada por `TarefaResponse.anexos`. O filesystem em `storage/{cliente_id}/{projeto_id}/{tarefa_id}/` é só o backing store — o JSON column é o índice.

A correção precisa mexer nos três lados de forma coordenada porque eles formam um circuito fechado: frontend lista → POST → backend persiste e devolve nomes salvos → frontend lista de novo → renderiza.

## Goals / Non-Goals

**Goals:**
- Fazer a aba "Anexos" funcionar ponta-a-ponta sem alterar a forma de armazenamento (filesystem + JSON column).
- Fazer o frontend consumir a verdade (`tarefa.anexos`) em vez de inventar um endpoint que não existe.
- Padronizar o nome do campo do form (`file`, singular) nos dois lados.
- Manter a interface HTTP atual: `POST/GET/DELETE /upload/{tarefa_id}[/filename]` — sem adicionar nem remover rotas.

**Non-Goals:**
- Adicionar suporte a upload múltiplo num único request (fora de escopo; o uso é sempre single-file).
- Migrar de filesystem para blob storage / S3.
- Trocar o esquema de nomes UUID por nomes humanizados.
- Adicionar autenticação por usuário, quotas, antivirus, ou scan de MIME.
- Internacionalização de mensagens de erro.

## Decisions

### 1. Campo FormData: `file` (singular) nos dois lados

**Decisão:** renomear parâmetro backend de `files: list[UploadFile]` para `file: UploadFile`. Frontend permanece `formData.append('file', file)`.

**Por quê:** o frontend envia exatamente um arquivo por request e processa um arquivo por vez (`FileUpload.jsx:46-48`, `e.dataTransfer.files[0]`). Manter o backend como `list[UploadFile]` seria simular capacidade que ninguém usa. O caminho de menor atrito é alinhar o singular nos dois lados e remover o `for file in files:` no controller.

**Alternativas consideradas:**
- *Manter `files: list[UploadFile]` e fazer o frontend enviar `formData.append('files', file)`.* Possível, mas força o caller JS a saber que pode mandar um array. Como o uso real é sempre unitário, é mais limpo o backend declarar o que ele realmente aceita.
- *Aceitar ambos os campos via `Union`.* Complexidade desnecessária, e abre ambiguidade.

### 2. Lista de anexos: ler de `tarefa.anexos`, não de uma rota nova

**Decisão:** remover `uploadAPI.list` e passar `anexos` para `FileUpload` via props. `TarefaDetail.jsx` já chama `tarefasAPI.get(id)` (`TarefaDetail.jsx:51`) e guarda o resultado em `tarefa`. Basta repassar `tarefa.anexos` para `FileUpload` e revalidar a tarefa após cada upload/delete.

**Por quê:** o backend **já tem** a fonte da verdade (`TarefaModel.anexos`, JSON column) e **já a devolve** em `TarefaResponse.anexos`. Criar `GET /upload/{tarefa_id}` seria duplicar informação e introduzir um problema de sincronia: o diretório em disco e a coluna JSON podem divergir após operações parciais. Lendo do JSON column, a UI sempre reflete o que o backend considera "salvo".

**Alternativas consideradas:**
- *Adicionar `GET /upload/{tarefa_id}` que lista lendo o diretório.* Cria fonte secundária de verdade e exige scan do filesystem a cada chamada. Rejeitado.
- *Adicionar `GET /upload/{tarefa_id}` que devolve `tarefa.anexos`.* Casca fina sobre `TarefaResponse.anexos`, sem ganho real. Rejeitado.

### 3. Helper `uploadAPI.delete`: renomear `file_id` → `filename`

**Decisão:** parâmetro JS vira `filename`. Internamente, é o valor que vai no path como segundo segmento, e o backend já o trata como filename (`upload_controller.py:78`).

**Por quê:** o valor guardado em `tarefa.anexos` **é** o filename (UUID + extensão, ver `upload_controller.py:45`). Não existe um `id` separado para o anexo. A assinatura `file_id` confundia quem lessem o helper achando que existe um identificador próprio.

**Alternativa considerada:**
- *Adicionar um campo `id` distinto no `tarefa.anexos`.* Exigiria migrar dados e mudar schema. Fora de proporção para um bug de nomenclatura.

### 4. `FileUpload` deixa de ser componente "data-loader"

**Decisão:** `FileUpload` vira puramente apresentacional. Recebe `anexos: string[]` e `onChange: () => void` via props. O pai (`TarefaDetail`) detém a verdade e dispara `fetchTarefa()` após mutações.

**Por quê:** elimina o `useEffect` que dispara `loadFiles()` (`FileUpload.jsx:21-23`) e centraliza a invalidação de cache. Padrão consistente com o resto do app (TarefasList, Kanban, Clientes list — todos puxam dados no pai, não no componente-folha).

**Alternativa considerada:**
- *Deixar `FileUpload` continuar com `useEffect` mas apontando para `tarefa.anexos` que veio via prop.* Possível, mas mistura ownership do estado.

## Risks / Trade-offs

- **Risco:** algum consumidor externo (curl, outro frontend) pode estar chamando `POST /upload/{tarefa_id}` com campo `files` (plural). **Mitigação:** o app é single-user local (`AGENTS.md`, "Auth"); não há documentação pública nem frontend alternativo. A mudança é interna. Se houver, o erro 422 atual já indicaria o problema, então pior cenário = mesmo sintoma.
- **Risco:** renomear o parâmetro no controller quebra qualquer teste/manual que chame a rota. **Mitigação:** `backend/tests/` não tem `test_upload.py` (verificado), então não há regressão automática; o que existe é a suíte 422/405 atual que passa a funcionar.
- **Trade-off:** ao mover a verdade para `TarefaDetail`, a aba "Anexos" re-renderiza o componente inteiro (e dispara `fetchTarefa`) após upload. Isso é uma request extra a `tarefasAPI.get`. Aceitável: o payload é pequeno, e evita o problema de sincronia mencionado na Decisão 2.
- **Risco:** se um anexo for removido manualmente do disco (fora do app), `tarefa.anexos` ainda o referencia e o link "baixar" quebra (404 do `GET /upload/.../filename`). **Mitigação:** já é o comportamento atual — fora do escopo desta change.

## Migration Plan

Sem migration de dados. Deploy em três passos, sem ordem rígida (as três pontas precisam estar alinhadas antes do próximo deploy):

1. Atualizar backend (`upload_controller.py`): `files` → `file`, remover loop.
2. Atualizar frontend (`api.js`, `FileUpload.jsx`, `TarefaDetail.jsx`): remover `list`, renomear `file_id` → `filename`, receber `anexos` via prop.
3. Subir a nova versão.

**Rollback:** como o estado em disco (`storage/...`) e o JSON column (`tarefas.anexos`) não são tocados, basta reverter código. Não há migração de schema.

## Open Questions

Nenhuma no momento. As três decisões (campo `file` singular, lista via `tarefa.anexos`, helper `filename`) cobrem todos os casos observados no console do browser.
