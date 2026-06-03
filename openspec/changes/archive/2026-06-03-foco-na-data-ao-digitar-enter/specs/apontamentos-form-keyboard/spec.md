## ADDED Requirements

### Requirement: Foco automático no campo data ao montar o formulário
O formulário de apontamentos SHALL focar automaticamente no campo data quando o componente for montado.

#### Scenario: Formulário montado em aba visível
- **WHEN** o componente `ApontamentoForm` é montado em uma aba visível
- **THEN** o campo data recebe foco automaticamente

### Requirement: Foco no campo data após salvamento bem-sucedido
O formulário SHALL retornar o foco ao campo data imediatamente após um apontamento ser salvo com sucesso.

#### Scenario: Submit com Enter no campo hora_fim
- **WHEN** o usuário digita Enter enquanto o campo hora_fim está focado
- **THEN** o formulário é submetido
- **AND** se o salvamento for bem-sucedido, o campo data recebe foco

#### Scenario: Submit com clique no botão +
- **WHEN** o usuário clica no botão +
- **THEN** o formulário é submetido
- **AND** se o salvamento for bem-sucedido, o campo data recebe foco

### Requirement: Foco NÃO deve ser redirecionado em caso de erro
Se o salvamento falhar, o formulário SHALL manter o foco onde estava (não redirecionar para o campo data), para que a mensagem de erro permaneça visível.

#### Scenario: Erro no salvamento
- **WHEN** o salvamento do apontamento falha
- **THEN** o campo data NÃO recebe foco automaticamente
- **AND** a mensagem de erro permanece visível
