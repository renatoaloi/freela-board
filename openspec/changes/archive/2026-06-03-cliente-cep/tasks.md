# Tasks: cliente-cep

## 1. Model + Migration

- [x] 1.1 Adicionar `cep: Mapped[str] = mapped_column(String(9), nullable=False)` ao `ClienteModel` em `backend/app/domain/models.py`
- [x] 1.2 Adicionar migration no lifespan (`backend/app/main.py`): `ALTER TABLE clientes ADD COLUMN cep VARCHAR(9) NOT NULL DEFAULT ''` com try/except

## 2. Schemas Pydantic

- [x] 2.1 Em `backend/app/domain/schemas.py`, adicionar `cep: str = Field(..., min_length=8, max_length=9)` no `ClienteCreate`
- [x] 2.2 Adicionar `cep: Optional[str] = Field(None, min_length=8, max_length=9)` no `ClienteUpdate`
- [x] 2.3 Adicionar `cep: str` no `ClienteResponse`
- [x] 2.4 Adicionar `cep: str` no `RelatorioClienteInfo`
- [x] 2.5 Adicionar `@field_validator("cep")` que remove não-dígitos, verifica 8 dígitos e formata como `XXXXX-XXX`

## 3. PDF Service + Template

- [x] 3.1 Em `backend/app/application/services/relatorio_pdf_service.py`, adicionar `"cep": cliente.cep` no `_build_context`
- [x] 3.2 Em `backend/app/templates/relatorio_pdf.html`, adicionar linha do CEP no bloco "Dados do Cliente" (formato `CEP XXXXX-XXX`)

## 4. Frontend — Formulário de Cliente

- [x] 4.1 Em `frontend/src/components/Clientes/ClienteForm.jsx`, adicionar `cep: ''` ao estado inicial
- [x] 4.2 Adicionar `cep: cliente.cep || ''` ao popular formulário em edição
- [x] 4.3 Adicionar campo input de texto para CEP no formulário (após campo de endereço)

## 5. Frontend — Listagem de Clientes

- [x] 5.1 Em `frontend/src/components/Clientes/ClientesList.jsx`, adicionar coluna "CEP" na tabela

## 6. Frontend — Relatório

- [x] 6.1 Em `frontend/src/components/Relatorios/RelatorioView.jsx`, adicionar CEP na exibição do endereço no formato `CEP XXXXX-XXX` (condicional: só exibir se não for vazio)

## 7. Testes

- [x] 7.1 Em `backend/tests/conftest.py`, adicionar `"cep": "04571-010"` ao `sample_cliente_data`
- [x] 7.2 Verificar que testes existentes continuam passando com o novo campo (`python -m pytest -v`)

## 8. Verificação

- [x] 8.1 Rodar `cd backend && pytest -v` e confirmar que todos os testes passam
- [x] 8.2 Rodar `docker compose build backend` e confirmar que a imagem builda sem erros
- [x] 8.3 Rodar `cd frontend && npm run build` e confirmar que o bundle compila sem erros
