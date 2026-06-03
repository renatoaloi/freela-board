## Context

O sistema possui cadastro de clientes com endereço (logradouro, complemento, bairro, cidade, estado), mas sem CEP. O CEP é obrigatório para documentos fiscais (notas, relatórios para contadores) e completa o endereço do cliente.

O banco SQLite é auto-criado via `Base.metadata.create_all()` no lifespan — não há migrations com Alembic. A adição de coluna precisa de um `ALTER TABLE` no lifespan.

## Goals / Non-Goals

**Goals:**
- Adicionar CEP (VARCHAR(9), `XXXXX-XXX`) em todas as camadas: model, schemas, API, frontend, PDF
- Exibir CEP em todos os lugares que mostram endereço
- Manter compatibilidade com dados existentes (clientes sem CEP recebem string vazia)

**Non-Goals:**
- Não implementar consulta automática de CEP (ViaCEP)
- Não alterar a estrutura de tabelas além da coluna `cep`
- Não criar sistema de migrations com Alembic

## Decisions

### 1. Armazenamento: VARCHAR(9) com máscara

O CEP é armazenado no formato `XXXXX-XXX` (9 caracteres). A validação no schema Pydantic recebe 8 dígitos, remove não-dígitos e formata com hífen. Isso evita armazenar dados inconsistentes.

### 2. Migration no lifespan

O `ALTER TABLE` é executado no lifespan do FastAPI, antes do `create_all`. O comando ignora erro caso coluna já exista (SQLite não suporta `IF NOT EXISTS` para colunas — usamos try/except).

```
FastAPI lifespan
  ├── try: ALTER TABLE clientes ADD COLUMN cep VARCHAR(9) NOT NULL DEFAULT ''
  ├── except: coluna já existe (ignorar)
  └── Base.metadata.create_all()
```

### 3. Display do CEP

O CEP é exibido junto do endereço em todos os locais, no formato:

```
Rua Exemplo, 123 - Sala 4 - Centro
CEP 04571-010 - São Paulo/SP
```

## Risks / Trade-offs

| Risco | Mitigação |
|---|---|
| Clientes existentes sem CEP | Default `''` no ALTER TABLE; display condicional no frontend |
| SQLite não valida tamanho VARCHAR | Validação no schema Pydantic cuida do formato |
| ALTER TABLE pode falhar | try/except no lifespan ignora erro de coluna duplicada |
