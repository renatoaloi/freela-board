# tarefa-transferencia-projeto Specification

## Purpose
Permite corrigir o cadastro de uma tarefa feita no projeto errado: move a tarefa (com apontamentos, horas e anexos) para outro projeto do mesmo cliente, sem precisar excluir e recriar.
## Requirements
### Requirement: Transferência restrita a projetos do mesmo cliente

O sistema MUST expor uma ação de transferência que aceite um `projeto_id` de destino pertencente ao **mesmo cliente** do projeto atual da tarefa. Projetos de outros clientes MUST NOT ser aceitos.

#### Scenario: Destino válido no mesmo cliente
- **WHEN** a tarefa T está no projeto P1 do cliente C e o usuário pede a transferência para P2 (também de C)
- **THEN** o sistema MUST atualizar `T.projeto_id` para P2
- **AND** os apontamentos de T MUST continuar existindo e somando as mesmas horas

#### Scenario: Destino de outro cliente é rejeitado
- **WHEN** o usuário pede a transferência para um projeto pertencente a outro cliente
- **THEN** o sistema MUST retornar `400` (ou `422`)
- **AND** a tarefa MUST permanecer no projeto de origem

#### Scenario: Somente projetos do cliente da tarefa são oferecidos
- **WHEN** o usuário abre a ação de mover tarefa
- **THEN** a lista de destinos MUST conter apenas projetos do cliente do projeto atual da tarefa

### Requirement: Projeto de destino precisa existir e ser diferente da origem

O `projeto_id` informado MUST corresponder a um projeto existente (404 caso contrário) e MUST ser diferente do projeto atual da tarefa (400 caso contrário). Tarefa inexistente MUST retornar 404.

#### Scenario: Projeto de destino inexistente
- **WHEN** o usuário informa um `projeto_id` que não existe
- **THEN** o sistema MUST retornar `404`

#### Scenario: Destino igual à origem
- **WHEN** o usuário seleciona o próprio projeto da tarefa
- **THEN** o sistema MUST retornar `400`
- **AND** nenhum efeito colateral MUST ocorrer (nenhum arquivo movido)

#### Scenario: Tarefa inexistente
- **WHEN** o `id` da tarefa não existe
- **THEN** o sistema MUST retornar `404`

### Requirement: Tarefa fechada ou em relatório não pode ser transferida

A tarefa MUST NOT ser transferida quando estiver com status `fechada` ou quando estiver vinculada a um relatório já fechado. Nesses casos o sistema MUST retornar `409` e MUST NOT alterar a tarefa nem os anexos.

#### Scenario: Tarefa fechada
- **WHEN** a tarefa está com status `fechada` e o usuário pede a transferência
- **THEN** o sistema MUST retornar `409`
- **AND** `projeto_id` MUST permanecer inalterado

#### Scenario: Tarefa vinculada a relatório fechado
- **WHEN** a tarefa consta em um relatório já fechado
- **THEN** o sistema MUST retornar `409` mesmo que o status tenha sido reaberto depois

#### Scenario: Tarefa em aberto é transferida normalmente
- **WHEN** a tarefa está `nova`, `em_andamento` ou `pronta` e não está em relatório
- **THEN** a transferência MUST ser concluída

### Requirement: Anexos são realocados para o novo projeto

Quando a tarefa possui anexos, o sistema MUST mover o conteúdo do diretório `storage/{cliente_id}/{projeto_origem}/{tarefa_id}/` para `storage/{cliente_id}/{projeto_destino}/{tarefa_id}/` na mesma operação. Após a transferência, download e preview dos anexos MUST continuar funcionando, e a lista `anexos` da tarefa MUST permanecer idêntica.

#### Scenario: Tarefa com anexos é movida
- **WHEN** uma tarefa com 2 anexos é transferida de P1 para P2 (mesmo cliente)
- **THEN** os arquivos MUST existir em `storage/{cliente}/P2/{tarefa}/`
- **AND** a pasta antiga `storage/{cliente}/P1/{tarefa}` MUST NOT existir mais
- **AND** `GET /upload/{tarefa}/{filename}` MUST continuar retornando o arquivo (200)

#### Scenario: Tarefa sem anexos
- **WHEN** uma tarefa sem anexos é transferida
- **THEN** a transferência MUST ser concluída sem criar pastas vazias e sem erro

#### Scenario: Falha ao mover reverte tudo
- **WHEN** ocorre qualquer erro durante a transferência (ex.: falha ao mover arquivos)
- **THEN** `projeto_id` MUST permanecer o de origem e os arquivos MUST continuar na pasta original

### Requirement: Ação disponível no detalhe da tarefa e no card do Kanban

A ação "Mover para outro projeto" MUST estar disponível na tela de detalhe da tarefa e no card do Kanban, abrindo uma seleção dos projetos do mesmo cliente. Após confirmar, a interface MUST recarregar os dados da tarefa/board refletindo o novo projeto.

#### Scenario: Mover a partir do detalhe
- **WHEN** o usuário está na tela `/tarefas/{id}` e escolhe outro projeto do cliente
- **THEN** a tarefa MUST passar a exibir o novo projeto
- **AND** o usuário MUST receber confirmação de sucesso

#### Scenario: Mover a partir do card do Kanban
- **WHEN** o usuário aciona a ação no card do Kanban e escolhe o destino
- **THEN** o board MUST ser recarregado
- **AND** a tarefa MUST sair das colunas do projeto filtrado (ela não pertence mais àquele projeto)

#### Scenario: Erros exibidos ao usuário
- **WHEN** o backend retorna 409/400/404
- **THEN** a interface MUST exibir a mensagem de erro em modal (padrão do projeto), sem `window.alert`

