## Why

Com o relatório detalhado em uso, apareceu uma folha praticamente em branco entre o cabeçalho do projeto e a primeira tarefa: a regra implementada era `page-break-before: always` em **toda** tarefa, inclusive a primeira do projeto. Quando o cabeçalho (ex.: "Laboratório / Valor hora: R$ 60,00 | Horas: 8,00h") caía no fim da página, ele ficava sozinho e a primeira tarefa era empurrada para a página seguinte.

O comportamento foi corrigido no template (`backend/app/templates/relatorio_pdf.html`), mas a requirement `relatorios-pdf` continua escrita como "cada tarefa inicia em página nova", o que deixa a spec em desacordo com o sistema.

## What Changes

Este change **não altera código**: somente alinha o texto da requirement `relatorios-pdf` ao comportamento já implementado:
- cada **projeto** passa a iniciar em página nova (a partir do segundo projeto);
- a **primeira tarefa** do projeto segue logo abaixo do cabeçalho, sem quebra;
- as **demais tarefas** do projeto abrem página nova;
- o cabeçalho do projeto nunca fica isolado no fim da página.

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `relatorios-pdf`: Ajusta a regra de quebra de página do detalhamento — projeto em página nova, primeira tarefa colada ao cabeçalho e demais tarefas em páginas próprias — e explicita a ausência de página em branco entre cabeçalho e primeira tarefa

## Impact

**Backend:**
- `backend/app/templates/relatorio_pdf.html` — alteração **já implementada** (classes `.projeto-nova-pagina`, `.projeto-cabecalho` com `page-break-after: avoid`, e `.tarefa-bloco-nova-pagina` aplicada apenas às tarefas após a primeira)

**Frontend / testes / dados:**
- Nenhum impacto: a mudança é apenas de redação do contrato de comportamento
