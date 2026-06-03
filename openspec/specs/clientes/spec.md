## Requirements

### Requirement: Cadastro de cliente inclui CEP

O cadastro de clientes MUST incluir o campo `cep` como VARCHAR(9) no formato `XXXXX-XXX`. O campo MUST ser obrigatório no cadastro e opcional na atualização (para compatibilidade com registros existentes).

#### Scenario: Criação de cliente com CEP válido
- **WHEN** o usuário cria um cliente informando `cep: "04571010"` (8 dígitos)
- **THEN** o sistema MUST armazenar `"04571-010"` (formatado com hífen)
- **AND** a resposta MUST incluir `cep: "04571-010"`

#### Scenario: Criação com CEP inválido (menos de 8 dígitos)
- **WHEN** o usuário informa `cep` com menos de 8 dígitos
- **THEN** o sistema MUST retornar erro de validação (422)

#### Scenario: Criação com CEP já formatado
- **WHEN** o usuário informa `cep: "04571-010"` (já com hífen)
- **THEN** o sistema MUST aceitar e armazenar como `"04571-010"`

#### Scenario: Atualização de cliente omitindo CEP
- **WHEN** o usuário atualiza um cliente sem enviar o campo `cep`
- **THEN** o sistema MUST manter o CEP existente inalterado

### Requirement: Endereço exibe CEP em todos os lugares

O CEP MUST ser exibido junto ao endereço do cliente em: listagem de clientes, formulário de edição, relatório na tela e relatório PDF.

#### Scenario: Listagem de clientes mostra CEP
- **WHEN** o usuário acessa a lista de clientes
- **THEN** a tabela MUST exibir uma coluna "CEP" com o valor formatado

#### Scenario: Relatório na tela mostra CEP
- **WHEN** o usuário gera um relatório de horas
- **THEN** o card "Dados do Cliente" MUST exibir o CEP junto ao endereço no formato `CEP XXXXX-XXX`

#### Scenario: PDF do relatório mostra CEP
- **WHEN** o usuário baixa o PDF do relatório
- **THEN** a seção "Dados do Cliente" MUST incluir o CEP no formato `CEP XXXXX-XXX`

### Requirement: Migração de dados existentes

Clientes cadastrados antes da adição do campo CEP MUST ter `cep` como string vazia (`""`), sem quebrar nenhuma funcionalidade.

#### Scenario: Cliente antigo sem CEP
- **WHEN** um cliente existente (sem CEP) é visualizado
- **THEN** o campo `cep` MUST ser retornado como `""`
- **AND** a exibição do endereço MUST omitir o CEP (não mostrar "CEP " vazio)

#### Scenario: Cliente antigo é atualizado com CEP
- **WHEN** um cliente existente (sem CEP) é editado e recebe um CEP válido
- **THEN** o sistema MUST armazenar e exibir o CEP normalmente
