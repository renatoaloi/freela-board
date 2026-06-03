## Why

O projeto exige Alembic para versionamento de schema (Project.md), mas atualmente as tabelas são criadas via `Base.metadata.create_all()` no startup e mudanças de schema são feitas com SQL puro no lifespan (`ALTER TABLE` com try/except). Isso não escala, não deixa rastro versionado e fere o requisito do projeto. Precisamos configurar e passar a usar Alembic de verdade.

## What Changes

- Configurar `env.py` para ler `sqlalchemy.url` do `settings.DATABASE_URL` (hoje está hardcoded no `alembic.ini`)
- Ativar `render_as_batch=True` no `env.py` para compatibilidade com SQLite
- Gerar migration inicial (`initial_schema`) refletindo o estado atual dos models (já incluindo a coluna `cep`)
- Substituir `Base.metadata.create_all()` + `ALTER TABLE` manual no `main.py` por chamada ao Alembic API (`alembic upgrade head`)
- Remover a gambiarra do `ALTER TABLE clientes ADD COLUMN cep` do lifespan
- Documentar o fluxo de trabalho com migrations para mudanças futuras

## Capabilities

### New Capabilities
- `db-migrations`: Versionamento de schema do banco via Alembic — setup, migration inicial, integração com startup da aplicação e workflow para changes futuras

### Modified Capabilities
Nenhuma. Nenhuma spec existente tem requisitos comportamentais alterados — a mudança é puramente de infraestrutura.

## Impact

- `backend/alembic/env.py` — modificado (URL dinâmica + batch mode)
- `backend/alembic.ini` — mantido como fallback, mas `env.py` sobrescreverá a URL
- `backend/alembic/versions/` — primeiro arquivo de migration adicionado
- `backend/app/main.py` — lifespan modificado (remover `create_all` + `ALTER TABLE`, adicionar `alembic upgrade head`)
- `backend/app/core/config.py` — inalterado (já tem `DATABASE_URL`)
- `backend/app/core/database.py` — inalterado
- `backend/app/domain/models.py` — inalterado
- `backend/` — pode ser necessário adicionar `alembic` às dependências se não estiver no `requirements.txt`
- Banco de dados existente: pode ser resetado (backup já feito pelo usuário)
