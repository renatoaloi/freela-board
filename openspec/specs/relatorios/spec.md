## ADDED Requirements

### Requirement: Resposta do relatório usa schema aninhado

O endpoint `GET /api/v1/relatorios` MUST retornar um JSON com a estrutura aninhada: `cliente: { id, nome, razao_social, documento, email, endereco, complemento, bairro, cidade, estado }`, `mes_referencia: string`, `totais: { total_horas, total_valor }`, `projetos: [RelatorioProjetoItem]`. MUST NOT usar chaves achatadas como `cliente_id`, `cliente_nome`, `cliente_documento`, `total_geral_horas`, `total_geral_valor`, `projeto_titulo` (essas chaves são de uma versão antiga do schema, removidas).

#### Scenario: Resposta bem-sucedida tem as chaves esperadas
- **WHEN** o frontend chama `GET /api/v1/relatorios?cliente_id=X&mes=5&ano=2026` com autenticação válida e há apontamentos no período
- **THEN** a resposta MUST conter `cliente` (objeto), `mes_referencia` (string `"05/2026"`), `totais` (objeto com `total_horas` e `total_valor` numéricos), e `projetos` (array, possivelmente vazio)
- **AND** a resposta MUST NOT conter as chaves achatadas `cliente_id`, `cliente_nome`, `cliente_documento`, `total_geral_horas`, `total_geral_valor` (são removidas no schema novo)

#### Scenario: Sem apontamentos no período retorna array vazio
- **WHEN** o frontend chama o endpoint para um mês/ano sem apontamentos
- **THEN** a resposta MUST conter `cliente` populado, `totais.total_horas == 0`, `totais.total_valor == 0`, e `projetos == []`

### Requirement: Resposta inclui dados fiscais completos do cliente

O objeto `cliente` na resposta MUST incluir os campos: `id`, `nome` (fantasia), `razao_social`, `documento` (CNPJ), `endereco`, `bairro`, `cidade`, `estado` (UF, 2 caracteres). MUST incluir `email` (contato do tomador). MUST incluir `complemento` quando o cliente tiver complemento cadastrado (pode ser string vazia / ausente caso `null` no banco).

#### Scenario: Cliente com todos os campos cadastrados
- **WHEN** o `ClienteModel` tem todos os campos preenchidos (incluindo `complemento` não-nulo)
- **THEN** a resposta MUST incluir `cliente.complemento` com o valor exato cadastrado

#### Scenario: Cliente sem complemento
- **WHEN** o `ClienteModel` tem `complemento == null`
- **THEN** a resposta MUST incluir `cliente.complemento` como `null` ou string vazia (não pode quebrar a renderização)

#### Scenario: Nome fantasia e razão social aparecem lado a lado
- **WHEN** o `ClienteModel` tem `nome == "Imediatum"` e `razao_social == "Imediatum Tecnologia LTDA"`
- **THEN** a resposta MUST incluir `cliente.nome == "Imediatum"` E `cliente.razao_social == "Imediatum Tecnologia LTDA"` (ambos expostos, distintos)

### Requirement: Resposta inclui totais consolidados

O objeto `totais` na resposta MUST incluir `total_horas` (soma de `total_horas` de todos os projetos do período) e `total_valor` (soma de `valor_total` de todos os projetos do período). Ambos MUST ser `float` com 2 casas decimais (já arredondados pelo service).

#### Scenario: Totais somam corretamente
- **WHEN** há 2 projetos no período, com `total_horas: 8.0` e `total_horas: 4.0`, e `valor_por_hora: 100.0` e `valor_por_hora: 150.0`
- **THEN** `totais.total_horas == 12.0` e `totais.total_valor == 1400.0` (800 + 600)

#### Scenario: Totais com 0 horas
- **WHEN** o mês/ano não tem apontamentos
- **THEN** `totais.total_horas == 0.0` e `totais.total_valor == 0.0` (não `null`, não `undefined`)

### Requirement: Resposta inclui projetos com tarefas agrupadas

