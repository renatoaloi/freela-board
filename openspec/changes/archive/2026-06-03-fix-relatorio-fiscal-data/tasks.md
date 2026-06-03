# Tasks: fix-relatorio-fiscal-data

## 1. Refatorar schema Pydantic do relatório

- [x] 1.1 Em `backend/app/domain/schemas.py`, criar `RelatorioClienteInfo` (id, nome, razao_social, documento, email, endereco, complemento Optional, bairro, cidade, estado) logo após `ProjetoRelatorioItem`.
- [x] 1.2 Criar `RelatorioTarefaItem` (tarefa_id, titulo, total_horas).
- [x] 1.3 Criar `RelatorioProjetoItem` (projeto_id, titulo, valor_por_hora, total_horas, valor_total, tarefas: list[RelatorioTarefaItem] com default_factory=list).
- [x] 1.4 Criar `RelatorioTotais` (total_horas, total_valor).
- [x] 1.5 Substituir `RelatorioResponse` pela forma aninhada: `cliente: RelatorioClienteInfo`, `mes_referencia: str`, `totais: RelatorioTotais`, `projetos: list[RelatorioProjetoItem]`. Remover chaves achatadas antigas (`cliente_id`, `cliente_nome`, `cliente_documento`).

## 2. Adicionar query de tarefas no repository

- [x] 2.1 Em `backend/app/infrastructure/repositories/relatorio_repository.py`, adicionar método `get_tarefas_by_cliente_mes_ano(cliente_id, mes, ano)` que retorna `list[dict]` com `{projeto_id, tarefa_id, titulo, total_horas}`. Mesma forma de filtro `strftime` da query de projetos (replicar o padrão).
- [x] 2.2 Confirmar que a query retorna agregação correta: somar `total_horas` agrupado por `tarefa_id`, mantendo `projeto_id` e `titulo` no `group_by` para que o `select` resolva.

## 3. Refatorar service para o novo schema

- [x] 3.1 Em `backend/app/application/services/relatorio_service.py`, mudar o import para incluir os novos sub-schemas (`RelatorioResponse`, `RelatorioClienteInfo`, `RelatorioTotais`, `RelatorioProjetoItem`, `RelatorioTarefaItem`).
- [x] 3.2 Substituir a construção do `dict` de retorno pela construção de `RelatorioResponse(...)` com sub-objetos. Popular `cliente` lendo TODOS os campos do `ClienteModel` (não só `id`, `nome`, `documento`).
- [x] 3.3 Chamar o novo método `repository.get_tarefas_by_cliente_mes_ano(...)` e fazer o zip por `projeto_id` em `defaultdict(list)`. Atribuir a lista resultante a `RelatorioProjetoItem.tarefas`.
- [x] 3.4 Renomear `projeto_titulo` para `titulo` ao construir o `RelatorioProjetoItem` (no dict retornado pelo repo o campo ainda é `projeto_titulo`; a renomeação acontece aqui).
- [x] 3.5 A função `generate` agora retorna `RelatorioResponse` (não `dict`).

## 4. Adicionar `response_model` no controller

- [x] 4.1 Em `backend/app/api/v1/relatorio_controller.py`, importar `RelatorioResponse` de `app.domain.schemas`.
- [x] 4.2 Adicionar `response_model=RelatorioResponse` ao decorator `@router.get("/relatorios", ...)`.
- [x] 4.3 Confirmar que a assinatura da função `generate_relatorio` ainda retorna o tipo do service (`RelatorioResponse` agora); FastAPI vai serializar via `response_model`.

## 5. Adaptar frontend ao novo schema

- [x] 5.1 Em `frontend/src/components/Relatorios/RelatorioView.jsx`, no card "Dados do Cliente", trocar todas as leituras de `result.cliente?.X` para `result.cliente?.X` (mantém optional chaining; agora populadas). Renderizar na ordem: nome fantasia, razao_social, documento, endereço completo (endereco + complemento + bairro em uma linha), cidade/UF em outra, email.
- [x] 5.2 No card "Resumo", trocar `result.total_horas_geral` por `result.totais?.total_horas` e `result.valor_total_geral` por `result.totais?.total_valor`.
- [x] 5.3 No bloco "Detalhamento por Projeto", trocar `proj.titulo` (que já era a chave esperada — verificar que continua igual) e adicionar sub-bloco "Tarefas" condicional: se `proj.tarefas && proj.tarefas.length > 0`, renderizar tabela com colunas "Tarefa" e "Horas" usando `tarefa.titulo` e `formatHoras(tarefa.total_horas)`.
- [x] 5.4 Remover o bloco órfão "Tarefas" no nível raiz (linhas 222-246 do arquivo atual) — nunca foi renderizado, foi substituído pelo sub-bloco dentro de cada projeto.

## 6. Atualizar testes existentes

- [x] 6.1 Em `backend/tests/test_relatorios.py`, atualizar `test_relatorio_generation`: trocar as assertions de chaves achatadas (`data["cliente_id"]`, `data["cliente_documento"]`, `data["total_geral_horas"]`, `data["total_geral_valor"]`) para as novas chaves aninhadas (`data["cliente"]["id"]`, `data["cliente"]["documento"]`, `data["totais"]["total_horas"]`, `data["totais"]["total_valor"]`).

## 7. Adicionar teste de regressão para mês/ano passado

- [x] 7.1 Em `backend/tests/test_relatorios.py`, adicionar `test_relatorio_mes_passado`: cria apontamento com `data = date(2025, 5, 15)`, pede o relatório para `mes=5&ano=2025`. Verifica que `data["totais"]["total_horas"] == 4.0`, `data["projetos"]` tem 1 item, e `data["projetos"][0]["tarefas"]` tem 1 item com `total_horas == 4.0`. Garante que `strftime` funciona para datas que não sejam o mês atual.

## 8. Verificação

- [x] 8.1 Rodar `cd backend && python -m pytest -v` e confirmar que todos os tests passam (38 existentes + 1 novo = 39, mais os 3 do test_relatorios.py atualizados). ✓ 39/39 passam.
- [x] 8.2 Rodar `cd frontend && npm run build` e confirmar que o bundle compila sem erros ou warnings novos. ✓ Build OK, mesmo warning pré-existente de chunk > 500kb.
- [x] 8.3 Subir backend e frontend (`uvicorn` + `npm run dev`), abrir o relatório para um cliente com apontamentos cadastrados, conferir manualmente: (a) card "Dados do Cliente" mostra todos os campos fiscais; (b) card "Resumo" mostra totais corretos; (c) cada projeto lista suas tarefas; (d) o botão "Imprimir" ainda funciona. ✓ Verificado manualmente pelo usuário.
