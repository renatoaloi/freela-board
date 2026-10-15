## Purpose

Geração do PDF do relatório de horas em layout A4 profissional para envio ao cliente/contador, renderizado a partir do snapshot gravado no fechamento do mês (echamento-mensal).
## Requirements
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

O PDF MUST conter todas as seções do relatório (dados do cliente, resumo de totais e detalhamento por projeto). No detalhamento, cada **projeto** MUST iniciar em página nova (a partir do segundo projeto da lista), e sua **primeira tarefa** MUST seguir logo abaixo do cabeçalho, na mesma página; as **demais tarefas** do projeto MUST abrir página nova. O cabeçalho do projeto MUST NOT ficar isolado no fim de uma página, e MUST NOT haver página em branco entre o cabeçalho do projeto e sua primeira tarefa.

#### Scenario: Dados do cliente
- **WHEN** o relatório é gerado
- **THEN** o PDF MUST exibir: razão social, nome fantasia, CNPJ formatado, endereço completo (endereço + complemento + bairro), cidade/estado, e email

#### Scenario: Resumo de totais
- **WHEN** o relatório é gerado
- **THEN** o PDF MUST exibir "Total de Horas" e "Valor Total" em seção própria
- **AND** o valor total MUST estar formatado como moeda (R$ 1.234,56)

#### Scenario: Detalhamento por projeto
- **WHEN** há projetos com tarefas selecionadas no período
- **THEN** o PDF MUST listar cada projeto com: título, valor por hora, total de horas e valor total
- **AND** o primeiro projeto MUST continuar no fluxo da seção e os demais MUST começar em página nova
- **AND** o cabeçalho do projeto MUST ser seguido imediatamente pela sua primeira tarefa

#### Scenario: Tarefas dentro de cada projeto
- **WHEN** um projeto tem tarefas selecionadas
- **THEN** cada tarefa MUST ser renderizada em bloco próprio
- **AND** a primeira tarefa MUST NOT forçar quebra de página

#### Scenario: Sem página em branco após o cabeçalho do projeto
- **WHEN** o cabeçalho do projeto termina próximo ao fim de uma página
- **THEN** o sistema MUST manter o cabeçalho junto da primeira tarefa (`page-break-after: avoid` no cabeçalho)
- **AND** o PDF MUST NOT gerar página em branco entre os dois

#### Scenario: Uma página por tarefa
- **WHEN** um projeto tem mais de uma tarefa
- **THEN** cada tarefa a partir da segunda MUST começar no topo de uma nova página (`page-break-before: always`)
- **AND** a primeira tarefa do projeto MUST seguir na mesma página do cabeçalho, sem forçar quebra
- **AND** o bloco da tarefa MUST NOT ser cortado no meio (`page-break-inside: avoid`)

#### Scenario: Apontamentos agrupados por dia dentro da tarefa
- **WHEN** uma tarefa do relatório teve apontamentos em 2026-05-10 e 2026-05-12
- **THEN** o bloco da tarefa MUST exibir uma entrada por dia, em ordem crescente, cada uma com a data e os apontamentos (hora início, hora fim e horas do dia) daquele dia

#### Scenario: Descrição da tarefa no PDF
- **WHEN** a tarefa tem descrição gravada no snapshot
- **THEN** o bloco da tarefa MUST exibir a descrição renderizada como texto simples (sem quebra de marcação markdown solta)
- **AND** quando não há descrição, a linha MUST ser omitida

#### Scenario: Mosaico de imagens da tarefa
- **WHEN** a tarefa tem de 1 a 10 imagens anexadas
- **THEN** o PDF MUST renderizar as imagens em mosaico dentro do bloco da tarefa (grid com largura proporcional à quantidade)
- **AND** cada imagem MUST manter a proporção e MUST NOT estourar a margem da página