O array `projetos` MUST incluir um item por projeto do cliente que teve apontamentos no período. Cada item MUST incluir `projeto_id`, `titulo` (renomeado de `projeto_titulo`), `valor_por_hora`, `total_horas`, `valor_total` (calculado como `total_horas * valor_por_hora`, arredondado para 2 casas), e `tarefas: [RelatorioTarefaItem]`. O array `tarefas` MUST agrupar os apontamentos por `tarefa_id`, somando `total_horas` dentro de cada tarefa.

#### Scenario: Projeto com 2 tarefas
- **WHEN** o projeto X tem apontamentos em 2 tarefas distintas (T1 com 4h, T2 com 3h)
- **THEN** `projetos[0].tarefas` MUST ter 2 itens: um com `tarefa_id == T1.id` e `total_horas == 4.0`, outro com `tarefa_id == T2.id` e `total_horas == 3.0`
- **AND** `projetos[0].total_horas == 7.0` e `projetos[0].valor_total == 7.0 * valor_por_hora`

#### Scenario: Projeto sem tarefas (apontamentos órfãos não agrupáveis)
- **WHEN** o projeto tem apontamentos mas o resultado da query de tarefas é vazio (improvável mas possível se houver race)
- **THEN** `projetos[0].tarefas == []` (array vazio, não `null`, não ausente)

#### Scenario: Campo `titulo` (não `projeto_titulo`)
- **WHEN** o frontend lê o nome do projeto
- **THEN** a chave MUST ser `titulo` (não `projeto_titulo`, que foi removido)

### Requirement: Filtro por mês e ano retorna apenas apontamentos do período

A query do relatório MUST filtrar os apontamentos pelo `mes` E `ano` fornecidos como query params. Apontamentos fora do par mês/ano MUST ser excluídos tanto do total consolidado quanto do detalhamento por projeto/tarefa.

#### Scenario: Apontamento de Maio/2026 aparece em pedido de Maio/2026
- **WHEN** há um apontamento com `data == 2026-05-15` e o frontend pede `mes=5&ano=2026`
- **THEN** o apontamento MUST ser contabilizado em `totais.total_horas`, no `projeto.total_horas` correspondente, e na `tarefa.total_horas` correspondente

#### Scenario: Apontamento de Maio/2025 NÃO aparece em pedido de Maio/2026
- **WHEN** há um apontamento com `data == 2025-05-15` e o frontend pede `mes=5&ano=2026`
- **THEN** o apontamento MUST NOT ser contabilizado (zero impacto em `totais`, projetos e tarefas)

#### Scenario: Apontamento de Abril/2026 NÃO aparece em pedido de Maio/2026
- **WHEN** há um apontamento com `data == 2026-04-30` e o frontend pede `mes=5&ano=2026`
- **THEN** o apontamento MUST NOT ser contabilizado (apesar de estar perto da fronteira)

#### Scenario: Múltiplos meses testáveis
- **WHEN** o test cria um apontamento com `data == 2025-05-15` e pede o relatório para `mes=5&ano=2025`
- **THEN** o relatório MUST retornar `totais.total_horas == 4.0` (referente ao apontamento criado)
- **AND** o test é reproduzível em qualquer data de execução (não depende de `date.today()`)

### Requirement: Endpoint requer autenticação e query params

O endpoint `GET /api/v1/relatorios` MUST exigir (a) header `X-API-Key` válido (rejeitando com 401 se ausente ou inválido), (b) query param `cliente_id` (string), (c) query param `mes` (int entre 1 e 12), (d) query param `ano` (int). Se o `cliente_id` não existir, MUST retornar 404. Se qualquer query param obrigatório estiver ausente, MUST retornar 422.

#### Scenario: Header de autenticação com valor inválido
- **WHEN** o frontend chama o endpoint com `X-API-Key` cujo valor não corresponde à chave configurada
- **THEN** o backend MUST retornar `401`

#### Scenario: Cliente inexistente
- **WHEN** o frontend chama o endpoint com `cliente_id` que não existe no banco
- **THEN** o backend MUST retornar `404` com `detail: "Cliente not found"`

#### Scenario: Query param obrigatório ausente
- **WHEN** o frontend chama o endpoint sem `cliente_id`, ou sem `mes`, ou sem `ano`
- **THEN** o backend MUST retornar `422` (validation error do FastAPI)

