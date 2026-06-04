## ADDED Requirements

### Requirement: Endpoint retorna PDF do relatório de horas

O endpoint `GET /api/v1/relatorios/pdf` MUST aceitar os mesmos query params do endpoint JSON (`cliente_id`, `mes`, `ano`) e retornar um documento PDF gerado no servidor. O PDF MUST ter o mesmo conteúdo do relatório JSON, renderizado em layout profissional A4.

#### Scenario: Chamada bem-sucedida retorna PDF
- **WHEN** o frontend chama `GET /api/v1/relatorios/pdf?cliente_id=X&mes=5&ano=2026` com `X-API-Key` válido e há apontamentos no período
- **THEN** a resposta MUST ter `Content-Type: application/pdf`
- **AND** a resposta MUST ter `Content-Disposition: attachment` com filename no padrão `relatorio-{slug}-{mes}-{ano}.pdf`
- **AND** o corpo MUST ser um PDF válido (inicia com `%PDF-`)

#### Scenario: Sem apontamentos retorna PDF com zeros
- **WHEN** o cliente existe mas não há apontamentos no mês/ano
- **THEN** o PDF MUST mostrar totais zerados e array de projetos vazio
- **AND** o cliente e o período MUST aparecer normalmente no cabeçalho

#### Scenario: Cliente inexistente retorna 404
- **WHEN** `cliente_id` não existe no banco
- **THEN** o endpoint MUST retornar `404` com `detail: "Cliente not found"`
- **AND** a resposta MUST ser JSON, não PDF

#### Scenario: Query params ausentes retorna 422
- **WHEN** qualquer query param obrigatório (`cliente_id`, `mes`, `ano`) está ausente
- **THEN** o endpoint MUST retornar `422` (validation error do FastAPI)

#### Scenario: Header de autenticação inválido retorna 401
- **WHEN** o `X-API-Key` não corresponde à chave configurada
- **THEN** o endpoint MUST retornar `401`

### Requirement: Layout profissional A4

O PDF MUST usar formato A4, margens de 2.5cm, tipografia Liberation Sans (≈Arial, padrão da indústria para documentos empresariais), e paleta sóbria em tons de cinza (sem cores, sem logos).

#### Scenario: Configuração de página
- **WHEN** o PDF é aberto em qualquer leitor (Adobe, Chrome, etc.)
- **THEN** o formato MUST ser A4 (210mm × 297mm)
- **AND** as margens esquerda/direita/superior MUST ser 2.5cm
- **AND** a margem inferior MUST ser 3.0cm (para comportar numeração de páginas)

#### Scenario: Numeração de páginas
- **WHEN** o PDF tem mais de uma página
- **THEN** toda página exceto a primeira (ou todas) MUST ter "Página X de Y" no rodapé centralizado

#### Scenario: Data de geração
- **WHEN** o PDF é gerado
- **THEN** o rodapé do documento MUST conter "Documento gerado em DD/MM/AAAA às HH:MM" com a data/hora atual do servidor

### Requirement: Conteúdo do relatório no PDF

O PDF MUST conter todas as seções do relatório: dados do cliente, resumo de totais, e detalhamento por projeto com tarefas aninhadas.

#### Scenario: Dados do cliente
- **WHEN** o relatório é gerado
- **THEN** o PDF MUST exibir: razão social, nome fantasia, CNPJ formatado, endereço completo (endereço + complemento + bairro), cidade/estado, e email

#### Scenario: Resumo de totais
- **WHEN** o relatório é gerado
- **THEN** o PDF MUST exibir "Total de Horas" e "Valor Total" em seção própria
- **AND** o valor total MUST estar formatado como moeda (R$ 1.234,56)

#### Scenario: Detalhamento por projeto
- **WHEN** há projetos com apontamentos no período
- **THEN** o PDF MUST listar cada projeto com: título, valor por hora, total de horas, valor total, e tabela de tarefas (título + horas)
- **AND** cada projeto MUST ter quebra de página mínima (`page-break-inside: avoid`) para não separar título da tabela

#### Scenario: Tarefas dentro de cada projeto
- **WHEN** um projeto tem tarefas com apontamentos
- **THEN** o PDF MUST renderizar uma tabela com colunas "Tarefa" e "Horas" abaixo do projeto
- **AND** se o projeto não tem tarefas agrupáveis, a tabela de tarefas MUST ser omitida

### Requirement: Botão "Baixar PDF" no frontend

O frontend MUST exibir um botão "Baixar PDF" ao lado do botão "Imprimir" existente, que dispara o download do PDF.

#### Scenario: Botão visível após gerar relatório
- **WHEN** o usuário clica "Gerar Relatório" e o resultado é exibido
- **THEN** o botão "Baixar PDF" MUST estar visível ao lado do botão "Imprimir"
- **AND** o botão MUST ter um ícone de download (ArrowDownTrayIcon ou similar)

#### Scenario: Click baixa o PDF
- **WHEN** o usuário clica "Baixar PDF"
- **THEN** o navegador MUST iniciar o download de um arquivo `relatorio-{nome_cliente}-{mes}-{ano}.pdf`
- **AND** o download MUST usar o nome gerado pelo servidor no `Content-Disposition`

#### Scenario: Erro ao baixar
- **WHEN** o servidor retorna erro (ex: 404, 422)
- **THEN** o frontend MUST exibir a mensagem de erro para o usuário (não tentar fazer download de JSON como PDF)

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
