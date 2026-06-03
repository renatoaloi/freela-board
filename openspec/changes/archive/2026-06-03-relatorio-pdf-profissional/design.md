## Context

O sistema gera relatórios de horas por cliente/mês/ano via `GET /api/v1/relatorios` que retorna JSON. O frontend renderiza esse JSON em HTML e oferece `window.print()` — sem CSS de impressão, resultando em uma página web sem formatação profissional.

Cliente precisa de um PDF para enviar a contadores de empresas contratantes. O PDF deve:
- Ter layout A4, margens generosas, tipografia padrão da indústria (Liberation Sans ≈ Arial)
- Ser sóbrio: apenas preto, branco e cinza — sem logos ou cores
- Incluir numeração de páginas e data de geração
- Ser baixado com um clique no frontend

## Arquitetura

```
Browser                          Backend (Docker)
  │                                │
  │  GET /relatorios/pdf           │
  │  ?cliente_id=X&mes=5&ano=2026 │
  │───────────────────────────────►│
  │                                │
  │                         ┌──────┴──────────┐
  │                         │ RelatorioService │
  │                         │  .generate()     │
  │                         │  → RelatorioResp │
  │                         └──────┬──────────┘
  │                                │
  │                         ┌──────┴──────────┐
  │                         │ RelatorioPdfSvc │
  │                         │  Jinja2 template│
  │                         │  WeasyPrint     │
  │                         │  → PDF bytes    │
  │                         └──────┬──────────┘
  │                                │
  │  Content-Type: application/pdf │
  │  Content-Disposition: attachm. │
  │◄───────────────────────────────│
  │                                │
  │  download('relatorio-...pdf')  │
```

## Goals / Non-Goals

**Goals:**
- Gerar PDF A4 a partir do mesmo `RelatorioResponse` do endpoint JSON, sem duplicar lógica de negócio
- Layout profissional: margens 2.5cm, Liberation Sans, seções numeradas, tabelas limpas, numeração de páginas
- Download síncrono com um clique no frontend
- Processamento 100% server-side, sem depender de capacidades do navegador

**Non-Goals:**
- Não alterar o schema do relatório JSON existente (é compatível retroativo)
- Não adicionar logo ou identidade visual (o cliente não tem)
- Não gerar PDF assíncrono com fila/background job (a geração é rápida e síncrona)
- Não implementar impressão customizada no frontend (`@media print`) — o PDF substitui essa necessidade

## Decisions

### 1. WeasyPrint (HTML+CSS → PDF) em vez de ReportLab ou jsPDF

| Alternativa | Prós | Contras | Veredito |
|---|---|---|---|
| **WeasyPrint** | CSS familiar, layout declarativo, numeração de páginas nativa, roda no Docker | Requer libs sistema (libcairo, libpango) | ✅ Escolhido — contadores valorizam layout, CSS é mais produtivo |
| ReportLab | Zero deps externas | Layout programático em Python, verboso, difícil manter | ❌ Muito esforço para layout complexo |
| jsPDF/browser | Sem deps servidor | Qualidade varia por browser, sem download direto, depende do cliente | ❌ Foge do requisito server-side |
| Puppeteer (chrome headless) | Pixel-perfect | ~400MB de imagem, lentidão, complexidade | ❌ Pesado demais para uma única funcionalidade |

### 2. Template HTML com Jinja2

O WeasyPrint renderiza HTML+CSS. Jinja2 (já disponível via FastAPI/Starlette) permite template limpo com herança e formatação. O template fica em `backend/app/templates/relatorio_pdf.html` e recebe o `RelatorioResponse` como contexto.

### 3. Síncrono, não assíncrono

A geração do PDF com WeasyPrint leva <1s para relatórios típicos (dezenas de projetos/tarefas). Não há ganho real em tornar o endpoint assíncrono com fila de background. Permanece síncrono como o endpoint JSON existente.

### 4. Conteúdo do PDF

```
┌─────────────────────────────────────────────┐
│          RELATÓRIO DE HORAS                  │
│              Maio / 2026                     │
│                                              │
│  1. DADOS DO CLIENTE                         │
│  ─────────────────────────────────            │
│  Razão Social: Imediatum Tecnologia LTDA     │
│  Nome Fantasia: Imediatum                    │
│  CNPJ: 12.345.678/0001-90                    │
│  Endereço: Rua Exemplo, 123 - Centro         │
│            São Paulo/SP                      │
│  E-mail: contato@imediato.com                │
│                                              │
│  2. RESUMO                                   │
│  ─────────────────────────────────            │
│  Total de Horas                   42,50h     │
│  Valor Total                  R$ 6.375,00    │
│                                              │
│  3. DETALHAMENTO POR PROJETO                 │
│                                              │
│  Projeto: Site Imediatum                     │
│  Valor/hora: R$ 150,00                       │
│  Tarefas:                                    │
│  Tarefa                     │ Horas          │
│  ─────────────────────────────────────       │
│  Header e navegação        │ 10,00h          │
│  Página inicial            │ 10,00h          │
│  Total do projeto: 20,00h · R$ 3.000,00     │
│                                              │
│  ─────────────────────────────────────       │
│  Documento gerado em 03/06/2026 às 14:30     │
└─────────────────────────────────────────────┘
```

### 5. Nome do arquivo

`relatorio-{nome_cliente_slug}-{mes}-{ano}.pdf`

Ex: `relatorio-imediatum-05-2026.pdf`

## Risks / Trade-offs

| Risco | Mitigação |
|---|---|
| WeasyPrint falha no Docker se libs sistema ausentes | Adicionar deps explicitamente no Dockerfile + testar no CI |
| Caracteres especiais (acentos, CNPJ) | UTF-8 no template + fontes com cobertura Latin (Liberation Sans cobre) |
| Quebra de página no meio de tabela | CSS `page-break-inside: avoid` nas linhas da tabela |
| Geração lenta para relatórios muito grandes (100+ tarefas) | Profiling; se necessário, async eventual — mas improvável para o uso típico |
| PDF muito grande (>10MB) | WeasyPrint gera PDF otimizado por padrão; monitorar |

## Open Questions

*(nenhuma — todas as decisões cobertas acima)*
