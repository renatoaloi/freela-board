## 1. Backend — Schemas

- [x] 1.1 Adicionar `RelatorioApontamentoItem` (`hora_ini`, `hora_fim`, `total_horas`) em `app/domain/schemas.py`
- [x] 1.2 Adicionar `RelatorioTarefaDia` (`data`, `total_horas`, `apontamentos: list[RelatorioApontamentoItem]`) em `app/domain/schemas.py`
- [x] 1.3 Acrescentar em `RelatorioTarefaItem` os campos `descricao: Optional[str]`, `anexos: list[str]` (default vazio) e `dias: list[RelatorioTarefaDia]` (default vazio)

## 2. Backend — Snapshot no fechamento

- [x] 2.1 Adicionar consulta em `RelatorioRepository` que retorne os apontamentos por tarefa filtrando mês/ano (id da tarefa, data, hora_ini, hora_fim, total_horas)
- [x] 2.2 Preencher `dias`, `descricao` e `anexos` em `_build_snapshot()` de `relatorio_service.py` para cada tarefa selecionada
- [x] 2.3 Garantir dias em ordem crescente e `total_horas` do dia consistente com a soma dos apontamentos

## 3. Backend — PDF

- [x] 3.1 Resolver os anexos de imagem do disco (caminho `cliente/projeto/tarefa`) em `relatorio_pdf_service.py`, embutindo como data URI base64
- [x] 3.2 Ignorar anexos que não são imagem (não renderizar lista nem nome)
- [x] 3.3 Omitir imagem cujo arquivo não exista no storage (sem quebrar o PDF)
- [x] 3.4 Limitar o mosaico a 10 imagens por tarefa
- [x] 3.4b Reduzir cada imagem para caber em 400x400 px (sem ampliar menores) e reencodar em JPEG qualidade 75 antes do data URI
- [x] 3.4c Adicionar `pillow` ao `requirements.txt` e `zlib1g-dev`/`libjpeg-dev` ao `Dockerfile` do backend (compilação do Pillow em armv7)
- [x] 3.5 Substituir a tabela `Tarefa | Horas` do template pelo bloco detalhado da tarefa, com `page-break-before: always`
- [x] 3.6 Renderizar no bloco da tarefa: título, total de horas, descrição, dias com apontamentos e mosaico de imagens (grid proporcional à quantidade)
- [x] 3.6b Não esticar a imagem reduzida no template (`width: auto; max-width: 100%`)

## 4. Frontend

- [x] 4.1 Exibir no detalhe do relatório (`RelatorioView.jsx`) os dias e apontamentos de cada tarefa
- [x] 4.2 Exibir a descrição da tarefa quando houver
- [x] 4.3 Exibir miniaturas das imagens via `uploadAPI.download` (mesmo padrão do `TarefaDetail`)

## 5. Testes

- [x] 5.1 Cobrir em `backend/tests/test_fechamento.py` que o snapshot traz `dias` (ordem e horas por dia), `descricao` e `anexos`
- [x] 5.2 Cobrir que apontamentos fora da competência não entram em `dias`
- [x] 5.3 Cobrir em `backend/tests/test_relatorios.py` os novos campos na leitura do relatório por `id`
- [x] 5.4 Cobrir em `backend/tests/test_relatorio_imagens.py` a redução para 400x400 (sem ampliar menores), conversão de PNG com alfa para JPEG, SVG preservado, limite de 10 imagens e anexo ausente ignorado
- [x] 5.5 Manter os testes de PDF atrás do guard `HAS_WEASYPRINT` e rodar `cd backend && pytest -v` (verde fora os 3 skipados sem GTK/cairo)

## 6. Documentação

- [x] 6.1 Atualizar o `README.md` descrevendo o detalhamento do relatório (página por tarefa, dias e imagens) e a limitação dos relatórios já fechados
