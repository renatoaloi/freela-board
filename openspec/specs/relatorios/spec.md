## Purpose

Memória de cálculo de horas por cliente/competência usada para emissão de nota fiscal: dados fiscais do cliente, resumo de totais e detalhamento por projeto com tarefas. O conteúdo vem do snapshot gravado no fechamento do mês (echamento-mensal) e é somente leitura.
## Requirements
### Requirement: Resposta do relatório usa schema aninhado

O endpoint de leitura `GET /api/v1/relatorios/{id}` MUST retornar o relatório já fechado com a estrutura aninhada: `id`, `cliente: { id, nome, razao_social, documento, email, endereco, complemento, bairro, cidade, estado }`, `mes_referencia: string`, `totais: { total_horas, total_valor }`, `projetos: [RelatorioProjetoItem]`. MUST NOT usar chaves achatadas como `cliente_id`, `cliente_nome`, `total_geral_horas`, `total_geral_valor`, `projeto_titulo`. Os valores MUST vir do snapshot gravado no fechamento, não de um recálculo dos apontamentos.

#### Scenario: Resposta bem-sucedida tem as chaves esperadas
- **WHEN** o frontend chama `GET /api/v1/relatorios/{id}` com autenticação válida
- **THEN** a resposta MUST conter `id`, `cliente` (objeto), `mes_referencia` (string `"05/2026"`), `totais` (objeto com `total_horas` e `total_valor` numéricos) e `projetos` (array)
- **AND** a resposta MUST NOT conter as chaves achatadas `cliente_id`, `cliente_nome`, `total_geral_horas`, `total_geral_valor`

#### Scenario: Sem apontamentos no período retorna array vazio
- **WHEN** o relatório foi fechado para um mês/ano em que as tarefas selecionadas não tinham horas computáveis
- **THEN** a resposta MUST conter `cliente` populado e `projetos == []` com totais zerados

#### Scenario: Leitura usa o snapshot gravado
- **WHEN** o frontend chama `GET /api/v1/relatorios/{id}` para um relatório já fechado
- **THEN** os valores retornados MUST ser exatamente os congelados no fechamento, sem recálculo dos apontamentos

#### Scenario: Relatório inexistente
- **WHEN** o `id` informado não corresponde a nenhum relatório fechado
- **THEN** a resposta MUST ser `404`

#### Scenario: Relatório sem tarefas selecionadas no projeto
- **WHEN** o relatório foi fechado selecionando tarefas de apenas um dos projetos do cliente
- **THEN** apenas o projeto com tarefas selecionadas MUST aparecer em `projetos`

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

O objeto `totais` MUST refletir os valores congelados no fechamento, calculados apenas sobre as tarefas selecionadas pelo usuário. Ambos os campos MUST ser `float` com 2 casas decimais.

#### Scenario: Totais somam corretamente
- **WHEN** o fechamento selecionou tarefas de dois projetos (P1: 8h a R$ 100/h; P2: 4h a R$ 150/h)
- **THEN** `totais.total_horas == 12.0` e `totais.total_valor == 1400.0` (800 + 600), conforme gravado no fechamento

#### Scenario: Totais com 0 horas
- **WHEN** o relatório foi fechado sem horas computáveis nas tarefas selecionadas
- **THEN** `totais.total_horas == 0.0` e `totais.total_valor == 0.0` (não `null`, não ausente)

#### Scenario: Totais congelados ignoram edições posteriores
- **WHEN** um apontamento de uma tarefa do relatório é editado após o fechamento
- **THEN** `totais.total_horas` e `totais.total_valor` MUST permanecer com os valores gravados no fechamento

### Requirement: Resposta inclui projetos com tarefas agrupadas

O array `projetos` MUST incluir um item por projeto que teve tarefas **selecionadas** no fechamento. Cada item MUST incluir `projeto_id`, `titulo`, `valor_por_hora`, `total_horas`, `valor_total` e `tarefas: [RelatorioTarefaItem]`, com apenas as tarefas escolhidas.

#### Scenario: Projeto com 2 tarefas
- **WHEN** o fechamento selecionou 2 tarefas do mesmo projeto (T1 com 4h, T2 com 3h)
- **THEN** `projetos[0].tarefas` MUST ter 2 itens: um com `tarefa_id == T1.id` e `total_horas == 4.0`, outro com `tarefa_id == T2.id` e `total_horas == 3.0`
- **AND** `projetos[0].total_horas == 7.0` e `projetos[0].valor_total == 7.0 * valor_por_hora`

#### Scenario: Projeto sem tarefas (apontamentos órfãos não agrupáveis)
- **WHEN** o projeto não teve nenhuma tarefa selecionada no fechamento
- **THEN** o projeto MUST NOT aparecer em `projetos` (array sem o item, não item com `tarefas == []`)

