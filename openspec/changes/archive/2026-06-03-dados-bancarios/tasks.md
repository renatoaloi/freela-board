## 1. Backend — Model, Enum e Schemas

- [x] 1.1 Adicionar enum `PixKeyType` (cpf, cnpj, email, telefone) em `app/domain/enums.py`
- [x] 1.2 Adicionar modelo `DadosBancariosModel` em `app/domain/models.py` (UUID PK, campos bancários opcionais, timestamps)
- [x] 1.3 Adicionar schemas `DadosBancariosUpdate` (all optional), `DadosBancariosResponse`, `RelatorioDadosBancariosInfo` em `app/domain/schemas.py`

## 2. Backend — Repositório, Serviço e Controller

- [x] 2.1 Criar `DadosBancariosRepository` em `app/infrastructure/repositories/dados_bancarios_repository.py` com método `get_or_create()`
- [x] 2.2 Criar `DadosBancariosService` em `app/application/services/dados_bancarios_service.py` com métodos `get()` e `update()`
- [x] 2.3 Criar `DadosBancariosController` em `app/api/v1/dados_bancarios_controller.py` com endpoints `GET` e `PUT /api/v1/dados-bancarios`
- [x] 2.4 Registrar rota em `app/api/v1/api.py`

## 3. Backend — Migração

- [x] 3.1 Gerar migration Alembic: `alembic revision --autogenerate -m "add dados_bancarios"`
- [x] 3.2 Revisar e aplicar migration: `alembic upgrade head`

## 4. Backend — Integração com Relatório

- [x] 4.1 Modificar `RelatorioResponse` em `app/domain/schemas.py` para incluir `dados_bancarios: Optional[RelatorioDadosBancariosInfo]`
- [x] 4.2 Modificar `RelatorioService.generate()` para buscar dados bancários e incluir na resposta
- [x] 4.3 Modificar `_build_context()` em `relatorio_pdf_service.py` para incluir dados bancários
- [x] 4.4 Modificar `relatorio_pdf.html` para adicionar seção condicional "2. Dados Bancários" entre cliente e resumo (renumerar seções existentes)

## 5. Frontend — API e Componente de Configurações

- [x] 5.1 Adicionar `dadosBancariosAPI` em `src/services/api.js` com métodos `get()` e `update()`
- [x] 5.2 Criar `src/components/Configuracoes/DadosBancariosForm.jsx` com formulário de edição (banco, número, agência, conta, chave PIX, tipo)
- [x] 5.3 Criar `src/components/Configuracoes/Configuracoes.jsx` como página container com painéis (inicialmente só DadosBancariosForm)
- [x] 5.4 Adicionar rota `/configuracoes` em `src/App.jsx`
- [x] 5.5 Adicionar item "Configurações" no menu lateral em `src/components/Layout/Sidebar.jsx`

## 6. Frontend — Integração com Relatório

- [x] 6.1 Modificar `RelatorioView.jsx` para exibir card "Dados Bancários" entre cliente e resumo (condicional, apenas se preenchido)

## 7. Testes

- [x] 7.1 Adicionar fixture `created_dados_bancarios` em `backend/tests/conftest.py`
- [x] 7.2 Criar `backend/tests/test_dados_bancarios.py` com testes para GET (criação automática), PUT (atualização parcial/completa), validação de enum, autenticação
- [x] 7.3 Atualizar testes de relatório para verificar campo `dados_bancarios` na resposta
