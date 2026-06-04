## Why

O sistema não possui cadastro de dados bancários do freelancer, que são necessários para emissão de relatórios/invoices profissionais com informações de pagamento. Atualmente o relatório de horas não inclui dados bancários, obrigando o usuário a preencher manualmente ao exportar.

## What Changes

- **Nova tabela `dados_bancarios`** no banco de dados (global, sem FK), com colunas: `banco_nome`, `banco_numero`, `agencia`, `conta`, `chave_pix`, `tipo_chave_pix`
- **Novo endpoint** `GET/PUT /api/v1/dados-bancarios` — apenas leitura e edição do registro único (sem criar/excluir)
- **Nova página de Configurações** no frontend, com painel de edição de dados bancários (futuramente extensível para outras configs)
- **Relatório de horas** (JSON + PDF) passa a incluir os dados bancários entre os dados do cliente e o resumo
- **Novo item no menu lateral**: "Configurações", que leva à página de configurações

## Capabilities

### New Capabilities
- `dados-bancarios`: Cadastro único de dados bancários do freelancer (banco, agência, conta, chave PIX com tipo), com edição via interface própria

### Modified Capabilities
- `relatorios`: Resposta JSON do relatório MUST incluir campo opcional `dados_bancarios` com os dados bancários do freelancer
- `relatorios-pdf`: PDF do relatório MUST incluir seção de dados bancários entre os dados do cliente e o resumo

## Impact

**Backend:**
- `app/domain/models.py` — novo modelo `DadosBancariosModel`
- `app/domain/schemas.py` — novos schemas `DadosBancariosUpdate`, `DadosBancariosResponse`, `RelatorioDadosBancariosInfo`; modificar `RelatorioResponse` para incluir `dados_bancarios` opcional
- `app/domain/enums.py` — novo enum `PixKeyType`
- `app/infrastructure/repositories/dados_bancarios_repository.py` — novo repositório
- `app/application/services/dados_bancarios_service.py` — novo serviço
- `app/application/services/relatorio_service.py` — buscar dados bancários no `generate()`
- `app/application/services/relatorio_pdf_service.py` — incluir dados bancários no contexto do PDF
- `app/api/v1/dados_bancarios_controller.py` — novo controller
- `app/api/v1/api.py` — incluir rota
- `app/templates/relatorio_pdf.html` — nova seção "2. Dados Bancários", renumerar "2. Resumo" → "3. Resumo" e "3. Detalhamento" → "4. Detalhamento"
- Nova migration Alembic

**Frontend:**
- `src/services/api.js` — novo `dadosBancariosAPI`
- `src/components/Configuracoes/` — nova pasta com componentes de configuração
- `src/App.jsx` — nova rota `/configuracoes`
- `src/components/Layout/Sidebar.jsx` — novo item "Configurações" no menu
- `src/components/Relatorios/RelatorioView.jsx` — exibir dados bancários entre cliente e resumo

**BD:**
- Nova tabela `dados_bancarios` com 1 registro (singleton, criado automaticamente no primeiro GET)
