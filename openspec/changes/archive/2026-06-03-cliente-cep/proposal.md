## Why

O cadastro de clientes não possui campo CEP, essencial para documentos fiscais e relatórios enviados a contadores. Sem o CEP, o endereço fica incompleto para notas fiscais e correspondências formais.

## What Changes

- Adicionar coluna `cep` na tabela `clientes` (VARCHAR(9), NOT NULL)
- Adicionar campo `cep` nos schemas Pydantic de criação, atualização, resposta e relatório
- Adicionar campo `cep` no formulário de cadastro de clientes (frontend)
- Exibir CEP em todos os lugares que mostram endereço: listagem de clientes, relatório na tela e PDF
- Atualizar fixtures de teste para incluir CEP
- Adicionarmigration no lifespan do app para criar a coluna em bases existentes

## Capabilities

### New Capabilities
- `clientes`: Cadastro de clientes com campos fiscais completos, incluindo CEP

### Modified Capabilities

*(nenhuma)*

## Impact

- **Model**: `ClienteModel` ganha campo `cep`
- **Schemas**: `ClienteCreate`, `ClienteUpdate`, `ClienteResponse`, `RelatorioClienteInfo` ganham campo `cep`
- **Migration**: `main.py` lifespan ganha `ALTER TABLE` para adicionar coluna em DBs existentes
- **Frontend**: `ClienteForm.jsx` ganha campo de input, `ClientesList.jsx` exibe CEP na tabela, `RelatorioView.jsx` exibe no endereço
- **PDF**: `relatorio_pdf.html` e `relatorio_pdf_service.py` incluem CEP na renderização
- **Testes**: `conftest.py` adiciona CEP no sample data
