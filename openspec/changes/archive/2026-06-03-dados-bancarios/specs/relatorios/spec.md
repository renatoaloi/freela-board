## ADDED Requirements

### Requirement: Resposta do relatório inclui dados bancários

O objeto `RelatorioResponse` MUST incluir um campo `dados_bancarios` (objeto, pode ser `null` se não houver dados). O objeto MUST conter: `banco_nome`, `banco_numero`, `agencia`, `conta`, `chave_pix`, `tipo_chave_pix` (todos strings, podem ser `null`). O frontend MUST ler `result.dados_bancarios` para exibir o card "Dados Bancários".

#### Scenario: Dados bancários preenchidos
- **WHEN** o relatório é gerado e os dados bancários estão preenchidos
- **THEN** `result.dados_bancarios` MUST ser um objeto com os campos preenchidos (ex: `banco_nome: "Nubank"`)

#### Scenario: Dados bancários vazios/inexistentes
- **WHEN** o relatório é gerado e não há dados bancários (tabela não existe ou todos os campos nulos)
- **THEN** `result.dados_bancarios` MUST ser `null` ou um objeto com todos os campos `null`

### Requirement: Frontend exibe dados bancários entre cliente e resumo

O componente `RelatorioView.jsx` MUST renderizar um card "Dados Bancários" entre o card "Dados do Cliente" e o card "Resumo", condicionalmente. O card MUST ser exibido apenas se ao menos um campo de `dados_bancarios` estiver preenchido.

#### Scenario: Card renderizado com dados
- **WHEN** `result.dados_bancarios` tem `banco_nome == "Nubank"`
- **THEN** o card "Dados Bancários" é renderizado com "Nubank" visível

#### Scenario: Card oculto sem dados
- **WHEN** `result.dados_bancarios` é `null` ou todos os campos são `null`
- **THEN** o card "Dados Bancários" NÃO é renderizado
