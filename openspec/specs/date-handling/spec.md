# Spec: date-handling

> Capability: `date-handling` — convenção do frontend para receber, exibir e gerar datas que vieram do backend. Aplica-se a qualquer data de domínio (`apontamento.data`, `tarefa.data_criacao`, `projeto.data_criacao`).

## Purpose

O backend devolve `date` (Pydantic v2 + SQLAlchemy `Date` + SQLite) como string `YYYY-MM-DD` no JSON, sem designador de fuso horário. Pela spec ECMAScript, `new Date("YYYY-MM-DD")` é interpretado como **UTC midnight**, o que faz `toLocaleDateString` recuar um dia em qualquer fuso a oeste do UTC (ex.: Brasil UTC-3 → D-1). Por isso o frontend centraliza a renderização e a geração de "hoje" em um único helper (`src/utils/date.js`) que **não usa** `new Date` para formatar nem `toISOString` para gerar a data corrente.

i18n (formatos diferentes de `dd/MM/yyyy` ou outros locales) está fora de escopo. O app é single-user pt-BR.

## Requirements

### Requirement: Renderização de data não aplica conversão de fuso horário

O frontend MUST exibir a string de data `YYYY-MM-DD` retornada pelo backend como **literal de calendário**, sem aplicar conversão de fuso horário. Especificamente, o frontend MUST NOT usar `new Date("YYYY-MM-DD")` (que a spec ECMAScript define como UTC midnight e gera drift de `D-1` em fusos a oeste do UTC) para renderizar essas strings.

#### Scenario: Data 11/06/2026 digitada pelo usuário é renderizada como 11/06/2026
- **WHEN** o backend devolve `"2026-06-11"` para `apontamento.data`, `tarefa.data_criacao` ou `projeto.data_criacao` em um fuso UTC-3 (BRT)
- **THEN** o frontend MUST renderizar a data como `11/06/2026`, e MUST NOT renderizar como `10/06/2026`

#### Scenario: Data 26/05/2026 é renderizada sem drift
- **WHEN** o backend devolve `"2026-05-26"` em um fuso UTC-3
- **THEN** o frontend MUST renderizar a data como `26/05/2026`, e MUST NOT renderizar como `25/05/2026`

#### Scenario: Data em fuso UTC+0 não tem drift visível
- **WHEN** o backend devolve `"2026-06-11"` em um fuso UTC+0
- **THEN** o frontend MUST renderizar a data como `11/06/2026` (sem regressão em fusos onde o bug original não se manifesta)

### Requirement: Helper único `formatDateBR` para formatar datas do backend

O frontend MUST expor uma função `formatDateBR(iso)` em `src/utils/date.js` que recebe uma string `YYYY-MM-DD` (ou `null`/`undefined`) e devolve a data no formato `dd/MM/yyyy` (ou string vazia para entrada nula/vazia). A função MUST ser a única forma de renderizar `apontamento.data`, `tarefa.data_criacao` e `projeto.data_criacao` no frontend; nenhum componente MUST reconstruir essa lógica inline.

#### Scenario: formatDateBR formata ISO para pt-BR
- **WHEN** o caller chama `formatDateBR("2026-06-11")`
- **THEN** a função MUST devolver `"11/06/2026"` (sem conversão de fuso, sem uso de `new Date`)

#### Scenario: formatDateBR devolve string vazia para entrada nula
- **WHEN** o caller chama `formatDateBR(null)` ou `formatDateBR(undefined)` ou `formatDateBR("")`
- **THEN** a função MUST devolver `""` (o caller decide o que exibir no lugar — em alguns sites é `"—"`, em outros é vazio)

#### Scenario: Não existe `new Date(...).toLocaleDateString('pt-BR')` em código de apresentação
- **WHEN** o bundle do frontend é gerado
- **THEN** `src/components/Tarefas/TarefaDetail.jsx`, `src/components/Projetos/ProjetosList.jsx` e `src/components/Dashboard/Dashboard.jsx` MUST NOT conter `new Date(tarefa.data_criacao).toLocaleDateString`, `new Date(ap.data).toLocaleDateString` ou `new Date(p.data_criacao).toLocaleDateString` (a string `".toLocaleDateString"` MUST aparecer em `src/utils/date.js` no máximo em comentário, não em código executável)

#### Scenario: Apenas sites conhecidos renderizam data de domínio
- **WHEN** o repositório é buscado por padrões de renderização de `data_criacao` ou `ap.data`
- **THEN** os únicos sites que MUST renderizar essas datas são `TarefaDetail.jsx` (linhas 172 e 234), `ProjetosList.jsx` (linha 128) e `Dashboard.jsx` (linha 200), e todos MUST usar `formatDateBR`

### Requirement: Helper `getTodayLocalISO` para default de data em formulário

O frontend MUST expor uma função `getTodayLocalISO()` em `src/utils/date.js` que devolve a data de **hoje no fuso do navegador** no formato `YYYY-MM-DD`. A função MUST ser usada como valor inicial do campo `data` em `ApontamentoForm`.

#### Scenario: Default do form é hoje no fuso local durante o dia (BRT)
- **WHEN** o usuário brasileiro abre `ApontamentoForm` entre 00h00 e 20h59 BRT
- **THEN** o campo `data` MUST estar pré-preenchido com a data de hoje no calendário de Brasília (formato `YYYY-MM-DD`)

#### Scenario: Default do form é hoje no fuso local à noite (BRT)
- **WHEN** o usuário brasileiro abre `ApontamentoForm` entre 21h00 e 23h59 BRT (quando UTC já virou o dia seguinte)
- **THEN** o campo `data` MUST estar pré-preenchido com a data de hoje no calendário de Brasília (formato `YYYY-MM-DD`), e MUST NOT mostrar a data de amanhã (que seria o resultado de `new Date().toISOString().split('T')[0]`)

#### Scenario: getTodayLocalISO não usa toISOString
- **WHEN** o bundle do frontend é gerado
- **THEN** `src/utils/date.js` MUST NOT usar `toISOString` para computar a data de hoje (o uso de `toISOString` para esse fim foi a causa do bug simétrico no default do form)

### Requirement: ApontamentoForm usa os helpers

O componente `ApontamentoForm` MUST usar `formatDateBR` e `getTodayLocalISO` exportados de `src/utils/date.js` para o estado inicial do campo `data` e para o reset do campo após salvar (linha 20 e linha 50 do arquivo atual).

#### Scenario: Inicialização usa getTodayLocalISO
- **WHEN** o componente `ApontamentoForm` é montado
- **THEN** o estado inicial de `data` MUST ser o resultado de `getTodayLocalISO()`, e MUST NOT ser o resultado de `new Date().toISOString().split('T')[0]`

#### Scenario: Reset após salvar usa getTodayLocalISO
- **WHEN** o usuário salva um apontamento com sucesso
- **THEN** o estado de `data` MUST ser resetado para `getTodayLocalISO()` (e não `new Date().toISOString().split('T')[0]`)
