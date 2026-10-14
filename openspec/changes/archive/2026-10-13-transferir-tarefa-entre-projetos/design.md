## Context

Hoje `TarefaUpdate` só aceita `titulo`, `descricao`, `status`, `data_criacao` e `anexos` — não há caminho para trocar `projeto_id`. `TarefaModel.projeto_id` tem FK para `projetos.id` e os uploads ficam em disco sob `storage/{cliente_id}/{projeto_id}/{tarefa_id}/`, caminho montado em runtime por `upload_controller._get_storage_path()` a partir de `tarefa.projeto.cliente_id` e `tarefa.projeto_id`. Ou seja: mudar só a FK deixa os arquivos órfãos e o download quebra com 404.

Existe ainda o vínculo `relatorio_tarefas` (criado no change `fechamento-mensal-relatorios`), que permite saber se uma tarefa já entrou num relatório fechado — insumo para a regra de bloqueio.

Requisitos em `specs/tarefa-transferencia-projeto/spec.md`; motivação em `proposal.md`.

## Goals / Non-Goals

**Goals:**
- Endpoint e UI para mover uma tarefa entre projetos do mesmo cliente
- Realocar os anexos no disco na mesma operação
- Bloquear tarefas `fechadas` ou já faturadas
- Falhas não deixam estado intermediário (FK mexida e arquivo parado no meio)

**Non-Goals:**
- Mover entre clientes (não faz sentido: o cliente é o tomador do relatório)
- Mover várias tarefas de uma vez (lote)
- Alterar apontamentos, horas ou valores na transferência
- Editar projeto via `PUT /tarefas/{id}` (o endpoint genérico continua sem `projeto_id`)
- Drag-and-drop de cards entre projetos no Kanban

## Decisions

### D1 — Endpoint dedicado em vez de liberar `projeto_id` no PUT
Será criado `PATCH /api/v1/tarefas/{id}/projeto` com body `{ projeto_id }`.

- *Alternativa*: adicionar `projeto_id` ao `TarefaUpdate` e reusar `PUT /tarefas/{id}`. Rejeitada: o PUT hoje é usado pelo drag-and-drop do Kanban (só status) e por edições de formulário; liberar a troca de projeto nele espalharia a regra de realocação de anexos e as validações de cliente/relatório por todos os caminhos, e não deixaria explícita a intenção na API.

### D2 — Service orquestra validação + update + mover arquivos
`TarefaService.mover_projeto(id, projeto_id)` faz: busca tarefa (404) → busca projeto destino (404) → valida `destino.cliente_id == atual.cliente_id` (400) e `destino.id != atual.id` (400) → bloqueia se `status == fechada` ou se existe linha em `relatorio_tarefas` (409) → move diretório de anexos → `commit`.

A movimentação dos arquivos fica num helper (`app/application/services/upload_service.py` ou função em `tarefa_service`) que resolve os dois caminhos a partir de `settings.STORAGE_PATH`, cria o diretório de destino, move cada arquivo da lista `anexos` e remove a pasta de origem se ficar vazia. Um único helper mantém a regra de storage junto da leitura/escrita, sem duplicar a construção do path (hoje espalhada nos três endpoints do upload controller).

### D3 — Ordem: arquivos primeiro, commit depois; rollback em memória
Como SQLite suporta transação mas mover arquivo **não**, a ordem é: mover arquivos → persistir FK → commit. Se o commit falhar, os arquivos são movidos de volta (best effort) e a exceção é propagada; se o `move` falhar antes, nada foi escrito no banco. Isso garante o cenário "Falha ao mover reverte tudo" sem exigir two-phase commit, que seria desproporcional para um app single-user.

- *Alternativa*: permitir estado inconsistente e expor um endpoint de “reparo”. Rejeitada: pior experiência e mais superfície de API.

### D4 — Checagem de relatório por tabela de vínculo
A consulta usa `RelatorioTarefaModel` (existente) filtrando por `tarefa_id` — mesma fonte usada para impedir que a tarefa reapareça como elegível em outro fechamento. Não depende do status, por isso cobre o caso de tarefa reaberta após faturada.

### D5 — UI compartilhada entre detalhe e Kanban
Um único componente de modal (`Common/MoverTarefaProjetoModal.jsx`) é usado por `TarefaDetail.jsx` e pelo card do Kanban (`KanbanCard.jsx`), alimentado por `projetosAPI.list(cliente_id)` — o cliente é obtido a partir do projeto atual da tarefa. Evita duplicar seleção/validação em dois lugares e mantém o padrão de `Modal`/`AlertModal` do repo.

- *Alternativa*: ação só no detalhe (usuário descartou) ou drag-and-drop entre colunas de projeto (usuário descartou; exigiria retrabalhar o `DragDropContext`, que hoje só troca status).

## Risks / Trade-offs

- **Arquivo move é operação de SO**: permissões/volume só de leitura (ex.: Docker com bind mount restrito) → a transferência falha e nada é gravado; erro é retornado ao usuário. Mitigação: checar `Path.rename` e propagar 500 com mensagem clara.
- **Duas tarefas no mesmo destino**: não há constraint de unicidade de título — aceito, sem impacto.
- **Tarefa transferida passa a valer para o fechamento do novo projeto**: esperado (horas agora são do projeto destino); relatórios futuros refletem isso.
- **Tarefas `fechadas` bloqueadas** → se o usuário quiser corrigir um projeto de tarefa já faturada, precisa antes reabrir e desvincular — aceito (decisão de produto confirmada; evita divergir do snapshot).

## Migration Plan

Sem migration de schema. Deploy normal (backend + rebuild do frontend; no Raspberry, `docker compose up -d --build` — lembrando que o código do backend entra via imagem, não há bind mount). Rollback = reverter o commit; nenhum dado é migrado e nada existente é alterado automaticamente.

## Open Questions

- Nenhuma: o recorte (mesmo cliente), os bloqueios e os dois pontos de UI foram confirmados com o usuário antes da escrita dos artifacts.
