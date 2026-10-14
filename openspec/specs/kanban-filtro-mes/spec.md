# kanban-filtro-mes Specification

## Purpose
Permite filtrar o Kanban por competência (mês e ano), exibindo apenas as tarefas que tiveram horas lançadas no período escolhido.
## Requirements
### Requirement: Filtro de competência considera a data dos apontamentos

O Kanban MUST permitir selecionar um mês e um ano e, quando ambos estiverem definidos, exibir apenas as tarefas que possuem ao menos um apontamento com data dentro daquele mês/ano. Tarefas sem apontamento no período MUST NOT ser exibidas, independentemente do status ou da data de criação.

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

### Requirement: Filtro de competência combina com cliente e projeto

O filtro de mês/ano MUST ser aplicado em conjunto com os filtros existentes de cliente e projeto, e MUST poder ser limpo, voltando a exibir todas as tarefas do recorte selecionado.

#### Scenario: Combinação com filtro de projeto
- **WHEN** o usuário seleciona projeto P e competência 05/2026
- **THEN** apenas tarefas de P com apontamento em 05/2026 MUST aparecer

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