#### Scenario: Response model declarado no controller
- **WHEN** o backend inicia e o Swagger é gerado
- **THEN** o endpoint MUST declarar `response_model=RelatorioResponse` (visível no OpenAPI gerado em `/docs`)

### Requirement: Frontend renderiza dados do novo schema

O componente `RelatorioView.jsx` MUST ler os campos do novo schema: `result.cliente.nome`, `result.cliente.razao_social`, `result.cliente.documento`, `result.cliente.endereco`, `result.cliente.complemento`, `result.cliente.bairro`, `result.cliente.cidade`, `result.cliente.estado`, `result.cliente.email`, `result.totais.total_horas`, `result.totais.total_valor`, `proj.titulo` (não `proj.projeto_titulo`), `proj.tarefas`. MUST NOT ler chaves achatadas removidas (`result.cliente_id`, `result.cliente_nome`, `result.total_geral_horas`, `result.total_geral_valor`, `result.projeto_titulo`).

#### Scenario: Card "Dados do Cliente" exibe todos os campos fiscais
- **WHEN** o relatório é gerado com sucesso
- **THEN** o card MUST exibir nome fantasia, razão social, CNPJ (documento), endereço completo (endereço + complemento + bairro em uma linha, cidade/UF em outra), e email

#### Scenario: Card "Resumo" lê de `totais`
- **WHEN** o relatório é gerado
- **THEN** "Total de Horas" MUST ser `result.totais.total_horas` (não `result.total_horas_geral`) e "Valor Total" MUST ser `result.totais.total_valor` (não `result.valor_total_geral`)

#### Scenario: Detalhamento por Projeto exibe nome correto
- **WHEN** o relatório lista os projetos
- **THEN** o nome do projeto MUST vir de `proj.titulo` (não `proj.projeto_titulo`)

#### Scenario: Sub-bloco "Tarefas" dentro de cada projeto
- **WHEN** um projeto tem `proj.tarefas.length > 0`
- **THEN** o frontend MUST renderizar um sub-bloco "Tarefas" dentro do card do projeto, listando `tarefa.titulo` e `tarefa.total_horas` para cada item
- **AND** se `proj.tarefas.length == 0`, o sub-bloco MUST NOT ser renderizado

#### Scenario: Bloco órfão "Tarefas" no nível raiz removido
- **WHEN** o relatório é gerado
- **THEN** o componente MUST NOT ter o bloco "Tarefas" antigo no nível raiz (que ficava depois de "Detalhamento por Projeto" e nunca era renderizado por falta de dados)

### Requirement: Resposta do relatório inclui dados bancários

O objeto `RelatorioResponse` MUST incluir um campo `dados_bancarios` (objeto, pode ser `null` se não houver dados). O objeto MUST conter: `banco_nome`, `banco_numero`, `agencia`, `conta`, `chave_pix`, `tipo_chave_pix` (todos strings, podem ser `null`). O frontend MUST ler `result.dados_bancarios` para exibir o card "Dados Bancários".

#### Scenario: Dados bancários preenchidos
- **WHEN** o relatório é gerado e os dados bancários estão preenchidos
- **THEN** `result.dados_bancarios` MUST ser um objeto com os campos preenchidos (ex: `banco_nome: "Nubank"`)

#### Scenario: Dados bancários vazios/inexistentes
- **WHEN** o relatório é gerado e não há dados bancários (tabela não existe ou todos os campos nulos)
- **THEN** `result.dados_bancarios` MUST ser `null` ou um objeto com todos os campos `null`

### Requirement: Frontend exibe dados bancários entre cliente e resumo

O componente `RelatorioView.jsx` MUST renderizar um card "Dados Bancários" entre o card "Dados do Cliente" e o card "Resumo", condicionalmente. O card MUST ser exibido apenas se ao menos um campo de `dados_bancarios` estiver preenchido.

#### Scenario: Card renderizado com dados
- **WHEN** `result.dados_bancarios` tem `banco_nome == "Nubank"`
- **THEN** o card "Dados Bancários" é renderizado com "Nubank" visível

#### Scenario: Card oculto sem dados
- **WHEN** `result.dados_bancarios` é `null` ou todos os campos são `null`
- **THEN** o card "Dados Bancários" NÃO é renderizado
