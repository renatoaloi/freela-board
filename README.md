# FreelaBoard

Sistema de controle de horas trabalhadas em tarefas para freelancers. Gera relatórios mensais por cliente como memória de cálculo para emissão de nota fiscal.

## Funcionalidades

- **Dashboard** — Visão geral com quantidade de tarefas por status, horas por cliente (últimos 6 meses), melhores clientes/projetos e acesso rápido aos últimos projetos
- **Clientes** — Cadastro completo com dados do CNPJ para emissão de notas fiscais
- **Projetos** — Cadastro por cliente com valor por hora individualizado e descrição em markdown
- **Kanban** — Quadro visual com colunas Nova → Em andamento → Pronta → Fechada, filtrável por cliente e projeto
- **Tarefas** — Gerenciamento com descrição markdown, upload de anexos (PDFs, imagens) e lançamento de horas
- **Apontamentos** — Registro de múltiplos períodos de hora início/fim por tarefa, com total de horas calculado automaticamente
- **Relatórios** — Listagem dos relatórios já fechados, com visualização do detalhe (memória de cálculo por projeto, total de horas e valor total) e download do PDF
- **Fechamento mensal** — Escolha de cliente, mês/ano (e opcionalmente projeto) e seleção das tarefas prontas que entram no relatório; ao fechar, o relatório fica gravado com os totais congelados e as tarefas selecionadas vão para o status Fechada

## Regras de Negócio

- Usuário único, autenticação via `X-API-Key` (sem login)
- Valor por hora atrelado ao projeto (pode variar por projeto mesmo para o mesmo cliente)
- CNPJ deve ter 14 dígitos — validado no servidor
- Duplicidade de CNPJ retorna erro 409
- Total de horas calculado automaticamente no backend (hora fim - hora início)
- Relatório gerado a partir do fechamento do mês e gravado como snapshot (não é recalculado depois)
- Só entram no fechamento tarefas com status `pronta` que tenham apontamentos no mês/ano escolhidos; cada cliente admite um relatório por competência
- Após o fechamento, as tarefas selecionadas passam para o status `fechada` e saem do fluxo do Kanban
- O filtro de mês/ano do Kanban considera a data dos apontamentos da tarefa; tarefas sem nenhum apontamento aparecem em qualquer competência selecionada, e ficam ocultas apenas as que têm apontamentos em outro período
- Upload de arquivos organizado em pastas `storage/{cliente_id}/{projeto_id}/{tarefa_id}/`

## Entidades

| Entidade | Campos principais |
|---|---|
| **Cliente** | id (UUID), nome, razao_social, email, documento (CNPJ), endereco, complemento, bairro, cidade, estado |
| **Projeto** | id (UUID), cliente_id, titulo, descricao, data_criacao, valor_por_hora |
| **Tarefa** | id (UUID), projeto_id, titulo, descricao, status (nova/em_andamento/pronta/fechada), data_criacao, anexos (JSON) |
| **Apontamento** | id (UUID), tarefa_id, data, hora_ini, hora_fim, total_horas |
| **Relatório** | id (UUID), cliente_id, mes, ano, total_horas, total_valor, data_fechamento, dados (snapshot JSON com cliente, dados bancários e projetos/tarefas) |
| **RelatórioTarefa** | id (UUID), relatorio_id, tarefa_id (vínculo das tarefas que compõem o relatório) |

## Tecnologias

### Backend
- Python 3.12+
- FastAPI
- SQLAlchemy 2.0 (síncrono)
- Alembic
- Pydantic v2 + pydantic-settings
- SQLite
- pytest + httpx (TestClient)

### Frontend
- React 18
- Vite 5
- Tailwind CSS 3
- React Router 6
- Axios
- React Markdown + Remark GFM
- Heroicons

## Arquitetura

```
FreelaBoard/
├── backend/
│   ├── app/
│   │   ├── core/                  # Config, engine DB, auth, security
│   │   ├── domain/                # Models SQLAlchemy, Schemas Pydantic, Enums
│   │   ├── application/services/  # Regras de negócio
│   │   ├── infrastructure/repositories/ # Acesso a dados
│   │   └── api/v1/                # Controllers (rotas FastAPI)
│   ├── tests/                     # Testes automatizados
│   └── alembic/                   # Migrations
├── frontend/
│   └── src/
│       ├── components/            # Feature-based (Clientes, Projetos, Kanban...)
│       ├── services/api.js        # Axios + funções da API
│       └── App.jsx                # Rotas
└── storage/                       # SQLite + uploads de arquivos
```

