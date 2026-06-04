## ADDED Requirements

### Requirement: GET /api/v1/dados-bancarios retorna o registro único

O endpoint `GET /api/v1/dados-bancarios` MUST retornar o registro único de dados bancários. Se não existir nenhum registro na tabela, o backend MUST criar um novo com UUID e todos os campos exceto `id` como `null`/string vazia, e retorná-lo. O endpoint MUST exigir `X-API-Key` válido (retornando 401 se ausente/inválido). A resposta MUST seguir o schema `DadosBancariosResponse`.

#### Scenario: Primeiro acesso (tabela vazia)
- **WHEN** o frontend chama `GET /api/v1/dados-bancarios` com `X-API-Key` válido e a tabela `dados_bancarios` está vazia
- **THEN** o backend cria um novo registro com `id` UUID, `banco_nome == null`, `banco_numero == null`, `agencia == null`, `conta == null`, `chave_pix == null`, `tipo_chave_pix == null`, e retorna status `200` com o registro criado

#### Scenario: Registro já existe
- **WHEN** o frontend chama `GET /api/v1/dados-bancarios` e já existe um registro na tabela
- **THEN** o backend retorna status `200` com os dados do registro existente

#### Scenario: Autenticação inválida
- **WHEN** o frontend chama o endpoint sem `X-API-Key` ou com valor inválido
- **THEN** o backend retorna `401`

### Requirement: PUT /api/v1/dados-bancarios atualiza o registro único

O endpoint `PUT /api/v1/dados-bancarios` MUST atualizar o registro único de dados bancários com os campos fornecidos no corpo da requisição. O corpo MUST aceitar `DadosBancariosUpdate` (todos os campos opcionais). Apenas os campos enviados (não-nulos) MUST ser atualizados. Se o registro não existir (improvável, dado o comportamento do GET), o backend MUST criá-lo. O endpoint MUST exigir `X-API-Key` válido.

#### Scenario: Atualização parcial
- **WHEN** o frontend envia `PUT /api/v1/dados-bancarios` com `{"banco_nome": "Nubank", "chave_pix": "123.456.789-00", "tipo_chave_pix": "cpf"}`
- **THEN** o backend atualiza apenas os campos enviados, mantendo os demais inalterados, e retorna status `200` com o registro completo atualizado

#### Scenario: Atualização completa
- **WHEN** o frontend envia `PUT /api/v1/dados-bancarios` com todos os campos preenchidos
- **THEN** o backend atualiza todos os campos e retorna status `200` com o registro completo atualizado

#### Scenario: Tipo de chave PIX inválido
- **WHEN** o frontend envia `PUT /api/v1/dados-bancarios` com `{"tipo_chave_pix": "invalido"}`
- **THEN** o backend retorna `422` com erro de validação

#### Scenario: Autenticação inválida
- **WHEN** o frontend chama `PUT` sem `X-API-Key` ou com valor inválido
- **THEN** o backend retorna `401`

### Requirement: Schema DadosBancariosResponse

O schema de resposta MUST conter: `id` (string UUID), `banco_nome` (string opcional), `banco_numero` (string opcional), `agencia` (string opcional), `conta` (string opcional), `chave_pix` (string opcional), `tipo_chave_pix` (string opcional), `created_at` (datetime), `updated_at` (datetime). MUST usar `model_config = {"from_attributes": True}`.

#### Scenario: Campo opcional nulo
- **WHEN** o registro tem `banco_nome == null` no banco
- **THEN** a resposta JSON MUST conter `"banco_nome": null`

### Requirement: Schema DadosBancariosUpdate

O schema de atualização MUST ter todos os campos como opcionais: `banco_nome` (string, max 255), `banco_numero` (string, max 20), `agencia` (string, max 20), `conta` (string, max 30), `chave_pix` (string, max 255), `tipo_chave_pix` (string, validado por enum `PixKeyType`).

#### Scenario: Todos os campos opcionais
- **WHEN** o frontend envia `PUT` com apenas `banco_nome`
- **THEN** a validação MUST aceitar (não exigir os demais campos)

### Requirement: Enum PixKeyType

O enum `PixKeyType` MUST ter os valores: `cpf`, `cnpj`, `email`, `telefone`. O schema `DadosBancariosUpdate` MUST validar `tipo_chave_pix` contra esse enum.

#### Scenario: Valor válido
- **WHEN** o frontend envia `tipo_chave_pix == "cpf"`
- **THEN** a validação aceita

#### Scenario: Valor inválido
- **WHEN** o frontend envia `tipo_chave_pix == "chave_aleatoria"`
- **THEN** a validação rejeita com `422`

### Requirement: Frontend — página /configuracoes com painel de dados bancários

