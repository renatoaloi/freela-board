## MODIFIED Requirements

### Requirement: Resposta inclui projetos com tarefas agrupadas

O array `projetos` MUST incluir um item por projeto que teve tarefas **selecionadas** no fechamento. Cada item MUST incluir `projeto_id`, `titulo`, `valor_por_hora`, `total_horas`, `valor_total` e `tarefas: [RelatorioTarefaItem]`, com apenas as tarefas escolhidas. Cada `RelatorioTarefaItem` MUST incluir `tarefa_id`, `titulo`, `total_horas`, `descricao` (pode ser `null`), `anexos` (lista de nomes de arquivo, possivelmente vazia) e `dias` — lista de dias em ordem crescente, cada um com `data`, `total_horas` do dia e `apontamentos` (`hora_ini`, `hora_fim`, `total_horas`).

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

#### Scenario: Detalhamento diário vem do snapshot
- **WHEN** o relatório é lido por `id`
- **THEN** `projetos[0].tarefas[0].dias` MUST conter os dias gravados no fechamento, cada um com seus apontamentos
- **AND** a soma de `total_horas` dos dias MUST ser igual a `total_horas` da tarefa no relatório

## ADDED Requirements

### Requirement: Frontend exibe detalhamento diário e imagens da tarefa

A tela de detalhe do relatório MUST exibir, dentro de cada projeto, o bloco de cada tarefa com: título, total de horas, dias com os respectivos apontamentos (data, hora início/fim e horas do dia), a descrição da tarefa (quando houver) e miniaturas das imagens anexadas, quando houver.

#### Scenario: Dias e apontamentos visíveis
- **WHEN** o usuário abre um relatório cuja tarefa teve apontamentos em 2 dias distintos
- **THEN** o bloco da tarefa MUST listar os 2 dias, cada um com seus apontamentos

#### Scenario: Miniaturas das imagens
- **WHEN** a tarefa do relatório tem 2 imagens anexadas
- **THEN** o bloco da tarefa MUST exibir as 2 imagens (miniaturas carregadas do endpoint de upload)

#### Scenario: Tarefa sem anexos de imagem
- **WHEN** a tarefa só tem anexos que não são imagem (ou nenhum anexo)
- **THEN** nenhuma miniatura MUST ser exibida para aquela tarefa