## Instalação e Uso

### Pré-requisitos

- Python 3.12+
- Node.js 18+
- npm

### 1. Backend

```bash
# Acessar o diretório
cd backend

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor de desenvolvimento
uvicorn app.main:app --reload --port 8000
```

O servidor será iniciado em `http://localhost:8000`.  
A documentação interativa da API estará disponível em:
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Frontend

```bash
# Em outro terminal, acessar o diretório
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

O frontend será iniciado em `http://localhost:5173` com proxy configurado para redirecionar chamadas `/api` para o backend em `localhost:8000`.

### 3. Docker (opcional)

```bash
# Construir e iniciar todos os serviços
docker compose up --build

# Rodar em background
docker compose up --build -d

# Parar os serviços
docker compose down

# Ver logs
docker compose logs -f
```

A aplicação estará disponível em `http://localhost:8080`.
- O frontend é servido via Nginx na porta 8080 (host) → 80 (container)
- A API fica em `http://localhost/api/v1/`
- O Docker Compose aguarda o backend responder antes de iniciar o frontend (health check)
- Uploads e banco SQLite são persistidos no volume `storage`

## Autenticação

Todas as requisições à API precisam do header:

```
X-API-Key: freela-secret-key-2024
```

O frontend já envia este header automaticamente.  
Para alterar a chave, defina a variável de ambiente `API_KEY` no backend.

## API Endpoints

Todos sob o prefixo `/api/v1`:

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/dashboard` | Estatísticas do dashboard |
| **Clientes** | | |
| `GET` | `/clientes` | Listar todos |
| `GET` | `/clientes/{id}` | Obter por ID |
| `POST` | `/clientes` | Criar |
| `PUT` | `/clientes/{id}` | Atualizar |
| `DELETE` | `/clientes/{id}` | Remover |
| **Projetos** | | |
| `GET` | `/projetos` | Listar (filtro: `?cliente_id=`) |
| `GET` | `/projetos/{id}` | Obter por ID |
| `POST` | `/projetos` | Criar |
| `PUT` | `/projetos/{id}` | Atualizar |
| `DELETE` | `/projetos/{id}` | Remover |
| **Tarefas** | | |
| `GET` | `/tarefas` | Listar (filtros: `?projeto_id=&status=&mes=&ano=`) |
| `GET` | `/tarefas/{id}` | Obter por ID |
| `POST` | `/tarefas` | Criar |
| `PUT` | `/tarefas/{id}` | Atualizar (inclui status) |
| `DELETE` | `/tarefas/{id}` | Remover |
| **Apontamentos** | | |
| `GET` | `/apontamentos` | Listar (`?tarefa_id=`) |
| `POST` | `/apontamentos` | Criar (hora_ini/hora_fim em HH:MM) |
| `PUT` | `/apontamentos/{id}` | Atualizar |
| `DELETE` | `/apontamentos/{id}` | Remover |
| **Upload** | | |
| `POST` | `/upload/{tarefa_id}` | Enviar arquivo |
| `GET` | `/upload/{tarefa_id}/{filename}` | Baixar arquivo |
| `DELETE` | `/upload/{tarefa_id}/{filename}` | Remover arquivo |
| **Relatórios** | | |
| `GET` | `/relatorios` | Listar relatórios fechados |
| `GET` | `/relatorios/{id}` | Obter o relatório fechado (snapshot) |
| `GET` | `/relatorios/{id}/pdf` | Baixar PDF do relatório fechado |
| **Fechamento mensal** | | |
| `GET` | `/fechamentos/tarefas-elegiveis` | Listar tarefas prontas do período aptas a fechamento (`?cliente_id=&mes=&ano=&projeto_id=`) |
| `POST` | `/fechamentos` | Fechar o mês (body: `cliente_id`, `mes`, `ano`, `tarefa_ids`) |

## Testes

```bash
cd backend
pytest -v                        # Todos os testes
pytest tests/test_clientes.py -v # Testes específicos
```

Os testes usam um banco SQLite separado (`backend/test_freelaboard.db`) que é recriado a cada execução.

## Tema Visual

- Fundo azul escuro (`#0a1929`)
- Cards com efeito glassmorphism
- Acentos em neon verde água (`#00ffab`) e rosa (`#ff0066`)
- Totalmente responsivo (sidebar recolhível em mobile)
- Descrições em markdown com preview formatado

## Licença

MIT
