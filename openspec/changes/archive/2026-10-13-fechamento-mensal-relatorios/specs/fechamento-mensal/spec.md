## Purpose

Permite consolidar as horas de um mês em um relatório fechado: o usuário escolhe cliente, mês/ano (e opcionalmente um projeto) e seleciona quais tarefas entram no relatório, gerando um registro persistido com totais congelados e marcando as tarefas selecionadas como encerradas.

## ADDED Requirements

### Requirement: Apenas tarefas prontas do período são elegíveis

O sistema MUST expor uma consulta de tarefas elegíveis ao fechamento que retorne **somente** tarefas que (a) pertençam a projetos do cliente informado, (b) tenham `status == "pronta"`, e (c) tenham ao menos um apontamento com data dentro do mês/ano informados. Tarefas nos status `nova`, `em_andamento` e `fechada` MUST NOT aparecer na lista de elegíveis.

#### Scenario: Tarefa pronta com apontamento no mês aparece
- **WHEN** o usuário escolhe cliente X, mês 05 e ano 2026, havendo uma tarefa `pronta` com apontamento em 2026-05-15
- **THEN** a tarefa MUST aparecer na lista de elegíveis, com suas horas somadas no mês

#### Scenario: Tarefa em andamento não aparece
- **WHEN** uma tarefa do cliente tem `status == "em_andamento"` e apontamento em 2026-05-15
- **THEN** a tarefa MUST NOT aparecer na lista de elegíveis

#### Scenario: Tarefa pronta sem apontamento no mês não aparece
- **WHEN** uma tarefa `pronta` do cliente só tem apontamentos em 2026-04-10
- **THEN** a tarefa MUST NOT aparecer na lista de elegíveis para mês 05/2026

#### Scenario: Tarefa já fechada não reaparece
- **WHEN** uma tarefa foi incluída em um fechamento anterior e está `fechada`
- **THEN** a tarefa MUST NOT aparecer na lista de elegíveis de outro fechamento

#### Scenario: Projeto usado como recorte adicional
- **WHEN** o usuário seleciona também um projeto do cliente
- **THEN** a lista MUST retornar apenas tarefas elegíveis daquele projeto

### Requirement: Fechamento exige cliente, período e ao menos uma tarefa

O endpoint de fechamento MUST exigir header `X-API-Key` válido (401 se ausente/inválido), `cliente_id` existente (404 caso contrário), `mes` entre 1 e 12, `ano`, e uma lista não vazia de `tarefa_ids`. Requisições fora dessas regras MUST retornar 422 (ou 404/400 conforme o caso) e MUST NOT criar relatório nem alterar status de tarefas.

#### Scenario: Lista de tarefas vazia é rejeitada
- **WHEN** o usuário confirma o fechamento sem selecionar nenhuma tarefa
- **THEN** o backend MUST retornar `422`
- **AND** nenhum relatório MUST ser criado

#### Scenario: Tarefa de outro cliente é rejeitada
- **WHEN** `tarefa_ids` contém uma tarefa cujo projeto pertence a outro cliente
- **THEN** o backend MUST retornar erro (`400` ou `422`)
- **AND** nenhum relatório MUST ser criado

#### Scenario: Tarefa fora do status elegível é rejeitada
- **WHEN** `tarefa_ids` contém uma tarefa que não está `pronta`
- **THEN** o backend MUST retornar erro (`400` ou `422`) e MUST NOT alterar o status da tarefa

#### Scenario: Cliente inexistente
- **WHEN** o `cliente_id` informado não existe
- **THEN** o backend MUST retornar `404` com `detail: "Cliente not found"`

### Requirement: Um relatório por cliente e competência

O sistema MUST permitir no máximo um relatório fechado por combinação de `cliente_id` + `mes` + `ano`.

#### Scenario: Segundo fechamento do mesmo cliente e mês é bloqueado
- **WHEN** já existe relatório fechado para o cliente X em 05/2026 e o usuário tenta fechar 05/2026 novamente
- **THEN** o backend MUST retornar `409`
- **AND** o relatório existente MUST NOT ser sobrescrito

#### Scenario: Mesmo cliente em meses diferentes é permitido
- **WHEN** já existe relatório de 05/2026 do cliente X e o usuário fecha 06/2026
- **THEN** o novo relatório MUST ser criado normalmente

### Requirement: Totais são congelados no fechamento

O relatório fechado MUST armazenar as horas e os valores calculados no momento do fechamento, considerando **apenas** as tarefas selecionadas. O total de horas de cada tarefa MUST ser a soma dos apontamentos daquela tarefa dentro do mês/ano de competência; o valor de cada projeto MUST ser `total_horas * valor_por_hora` do projeto, e o valor total MUST ser a soma dos projetos.

#### Scenario: Snapshot ignora apontamentos futuros
- **WHEN** um apontamento é lançado/editado em uma tarefa depois que o relatório do mês foi fechado
- **THEN** os totais do relatório já fechado MUST permanecer inalterados

#### Scenario: Projeto sem tarefas selecionadas não entra
- **WHEN** o cliente tem um projeto com tarefas elegíveis que não foram selecionadas
- **THEN** o projeto MUST NOT aparecer no relatório fechado

#### Scenario: Soma por projeto e total geral
- **WHEN** são selecionadas tarefas de dois projetos (P1: 8h a R$ 100/h; P2: 4h a R$ 150/h)
- **THEN** o relatório MUST registrar P1 com `total_horas == 8.0` e `valor_total == 800.0`, P2 com `total_horas == 4.0` e `valor_total == 600.0`
- **AND** o total geral MUST ser `12.0` horas e `1400.0` de valor

### Requirement: Tarefas selecionadas vão para status fechada

Ao concluir o fechamento, o sistema MUST atualizar o `status` de todas as tarefas selecionadas para `fechada`, na mesma operação em que o relatório é gravado. Tarefas não selecionadas MUST manter o status anterior.

#### Scenario: Status atualizado após fechamento
- **WHEN** o relatório de 05/2026 é fechado com as tarefas T1 e T2 selecionadas
- **THEN** T1 e T2 MUST estar com `status == "fechada"`

#### Scenario: Tarefas não selecionadas permanecem prontas
- **WHEN** a tarefa T3 elegível não foi selecionada no fechamento
- **THEN** T3 MUST permanecer com `status == "pronta"`

#### Scenario: Falha no fechamento não altera nada
- **WHEN** o fechamento falha por qualquer regra de validação
- **THEN** nenhuma tarefa MUST ter seu status alterado e nenhum relatório MUST ser gravado
