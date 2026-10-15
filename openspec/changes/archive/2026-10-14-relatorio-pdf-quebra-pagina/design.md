## Context

O detalhamento do PDF é montado em `backend/app/templates/relatorio_pdf.html` a partir do contexto de `_build_context()` (`relatorio_pdf_service.py`), com uma hierarquia: seção de detalhamento → bloco por projeto (`.projeto`, com `.projeto-header` e `.projeto-meta`) → bloco por tarefa (`.tarefa-bloco`).

O ajuste de layout discutido aqui **já está implementado**: `page-break-before: always` deixou de estar em `.tarefa-bloco` e passou a valer por duas classes aplicadas no template via Jinja — `.projeto-nova-pagina` (projetos a partir do segundo) e `.tarefa-bloco-nova-pagina` (tarefas a partir da segunda de cada projeto) — além de `.projeto-cabecalho { page-break-after: avoid }` para o cabeçalho não ficar órfão no rodapé.

Requisitos atualizados em `specs/relatorios-pdf/spec.md`; motivação em `proposal.md`.

## Goals / Non-Goals

**Goals:**
- Descrever na spec a regra de quebra de página como ela é de fato: projeto em página nova, primeira tarefa colada ao cabeçalho, demais tarefas em páginas próprias
- Registrar explicitamente a ausência de página em branco entre cabeçalho e primeira tarefa
- Manter intactas as demais regras do detalhamento (dias, descrição, mosaico, redução de imagens)

**Non-Goals:**
- Alterar código, endpoints ou dados (nada é implementado neste change)
- Mudar o formato A4, margens, cabeçalho/rodapé, resumo financeiro ou o modo de embutir imagens
- Reintroduzir a trava de uma página por tarefa em sentido estrito

## Decisions

### D1 — A quebra passa a ser por projeto + por tarefa subsequente
A unidade que abre página é o **projeto**, e dentro dele cada **tarefa adicional**. A primeira tarefa fica na mesma página do cabeçalho (que traz título, valor/hora e total de horas — informação curta que sobra espaço).

- *Alternativa 1*: manter `page-break-before` na primeira tarefa e resolver a folha branca apenas com `page-break-inside: avoid` no bloco do projeto. Rejeitada: `page-break-inside: avoid` em um bloco grande (várias páginas) é ignorado pelo motor de paginação e o problema volta.
- *Alternativa 2*: forçar quebra também antes do cabeçalho de cada projeto e manter quebra em toda tarefa (situação anterior). Rejeitada: é exatamente o que produzia a página em branco relatada.

### D2 — Prevenir cabeçalho órfão
`.projeto-cabecalho { page-break-after: avoid }` garante que, se o cabeçalho não couber com a primeira tarefa, ele seja empurrado inteiro para a página seguinte em vez de ficar sozinho.

### D3 — Nada de código neste change
Como o comportamento já está no repositório, o change serve para fechar a defasagem entre spec e sistema — caminho escolhido em vez de editar `openspec/specs/relatorios-pdf/spec.md` direto (edição manual de spec principal não é o fluxo do projeto).

## Risks / Trade-offs

- **Agrupamento por projeto pode gerar página com cabeçalho + tarefa longa**: aceito — é melhor que folha em branco, e o `page-break-inside: avoid` do bloco da tarefa evita cortar a tarefa no meio.
- **Projetos com uma única tarefa** ocupam uma página com cabeçalho + tarefa: esperado e desejável.
- **Verificação visual depende de WeasyPrint**, indisponível no ambiente de desenvolvimento Windows (GTK/cairo): a conferência do layout precisa ser feita onde a lib roda (container/Pi).

## Migration Plan

Sem deploy: nenhuma linha de código é alterada, o comportamento já está na branch. Basta arquivar o change para a spec principal refletir o sistema.

## Open Questions

- Nenhuma: o comportamento foi validado em uso pelo usuário antes da escrita dos artifacts.
