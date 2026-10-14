## ADDED Requirements

### Requirement: Fechamento registra o detalhamento diário e os anexos da tarefa

O snapshot gravado no fechamento MUST conter, para cada tarefa selecionada, além de `tarefa_id`, `titulo` e `total_horas`: a `descricao` da tarefa, a lista de `anexos` (nomes dos arquivos) e os apontamentos **agrupados por dia** — cada dia com `data`, `total_horas` do dia e a lista de apontamentos (`hora_ini`, `hora_fim`, `total_horas`). Apenas os apontamentos pertencentes à competência fechada MUST entrar no detalhamento, e os dias MUST vir em ordem crescente de data.

#### Scenario: Tarefa com apontamentos em dois dias
- **WHEN** uma tarefa teve apontamentos em 2026-05-10 (08:00-10:00) e 2026-05-12 (14:00-17:00) e o mês 05/2026 é fechado
- **THEN** o snapshot da tarefa MUST conter 2 dias, nessa ordem
- **AND** cada dia MUST listar seus apontamentos com `hora_ini`, `hora_fim` e `total_horas`

#### Scenario: Apontamentos fora da competência ficam de fora
- **WHEN** a tarefa também tem um apontamento em 2026-04-30 e o fechamento é de 05/2026
- **THEN** o apontamento de abril MUST NOT aparecer no detalhamento da tarefa

#### Scenario: Descrição e anexos são congelados junto
- **WHEN** o fechamento é realizado e a tarefa tem descrição e 2 anexos
- **THEN** o snapshot MUST conter a `descricao` e a lista com os 2 nomes de arquivos
- **AND** anexos adicionados depois MUST NOT aparecer no relatório já fechado

#### Scenario: Tarefa sem descrição e sem anexos
- **WHEN** o fechamento seleciona uma tarefa sem descrição e sem nenhum anexo
- **THEN** `descricao` MUST ser `null` e `anexos` MUST ser uma lista vazia (não `null`)
