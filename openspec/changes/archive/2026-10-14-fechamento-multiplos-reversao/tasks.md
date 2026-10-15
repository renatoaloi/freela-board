## 1. Backend — Modelo e migration

- [x] 1.1 Adicionar campo `numero` em `RelatorioModel` (`Integer`, `nullable=False`, `default=1`)
- [x] 1.2 Remover a `UniqueConstraint("cliente_id", "mes", "ano")` do modelo
- [x] 1.3 Gerar migration: `cd backend && python -m alembic revision --autogenerate -m "remove unique competencia and add numero"`
- [x] 1.4 Revisar a migration (garantir `batch_alter_table` para SQLite) e aplicar `alembic upgrade head`

## 2. Backend — Repositório

- [x] 2.1 Adicionar consulta que devolva o próximo `numero` por cliente/mês/ano em `RelatorioRepository`
- [x] 2.2 Ajustar `create_relatorio` para gravar o `numero` recebido
- [x] 2.3 Adicionar consulta dos `tarefa_id` vinculados a um relatório (para a reversão)
- [x] 2.4 Garantir que a exclusão do relatório remova os vínculos em cascata

## 3. Backend — Serviço

- [x] 3.1 Remover a checagem de competência existente (409) em `RelatorioService.fechar()`
- [x] 3.2 Calcular e gravar o número sequencial do fechamento dentro da mesma transação
- [x] 3.3 Manter a checagem `tarefas_vinculadas()` para barrar tarefa já faturada (422)
- [x] 3.4 Implementar `RelatorioService.reverter(id)`: 404 quando inexistente, exclusão do relatório, captura dos ids antes de apagar e volta para `pronta` das tarefas que ainda não pertencem a outro relatório
- [x] 3.5 Expor `numero` em `RelatorioService.listar()` e no detalhe (`RelatorioResponse`)

## 4. Backend — Controller e schemas

- [x] 4.1 Adicionar `numero` em `RelatorioResumo` e `RelatorioResponse` em `app/domain/schemas.py`
- [x] 4.2 Adicionar `DELETE /api/v1/relatorios/{id}` em `relatorio_controller.py` com `Depends(get_api_key)`
- [x] 4.3 Incluir o número no nome do PDF gerado (`filename`) quando for maior que 1

## 5. Frontend

- [x] 5.1 Adicionar `relatoriosAPI.reverter(id)` em `src/services/api.js`
- [x] 5.2 Exibir o nº do fechamento na listagem (`RelatoriosList.jsx`)
- [x] 5.3 Adicionar ação "Reverter" com `ConfirmModal` na listagem, recarregando a lista e usando `AlertModal` em erro
- [x] 5.4 Exibir o nº do fechamento no detalhe do relatório (`RelatorioView.jsx`)
- [x] 5.5 Em `FechamentoMensal.jsx`, mostrar o próximo número do fechamento e remover o tratamento específico de 409 por competência

## 6. Testes

- [x] 6.1 Substituir em `backend/tests/test_fechamento.py` o teste de 409 por teste de segundo fechamento no mesmo cliente/mês (permitido, com `numero == 2`)
- [x] 6.2 Cobrir numeração independente por competência e tarefa já faturada barrada em novo fechamento
- [x] 6.3 Cobrir em `backend/tests/test_relatorios.py` a reversão: tarefas voltam a `pronta`, relatório sai da lista, 404 no detalhe/PDF e 401 sem chave
- [x] 6.4 Rodar `cd backend && pytest -v` — verde fora os 3 testes de PDF skipados

## 7. Documentação

- [x] 7.1 Atualizar o `README.md` (fim da trava de um relatório por mês, numeração dos fechamentos e endpoint de reversão)
