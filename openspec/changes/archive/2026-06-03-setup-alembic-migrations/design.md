## Context

Atualmente o banco de dados é gerenciado por:

1. `Base.metadata.create_all()` no lifespan do FastAPI — cria tabelas que não existem, mas nunca altera colunas existentes
2. `ALTER TABLE` raw no lifespan para a coluna `cep` — gambiarra com try/except que silencia erros

O Alembic está instalado e configurado (env.py, alembic.ini, script.py.mako) desde o initial commit, mas `alembic/versions/` está vazio — nunca foi gerada uma migration. A URL do banco no `alembic.ini` está hardcoded, e o `env.py` não lê do `settings.DATABASE_URL`.

O banco é SQLite (suporte limitado a ALTER TABLE), e o usuário já fez backup, então podemos resetar o banco se necessário.

## Goals / Non-Goals

**Goals:**
- Alembic se torna a única fonte de verdade para schema do banco
- Migration inicial (`initial_schema`) reflete todos os modelos atuais (incluindo `cep`)
- Startup da aplicação roda `alembic upgrade head` via API Python
- `env.py` lê a URL do banco do `settings.DATABASE_URL` (não mais hardcoded)
- Batch mode ativado no `env.py` para compatibilidade SQLite com ALTER TABLE
- Workflow documentado para criar novas migrations

**Non-Goals:**
- Não alterar models, schemas, ou qualquer lógica de negócio
- Não adicionar rollback automatizado (SQLite não suporta downgrade confiável de colunas)
- Não criar script CLI separado — migrations rodam no startup via API
- Não modificar o sistema de testes (pytest continua resetando o banco via fixture)

## Decisions

| Decisão | Escolha | Alternativa | Rationale |
|---|---|---|---|
| **URL do banco** | `env.py` lê de `settings.DATABASE_URL` | Manter hardcoded no `alembic.ini` | Se `DATABASE_URL` for sobrescrita via env var, Alembic precisa enxergar |
| **Batch mode** | `render_as_batch=True` | Não usar | SQLite não suporta DROP COLUMN/ALTER COLUMN sem batch mode — migrations futuras vão precisar |
| **Como rodar migrations** | Alembic API (`command.upgrade`) no lifespan | `subprocess` chamando CLI | Mais limpo, integrado ao Python, sem dependência de CLI no startup |
| **Migration inicial** | Única migration (`initial_schema`) já com `cep` | Duas migrations (schema original + add cep) | O repositório é jovem (6 commits), não há dados históricos para preservar. Opção A combinada com o usuário |
| **Banco existente** | Resetar (`stamp head` ou deletar) | Preservar com `stamp` | Backup já feito. Mais simples começar do zero |
| **create_all()** | Remover do lifespan | Manter como fallback | Não pode ter duas fontes de verdade para schema |
| **ALTER TABLE cep** | Remover do lifespan | Manter | A migration inicial já inclui a coluna cep |

## Risks / Trade-offs

- **[SQLite batch mode]** O batch mode do Alembic recria tabelas inteiras para fazer ALTER TABLE — em tabelas grandes pode ser lento. → Mitigação: banco single-user local, dados modestos, baixo risco
- **[Startup lento]** Rodar migrations no startup adiciona latência na inicialização. → Mitigação: migrations são rápidas em SQLite vazio ou com poucas mudanças
- **[env.py divergir do .ini]** Se alguém rodar `alembic` CLI manual sem passar pela aplicação, pode usar URL errada. → Mitigação: `env.py` sobrescreve a URL, então `alembic upgrade head` via CLI também funciona corretamente
- **[Remoção de create_all()]** Se a migration inicial falhar, o banco não é criado. → Mitigação: a migration inicial é testada e versionada; erro é explícito (diferente do try/except silencioso atual)

## Migration Plan

1. Modificar `env.py`: ler URL do settings, ativar batch mode
2. Deletar `storage/freelaboard.db` (se existir)
3. Gerar migration inicial com `alembic revision --autogenerate -m "initial_schema"`
4. Rodar `alembic upgrade head` via CLI para verificar
5. Modificar `main.py`: substituir `create_all()` + `ALTER TABLE` por `alembic upgrade head`
6. Rodar `pytest -v` para verificar que os testes passam com o novo setup
7. Remover ALTER TABLE manual do lifespan

Rollback: restaurar backup do banco e reverter commits das alterações.
