# kanban-filtro-mes Specification

## Purpose
Permite filtrar o Kanban por competência (mês e ano), exibindo as tarefas que tiveram horas lançadas no período escolhido mais as que não têm nenhum apontamento (qualquer competência).
## Requirements
### Requirement: Filtro de competência considera a data dos apontamentos

O Kanban MUST permitir selecionar um mês e um ano e, quando ambos estiverem definidos, exibir as tarefas que possuem ao menos um apontamento com data dentro daquele mês/ano **ou** que não possuem nenhum apontamento. Uma tarefa que tem apontamentos apenas em **outros** meses/anos MUST NOT aparecer na competência filtrada, independentemente do status ou da data de criação.

#### Scenario: Tarefa com apontamento no mês aparece
- **WHEN** o usuário seleciona 05/2026 e existe uma tarefa com apontamento em 2026-05-15
- **THEN** a tarefa MUST aparecer no Kanban

#### Scenario: Tarefa sem apontamento no mês não aparece
- **WHEN** o usuário seleciona 05/2026 e uma tarefa (mesmo `pronta`) só tem apontamentos em 2026-04-30
- **THEN** a tarefa MUST NOT aparecer no Kanban

#### Scenario: Múltiplos apontamentos não duplicam a tarefa
- **WHEN** uma tarefa tem apontamentos em 2026-05-10, 2026-05-12 e 2026-05-20
- **THEN** a tarefa MUST aparecer uma única vez no Kanban

#### Scenario: Mês diferente com mesmo número
- **WHEN** há apontamento em 2025-05-15 e o filtro é 05/2026
- **THEN** a tarefa MUST NOT aparecer (o ano também é considerado)

#### Scenario: Tarefa sem nenhum apontamento aparece em qualquer competência
- **WHEN** uma tarefa recém-criada não tem nenhum apontamento e a competência selecionada é 05/2026
- **THEN** a tarefa MUST aparecer no Kanban
- **AND** a tarefa MUST aparecer em qualquer outro mês/ano selecionado (enquanto não tiver apontamentos)

#### Scenario: Tarefa sem apontamento continua visível ao trocar a competência
- **WHEN** a competência é alterada de 05/2026 para 06/2026 e existe uma tarefa sem apontamentos
- **THEN** a tarefa MUST continuar visível no Kanban

### Requirement: Filtro de competência combina com cliente e projeto

O filtro de mês/ano MUST ser aplicado em conjunto com os filtros existentes de cliente e projeto, exibindo as tarefas do recorte que tenham apontamento na competência selecionada ou não tenham nenhum apontamento. O filtro MUST poder ser limpo, voltando a exibir todas as tarefas do recorte selecionado.

#### Scenario: Combinação com filtro de projeto
- **WHEN** o usuário seleciona projeto P e competência 05/2026
- **THEN** as tarefas de P exibidas MUST ser as que têm apontamento em 05/2026 mais as que não têm nenhum apontamento
- **AND** as tarefas de P com apontamentos apenas fora de 05/2026 MUST NOT aparecer

#### Scenario: Sem competência selecionada exibe todas
- **WHEN** o usuário limpa o filtro de mês/ano
- **THEN** o Kanban MUST exibir todas as tarefas dos filtros de cliente/projeto ativos, sem restrição de período

### Requirement: Competência selecionada é preservada entre sessões

O mês e o ano escolhidos no Kanban MUST ser persistidos (mesmo mecanismo de `localStorage` já usado para cliente e projeto) e restaurados ao reabrir a tela. Quando não houver valor salvo, o filtro MUST iniciar no mês/ano corrente.

#### Scenario: Preferência restaurada
- **WHEN** o usuário seleciona 05/2026, sai da tela e retorna
- **THEN** o filtro MUST estar em 05/2026

#### Scenario: Primeiro acesso usa o mês atual
- **WHEN** o usuário abre o Kanban sem competência salva
- **THEN** o filtro MUST iniciar com o mês e o ano de hoje

