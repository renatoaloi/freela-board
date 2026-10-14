## Context

Hoje o detalhamento do PDF é uma tabela `Tarefa | Horas` gerada em `_build_context()` a partir de `RelatorioTarefaItem(tarefa_id, titulo, total_horas)` — não existe dado algum sobre dias ou anexos no caminho do relatório. O snapshot do fechamento é gravado como `RelatorioResponse.model_dump(mode="json")` na coluna JSON `relatorios.dados`, então **qualquer dado novo precisa ser incluído no momento do fechamento** (decisão do usuário: relatórios antigos não são recalculados).

Os anexos ficam em disco em `storage/{cliente_id}/{projeto_id}/{tarefa_id}/{uuid}{ext}` (`upload_controller._get_storage_path`) e a tarefa guarda a lista de nomes em `TarefaModel.anexos` (coluna JSON). O template Jinja `relatorio_pdf.html` é renderizado por WeasyPrint em `RelatorioPdfService.generate()`, que importa a lib de forma lazy (necessário: sem GTK/cairo o app nem sobe).

Requisitos em `specs/*/spec.md`; motivação em `proposal.md`.

## Goals / Non-Goals

**Goals:**
- Snapshot do fechamento com dias/apontamentos, descrição e anexos por tarefa
- PDF com uma página por tarefa: dias, descrição e mosaico de imagens
- Frontend exibindo o mesmo detalhamento no detalhe do relatório

**Non-Goals:**
- Recalcular detalhe de relatórios já fechados (aceito: só novos fechamentos)
- Redimensionar/comprimir imagens (sem dependência de Pillow hoje)
- Listar anexos não-imagem no PDF
- Quebrar página por dia dentro da tarefa (escolhido: uma página por tarefa, dias em sequência dentro dela)
- Alterar formato A4, margens, cabeçalho/rodapé ou o resumo financeiro

## Decisions

### D1 — Detalhamento entra no snapshot, não é recalculado depois
`_build_snapshot()` passa a consultar os apontamentos das tarefas selecionadas **filtrando a competência** (`strftime("%m"/"%Y")` — mesmo padrão já usado no repositório de relatórios), agrupando por `data` em ordem crescente, e a guardar junto de `descricao` e `anexos` em `RelatorioTarefaItem`. O dado fica em JSON dentro da coluna `dados`, sem migration.

- *Alternativa*: preencher o detalhe na leitura (`RelatorioService.obter()`) consultando as tabelas atuais. Rejeitada pelo usuário: manteria maio/2026 recuperável, mas transformaria o detalhe em algo mutável — divergindo do princípio de snapshot que foi decidido no change `fechamento-mensal-relatorios`.

### D2 — Imagens vão para o HTML como data URI, já reduzidas
`RelatorioPdfService` resolve cada anexo de imagem (`jpg/jpeg/png/gif/webp/svg/bmp/ico`, mesma lista já usada no frontend para capa) em `storage/{cliente_id}/{projeto_id}/{tarefa_id}/{nome}`, **reduz a imagem para caber em 400x400 px** (sem ampliar menores; SVG entra sem alteração, pois já é vetorial) e embute o resultado JPEG (qualidade 75) como `<img src="data:image/jpeg;base64,...">`.

A redução usa **Pillow** (nova dependência em `requirements.txt`). Sem ela, uma foto de celular entraria com resolução original: no layout uma única imagem ocupava uma página inteira e o PDF ficava pesado. Ajuste pedido depois do primeiro teste do relatório.

- Imagem menor que o limite MUST NOT ser ampliada (`ImageOps`/`thumbnail` já preservam proporção e nunca ampliam).
- No template a imagem passa a ser renderizada em tamanho natural (`width: auto; max-width: 100%`) para o CSS não esticar de volta o que foi reduzido.
- Observação de deploy: Pillow tem wheel pronto para amd64/arm64; em Raspberry Pi OS **32-bit** (armv7) ele compila do zero. Por isso o `Dockerfile` do backend passa a instalar também `zlib1g-dev` e `libjpeg-dev` ao lado do `gcc` já presente.

