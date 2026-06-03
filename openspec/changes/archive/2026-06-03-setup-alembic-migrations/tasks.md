## 1. Configurar env.py

- [x] 1.1 Modificar `backend/alembic/env.py` para importar `from app.core.config import settings` e usar `settings.DATABASE_URL` como `sqlalchemy.url`
- [x] 1.2 Ativar `render_as_batch=True` na configuração do context (offline e online)
- [x] 1.3 Verificar que `env.py` continua importando `from app.domain.models import *` para carregar metadata

## 2. Gerar migration inicial

- [x] 2.1 Deletar `storage/freelaboard.db` (backup já feito)
- [x] 2.2 Executar `alembic revision --autogenerate -m "initial_schema"` a partir de `backend/`
- [x] 2.3 Revisar o arquivo gerado em `backend/alembic/versions/` para confirmar que todas as tabelas (clientes, projetos, tarefas, apontamentos) e a coluna `cep` estão incluídas
- [x] 2.4 Executar `alembic upgrade head` via CLI para verificar que a migration aplica sem erros
- [x] 2.5 Deletar `storage/freelaboard.db` novamente (limpar após teste manual)

## 3. Modificar o lifespan do FastAPI

- [x] 3.1 Adicionar import do Alembic no `backend/app/main.py`: `from alembic.config import Config` e `from alembic import command`
- [x] 3.2 Substituir `Base.metadata.create_all(bind=engine)` por `alembic_cfg = Config("alembic.ini"); command.upgrade(alembic_cfg, "head")`
- [x] 3.3 Remover o bloco `try/except` do `ALTER TABLE clientes ADD COLUMN cep`
- [x] 3.4 Remover import de `text` do SQLAlchemy se não for mais usado
- [x] 3.5 Remover import de `Base` e `engine` se não forem mais usados diretamente (engine ainda pode ser necessário)

## 4. Verificar e testar

- [x] 4.1 Rodar `pytest -v` para garantir que todos os testes passam com o novo setup
- [x] 4.2 Rodar a aplicação (`uvicorn app.main:app --reload --port 8000`) e verificar que inicializa sem erros
- [x] 4.3 Verificar que o banco `storage/freelaboard.db` foi criado com as tabelas corretas via migration
- [x] 4.4 Confirmar que o endpoint `/api/v1/clientes` funciona (CRUD básico)
- [x] 4.5 Confirmar que o endpoint `/api/v1/relatorios` funciona (relatório com CEP)

## 5. Atualizar documentação

- [x] 5.1 Atualizar `AGENTS.md` com instruções do workflow de migrations para mudanças futuras de schema
