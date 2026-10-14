## ADDED Requirements

### Requirement: Endpoint retorna PDF do relatório fechado

O endpoint `GET /api/v1/relatorios/{id}/pdf` MUST retornar o PDF do relatório **já fechado** correspondente ao `id` informado. O conteúdo MUST refletir o snapshot gravado no fechamento (tarefas selecionadas e totais congelados), e não um recálculo dos apontamentos do período.

#### Scenario: Chamada bem-sucedida retorna PDF
- **WHEN** o frontend chama `GET /api/v1/relatorios/{id}/pdf` com `X-API-Key` válido
- **THEN** a resposta MUST ter `Content-Type: application/pdf`
- **AND** a resposta MUST ter `Content-Disposition: attachment` com filename no padrão `relatorio-{slug}-{mes}-{ano}.pdf`
- **AND** o corpo MUST ser um PDF válido (inicia com `%PDF-`)

#### Scenario: Relatório inexistente retorna 404
- **WHEN** o `id` não corresponde a nenhum relatório fechado
- **THEN** o endpoint MUST retornar `404`
- **AND** a resposta MUST ser JSON, não PDF

#### Scenario: Header de autenticação inválido retorna 401
- **WHEN** o `X-API-Key` não corresponde à chave configurada
- **THEN** o endpoint MUST retornar `401`

#### Scenario: Conteúdo limitado às tarefas selecionadas
- **WHEN** o fechamento selecionou apenas parte das tarefas elegíveis
- **THEN** o PDF MUST listar somente as tarefas selecionadas e seus totais congelados

### Requirement: Botão "Baixar PDF" no relatório fechado

O frontend MUST exibir um botão "Baixar PDF" na visualização do relatório fechado (na lista e/ou no detalhe), que dispara o download do PDF daquele relatório. A ação MUST NOT depender de uma geração prévia na tela.

#### Scenario: Botão disponível na lista e no detalhe
- **WHEN** o usuário visualiza a lista de relatórios fechados ou o detalhe de um deles
- **THEN** o botão "Baixar PDF" MUST estar visível, sem exigir gerar relatório antes

#### Scenario: Download a partir da lista
- **WHEN** o usuário clica em "Baixar PDF" em um item da lista de relatórios fechados
- **THEN** o navegador MUST iniciar o download de `relatorio-{nome_cliente}-{mes}-{ano}.pdf`
- **AND** o download MUST usar o nome gerado pelo servidor no `Content-Disposition`

#### Scenario: Erro ao baixar
- **WHEN** o servidor retorna erro (ex: 404)
- **THEN** o frontend MUST exibir a mensagem de erro para o usuário (não tentar fazer download de JSON como PDF)

## REMOVED Requirements

### Requirement: Endpoint retorna PDF do relatório de horas
**Reason**: O PDF deixa de ser gerado sob demanda por `cliente_id`/`mes`/`ano` e passa a sair do snapshot de um relatório já fechado, identificado por `id`.
**Migration**: Usar `GET /api/v1/relatorios/{id}/pdf` com o `id` retornado pelo fechamento do mês.

### Requirement: Botão "Baixar PDF" no frontend
**Reason**: O botão deixa de estar condicionado ao relatório gerado na tela (que não existe mais) e passa a atuar sobre relatórios fechados listados/detalhados.
**Migration**: Ver Requirement "Botão 'Baixar PDF' no relatório fechado".