#### Scenario: Imagens são reduzidas antes de entrar no PDF
- **WHEN** o PDF é gerado para uma tarefa com imagens anexadas
- **THEN** cada imagem MUST ser redimensionada para caber em uma caixa de 400x400 pixels (mantendo a proporção e sem ampliar imagens menores) antes de ser embutida
- **AND** a imagem MUST ser codificada como JPEG (qualidade 75), descartando canal alfa quando houver

#### Scenario: Imagem renderizada no tamanho reduzido
- **WHEN** o PDF é aberto em um leitor
- **THEN** a imagem MUST ser exibida no tamanho reduzido (tamanho natural da versão redimensionada), sem ampliação para a largura da coluna
- **AND** uma imagem MUST NOT ocupar sozinha mais da metade da área útil da página

#### Scenario: Anexos não-imagem são ignorados
- **WHEN** a tarefa tem anexos PDF e uma imagem
- **THEN** apenas a imagem MUST aparecer no PDF
- **AND** nenhuma lista de nomes de arquivos MUST ser renderizada

#### Scenario: Arquivo de imagem ausente não quebra o PDF
- **WHEN** o anexo consta no snapshot mas o arquivo não existe no storage (ex.: apagado após o fechamento)
- **THEN** aquela imagem MUST ser omitida e o restante do relatório MUST ser gerado normalmente

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

### Requirement: Endpoint retorna PDF do relatório fechado

O endpoint `GET /api/v1/relatorios/{id}/pdf` MUST retornar o PDF do relatório **já fechado** correspondente ao `id` informado. O conteúdo MUST refletir o snapshot gravado no fechamento (tarefas selecionadas e totais congelados), e não um recálculo dos apontamentos do período.

#### Scenario: Chamada bem-sucedida retorna PDF
- **WHEN** o frontend chama `GET /api/v1/relatorios/{id}/pdf` com `X-API-Key` válido
- **THEN** a resposta MUST ter `Content-Type: application/pdf`
- **AND** a resposta MUST ter `Content-Disposition: attachment` com filename no padrão `relatorio-{slug}-{mes}-{ano}.pdf`
- **AND** o corpo MUST ser um PDF válido (inicia com `%PDF-`)

#### Scenario: Relatório inexistente retorna 404
- **WHEN** o `id` não corresponde a nenhum relatório fechado
- **THEN** o endpoint MUST retornar `404`
- **AND** a resposta MUST ser JSON, não PDF

#### Scenario: Header de autenticação inválido retorna 401
- **WHEN** o `X-API-Key` não corresponde à chave configurada
- **THEN** o endpoint MUST retornar `401`

#### Scenario: Conteúdo limitado às tarefas selecionadas
- **WHEN** o fechamento selecionou apenas parte das tarefas elegíveis
- **THEN** o PDF MUST listar somente as tarefas selecionadas e seus totais congelados

### Requirement: Botão "Baixar PDF" no relatório fechado

O frontend MUST exibir um botão "Baixar PDF" na visualização do relatório fechado (na lista e/ou no detalhe), que dispara o download do PDF daquele relatório. A ação MUST NOT depender de uma geração prévia na tela.

#### Scenario: Botão disponível na lista e no detalhe
- **WHEN** o usuário visualiza a lista de relatórios fechados ou o detalhe de um deles
- **THEN** o botão "Baixar PDF" MUST estar visível, sem exigir gerar relatório antes

#### Scenario: Download a partir da lista
- **WHEN** o usuário clica em "Baixar PDF" em um item da lista de relatórios fechados
- **THEN** o navegador MUST iniciar o download de `relatorio-{nome_cliente}-{mes}-{ano}.pdf`
- **AND** o download MUST usar o nome gerado pelo servidor no `Content-Disposition`

#### Scenario: Erro ao baixar
- **WHEN** o servidor retorna erro (ex: 404)
- **THEN** o frontend MUST exibir a mensagem de erro para o usuário (não tentar fazer download de JSON como PDF)