#### Scenario: Campo `titulo` (não `projeto_titulo`)
- **WHEN** o frontend lê o nome do projeto
- **THEN** a chave MUST ser `titulo` (não `projeto_titulo`, que foi removido)

#### Scenario: Apenas tarefas selecionadas aparecem
- **WHEN** o projeto tinha 3 tarefas elegíveis e 2 foram selecionadas no fechamento
- **THEN** `projetos[0].tarefas` MUST conter exatamente 2 itens

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

O objeto `RelatorioResponse` MUST incluir o campo `dados_bancarios` conforme registrado no momento do fechamento (objeto com `banco_nome`, `banco_numero`, `agencia`, `conta`, `chave_pix`, `tipo_chave_pix`, podendo ser `null` quando vazios). Alterações posteriores nos dados bancários MUST NOT alterar relatórios já fechados.

#### Scenario: Dados bancários preenchidos
- **WHEN** o relatório foi fechado com dados bancários cadastrados (ex: `banco_nome: "Nubank"`)
- **THEN** `dados_bancarios` MUST ser um objeto com os campos preenchidos

#### Scenario: Dados bancários vazios/inexistentes
- **WHEN** o relatório foi fechado sem dados bancários cadastrados
- **THEN** `dados_bancarios` MUST ser `null`

#### Scenario: Dados bancários congelados no fechamento
- **WHEN** o relatório foi fechado quando `banco_nome == "Nubank"` e depois o usuário altera para `"Itaú"`
- **THEN** `dados_bancarios.banco_nome` MUST continuar `"Nubank"`

### Requirement: Frontend exibe dados bancários entre cliente e resumo

O componente `RelatorioView.jsx` MUST renderizar um card "Dados Bancários" entre o card "Dados do Cliente" e o card "Resumo", condicionalmente. O card MUST ser exibido apenas se ao menos um campo de `dados_bancarios` estiver preenchido.

#### Scenario: Card renderizado com dados
- **WHEN** `result.dados_bancarios` tem `banco_nome == "Nubank"`
- **THEN** o card "Dados Bancários" é renderizado com "Nubank" visível

#### Scenario: Card oculto sem dados
- **WHEN** `result.dados_bancarios` é `null` ou todos os campos são `null`
- **THEN** o card "Dados Bancários" NÃO é renderizado

### Requirement: Endpoint de listagem de relatórios fechados

O sistema MUST expor `GET /api/v1/relatorios` que retorna a lista de relatórios fechados, ordenada da competência mais recente para a mais antiga, cada item com `id`, `cliente` (id e nome), `mes`, `ano`, `total_horas`, `total_valor` e `data_fechamento`.

#### Scenario: Listagem autenticada
- **WHEN** o frontend chama `GET /api/v1/relatorios` com `X-API-Key` válido
- **THEN** a resposta MUST ser um array (possivelmente vazio) em ordem decrescente de ano/mês

#### Scenario: Sem autenticação
- **WHEN** a chamada é feita sem `X-API-Key` ou com chave inválida
- **THEN** a resposta MUST ser `401`

### Requirement: Relatórios somente leitura

Os relatórios fechados MUST ser somente leitura: MUST NOT haver endpoints de criação, atualização ou exclusão de relatório pela tela de Relatórios (a criação ocorre exclusivamente no fechamento do mês).

#### Scenario: Tentativa de leitura de id inexistente
- **WHEN** o frontend pede um `id` inexistente
- **THEN** a resposta MUST ser `404` com JSON de erro

### Requirement: Frontend lista e exibe relatórios fechados

A tela de Relatórios MUST listar os relatórios já fechados (cliente, competência `mes_referencia`, total de horas e valor total) e permitir abrir o detalhe de um deles, exibindo `cliente`, `dados_bancarios` (quando houver), `totais` e `projetos` com suas tarefas. A tela MUST NOT oferecer mais a ação de gerar relatório a partir de cliente/mês/ano.

#### Scenario: Lista de relatórios fechados
- **WHEN** o usuário abre a tela de Relatórios e existem relatórios fechados
- **THEN** cada relatório MUST ser exibido com cliente, mês/ano de referência, total de horas e valor total

#### Scenario: Lista vazia
- **WHEN** nenhum fechamento foi realizado
- **THEN** a tela MUST exibir estado vazio orientando a usar a tela de Fechamento Mensal

#### Scenario: Detalhe do relatório
- **WHEN** o usuário seleciona um relatório da lista
- **THEN** o detalhe MUST exibir dados do cliente, resumo de totais e detalhamento por projeto com suas tarefas

