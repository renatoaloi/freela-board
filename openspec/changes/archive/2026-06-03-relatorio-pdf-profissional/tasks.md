# Tasks: relatorio-pdf-profissional

## 1. Docker + Dependências

- [x] 1.1 Adicionar `weasyprint>=61.0` e `jinja2>=3.1.0` ao `backend/requirements.txt`
- [x] 1.2 Adicionar libs sistema do WeasyPrint ao `backend/Dockerfile`: `libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 shared-mime-info fonts-liberation`
- [x] 1.3 Buildar a imagem Docker (`docker compose build backend`) e confirmar que instala sem erros

## 2. Template HTML do PDF

- [x] 2.1 Criar `backend/app/templates/relatorio_pdf.html` com layout A4, margens 2.5cm, Liberation Sans, paleta cinza
- [x] 2.2 Incluir @page com numeração de páginas (`counter(page) / counter(pages)`) e data de geração
- [x] 2.3 Estruturar seções: cabeçalho centralizado, "1. DADOS DO CLIENTE", "2. RESUMO", "3. DETALHAMENTO POR PROJETO" com sub-tabela de tarefas
- [x] 2.4 Aplicar `page-break-inside: avoid` nas tabelas e blocos de projeto

## 3. PDF Service

- [x] 3.1 Criar `backend/app/application/services/relatorio_pdf_service.py` com classe `RelatorioPdfService`
- [x] 3.2 Implementar método `generate(relatorio_response: RelatorioResponse) -> bytes`: carrega template Jinja2, renderiza com contexto, converte via `HTML(string=...).write_pdf()`
- [x] 3.3 Formatar valores no template: horas com `formatHoras` (vírgula decimal), moeda com `formatMoeda` (R$), CNPJ com máscara (XX.XXX.XXX/XXXX-XX)
- [x] 3.4 Sanitizar nome do cliente para filename (slugify: remover acentos, espaços → hífen)

## 4. Endpoint PDF

- [x] 4.1 Em `backend/app/api/v1/relatorio_controller.py`, adicionar `GET /relatorios/pdf` com mesmos query params do endpoint JSON
- [x] 4.2 No handler, chamar `RelatorioService.generate()` e depois `RelatorioPdfService.generate()`
- [x] 4.3 Retornar `Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=..."})`
- [x] 4.4 Tratar erros: 404 se cliente não encontrado, 422 se params ausentes (já tratado pelo FastAPI), 401 se API key inválida

## 5. Frontend — Botão Baixar PDF

- [x] 5.1 Em `frontend/src/services/api.js`, adicionar `generatePdf(cliente_id, mes, ano)` em `relatoriosAPI` com `responseType: 'blob'`
- [x] 5.2 Em `frontend/src/components/Relatorios/RelatorioView.jsx`, adicionar botão "Baixar PDF" ao lado de "Imprimir" com ícone de download
- [x] 5.3 Implementar handler: chama `generatePdf`, obtém blob, cria `URL.createObjectURL`, dispara `<a download>`, revoga URL
- [x] 5.4 Tratar erro de download: exibir mensagem sem tentar baixar JSON como PDF

## 6. Testes

- [x] 6.1 Em `backend/tests/test_relatorios.py`, adicionar `test_relatorio_pdf_endpoint`: chama `GET /relatorios/pdf` com cliente válido e verifica `Content-Type == application/pdf` e corpo inicia com `%PDF-`
- [x] 6.2 Adicionar `test_relatorio_pdf_cliente_not_found`: chama com `cliente_id` inexistente e verifica 404
- [x] 6.3 Adicionar `test_relatorio_pdf_sem_apontamentos`: chama para mês/ano sem apontamentos e verifica PDF válido gerado

## 7. Verificação

- [x] 7.1 Rodar `cd backend && pytest -v` e confirmar que todos os testes passam (existentes + novos)
- [x] 7.2 Rodar `docker compose build backend` e confirmar que a imagem builda sem erros
- [x] 7.3 Rodar `cd frontend && npm run build` e confirmar que o bundle compila sem erros
- [x] 7.4 Teste manual: abrir frontend, gerar relatório, clicar "Baixar PDF", confirmar que o PDF baixa e abre corretamente com layout profissional
