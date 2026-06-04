## ADDED Requirements

### Requirement: PDF inclui seção de dados bancários

O PDF MUST incluir uma seção "2. Dados Bancários" entre "1. Dados do Cliente" e "3. Resumo". A seção renumerada será: "1. Dados do Cliente", "2. Dados Bancários", "3. Resumo", "4. Detalhamento por Projeto". O conteúdo MUST exibir os campos preenchidos (Banco, Nº do Banco, Agência, Conta, Chave PIX com tipo). A seção MUST ser omitida se todos os campos estiverem vazios/nulos. Se omitida, a numeração volta a ser "1. Dados do Cliente", "2. Resumo", "3. Detalhamento por Projeto".

#### Scenario: PDF com dados bancários
- **WHEN** o PDF é gerado e há dados bancários preenchidos
- **THEN** o PDF contém, após "1. Dados do Cliente", a seção "2. Dados Bancários" com os campos visíveis
- **AND** o resumo passa a ser "3. Resumo" e "4. Detalhamento por Projeto"

#### Scenario: PDF sem dados bancários
- **WHEN** o PDF é gerado e os dados bancários estão todos vazios
- **THEN** a seção "2. Dados Bancários" é omitida e a numeração segue a sequência normal de 3 seções

### Requirement: Template Jinja2 condicional

O template `relatorio_pdf.html` MUST usar Jinja2 condicional (`{% if ... %}`) para exibir ou omitir a seção de dados bancários. A condição MUST verificar se ao menos um campo de `dados_bancarios` está preenchido.

#### Scenario: Condicional correta
- **WHEN** `dados_bancarios.banco_nome` não está vazio
- **THEN** a seção é renderizada com os dados disponíveis
- **WHEN** todos os campos de `dados_bancarios` estão vazios
- **THEN** a seção não é renderizada
