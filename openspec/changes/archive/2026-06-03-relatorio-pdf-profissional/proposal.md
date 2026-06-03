## Why

O relatório de horas atual é servido como JSON e renderizado no navegador com um botão "Imprimir" que chama `window.print()` sem CSS de impressão. O resultado é uma página web crus, sem layout profissional — inadequado para envio a contadores de empresas clientes, que esperam um documento PDF sóbrio, formatado, com fontes padrão da indústria e pronto para arquivamento.

## What Changes

- Novo endpoint `GET /api/v1/relatorios/pdf` que retorna um PDF gerado no servidor via WeasyPrint
- Template HTML profissional com layout A4, margens generosas, tipografia Liberation Sans, seções numeradas e numeração de páginas
- Botão "Baixar PDF" no frontend ao lado do botão "Imprimir" existente
- Download direto do PDF com `Content-Disposition: attachment`
- Dockerfile atualizado com dependências do WeasyPrint (libcairo2, libpango, fonts-liberation)
- Nenhuma alteração no schema de dados do relatório existente

## Capabilities

### New Capabilities
- `relatorios-pdf`: Geração server-side de PDF do relatório de horas com layout profissional A4

### Modified Capabilities

*(nenhuma — o schema do relatório existente não é alterado)*

## Impact

- **Backend**: Novo serviço `RelatorioPdfService`, novo template HTML, novo endpoint `/relatorios/pdf`
- **Frontend**: Novo botão "Baixar PDF" em `RelatorioView.jsx`, nova entry em `relatoriosAPI`
- **Dependências**: `weasyprint>=61.0` e `jinja2>=3.1.0` adicionadas ao `requirements.txt`
- **Docker**: Sistema deps adicionadas ao `backend/Dockerfile` (libcairo2, libpango, fonts-liberation, etc.)
- **Arquivos**: `backend/app/templates/relatorio_pdf.html` criado
