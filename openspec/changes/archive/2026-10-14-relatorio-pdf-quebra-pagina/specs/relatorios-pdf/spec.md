## MODIFIED Requirements

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
