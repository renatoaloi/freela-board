## MODIFIED Requirements

### Requirement: Apenas tarefas prontas do período são elegíveis

O sistema MUST expor uma consulta de tarefas elegíveis ao fechamento que retorne **somente** tarefas que (a) pertençam a projetos do cliente informado, (b) tenham `status == "pronta"`, (c) tenham ao menos um apontamento com data dentro do mês/ano informados, e (d) **não estejam vinculadas a nenhum relatório existente**. Tarefas nos status `nova`, `em_andamento` e `fechada` MUST NOT aparecer na lista de elegíveis, e uma tarefa liberada por uma reversão MUST voltar a aparecer.

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
- **WHEN** uma tarefa foi incluída em um relatório e voltou ao fluxo (ex.: status alterado manualmente) mantendo o vínculo
- **THEN** a tarefa MUST NOT aparecer na lista de elegíveis de outro fechamento

#### Scenario: Projeto usado como recorte adicional
- **WHEN** o usuário seleciona também um projeto do cliente
- **THEN** a lista MUST retornar apenas tarefas elegíveis daquele projeto

#### Scenario: Tarefa liberada por reversão volta a ser elegível
- **WHEN** um relatório que continha a tarefa foi revertido e a tarefa voltou a `pronta`
- **THEN** a tarefa MUST reaparecer na lista de elegíveis da mesma competência

### Requirement: Fechamento exige cliente, período e ao menos uma tarefa

O endpoint de fechamento MUST exigir header `X-API-Key` válido (401 se ausente/inválido), `cliente_id` existente (404 caso contrário), `mes` entre 1 e 12, `ano`, e uma lista não vazia de `tarefa_ids`. Todas as tarefas MUST pertencer ao cliente informado, estar `pronta` e não estar vinculadas a outro relatório. Requisições fora dessas regras MUST retornar 422 (ou 404 conforme o caso) e MUST NOT criar relatório nem alterar status de tarefas.

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

#### Scenario: Tarefa já faturada em outro relatório é rejeitada
- **WHEN** `tarefa_ids` contém uma tarefa vinculada a um relatório já existente (mesmo mês ou não)
- **THEN** o backend MUST retornar erro (`400` ou `422`)
- **AND** a tarefa MUST NOT entrar em um segundo relatório

## ADDED Requirements

### Requirement: Múltiplos fechamentos por cliente e competência

O sistema MUST permitir mais de um relatório fechado para a mesma combinação de cliente, mês e ano. Cada fechamento daquele cliente/competência MUST receber um `numero` sequencial (1, 2, 3...) calculado no momento do fechamento, e esse número MUST acompanhar o relatório na listagem, no detalhe e no nome do PDF.

#### Scenario: Segundo fechamento do mesmo cliente e mês é permitido
- **WHEN** já existe o relatório 1 do cliente X em 10/2026 e o usuário fecha outra tarefa elegível de 10/2026
- **THEN** um novo relatório MUST ser criado com `numero == 2`
- **AND** o relatório 1 MUST permanecer inalterado na lista

#### Scenario: Numeração por competência
- **WHEN** o cliente fecha um relatório em 10/2026 e outro em 11/2026
- **THEN** cada um MUST ter `numero == 1` (a numeração é por cliente + mês + ano)

#### Scenario: Numeração após reversão
- **WHEN** o relatório 2 de um cliente/mês é revertido e um novo fechamento é feito
- **THEN** o novo relatório MUST receber o próximo número disponível sem reaproveitar o número revertido quando houver outro relatório ativo com o mesmo número

## REMOVED Requirements

### Requirement: Um relatório por cliente e competência
**Reason**: Um mês pode ter mais de um faturamento por cliente (fechamentos parciais, frentes distintas), e a trava impedia inclusive refazer um fechamento com tarefas esquecidas — problema agora resolvido pela reversão. A proteção contra duplicidade passa a ser por tarefa, não por competência.
**Migration**: O endpoint deixa de retornar `409` por competência existente; clientes que tratavam o 409 devem passar a tratar apenas erro de tarefa não elegível (`422`).
