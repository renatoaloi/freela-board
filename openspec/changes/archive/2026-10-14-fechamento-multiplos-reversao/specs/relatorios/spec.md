## ADDED Requirements

### Requirement: Reversão exclui o relatório e libera as tarefas

O sistema MUST permitir reverter um fechamento via `DELETE /api/v1/relatorios/{id}`: o relatório MUST ser removido (saindo da listagem e do download) e todas as tarefas que ele continha MUST voltar ao status `pronta` quando estiverem `fechada`, ficando elegíveis novamente para outro fechamento.

#### Scenario: Tarefas voltam a pronta
- **WHEN** o usuário reverte um relatório cujas tarefas estão `fechada`
- **THEN** cada tarefa do relatório MUST voltar para `status == "pronta"`

#### Scenario: Relatório sai da lista e do download
- **WHEN** a reversão é concluída e a lista de relatórios é consultada
- **THEN** o relatório MUST NOT aparecer na listagem
- **AND** `GET /relatorios/{id}` e `GET /relatorios/{id}/pdf` MUST retornar `404`

#### Scenario: Relatório inexistente
- **WHEN** é feita a reversão de um `id` inexistente
- **THEN** o backend MUST retornar `404`

#### Scenario: Autenticação obrigatória
- **WHEN** a reversão é chamada sem `X-API-Key` ou com chave inválida
- **THEN** o backend MUST retornar `401` e MUST NOT alterar nada

#### Scenario: Tarefa que mudou de status não é forçada
- **WHEN** uma tarefa do relatório revertido estava em outro status que não `fechada` (ex.: movida no Kanban depois do fechamento)
- **THEN** o status atual MUST ser preservado e a tarefa MUST voltar a ser elegível (o vínculo foi removido)

#### Scenario: Vínculos são removidos junto
- **WHEN** a reversão é concluída
- **THEN** as linhas que ligam tarefas ao relatório MUST ser removidas, sem deixar tarefas órfãs bloqueadas em fechamentos futuros

### Requirement: Tela de relatórios oferece a reversão

A listagem de relatórios MUST oferecer uma ação de reversão por relatório, com confirmação antes de executar (padrão de diálogo do projeto), exibindo mensagem de erro quando a operação falhar. Após reverter, a lista MUST ser recarregada.

#### Scenario: Confirmação antes de reverter
- **WHEN** o usuário aciona "Reverter" em um relatório da lista
- **THEN** o sistema MUST exibir um diálogo de confirmação informando que as tarefas voltarão a `pronta`
- **AND** nada MUST ser alterado até a confirmação

#### Scenario: Lista recarregada após reverter
- **WHEN** a reversão é confirmada e concluída
- **THEN** o relatório MUST desaparecer da lista automaticamente

#### Scenario: Erro na reversão
- **WHEN** o backend retorna erro na reversão
- **THEN** a interface MUST exibir a mensagem em modal (sem `window.alert`)

## REMOVED Requirements

### Requirement: Relatórios somente leitura
**Reason**: Passou a existir a operação de reversão, que exclui o relatório e devolve as tarefas para `pronta`. O relatório continua sem edição de conteúdo (não há update), mas não é mais somente leitura no sentido estrito.
**Migration**: Usar `DELETE /api/v1/relatorios/{id}` para reverter um fechamento; criação/atualização de relatório continuam inexistentes (a criação segue exclusiva do endpoint de fechamento).