- *Alternativa 1*: `file://` absoluto no `src`. Rejeitada: depende do WeasyPrint ter permissão de leitura no caminho e do caminho existir na máquina que renderiza — no Docker o storage é montado, mas isso amarra render e filesystem; o data URI mantém o HTML autocontido.
- *Alternativa 2*: servir via HTTP pelo próprio backend. Rejeitada: exigiria o app de pé para gerar o PDF e introduziria latência/autenticação no caminho do WeasyPrint.
- Arquivo inexistente (anexo apagado após o fechamento) → a imagem é **omitida** silenciosamente em vez de quebrar o PDF.

### D3 — Mosaico em CSS grid, decidido por quantidade
O template posiciona as imagens em um grid com número de colunas derivado da quantidade (1 → 1 coluna; 2 → 2 colunas; 3–4 → 2 colunas; ≥5 → 3 colunas), com `page-break-inside: avoid` no bloco da tarefa para não cortar o mosaico no meio. Limite prático de 10 imagens (`[:10]`), alinhado ao uso real informado. Como as imagens agora chegam com no máximo 400px, o grid trabalha com `width: auto` e não estica o conteúdo.

### D4 — Uma página por tarefa via CSS
`page-break-before: always` no bloco da tarefa, mantendo o agrupamento por projeto (o título do projeto abre a sequência e as tarefas vêm em páginas seguintes). A tabela `Tarefa | Horas` do template é substituída pelo bloco detalhado — a informação de horas continua presente (no cabeçalho da tarefa e por dia).

### D5 — Frontend reaproveita o upload endpoint
No detalhe do relatório, as miniaturas usam `uploadAPI.download(tarefa_id, filename)` (blob + `URL.createObjectURL`), padrão já usado em `TarefaDetail` para a capa. Como o snapshot guarda apenas os nomes dos arquivos e o caminho é derivado de `cliente/projeto/tarefa`, isso continua funcionando mesmo depois da tarefa mudar de projeto (o `storage` acompanha a transferência implementada em `transferir-tarefa-entre-projetos`).

## Risks / Trade-offs

- **PDF pode ficar pesado**: mitificado reduzindo cada imagem para até 400x400 px e reencodando em JPEG 75 antes do base64; com isso o peso cai na mesma ordem da redução de área e o limite de 10 imagens por tarefa continua como teto.
- **Dependência nova (Pillow)**: aumenta o build da imagem Docker; em Pi 32-bit pode compilar (ver D2 quanto aos headers instalados no Dockerfile). Fallback: se quiser voltar atrás, basta remover o Pillow e embutir o arquivo original — o resto do pipeline (data URI, grid, template) não muda.
- **Relatórios antigos ficam sem detalhe**: aceito; se o usuário precisar do novo formato para maio/2026, o caminho é refazer o fechamento (exige reabrir as tarefas — sem suporte a excluir relatório hoje).
- **Anexo apagado do disco** após o fechamento → imagem omitida; o relatório continua válido, mas perde evidência. Registrar no log ajudaria no futuro.
- **Descrição markdown renderizada como texto cru**: o PDF mostra o texto como está (com os `#`/`*` visíveis se houver). Aceito neste change; se incomodar, avaliar conversão simples depois.

## Migration Plan

Sem migration de schema (o detalhamento cabe na coluna JSON). Deploy normal; no Raspberry lembrar que o código do backend entra pela imagem (`docker compose up -d --build`). Relatórios já fechados continuam sendo exibidos sem o bloco de detalhes/`dias`. Rollback: reverter o commit — nenhum dado é alterado ou migrado.

## Open Questions

- Redimensionar imagens (Pillow) antes de embutir? Fora do escopo agora; só vale se o tamanho do PDF incomodar no uso real.
