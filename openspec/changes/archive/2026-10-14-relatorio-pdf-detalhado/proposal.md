## Why

O relatório entregue ao cliente serve como **memória de cálculo** e hoje é raso: no detalhamento por projeto cada tarefa aparece apenas como uma linha `título + total de horas`. Não há como o cliente verificar **que horas foram feitas em que dia**, o que foi feito (descrição) nem a **evidência fotográfica** — o padrão de trabalho é um diário por dia, com apontamentos, descrição e fotos.

Além disso, o snapshot gravado no fechamento (`RelatorioTarefaItem`) só contém `tarefa_id`, `titulo` e `total_horas`, então nem o detalhe na tela nem o PDF teriam de onde tirar essas informações.

## What Changes

- **Fechamento passa a gravar detalhamento**: para cada tarefa selecionada, o snapshot registra os apontamentos **agrupados por dia** (data, hora_ini/hora_fim/horas do dia), a `descricao` e a lista de `anexos`.
- **PDF com uma página por tarefa**: cada tarefa começa em página nova e mostra, dentro dela, seus dias com apontamentos, a descrição e um **mosaico com as imagens** da tarefa (normalmente 1–2, até 10).
- **Agrupamento por projeto mantido**: os projetos continuam abrindo o detalhamento; as tarefas deixam de ser uma linha de tabela e passam a ocupar páginas próprias.
- **Anexos que não são imagem são ignorados** no PDF (não aparecem nem como lista).
- Relatórios **já fechados** não ganham o detalhe retroativamente — o snapshot continua valendo exatamente como foi gravado.

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `fechamento-mensal`: o snapshot do fechamento passa a incluir o detalhamento diário dos apontamentos, a descrição e os anexos de cada tarefa selecionada
- `relatorios`: a resposta do relatório fechado passa a expor, por tarefa, os dias com apontamentos, a descrição e os anexos
- `relatorios-pdf`: o detalhamento passa a ter uma página por tarefa, com dias, descrição e mosaico de imagens

## Impact

**Backend:**
- `app/domain/schemas.py` — novos schemas `RelatorioApontamentoItem` (hora_ini, hora_fim, total_horas), `RelatorioTarefaDia` (data, apontamentos, total_horas) e campos novos em `RelatorioTarefaItem` (`descricao`, `dias`, `anexos`)
- `app/application/services/relatorio_service.py` — `_build_snapshot()` passa a consultar os apontamentos por dia das tarefas selecionadas e guardar no snapshot
- `app/infrastructure/repositories/relatorio_repository.py` — consulta de apontamentos por tarefa filtrando a competência
- `app/application/services/relatorio_pdf_service.py` — `_build_context()` passa a resolver caminhos/bytes das imagens dos anexos para o template
- `app/templates/relatorio_pdf.html` — nova seção de tarefa em página própria + mosaico de imagens

**Frontend:**
- `src/components/Relatorios/RelatorioView.jsx` — detalhe passa a exibir os dias/apontamentos, a descrição e miniaturas das imagens da tarefa

**Testes:**
- `backend/tests/test_fechamento.py` — cobrir que o snapshot traz dias/anexos
- `backend/tests/test_relatorios.py` — cobrir os novos campos na leitura do relatório; testes de PDF seguem atrás do guard `HAS_WEASYPRINT`

**Dados:** sem migration — o detalhamento cabe no campo JSON `dados` já existente na tabela `relatorios`.