A aplicação frontend MUST ter uma rota `/configuracoes` que renderiza a página `Configuracoes`. Esta página MUST conter um painel/card "Dados Bancários" com um formulário de edição. O formulário MUST carregar os dados via `dadosBancariosAPI.get()` ao montar o componente, e salvar via `dadosBancariosAPI.update()` ao clicar em "Salvar". O formulário MUST ter campos: Banco (text), Nº do Banco (text), Agência (text), Conta (text), Chave PIX (text), Tipo da Chave PIX (select com opções CPF, CNPJ, E-mail, Telefone). O sidebar MUST incluir um item "Configurações" que navega para `/configuracoes`.

#### Scenario: Página carrega dados existentes
- **WHEN** o usuário navega para `/configuracoes`
- **THEN** o formulário exibe os dados bancários carregados da API (ou vazio se nunca preenchido)

#### Scenario: Usuário preenche e salva
- **WHEN** o usuário preenche todos os campos e clica "Salvar"
- **THEN** o frontend chama `PUT /api/v1/dados-bancarios` com os dados preenchidos
- **AND** exibe mensagem de sucesso ao finalizar

#### Scenario: Erro ao salvar
- **WHEN** o usuário tenta salvar e a API retorna erro
- **THEN** o frontend exibe a mensagem de erro para o usuário

#### Scenario: Sidebar exibe "Configurações"
- **WHEN** o usuário abre o menu lateral
- **THEN** MUST haver um item "Configurações" com link para `/configuracoes`

### Requirement: Relatório JSON inclui dados bancários

O schema `RelatorioResponse` MUST incluir um campo opcional `dados_bancarios: Optional[RelatorioDadosBancariosInfo]`. O schema `RelatorioDadosBancariosInfo` MUST conter: `banco_nome`, `banco_numero`, `agencia`, `conta`, `chave_pix`, `tipo_chave_pix` (todos strings opcionais). O service de relatório MUST buscar os dados bancários e incluí-los na resposta. O campo MUST ser sempre incluído (pode ser `null` se o registro não existir/excepcionalmente).

#### Scenario: Dados bancários preenchidos
- **WHEN** o relatório é gerado e os dados bancários estão preenchidos
- **THEN** `result.dados_bancarios` MUST conter os campos preenchidos

#### Scenario: Dados bancários vazios
- **WHEN** o relatório é gerado e os dados bancários estão todos vazios
- **THEN** `result.dados_bancarios` MUST ser incluído com `banco_nome == null`, `banco_numero == null`, etc. (não ausente)

### Requirement: Frontend — dados bancários no relatório

O componente `RelatorioView.jsx` MUST exibir os dados bancários entre o card "Dados do Cliente" e o card "Resumo", em um card intitulado "Dados Bancários". O card MUST ser exibido apenas se ao menos um campo de dados bancários estiver preenchido (diferente de `null`/string vazia). O card MUST exibir: Banco, Nº do Banco, Agência, Conta, Chave PIX (com tipo entre parênteses).

#### Scenario: Card exibido com dados
- **WHEN** o relatório é gerado e `dados_bancarios.banco_nome == "Nubank"` e `dados_bancarios.chave_pix == "123.456.789-00"` e `dados_bancarios.tipo_chave_pix == "cpf"`
- **THEN** o card "Dados Bancários" MOSTRA "Nubank", a chave "123.456.789-00" com texto "(CPF)"

#### Scenario: Card oculto quando vazio
- **WHEN** o relatório é gerado e `dados_bancarios.banco_nome == null` e todos os demais campos são `null`
- **THEN** o card "Dados Bancários" NÃO é renderizado

### Requirement: PDF inclui dados bancários

O template `relatorio_pdf.html` MUST incluir uma seção "2. Dados Bancários" entre "1. Dados do Cliente" e "3. Resumo" (renumerando "2. Resumo" → "3. Resumo" e "3. Detalhamento" → "4. Detalhamento"). A seção MUST exibir: Banco, Nº do Banco, Agência, Conta, Chave PIX (com tipo). A seção MUST ser omitida se todos os campos estiverem vazios.

#### Scenario: PDF exibe dados bancários
- **WHEN** o PDF é gerado com dados bancários preenchidos
- **THEN** o PDF contém uma seção "2. Dados Bancários" entre os dados do cliente e o resumo, listando os campos preenchidos

#### Scenario: PDF omite seção vazia
- **WHEN** o PDF é gerado sem dados bancários preenchidos
- **THEN** o PDF não contém a seção "2. Dados Bancários" (a numeração segue "1. Dados do Cliente" → "2. Resumo" → "3. Detalhamento")
